# Multi-tenant RAG with Qdrant — Qdrant Filters and HNSW

This lecture introduces two important ideas:

- HNSW: How a vector database can search efficiently through a large collection of vectors.
- Metadata filtering: How to restrict retrieval to relevant records using fields such as `category` and `is_active`.

## HNSW — efficient vector search

HNSW stands for Hierarchical Navigable Small World. It is a graph-based approximate nearest-neighbor (ANN) search algorithm used by vector databases, including Qdrant.

### The problem: linear search

Imagine a collection containing ten million vectors. For every incoming query, a brute-force approach could calculate similarity against every stored vector, then rank the results.

If there are `N` vectors and each has `d` dimensions, a straightforward scan has work roughly proportional to `(N × d)` per query.

For example:

- Number of vectors: 10,000,000
- Dimensions per vector: 384
- Each query may require examining millions of candidates in a brute-force scan.

This can become expensive at scale.

### Analogy: Traveling to Destination

The lecturer explains HNSW using a journey from a small town to a particular jewellery shop in Connaught Place, Delhi.

#### Linear search

Visit every street and shop one by one until the destination is found. This may eventually find the target, but it wastes effort exploring irrelevant locations.

#### HNSW

Follow connections between increasingly relevant regions, then search locally near the likely destination rather than examining every possible location.

The analogy illustrates the main idea: use connections between candidates to navigate toward promising regions of the vector space.

### How HNSW works conceptually

HNSW builds a graph in which vectors are represented by nodes connected to other nearby nodes. It uses multiple hierarchical layers:

1. Upper layers are relatively sparse and help the search move quickly across larger distances.
2. Lower layers contain more connections and allow more detailed exploration.
3. Search begins at an entry point and follows promising connections toward vectors closer to the query.
4. The algorithm explores a limited set of candidates instead of necessarily comparing the query against every vector.

![What is Vector Embedding? | IBM](https://images.openai.com/static-rsc-4/snyiwLzMoP0NtEOM_8WvhVEm8buuvb2ciO5wFgQ3djyzaaSCv13iSMYbDnJTB_9K1CAIxvQjLWYYlD5KvH5jbxwmeNud6v1C_z07D4n0MjtKNlTQNVaparGiPGT5N7_e-Fd6L2ZByzIiTS1YJHqjfQwfBfyBEiKyJk2BYnQBXcs?purpose=inline)


This is approximate nearest-neighbor search: it aims to find highly relevant neighbors efficiently, but it does not guarantee the exact same result as exhaustive search in every configuration.

### Why HNSW matters in Qdrant

HNSW helps Qdrant perform vector retrieval efficiently on large collections. You do not normally implement the graph-search algorithm yourself when using the standard Qdrant client.

The lecture's central takeaway is that HNSW is an internal search mechanism, whereas filters are conditions you supply to influence which records can be returned.

## Why metadata filtering matters

The lecture moves from a simple text file to a structured knowledge base, typically represented as JSON.

A policy record might look like this:

```
{
  "text": "Employees receive 24 vacation days per year.",
  "category": "leave",
  "is_active": true
}
```

Here, `text` contains the policy, `category` describes the type of policy, and `is_active` indicates whether the record is currently valid.

Imagine a collection with these records:

| ID | Text                                       | Category      | Active  |
| -- | ------------------------------------------ | ------------- | ------- |
| 1  | Employees receive 24 vacation days         | leave         | `true`  |
| 2  | Employees work 8 hours per day             | workplace     | `true`  |
| 3  | Employees receive 12 vacation days         | leave         | `false` |
| 4  | Travel expenses require receipts           | reimbursement | `true`  |
| 5  | Employees can claim eligible travel costs  | reimbursement | `true`  |
| 6  | Career development resources are available | career        | `true`  |

Now consider the query:

> How many days of vacation do I get?

A vector search may identify semantically relevant passages, but it could also retrieve an outdated policy or content from a different category. Metadata filters let you restrict retrieval to records satisfying conditions such as:

- `category` must be `leave`.
- `is_active` must be `true`.

This can improve retrieval precision, avoid outdated information, and reduce the candidate set considered by the search.

Important distinction: semantic similarity and metadata filtering solve different problems.

| Semantic vector search                         | Metadata filtering                                     |
| ---------------------------------------------- | ------------------------------------------------------ |
| Finds content with similar meaning             | Applies explicit conditions to fields                  |
| Uses query and document embeddings             | Uses payload values such as strings, booleans or dates |
| Answers “Which content is semantically close?” | Answers “Which records are allowed to match?”          |

In production RAG, these are often combined into one retrieval operation.

## Payload indexes in Qdrant

### What is a payload index?

A payload index is an index over a payload field, such as `category`, `is_active`, or `company`.

It helps Qdrant efficiently identify records that satisfy metadata filters. It is conceptually similar to indexing a column in a relational database, although the underlying implementations differ.

Suppose your collection contains millions of points. You repeatedly filter on `category`. Rather than relying on an inefficient scan of payload values, you can create an index on that field.

The lecture's analogy is a book index: instead of reading the whole book to locate a topic, consult the index to find the relevant pages.

### Creating payload indexes

For the lecture's `category` field, the code is:

```py
client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="category",
    field_schema=PayloadSchemaType.KEYWORD,
)
```

For the boolean `is_active` field:

```py
client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="is_active",
    field_schema=PayloadSchemaType.BOOL,
)
```

Common field schema types include:

| Schema type | Typical use                                             |
| ----------- | ------------------------------------------------------- |
| `KEYWORD`   | Exact-match strings, such as `leave` or `reimbursement` |
| `BOOL`      | Boolean values, such as `true` and `false`              |
| `INTEGER`   | Whole numbers                                           |
| `FLOAT`     | Decimal numbers                                         |
| `DATETIME`  | Date/time values                                        |

Use an index for fields you actually filter on and choose the schema appropriate to the data. Creating an index is not mandatory for every payload field.

### When should you create an index?

Create a payload index when you expect to filter on a field regularly and want Qdrant to optimize those conditions.

For example, an HR knowledge base may need indexes on:

- `category`
- `is_active`
- `company`

If employees must only retrieve policies belonging to their own company, the company filter can be essential for correctness and data isolation, not merely speed.

A filter by itself does not guarantee efficient filtering in every configuration. Indexes help, and Qdrant's query planner and filter-aware search mechanisms determine how retrieval is performed.

## `must`, `must_not`, and `should`

Qdrant's `Filter` object can combine conditions using three main clauses.

### `must` — every condition must match

Use `must` when all specified conditions are required.

```py
from qdrant_client.models import (Filter, FieldCondition, MatchValue,)
active_leave_filter = Filter(
    must=[
        FieldCondition(
            key="category",
            match=MatchValue(value="leave"),
        ),
        FieldCondition(
            key="is_active",
            match=MatchValue(value=True),
        ),
    ])
```

This filter selects points where:

- `category == "leave"` AND
- `is_active == True`

A point that satisfies only one of those conditions does not qualify.

### `must_not` — exclude matching conditions

Use `must_not` to exclude points matching a condition.

```py
exclude_reimbursement_filter = Filter(
    must_not=[
        FieldCondition(
            key="category",
            match=MatchValue(value="reimbursement"),
        )
    ])
```

This excludes reimbursement records. Other categories can still qualify.

### `should` — at least one alternative should match

Use `should` when one or more alternatives are acceptable.

```py
leave_or_workplace_filter = Filter(
    should=[
        FieldCondition(
            key="category",
            match=MatchValue(value="leave"),
        ),
        FieldCondition(
            key="category",
            match=MatchValue(value="workplace"),
        ),
    ])
```

This expresses the alternatives:

`category == "leave"` OR `category == "workplace"`.

### Quick comparison

| Clause     | Logical intuition | Use case                                      |
| ---------- | ----------------- | --------------------------------------------- |
| `must`     | AND               | Leave policy and active record                |
| `must_not` | NOT               | Exclude inactive or unwanted category records |
| `should`   | OR                | Leave policy or workplace policy              |

These are useful mental models for combining filter conditions. With multiple clauses, the conditions across the clauses work together: for example, `must` conditions still need to match even if a `should` alternative matches.

## Walkthrough of the Python code

### Part 1 — Imports and environment

```py
import json, os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, MatchAny, PayloadSchemaType,)
from sentence_transformers import SentenceTransformer
from groq import Groq
```

What the imports do:

- `os`: reads environment variables.
- `json`: loads structured JSON data.
- `load_dotenv`: loads variables from a local `.env` file.
- `Groq`: calls the language model.
- `SentenceTransformer`: converts text into embeddings.
- `QdrantClient`: connects to Qdrant.
- `Distance` and `VectorParams`: configure the vector collection.
- `PointStruct`: constructs a point containing an ID, vector and payload.
- `Filter`, `FieldCondition`, `MatchValue`, `MatchAny`: construct metadata filter conditions.
- `PayloadSchemaType`: specifies the type of a payload index.

`MatchAny` supports matching a field against one of several specified values. The supplied code imports it, although it does not actually use it.

The environment setup is:

```py
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
```

These values should be configured in `.env`:

```
GROQ_API_KEY=your_groq_api_key
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_URL=your_qdrant_cluster_url
```

### Part 2 — Connect to Qdrant Cloud

```py
client = QdrantClient( url=QDRANT_URL, api_key=QDRANT_API_KEY, )
```

This creates the client used for collection management, point uploads, indexing and retrieval.

### Part 3 — Create the collection

```py
COLLECTION_NAME = "knowledge filter"
EMBEDDING_SIZE = 384
client.create_collection(    
    collection_name=COLLECTION_NAME,    
    vectors_config=VectorParams(        
        size=EMBEDDING_SIZE,        
        distance=Distance.COSINE,    
    ),
)
```

The `384` dimensions correspond to the embeddings produced by `all-MiniLM-L6-v2`.

The cosine distance configuration tells Qdrant which distance measure to use when comparing vectors.

Destructive-operation warning: your complete code deletes the existing `knowledge` collection before recreating it. That is acceptable for a disposable tutorial environment, but can destroy stored data in a real application. Prefer explicit migrations or a separate development collection.

### Part 4 - Payload Indexes

```py
client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="category",
    field_schema=PayloadSchemaType.KEYWORD,
)
```

A payload index helps Qdrant efficiently filter records by a metadata field.

Here, `KEYWORD` is appropriate for exact categorical values such as "reimbursement" or "leave".

If you later filter on is_active, consider indexing it as a boolean field too:

```py
client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="is_active",
    field_schema=PayloadSchemaType.BOOL,
)
```

Create indexes for fields you actually filter on. An index does not itself filter results; the query must specify a filter.

### Part 5 — Load the JSON knowledge base

We'll create a structured `knowledge.json` file.

A record could look like this:

```
[
  {
    "text": "Employees receive 24 vacation days per year.",
    "category": "leave",
    "is_active": true
  },
  {
    "text": "Eligible employees can claim travel expenses.",
    "category": "reimbursement",
    "is_active": true
  }
]
```

Load it with:

```py
with open("knowledge.json", "r", encoding="utf-8") as f:    
    documents = json.load(f)
```

This assumes the file contains a JSON array of objects.

### Part 6 — Create embeddings from text

```py
model = SentenceTransformer("all-MiniLM-L6-v2")
texts = [document["text"] for document in documents]
embeddings = model.encode(texts)
```

Only the `text` field is embedded. The category and active-status fields remain metadata used for filtering.

That separation is intentional:

- `text` → semantic representation.
- `category` and `is_active` → filterable payload fields.

### Part 7 — Create points with structured payloads

```py
point = PointStruct(    
    id=i + 1,    
    vector=embeddings[i].tolist(),    
    payload=documents[i],
)
```

The payload here is the complete JSON object. It therefore contains `text`, `category` and `is_active`.

That difference is important. A filter on `category` will only work if the uploaded payload actually contains that field.

### Part 8 — Upload points

```py
client.upsert(    
    collection_name=COLLECTION_NAME,    
    points=points,
)
```

`upsert` inserts new points or updates existing points with matching IDs. It does not mean that the collection is automatically recreated each time.

### Part 8 — Search with a filter

```py
def search(query, top_k=3):    
    query_vector = model.encode(query)    
    results = client.query_points(        
        collection_name=COLLECTION_NAME,        
        query=query_vector,        
        limit=top_k,        
        with_payload=True,    
    ).points    
    return results
```

```py
def search_with_filter(query, query_filter=None, top_k=3):    
    query_vector = model.encode(query).tolist()    
    results = client.query_points(        
        collection_name=COLLECTION_NAME,        
        query=query_vector,        
        limit=top_k,        
        with_payload=True,        
        query_filter=query_filter,    
    ).points    
    return results
```

The second function accepts `query_filter`, which is passed to Qdrant's query operation. When a filter is supplied, Qdrant applies its conditions during retrieval rather than simply returning the unrestricted top results.

### Part 9 — Build the filter

Your example uses:

```py
reimbursement_filter = Filter(    
    must=[        
        FieldCondition(            
            key="category",            
            match=MatchValue(value="reimbursement"),        
        )    
    ])
```

This means: retrieve only points whose `category` payload field equals `"reimbursement"`.

### Part 10 — Generate an answer using Groq

The code constructs a prompt containing the retrieved context and question:

```py
def ask_llm(question, context):    
    prompt = f"""    
        Answer the question using only the information provided below.    
        Context: {context}    
        Question: {question}    
        If the answer is not present in the context, answer:    
        "I can't provide the answer to this question based on the information provided."    """    
        response = groq_client.chat.completions.create(        
            model="openai/gpt-oss-120b",        
            messages=[            
                {"role": "user", "content": prompt},        
            ],    
        )    
        return response.choices[0].message.content
```

## End-to-end version

There is one significant inconsistency in your supplied code: you define `search_with_filter()` and a filter, but the final RAG pipeline calls `search()` instead. That means the final answer is generated using unfiltered retrieval.

The following version combines the ideas correctly, adds a payload index, and applies the filter to the actual question.

Example assumes `knowledge.json` contains a list of objects with `text`, `category`, and `is_active` fields.

```py
import os
import json

from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
)

# 1. Environment
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")

if not all([GROQ_API_KEY, QDRANT_API_KEY, QDRANT_URL]):
    raise ValueError("Missing required API key or Qdrant URL.")

# 2. Connect to services
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

COLLECTION_NAME = "knowledge"
EMBEDDING_SIZE = 384

# 3. Load knowledge
with open("knowledge.json", "r", encoding="utf-8") as f:
    documents = json.load(f)

if not documents:
    raise ValueError("knowledge.json contains no documents.")

# Validate required fields
for doc in documents:
    if not all(key in doc for key in ("text", "category", "is_active")):
        raise ValueError("Each record needs text, category, and is_active.")

# 4. Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

texts = [doc["text"] for doc in documents]
embeddings = model.encode(texts)

# 5. Create collection
# Tutorial reset only: deletes existing data in this collection.
if client.collection_exists(COLLECTION_NAME):
    client.delete_collection(COLLECTION_NAME)

client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=EMBEDDING_SIZE,
        distance=Distance.COSINE,
    ),
)

# 6. Index fields used by filters
client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="category",
    field_schema=PayloadSchemaType.KEYWORD,
)

client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="is_active",
    field_schema=PayloadSchemaType.BOOL,
)

# 7. Create and upload points
points = [
    PointStruct(
        id=i + 1,
        vector=embeddings[i].tolist(),
        payload=doc,
    )
    for i, doc in enumerate(documents)
]

client.upsert(
    collection_name=COLLECTION_NAME,
    points=points,
)

# 8. Filtered semantic search
def search(query, query_filter=None, top_k=3):
    query_vector = model.encode(query).tolist()

    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=query_filter,
        limit=top_k,
        with_payload=True,
    )

    return response.points

# 9. Construct filter for current leave policies
leave_filter = Filter(
    must=[
        FieldCondition(
            key="category",
            match=MatchValue(value="leave"),
        ),
        FieldCondition(
            key="is_active",
            match=MatchValue(value=True),
        ),
    ]
)

# 10. Ask the question
def ask_llm(question, context):
    prompt = f"""
        Answer using only the supplied context.
        If the context does not contain the answer, say:
        "I can't provide the answer based on the information provided."

        Context:
        {context}

        Question:
        {question}
    """

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content

question = "How many days of vacation do I get?"

results = search(
    query=question,
    query_filter=leave_filter,
    top_k=3,
)

context = "\n".join(
    point.payload["text"]
    for point in results
    if point.payload and point.payload.get("text")
)

if not context:
    print("No matching policy was found.")
else:
    answer = ask_llm(question, context)
    print("Final Answer:")
    print(answer)    
```

## Important corrections and engineering caveats

These points are worth understanding beyond simply following the lecture.

### A. HNSW is approximate, not a guarantee of exact results

HNSW is designed to balance search speed, recall and resource usage. It does not guarantee that every search returns the mathematically exact nearest neighbors. Its behavior depends on configuration and query settings.

### B. Filters are not a substitute for authorization

A filter can restrict results by `company`, `user_id` or another field, but a secure application must enforce the correct filter server-side. Do not trust a client to provide its own access-control conditions.

### C. Filter before generating the answer

The supplied code's final pipeline calls `search()` without a filter. If you intend to enforce a category or active-status restriction, call `search_with_filter()` or pass the filter to the unified `search()` function, as in the corrected example.

### D. Create indexes for the fields you filter on

The lecture demonstrates indexing `category`. If you also frequently filter on `is_active`, consider indexing that field as well. The payload must contain correctly typed values for these conditions to match.

### E. Metadata must reflect the actual policy

Filtering on `is_active=True` only helps if the source data correctly marks old policies as inactive. It is not enough to add the field; the ingestion and update process must maintain it accurately.

### F. Top-k is not a relevance guarantee

`top_k=3` means the search returns up to three candidates, subject to the query and filter. It does not mean all three candidates are sufficiently relevant. Evaluate scores, consider a relevance threshold where appropriate, and handle empty or weak retrievals.

### G. The LLM can still make mistakes

A prompt that says “use only the context” is helpful, but not a guarantee against hallucinations. Test the answer against the retrieved source, and return citations that are linked to actual retrieved passages.

## Important questions

### What is HNSW?

HNSW stands for Hierarchical Navigable Small World. It is a graph-based approximate nearest-neighbor algorithm used to find similar vectors efficiently in high-dimensional vector spaces.

### Why is HNSW preferred over brute-force vector search for large datasets?

Brute-force search compares the query with every vector. HNSW navigates a graph to explore promising candidates, generally reducing the amount of work required at the cost of potentially missing some exact nearest neighbors.

### What is a payload in Qdrant?

A payload is data associated with a point, such as text, category, status, URL or timestamp. It can be returned with search results and used in filtering.

### What is a payload index?

It is an index on a payload field that helps Qdrant efficiently evaluate filters on that field.

### Explain `must`, `must_not` and `should`.

`must` requires all listed conditions to match, `must_not` excludes points matching those conditions, and `should` represents alternatives where at least one condition should match.

### Why embed only the text instead of the whole JSON object?

The text contains the semantic content to search. Category and status are structured metadata, so they can be used for explicit filtering without being mixed into the semantic embedding.

### Does Qdrant use HNSW because you explicitly call it in your code?

No. In this example, you configure a vector collection and use the Qdrant query API. Qdrant manages its vector-search implementation; you do not manually construct the HNSW graph.

### What is the difference between vector search and filtered vector search?

Ordinary vector search ranks candidates by vector similarity. Filtered vector search additionally restricts eligible results using conditions on payload fields.