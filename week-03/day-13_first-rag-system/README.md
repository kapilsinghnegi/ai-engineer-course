# Build Your First RAG System

Earlier, we learned what RAG is, we also learned about embeddings and cosine similarity. Now we combine those concepts to build a working RAG system.

The main objective is to replace simple keyword-based retrieval with embedding-based retrieval, so the system can find relevant information even when the user's question uses different wording from the knowledge base.

## What we are building

Suppose a company has an internal knowledge base containing information about employee benefits.

One document says:

> Employees receive 24 days of paid leave per year.

A user asks:

> How much vacation do I get?

The keyword `"vacation"` does not appear in the document. A basic keyword-matching system may fail to retrieve the correct information.

But a human understands that vacation and paid leave are related concepts.

Our new RAG system will:

- Convert knowledge-base documents into embeddings.
- Convert the user's query into an embedding.
- Calculate the cosine similarity between the query and each document.
- Select the document with the highest similarity score.
- Pass that document as context to an LLM.
- Generate an answer based on the retrieved information.

`Knowledge base`: Company documents and employee policies -> `Embedding model`: Represent each document as a vector -> `Semantic retrieval`: Compare query and document vectors -> `LLM`: Answer using the retrieved context

The key lesson is that RAG remains the same overall architecture; we are improving its retrieval component.

## Project setup and dependencies

### Install the dependencies

```bash
uv add groq python-dotenv sentence-transformers numpy
```

Their roles are:

| Library                    | Purpose                                                 |
| -------------------------- | ------------------------------------------------------- |
| `groq`                     | Communicate with the Groq-hosted LLM                    |
| `python-dotenv`            | Load environment variables from a `.env` file           |
| `sentence-transformers`    | Generate embeddings for text                            |
| `numpy`                    | Work with numerical arrays                              |
| Cosine similarity function | Compare the query embedding against document embeddings |

### Configure the API key

Create a `.env` file:

```
GROQ_API_KEY=your_groq_api_key
```

## Creating the knowledge base

We'll create a small collection of company documents. Each line represents a piece of information that the system can retrieve.

For example:

```py
documents = [
    "Employees receive 24 days of paid leave per year.",
    "Employees can work from home.",
    "Employees receive a salary of 3000 per month.",
    "The company office is located in Delhi.",
    "Employees work five days per week.",
    "The company uses Python for backend development."
]
```

The important point is that the knowledge base is a collection of text documents. Each document will be converted into an embedding.

### Why use individual lines?

For this introductory example, each line is treated as one retrieval unit. That makes it easy to calculate a score for every line and select the best match.

In a larger application, documents are often divided into chunks before embedding. A chunk might contain a paragraph or a few hundred tokens rather than an entire document.

Chunking helps retrieve a focused piece of information instead of passing an unnecessarily large document to the LLM.

## Generating document embeddings

Load the embedding model:

```py
from sentence_transformers import SentenceTransformer
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
```

Now convert every knowledge-base document into a vector:

```py
document_embeddings = embedding_model.encode(documents)
print(document_embeddings.shape)
```

With six documents and the `all-MiniLM-L6-v2` model, the expected shape is:

```
(6, 384)
```

This means:

- There are six documents.
- Each document has a 384-dimensional embedding.

The model transforms the text into vectors. It does not directly generate the answer to the user's question.

Important: The document embeddings can be generated once and reused for multiple queries, as long as the underlying documents and embedding model remain unchanged.

## Generating the query embedding

Now consider the user's query:

```
query = "How much vacation do I get?"
```

The knowledge base contains `"paid leave"` rather than `"vacation"`. This is precisely the type of mismatch we want semantic retrieval to handle.

Convert the query into an embedding:

```py
query_embedding = embedding_model.encode(query)
```

Now we have:

- `document_embeddings`: vectors representing all the knowledge-base documents.
- `query_embedding`: the vector representing the user's question.

We can compare the query vector with each document vector.

The retrieval stage no longer depends on finding the exact word `"vacation"` in the documents.

## Implementing semantic retrieval

Here, retrieval function performs four main operations:

1. Iterate through the document embeddings.
2. Calculate the cosine similarity between each document and the query.
3. Associate each similarity score with its original document.
4. Sort the results by score and return the highest-scoring document.

Here is a clean implementation of that logic.

```py
def cosine_similarity(a,b):
    return np.dot(a,b)/ (np.linalg.norm(a) * np.linalg.norm(b))

def retrieve(query_embedding):    
    scores = []    
    for index, document_embedding in enumerate(document_embeddings):
       score = cosine_similarity(query_embedding, document_embedding)
       scores.append((score, documents[index]))
    scores.sort(reverse=True)    
    return scores[0]
```

### Run retrieval

```py
score, context = retrieve(query_embedding)
print("Score:", score)
print("Context:", context)
```

For the example query, the intended result is the document about employees receiving 24 days of paid leave.

### Why is this better than keyword matching?

The query uses the term `"vacation"`, while the document uses `"paid leave"`. The embedding model represents their learned semantic relationship numerically, and cosine similarity helps rank the relevant document.

The score is a ranking signal, not proof that the document is correct. We still need to inspect retrieval quality and handle cases where nothing relevant exists in the knowledge base.

## Connecting retrieval to the LLM

Once the relevant document has been retrieved, we need to send it to the LLM.

This is the generation stage of RAG.

The main change is that the function now receives the context returned by embedding-based retrieval rather than retrieving information through keyword matching itself.

Here is a representative implementation using the Groq Python client:

```py
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_llm(query, context):    
    response = client.chat.completions.create(
        model="YOUR_SUPPORTED_GROQ_MODEL",
        messages=[
            {
                "role": "system",
                "content": """Answer using the provided context. If the context does not contain the answer, say you do not have enough information. Context: {context}"""
            },
            {
                "role": "user",
                "content": query
            }
        ],
        temperature=0
    )    
    return response.choices[0].message.content
```

Now connect the two stages:

```py
query = "How much vacation do I get?"
query_embedding = embedding_model.encode(query)
score, context = retrieve(query_embedding)
answer = ask_llm(query, context)
print(answer)
```

A successful response should communicate that employees receive 24 days of paid leave per year.

The key distinction is:

- The embedding model finds relevant information.
- The LLM reads that information and generates the answer.

The embedding model does not itself write the final natural-language answer in this pipeline.

## Understanding the complete RAG pipeline

Let's connect all the components.

1. `Knowledge base`: Store the company's text documents
2. `Document embeddings`: Encode each document once
3. `User query` Example: “How much vacation do I get?”
4. `Query embedding`: Encode the question into a vector
5. `Retrieval`: Compare vectors and select relevant context
6. `LLM generation`: Generate an answer using retrieved context

The LLM can remain the same; we change how the system selects the information that gets passed to it.

## Why vector databases are needed

The instructor then explains why calculating every similarity score manually is not a scalable solution.

For six documents, the approach is straightforward:

- Store six document embeddings in memory.
- Compare the query against each of the six vectors.
- Sort the scores.
- Return the best result.

But a company's knowledge base may contain hundreds of thousands or millions of chunks.

### Problem 1: Memory usage

The memory occupied in the above example by its small collection of embeddings at roughly 7 KB, then instructor illustrates how storage requirements grow as the number of documents increases.

The underlying principle is correct: if the number of embeddings grows, their storage requirements grow too.

For an embedding with `d` dimensions, `N` vectors, and `b` bytes per numerical value, the approximate raw vector storage is:

```
Storage ≈ N × d × b
```

For example, using 384-dimensional embeddings stored as 32-bit floating-point values:

```
1,000,000 × 384 × 4 = 1.536 GB
```

That is approximately 1.536 GB of raw vector values alone. Actual memory usage can be higher due to indexing structures, metadata, document text, and application overhead.

### Problem 2: Search performance

The basic implementation calculates a similarity score for every document for every query.

If there are `N` document vectors and each has `d` dimensions, a brute-force comparison generally takes work proportional to `N × d` per query.

With millions of vectors, this can become expensive, especially when many users query the system at once.

### What does a vector database do?

A vector database stores vectors and supports similarity search, often with indexing and metadata filtering.

For example, [Qdrant](https://qdrant.tech/documentation/?utm_source=chatgpt.com) is a vector database that can store embeddings along with associated information.

Instead of manually keeping all vectors in a Python list and sorting every score yourself, you can store vectors in a vector database and query for the nearest matches.

| Manual Python retrieval                    | Vector database                                             |
| ------------------------------------------ | ----------------------------------------------------------- |
| Stores vectors in application memory       | Provides persistent vector storage                          |
| Can compare every vector for every query   | Can use indexes to accelerate nearest-neighbor search       |
| Requires you to manage the data structures | Provides search and data-management infrastructure          |
| Useful for learning and small datasets     | Useful when you need more scalable retrieval infrastructure |

A vector database does not automatically solve every performance problem. The appropriate index, search settings, hardware, and dataset size all matter.

### Does a vector database change RAG?

No. It changes how the retrieval component stores and searches vectors, not the fundamental RAG architecture.

The pipeline remains:

Query → Retrieve relevant context → Pass context to the LLM → Generate answer

The retrieval backend can be a simple Python implementation, a vector database, a keyword search engine, or a hybrid of these systems.

## Important questions

### Why do we generate document embeddings?

So that documents can be represented as vectors and compared with a user's query based on semantic similarity.

### Why do we generate a query embedding?

Because we need the query and the documents in the same embedding space to compare their vectors.

### Why do we store the score along with the document?

The score tells us how well a document matches the query. Keeping the original document alongside it allows us to retrieve the text associated with the score.

### Why do we sort the scores in descending order?

To put the highest-scoring document first and retrieve the best-ranked candidate.

### What is the limitation of retrieving only the highest-scoring document?

It always returns a candidate, even if every document is irrelevant. A threshold or another relevance check can help reject unsuitable results.

### Why use a vector database?

To store and search large collections of vectors more efficiently, with features such as indexing and metadata filtering.

### Does RAG require a vector database?

No. A small RAG system can use an in-memory list of embeddings and manual similarity calculations. A vector database becomes useful when storage, search performance, persistence, or operational requirements justify it.

### What is the difference between an embedding model and an LLM?

The embedding model converts text into vectors for retrieval. The LLM generates a response from the question and the retrieved context.

### What is the difference between similarity search and RAG?

Similarity search identifies relevant content. RAG uses retrieved content to augment the LLM's input and generate an answer.
