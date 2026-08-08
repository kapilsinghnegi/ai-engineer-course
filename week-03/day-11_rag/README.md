# RAG - Retrieval Augmented Generation

The lesson starts with a simple problem: an LLM can answer questions using information it has learned, but what happens when you ask about private company documents, internal code, or information that was never included in its training data?

RAG addresses this by retrieving relevant information from an external knowledge base and providing it to the LLM as context before generating an answer.

## What is RAG?

RAG stands for:

### R - Retrieval

Finding the relevant information from a knowledge base.

### A - Augmented

Enhancing the LLM's input with the retrieved information.

### G - Generation

Using the LLM to generate an answer based on the supplied context.

In simple words:

RAG retrieves relevant information, gives it to an LLM, and lets the LLM generate an answer using that information.

Imagine asking an AI assistant about your company's internal software architecture. A general-purpose LLM might not know the answer. With RAG, your application can retrieve the relevant architecture documentation and pass it to the model.

The model can then answer using that documentation instead of relying only on its existing knowledge.

## Why do we need RAG?

### Example A: Public information

Question: "How many subscribers does a YouTube channel have?"

An LLM may know the answer from information in its training data, or an application can retrieve the latest number from a public source.

### Example B: Private information

Question: "What is the internal architecture of a company's software?"

That information may exist only in the company's internal documentation. A general-purpose LLM cannot be expected to know it.

### Example C: Personal or custom information

Suppose you ask an AI assistant to evaluate your resume.

Without seeing your resume, it cannot reliably evaluate your actual skills and experience. Once you provide the resume, it has additional information to work with.

The same idea applies to RAG, except the information can be retrieved automatically from a knowledge base rather than manually supplied with every question.

### The underlying problem

LLM without relevant context

The model may lack the necessary information and could generate an incorrect or unsupported answer.

LLM with retrieved context

The model receives relevant information that can help it answer the specific question.

An important distinction: RAG does not guarantee correctness. The retrieved documents can be incomplete, outdated, irrelevant, or incorrect. The model can also misinterpret the context.

## The three components of a RAG system

A basic RAG system consists of three logical components.

1\. Knowledge Base

PDFs, text files, JSON, documentation

2\. Retrieval Software

Find information relevant to the question

3\. LLM

Read the retrieved context and generate an answer

The important insight from the episode is that the LLM does not need to read the entire knowledge base for every question. A separate retrieval component selects the relevant information first.

### What is a knowledge base?

A knowledge base is the collection of information that your application can search.

Examples include:

- Company architecture documentation
- Internal software engineering guides
- Product manuals
- PDFs and text files
- JSON data
- Resume information

For a company with thousands of documents, the knowledge base can contain a substantial amount of information.

## How RAG works

Let's use an example to understand this.

Suppose the knowledge base contains:

```
Chapter 1: How to play cricket
Chapter 2: How to play football
Chapter 3: How to play kho-kho
```

The user asks:

> How do I play cricket?

A basic RAG pipeline works like this:

Step 1 — User asks a question

"How do I play cricket?"

Step 2 — Retrieve relevant information

The retrieval component searches the knowledge base and selects the cricket chapter.

Step 3 — Supply the context

The selected cricket information is added to the LLM's input.

Step 4 — Generate the answer

The LLM uses the supplied context to answer the question.

This is the core idea behind Retrieval-Augmented Generation.

## Why not upload every document directly to the LLM?

Two initial approaches and their limitations discussed in the video are:

### Approach A: Put everything in the system prompt

You could write a few facts about your application or company in the system prompt.

This works for small amounts of information, such as:

- The application's purpose
- A few business rules
- Basic instructions for the assistant

However, it becomes impractical when you need to supply hundreds or thousands of pages of internal documentation.

### Approach B: Upload a complete PDF

You could create a PDF containing all the relevant company information and provide it to the LLM.

This can work for small tasks, such as analyzing one resume. But large organizations may have thousands of documents, including architecture specifications, implementation guides, testing documents, and user manuals.

Sending all of them with every question can cause problems:

- Context limits: The entire input may not fit in the model's context window.
- Token usage: Processing large amounts of text consumes more tokens.
- Cost: Repeatedly sending unnecessary documents can increase API costs.
- Efficiency: The model processes information unrelated to the current question.

The solution introduced in the video is to retrieve only the relevant information.

## Implementing a simple RAG system in Python

The instructor demonstrates the first, deliberately simplified iteration of RAG using a Python dictionary and keyword matching.

This is a teaching example, not a production-ready retrieval system.

### Step 1 — Create a knowledge base

```py
knowledge_base = {    
    "age": "The age of Pratyush is 25 years.",    
    "net_worth": "The net worth of Pratyush is 2000."
}
```

The dictionary represents our knowledge base. In a real application, the information might come from company documents, PDFs, or a database.

### Step 2 — Write a retrieval function

```py
def retrieve_info(question):    
    question = question.lower()    
    if "age" in question:        
        return knowledge_base["age"]    
    elif "networth" in question:        
        return knowledge_base["networth"]    
    return None
```

Let's understand the function.

For example:

```
print(retrieve_info("What is Pratyush's age?"))
```

Output:

```
The age of Pratyush is 25 years.
```

But this question causes a problem:

```
print(retrieve_info("How old is Pratyush?"))
```

Output:

```
None
```

Why? Because the function searches for the literal word `age`, which does not appear in the question.

The two questions have essentially the same meaning, but the retrieval function does not understand that relationship.

### Step 3 — Pass the retrieved information to the LLM

The next step is to modify the LLM call so it receives both the user's question and the retrieved context.

Conceptually:

```py
context = retrieve_info(question)
system_prompt = f"""
    Answer only based on this context:{context}. Do not hallucinate.
"""
```

Then include that system prompt in the messages sent to the model.

The model's job is now to generate an answer based on the retrieved information.

Important: The code above illustrates the retrieval and context-injection concepts from the lesson. It is a simplified excerpt; the actual LLM call also requires the appropriate client, model, and message structure.

### Step 4 — Restrict the answer to the context

The instructor uses instructions equivalent to:

```
Answer only based on this context.
Do not hallucinate.
```

Why is this useful?

Suppose the knowledge base contains the person's age but not their educational qualifications. The system should not invent those qualifications simply because the model may have general knowledge about similar people.

However, a prompt is not a guarantee against hallucination. A robust system should also handle missing context explicitly, for example by telling the model to say when the available information is insufficient.

## Problems with the first iteration of RAG

The first implementation demonstrates the core idea, but it also reveals why simple keyword matching is insufficient.

### Problem 1 — Different wording, same meaning

Consider these questions:

| Question                     | Expected retrieval |
| ---------------------------- | ------------------ |
| What is Pratyush's age?      | Age information    |
| How old is Pratyush?         | Age information    |
| Tell me how old Pratyush is. | Age information    |

The dictionary-based function only recognizes the keyword `age`.

It fails on the other phrasings because it does not understand semantic similarity.

### Problem 2 — Different names

The instructor also tests a question about a different person, such as Sumit.

If the knowledge base contains information about Pratyush, the system should not use Pratyush's information to answer a question about Sumit.

A basic keyword-based implementation does not reliably understand entities, relationships, or whether the retrieved information is relevant to the person being asked about.

### Problem 3 — Rigid retrieval rules

The function is built around manually defined conditions:

```py
if "age" in question:    
    ...
elif "networth" in question:    
    ...
```

Every new information category requires additional logic. Variations in wording create further problems.

This approach becomes difficult to maintain as the knowledge base and number of possible questions grow.

### Problem 4 — Retrieving relevant information is a separate engineering problem

Even when an LLM can generate excellent answers, the overall application can fail if the retrieval component does not supply the correct information.

A RAG system therefore depends on both:

- The quality of the retrieved context
- The LLM's ability to use that context correctly

A better generation prompt cannot reliably fix a retrieval component that selects the wrong document.

## Why vector databases are needed

The video introduces vector databases as part of the evolution from simple keyword-based retrieval to more sophisticated retrieval systems.

A vector database stores and searches vector representations of information. These representations are commonly called embeddings.

### Keyword search versus semantic search

Suppose a document contains:

> The employee is 25 years old.

A user asks:

> How old is the employee?

A literal keyword system might look for the word `age` and fail to find the relevant document.

A semantic retrieval system can use embeddings to represent the meaning of the question and document, helping it identify that both concern the employee's age.

Keyword-based retrieval

Matches explicit words or patterns.

`age` → no literal match

Semantic retrieval

Uses vector representations to help match meaning.

`How old?` → employee's age information

Semantic retrieval is not perfect either. Similarity does not guarantee that a document is factually correct or relevant enough to answer the question. Real-world systems often combine semantic search with keyword search, metadata filters, reranking, and other techniques.

### Where does Qdrant fit in?

Qdrant is an example of a vector database used in AI applications.

A modern RAG pipeline can use it to store embeddings of document chunks and retrieve relevant chunks for a user's question.

A typical production-oriented flow looks like this:

```
Documents
    |
    v
Extract text
    |
    v
Split into chunks
    |
    v
Generate embeddings
    |
    v
Store vectors in Qdrant
    |
    v
User asks a question
    |
    v
Search for relevant chunks
    |
    v
Pass retrieved context to LLM
    |
    v
Generate answer
```

The chunking, embedding, and vector-search steps are the broader implementation concepts that build on the foundation introduced in this episode.

## Important questions

### What is RAG?

RAG stands for Retrieval-Augmented Generation. It is a technique in which an application retrieves relevant external information and provides it to an LLM as context to generate an answer.

### Why do we need RAG if LLMs are already trained?

An LLM's training data may not contain private, proprietary, recent, or application-specific information. RAG lets an application retrieve such information at query time.

### What is a knowledge base?

A knowledge base is a collection of information that an application can search, such as documents, PDFs, JSON data, and internal documentation.

### What is the role of retrieval in RAG?

Retrieval identifies and returns information relevant to the user's question from the knowledge base.

### What does augmentation mean in RAG?

Augmentation means adding the retrieved information to the LLM's input so it can use that information while generating its answer.

### Why not send the entire knowledge base to the LLM?

Doing so can exceed context limits, increase token usage and cost, and waste computation on irrelevant information.

### What is the limitation of keyword-based retrieval?

It depends on explicit words or manually defined rules. It can fail when the user expresses the same meaning using different words.

### What is the difference between a knowledge base and an LLM?

The knowledge base stores the external information that the application can retrieve. The LLM processes the supplied context and generates a response.

### Does RAG eliminate hallucinations?

No. RAG can reduce unsupported answers by providing relevant context, but incorrect retrieval, incomplete information, or model errors can still produce hallucinations.

### What is a vector database used for in RAG?

A vector database stores and searches vector representations of information, enabling similarity-based retrieval that can identify related meanings even when exact keywords differ.

## Quick revision

| Concept          | Remember                                          |
| ---------------- | ------------------------------------------------- |
| RAG              | Retrieval-Augmented Generation                    |
| Knowledge base   | External information available to the application |
| Retrieval        | Find relevant information                         |
| Augmentation     | Add retrieved information to the model's input    |
| Generation       | Produce an answer using the context               |
| Keyword matching | Searches for explicit words or patterns           |
| Embeddings       | Vector representations of information             |
| Vector database  | Stores and searches vectors                       |
| Main objective   | Give the LLM relevant information at query time   |

## 11. Key takeaways

1. An LLM cannot be assumed to know your private or application-specific information.
2. RAG allows an application to supply relevant external information without requiring the model to be retrained for every new document.
3. The knowledge base can consist of PDFs, JSON files, dictionaries, or other information sources.
4. A separate retrieval component selects information relevant to the user's question.
5. The retrieved information is provided to the LLM as context.
6. The first implementation in the lesson uses Python dictionaries and keyword matching to demonstrate the concept.
7. Exact keyword matching is rigid and fails when questions use different wording.
8. Large knowledge bases make it impractical to send every document with every request.
9. Vector databases and embeddings support more flexible, meaning-based retrieval.
10. RAG improves the information available to the model, but it does not guarantee that every answer will be correct.