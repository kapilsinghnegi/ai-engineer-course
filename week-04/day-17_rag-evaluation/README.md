# Episode 17: RAG Evaluation — Measuring Whether Your RAG System Actually Works

## What is RAG evaluation?

**RAG evaluation is the process of measuring whether a Retrieval-Augmented Generation system retrieves the right information and produces a useful, context-supported, factually correct answer.**

Building a RAG system is only the first step. You also need to establish whether it works reliably—and, when it fails, identify *which part* is responsible.

Think of a RAG system as a student taking an exam:

- **Knowledge base:** the source material or textbook.
- **Retriever:** the teacher selecting relevant notes for the question.
- **Retrieved context:** the notes given to the student.
- **LLM:** the student writing the answer.
- **Evaluation:** checking both the notes and the student's final answer against what should be correct.

Passing a single test question does not prove the whole system works. Evaluation means testing multiple questions systematically.

### The RAG pipeline

1. **Knowledge base**

Company policies in `knowledge.json`

2. **Embedding model → Qdrant**

Store document vectors and payloads

3. **Question → Retrieval**

Retrieve top-k relevant documents

4. **LLM → Answer**

Generate an answer using the retrieved context

5. **Evaluation**

Measure retrieval quality and answer quality

The key idea from this episode is that **an incorrect answer does not automatically mean the LLM is the problem**. The source data, retrieval step, or answer generation step may be responsible.

## The three main failure points

**Failure 1: Incorrect knowledge**

The source contains wrong or outdated information. Even a perfect retriever and LLM may return the wrong answer because the underlying data is wrong.

*Fix:* verify the source documents and the knowledge base.

**Failure 2: Incorrect retrieval**

The knowledge base contains the right information, but the retriever returns irrelevant chunks or misses important ones.

*Fix:* inspect retrieved chunks, embedding quality, `top_k`, similarity thresholds, chunking, and filters.

**Failure 3: Incorrect answer generation**

The retriever returns appropriate context, but the LLM misinterprets it, invents information, or answers a different question.

*Fix:* improve the prompt, grounding instructions, answer format, or model configuration.

These failure points explain why RAG evaluation needs multiple metrics instead of a single pass/fail result.

## Golden dataset and ground truth

A **golden dataset** is a collection of test questions with human-verified expected answers. It is similar to the test cases used to evaluate a DSA solution.

Your code defines five test cases:

| ID | Question | Ground-truth answer |
|---:|---|---|
| 1 | How many days of holidays do I get? | 24 days of paid leave per year |
| 2 | What's your work-from-home policy? | Office on Tuesday, Wednesday and Thursday |
| 3 | How much internet reimbursement do employees receive? | ₹2,000 per month |
| 4 | When do promotions happen? | March and September |
| 5 | What is the gym benefit? | ₹3,000 per month for gym memberships or fitness apps |

These answers are based on the supplied `knowledge.json`.
Each test case has three fields:

```python
{
    "id": 1,
    "question": "How many days of holidays do I get?",
    "ground_truth": "Employees in India receive 24 days of paid leave per year.",
    "expected_information": "The retrieved context should contain information about 24 days of paid leave."
}
```

- **`id`** — identifies the test case.
- **`question`** — the query submitted to the RAG system.
- **`ground_truth`** — the reference answer used to evaluate factual correctness and context coverage.
- **`expected_information`** — describes what information should be retrieved or included in the answer.

### Ground truth vs. expected information

They serve related but different purposes.

- **Ground truth:** What should the correct answer be?
- **Expected information:** What information do we expect to see in the retrieved context or final response?

For example:

- Question: “How much internet reimbursement do employees receive?”
- Ground truth: “Employees receive Rs 2000 per month for home internet reimbursement.”
- Expected information: The context should contain the ₹2,000 monthly reimbursement policy.

Ground truth is a reference for correctness. Expected information can help define retrieval or answer-quality requirements.

**Important code observation:** Your current evaluation code defines `expected_information`, but does not actually use that field in any evaluation function. The code instead uses `ground_truth` for context recall and answer correctness.

A golden dataset should cover the important policies, different ways users may phrase questions, missing-information cases, and questions that could retrieve misleadingly similar documents. Five examples are enough to demonstrate the method, but usually not enough to establish production reliability.

## The five evaluation metrics
We'll evaluate the RAG system using five metrics: **context precision, context recall, faithfulness, answer relevancy, and answer correctness.**

The first two focus on retrieval; the remaining three focus on the generated answer.

**1. Context precision**

Retrieval quality · How much of what was retrieved is relevant?

It measures the proportion of retrieved chunks that are relevant to the question.

Example: Qdrant returns three chunks, and two are relevant. `(0.67%)`

A low score indicates that retrieval is bringing back too much irrelevant information.

**2. Context recall**

Retrieval quality · Did we retrieve enough of the necessary information?

It measures whether the retrieved context contains the information needed to answer the question.

In the episode's example, suppose two chunks are necessary to answer a question, but only one is retrieved. The conceptual recall is: `50%`

A low score indicates that relevant information may be missing from the retrieved context.

**3. Faithfulness**

Answer quality · Is the answer supported by the retrieved context?

A faithful answer does not introduce unsupported claims that are absent from, or contradict, the retrieved context.

Example:

- Context: “Employees receive 24 days of paid leave per year.”
- Answer: “Employees receive 30 days of paid leave per year.”

The answer is not faithful to the context because it changes the stated number.

**4. Answer relevancy**

Answer quality · Does the answer actually address the question?

Example:

- Question: “When do promotions happen?”
- Answer: “A promotion is an advancement to a higher role.”

The definition may be true, but it does not answer *when* promotions happen. It is therefore irrelevant to the user's specific question.

**5. Answer correctness**

Answer quality · Is the answer factually correct against the ground truth?

Example:

- Ground truth: “Employees receive ₹2,000 per month for home internet reimbursement.”
- Answer: “Employees receive ₹1,000 per month.”

The answer is factually incorrect against the reference answer.

### The critical distinction: faithfulness vs. correctness

These two are related, but they measure different things.

| Situation | Faithfulness | Correctness |
|---|---|---|
| Context is correct and answer matches it | High | High |
| Context is wrong and answer repeats it accurately | High | Low |
| Context is correct but answer contradicts it | Low | Potentially low |
| Answer is factually right but introduces unsupported information | May be low | May be high |

For example, suppose the true company policy is 24 days of paid leave, but the knowledge base incorrectly says 20 days.

- The LLM reads the retrieved context and answers “20 days.”
- It is **faithful** because it followed the context.
- It is **incorrect** because the real policy says 24 days.

This distinction helps identify the likely failure point: if the answer faithfully follows bad information, investigate the source data and retrieval before blaming the LLM.

One caveat: correctness and faithfulness are not guaranteed to be perfectly independent in every evaluation setup. Their scores depend on the reference answer, the context, and the evaluator's judgment.

### Precision and recall: the other important distinction

| Metric | The question it answers |
|---|---|
| Context precision | Of the chunks retrieved, how many were useful? |
| Context recall | Of the information needed, how much was retrieved? |

A retriever can have high precision but low recall: it returns one relevant chunk and misses another essential chunk.

It can also have high recall but low precision: it retrieves all the necessary information, but includes many irrelevant chunks too.

In the provided code, precision is calculated as a fraction of relevant retrieved documents, whereas context recall is assigned a graded LLM-judge score. They are therefore related to the same concepts, but the implementations are not mathematically identical measures.

## Understanding the code step by step

Your implementation reuses the Qdrant + Sentence Transformers + Groq RAG pipeline and adds a golden dataset and five evaluation functions.

### Step 1 — Imports and environment variables

```python
import os, json
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    PayloadSchemaType,
)
from sentence_transformers import SentenceTransformer
from groq import Groq
```

Each library has a specific role:

- `os`: reads environment variables.
- `json`: loads the knowledge base and parses structured judge responses.
- `dotenv`: loads variables from `.env`.
- `QdrantClient`: connects to the vector database.
- `VectorParams`, `Distance`: configure vector size and similarity.
- `PointStruct`: represents a stored vector and its payload.
- `PayloadSchemaType`: defines the category index type.
- `SentenceTransformer`: converts documents and queries into embeddings.
- `Groq`: calls the LLM for answer generation and evaluation.

### Step 2 — Create the Qdrant collection

```python
COLLECTION_NAME = "rag_eval"
EMBEDDING_SIZE = 384

if client.collection_exists(COLLECTION_NAME):
    client.delete_collection(COLLECTION_NAME)

client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=EMBEDDING_SIZE,
        distance=Distance.COSINE
    ),
)
```

- `rag_eval` is the collection used for this evaluation run.
- `384` matches the output dimension of `all-MiniLM-L6-v2`.
- `Distance.COSINE` configures cosine distance/similarity for vector retrieval.
- The existing collection is deleted and recreated so the example starts from a clean state.

**Production caution:** deleting a collection is destructive. A production system should not delete an existing collection automatically just to run an evaluation. Use a dedicated test collection or a safe setup/migration strategy.

### Step 3 — Create the category payload index

```python
client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="category",
    field_schema=PayloadSchemaType.KEYWORD,
)
```

Your documents contain categories such as `leave_policy`, `work_policy`, `reimbursement`, and `promotion`.

A keyword payload index supports efficient filtering on categorical metadata. The current `search()` function does not apply a category filter, but the index prepares the collection for such filtering.

### Step 4 — Load knowledge and create embeddings

```python
with open("knowledge.json", "r", encoding="utf-8") as f:
    documents = json.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")

texts = [document["text"] for document in documents]
embeddings = model.encode(texts)
```

The code:

1. Loads the policy objects from `knowledge.json`.
2. Extracts each document's `text`.
3. Encodes the text into a vector.
4. Keeps the original object—including its category—for the payload.

The embedding model must be compatible between document indexing and query-time retrieval. Using a different, incompatible embedding model for queries can degrade retrieval quality.

### Step 5 — Store points in Qdrant

```python
points = []

for i, embedding in enumerate(embeddings):
    point = PointStruct(
        id=i + 1,
        vector=embedding.tolist(),
        payload=documents[i],
    )
    points.append(point)

client.upsert(
    collection_name=COLLECTION_NAME,
    points=points,
)
```

Each Qdrant point contains:

- A unique ID.
- The document's vector.
- The original payload, including `category` and `text`.

The `upsert()` call inserts the points or updates points with matching IDs.

### Step 6 — Retrieve context for a question

```python
def search(query, top_k=2):
    query_vector = model.encode(query).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    ).points

    return results
```

The query follows the same embedding-and-search process as document retrieval:

1. Convert the user's question into a vector.
2. Search Qdrant using that vector.
3. Return up to `top_k` results.
4. Include payloads so the application can access the retrieved text.

During evaluation, the code calls:

```python
results = search(question, top_k=3)
```

This means the evaluation retrieves up to three documents per test question.

### Step 7 — Generate the answer

```python
def ask_llm(question, context):
    prompt = f"""
    Answer using only the supplied context. Don't hallucinate.
    If the context does not contain the answer, say:
    "I can't provide the answer based on the information provided."

    Context: {context}
    Question: {question}
    """

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    return response.choices[0].message.content
```

This prompt asks the LLM to:

- Use the retrieved context rather than general knowledge.
- Avoid unsupported claims.
- Admit when the context does not contain the answer.

This is an important grounding instruction, but a prompt alone cannot guarantee that the model will always comply. Faithfulness evaluation helps check its actual behavior.

### Step 8 — Ask an LLM to act as a judge

```python
def llm_judge(prompt):
    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0,
    )

    answer = response.choices[0].message.content
    return json.loads(answer)
```

Instead of having a human manually assess every output, the code asks an LLM to score the results.

`temperature=0` requests more deterministic generation, while JSON response mode is intended to produce structured output that `json.loads()` can parse.

The evaluator is given a metric-specific prompt and returns a score or a relevance decision plus a reason.

**Important:** an LLM judge is an automated evaluator, not an infallible source of truth. It can misjudge an answer, so evaluation results should be checked against human-reviewed examples, especially for important business policies.

### Step 9 — The five evaluation functions

The code implements each metric separately.

| Function | Inputs | What it evaluates |
|---|---|---|
| `context_precision()` | Question, retrieved documents | Whether each retrieved chunk is relevant |
| `context_recall()` | Question, ground truth, context | Whether the context contains enough information |
| `evaluate_faithfulness()` | Question, context, answer | Whether answer claims are supported by context |
| `evaluate_relevancy()` | Question, answer | Whether the answer addresses the question |
| `evaluate_correctness()` | Answer, ground truth | Whether the answer matches the reference facts |

**Context precision** evaluates retrieved chunks one at a time. The judge returns `true` or `false` for relevance, and the function calculates:

```python
return relevant_chunks / len(retrieved_docs)
```

If no documents were retrieved, it returns `0.0`, avoiding division by zero.

The other four functions ask the judge for a score between `0.0` and `1.0` with a short explanation. The prompts define the meanings of scores such as `1.0`, `0.7`, `0.5`, and `0.0`.

These graded scores are useful for this demonstration, but they are not automatically calibrated probabilities. A score of `0.7` should be understood as the judge's assessment under the supplied rubric, not a guarantee of 70% accuracy.

### Step 10 — Run the full evaluation

The `run_evaluation()` function loops through each golden test case and:

1. Reads the question.
2. Retrieves the top three documents from Qdrant.
3. Prints the retrieved documents and similarity scores.
4. Combines their text into a context string.
5. Generates an answer with the LLM.
6. Calculates all five evaluation metrics.
7. Stores each metric's score.
8. Prints a diagnosis for scores below `0.7`.
9. Calculates the average score for each metric after all tests finish.

The diagnosis logic is:

```python
if precision < 0.7:
    print("Retrieval is returning irrelevant chunks.")

if recall < 0.7:
    print("Retrieval is missing important information.")

if faithfulness < 0.7:
    print("Answer is not properly grounded.")

if relevancy < 0.7:
    print("Answer is not sufficiently relevant.")

if correctness < 0.7:
    print("Answer is not sufficiently correct.")
```

The threshold `0.7` is a chosen heuristic in this example, not a universal standard. A production application should select thresholds based on its data, risk tolerance, and validated evaluation results.

The final summary calculates the arithmetic mean of each metric across all test questions. This is useful for comparing runs, but averages can hide individual failures. A system with a good average may still give a dangerous or seriously incorrect answer to one specific question.

## How to diagnose and fix failures 

Use the evaluation results to choose the next debugging step rather than changing the LLM blindly.

| Evaluation result | Likely issue | What to investigate |
|---|---|---|
| Low precision | Too many irrelevant chunks | Reduce `top_k`, add a validated similarity threshold, improve chunking or filtering |
| Low recall | Important information was missed | Increase `top_k`, examine similarity thresholds, improve chunking and retrieval |
| Low faithfulness | Unsupported or invented claims | Strengthen grounding instructions; inspect context and generated claims |
| Low answer relevancy | The answer misses the user's intent | Clarify the prompt, question interpretation, and answer format |
| Low correctness | The answer disagrees with ground truth | Check source accuracy first, then retrieval completeness and generation |

### A practical example

Suppose the user asks, “How much internet reimbursement do employees receive?”

The source says ₹2,000 per month, but Qdrant retrieves the gym benefit of ₹3,000 instead.

- **Context precision:** may be low if the retrieved chunks are irrelevant.
- **Context recall:** may be low because the internet policy is missing.
- **Faithfulness:** the answer “₹3,000” could be high if it faithfully repeats the retrieved gym-benefit context.
- **Answer relevancy:** it might be low because the answer is about the wrong benefit.
- **Answer correctness:** it is low because the expected answer is ₹2,000.

This is why evaluating only the final answer is not enough: different metrics help explain *how* the system went wrong.

### How `top_k` and similarity thresholds affect precision and recall

- Reducing `top_k` can reduce irrelevant results, potentially improving precision—but it can also remove useful evidence and hurt recall.
- Increasing `top_k` can retrieve more of the necessary information, potentially improving recall—but it can add irrelevant chunks and hurt precision.
- Raising a similarity threshold can filter weak matches, potentially improving precision while reducing recall.
- Lowering a threshold can allow more candidate chunks through, potentially improving recall while adding noise.

These are trade-offs, not guaranteed outcomes. Test changes against the same golden dataset and compare results before deciding whether a change improved the system.

## Important questions and revision

**Q1. What is RAG evaluation, and why is it necessary?**

RAG evaluation measures retrieval quality and answer quality to determine whether a RAG system works reliably. It helps identify whether failures originate from the knowledge base, retrieval, or generation.

**Q2. What is a golden dataset?**

A collection of representative test questions and verified reference answers used to evaluate a system consistently across test runs.

**Q3. What is the difference between context precision and context recall?**

Precision measures how much of the retrieved information is relevant. Recall measures how much of the information needed to answer the question was retrieved.

**Q4. What is the difference between faithfulness and correctness?**

Faithfulness checks whether the answer is supported by the retrieved context. Correctness checks whether the answer matches the reference facts. An LLM can faithfully repeat incorrect context and still produce an incorrect answer.

**Q5. What is answer relevancy?**

It measures whether the generated answer actually addresses the user's question rather than providing unrelated or tangential information.

**Q6. What is an LLM-as-a-judge approach?**

It uses an LLM to evaluate outputs against a rubric and return structured judgments or scores. It can automate evaluation, but its judgments should be validated against human-reviewed examples.

**Q7. How would you improve low context precision?**

Inspect irrelevant retrieved chunks, experiment with a smaller `top_k`, test similarity thresholds, and improve chunking or metadata filtering. Verify the change against the evaluation dataset.

**Q8. Why might a RAG answer be incorrect even when faithfulness is high?**

The retrieved context may itself be wrong or incomplete. The LLM can accurately follow that context while still disagreeing with the actual ground truth.

### Quick revision sheet

| Metric | Remember it as |
|---|---|
| Context precision | Are the retrieved chunks relevant? |
| Context recall | Did retrieval find the information needed? |
| Faithfulness | Is the answer supported by the context? |
| Answer relevancy | Does the answer address the question? |
| Answer correctness | Is the answer factually right against the reference? |

The evaluation workflow is:

**Golden dataset**

**Run every question through the RAG pipeline**

**Capture retrieved context and generated answer**

**Evaluate five metrics**

**Diagnose failures and improve the system**
