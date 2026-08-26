# Chunking Strategies for RAG

## What is chunking?

Chunking is the process of splitting a large document into smaller pieces so that each piece can be embedded and retrieved independently.

Suppose you have a 300-page book. You could create:

- One embedding for the entire book.
- One embedding per page.
- One embedding per paragraph.
- One embedding for every 500 characters.
- Chunks based on sentences, code structure, or changes in meaning.

Each choice creates a different set of chunks and can produce different retrieval results.

In RAG, we generally embed each chunk, rather than treating a large knowledge base as one giant text input.

`Large document`: Book, PDF, webpage, or codebase
↓
`Chunking strategy`: Split using size, paragraphs, separators, or meaning
↓
`Chunk 1`: Text segment
↓
`Chunk 2`: Text segment
↓
`Chunk 3`: Text segment
↓
`Embedding` → `Vector database`

Each chunk gets its own vector and can be retrieved

### Why does chunking matter?

Imagine the original sentence:

> The man who did the crime was John.

If chunking splits it into:

- Chunk 1: “The man who did the crime was”
- Chunk 2: “John.”

A question such as “Who committed the crime?” may retrieve the first chunk without retrieving the second. The retrieved text then lacks the answer.

Chunking can therefore affect:

- Whether a complete fact survives splitting.
- Whether related context is retrieved together.
- How much irrelevant text is passed to the LLM.
- Embedding and retrieval costs.
- The overall accuracy of a RAG system.

## Four chunking strategies

The lecture discusses four broad approaches. The first three are demonstrated in your code; semantic chunking is explained conceptually.


### 1\. Fixed-size chunking

![Text chunking techniques · Hyperskill](https://images.openai.com/static-rsc-4/7hQu59IgQR4K_jAVoa4OW4KxJaDWe-U6C1cmrXJxOvV08YXYZv-lgDAGNTDsbH-mj3icSEbYSHY7v8IwNCN9TKQ2-PQC7qznA2BZmtEqS6NxvZFkGgKqUjxQixHHiCayQCVk6kSwYzCtasWsysbvamdX1vEEirCy-R2ZQp8_owk?purpose=inline)

Divide text into pieces with a fixed character or token limit, regardless of sentence or paragraph boundaries.

Main risk: a sentence or fact may be split in the middle.

### 2\. Paragraph-based chunking

![Designing AI Systems](https://images.openai.com/static-rsc-4/72FMpOo9F0D3sLlTKhpYvlI_LtMgM-xZWe0TjCPXUODvQ6HyMudCGUs5d4oN2C2IN3p9q_5x6lJOVLBQ_tGOTqBTYMRNcBiAbkrwETYcc9Ul_N35sAH_hR3qB-oQbIrljI50KZGWPff7UJwvysvmxRIImmzGQzuR1oArf8S7LPU?purpose=inline)

Use paragraph boundaries to keep related sentences together.

Main risk: paragraph lengths can vary substantially.

### 3\. Recursive chunking

![The Art and Science of Text Chunking for Better AI Retrieval | by Priyanka Dave | Medium](https://images.openai.com/static-rsc-4/3ArIZd8TIhV5AP8j9Qw4TsOJ7BTS8QaZgODCAGk3J88NExe5zCkYOG8D8I8qLkY9XqnbCptOyIgnLUor-tEcelU2N90Sw_sAn11OWHO5TVXTjsNHvSUdoM1GvzQTl1OkU3SsA-oHWpDeMBGt60Gm2QCmLtuoYqBGVs8HXQ-aBao?purpose=inline)

Try preferred separators first, then split oversized pieces using progressively finer separators.

Benefit: balances size limits with preserving natural text boundaries.


### 4\. Semantic chunking

![9 Chunking Strategies to Improve RAG Performance](https://images.openai.com/static-rsc-4/R6155J9tyQ8GiWAKG1YWd4jggLxwcstiXAHX6q-1dnLM-lEtTkhCok0z9XUN7CRYRY3CzgmKDMdqk-8D6B-gvGDLVJAldEHonQ3sSNR2jgPQE0OodOSbcWOAJNnSpTJeCWf3ChUgWHCdtzvsbXzeFr1RPWu7Vk5zEvx6MZ-wGPo?purpose=inline)

Group text according to changes in meaning or topic, typically using semantic similarity methods.

Benefit: can preserve topic-level context; often requires more computation and tuning.

### Strategy 1: Fixed-size chunking

Your code:

```py
fixed = CharacterTextSplitter(    
    separator="",    
    chunk_size=100,    
    chunk_overlap=0
)
```

Here:

- `separator=""` means there is no separator string between which to split; the splitter uses character-length boundaries.
- `chunk_size=100` sets a maximum chunk length of 100 characters for this splitter.
- `chunk_overlap=0` means no intentional overlap between adjacent chunks.

The lecture demonstrates how a word can be cut in the middle when a fixed boundary falls inside it.

When it can work: text where boundaries matter less, or when you need a simple baseline.

When it can fail: prose containing important multiword facts, sentences, or names that should stay together.

### Strategy 2: Paragraph-based chunking

```py
paragraph = CharacterTextSplitter(    
    separator="\n\n",    
    chunk_size=100,    
    chunk_overlap=0
)
```

The separator `"\n\n"` looks for a blank line between paragraphs.

The intention is to keep each paragraph intact when possible. However, the `chunk_size=100` limit still applies. If a paragraph is too large, this splitter may split it further, so this is not an unconditional guarantee that every paragraph stays intact.

When it can work: FAQs, short articles, and documents with consistently sized paragraphs.

When it can fail: extremely long or very short paragraphs, or content where one paragraph contains multiple unrelated ideas.

### Strategy 3: Recursive chunking

Your code:

```py
recursive = RecursiveCharacterTextSplitter(    
    chunk_size=100,    
    chunk_overlap=20
)
```

This is the most flexible of the three splitters demonstrated in your code.

The default separator priority in `RecursiveCharacterTextSplitter` generally starts with:

1. `"\n\n"` — paragraph boundaries.
2. `"\n"` — line boundaries.
3. `" "` — word boundaries.
4. `""` — character boundaries.

The splitter tries to preserve larger text units first. If a unit is too large, it can split it using a finer separator.

For example, an oversized paragraph might be divided into sentences, and if a sentence is still too long, the splitter can fall back to word or character boundaries.

The exact separators can vary with the splitter configuration and language-specific settings.

#### Why is this useful?

It tries to preserve natural structure while respecting a target chunk size. It also supports overlap, which helps retain context around chunk boundaries.

### Strategy 4: Semantic chunking

Semantic chunking aims to split text where the meaning or topic changes, rather than only at a fixed character count or a paragraph boundary.

For example, a report might contain:

- A section about a new phone's specifications.
- A section about the company's financial performance.

Even if those sections appear close together in the original text, semantic chunking can separate them into different chunks because they cover different topics.

Unlike the first three approaches, semantic chunking usually requires an additional method for estimating semantic similarity or detecting topic changes. The lecture introduces the concept but does not implement it in the supplied code.

## Understanding your Python code

You import two classes from LangChain:

```py
from langchain_text_splitters import (CharacterTextSplitter, RecursiveCharacterTextSplitter,)
```

- `CharacterTextSplitter` splits text using a specified separator. With an empty separator, it can be used for character-based splitting.
- `RecursiveCharacterTextSplitter` tries a hierarchy of separators to divide text while preserving larger units when possible.

The sample text contains three paragraphs about a detective investigating a crime. All three strategies process this same text, making it easier to compare how different splitting rules affect the output.

### Experiment A: Fixed-size splitting

```py
fixed = CharacterTextSplitter(    
    separator="",    
    chunk_size=100,    
    chunk_overlap=0
)

for i, chunk in enumerate(fixed.split_text(text), 1):    
    print(f"\nChunk {i}:")    
    print(chunk)
```

`split_text(text)` returns a list of chunks. `enumerate(..., 1)` numbers them starting from 1.

The `chunk_size` is measured in characters by default here, not words or tokens.

The main thing to inspect in the output is whether a word or sentence gets split at the boundary.

### Experiment B: Paragraph splitting

```py
paragraph = CharacterTextSplitter(    
    separator="\n\n",    
    chunk_size=100,    
    chunk_overlap=0
)
```

Your source text uses two newline characters between paragraphs. The splitter uses that pattern to identify paragraph boundaries.

One technical detail worth remembering: `CharacterTextSplitter` does not necessarily split an oversized paragraph internally. A single paragraph can exceed the configured chunk size. If you need large paragraphs to be subdivided, recursive splitting is a better starting point.

### Experiment C: Recursive splitting

```py
recursive = RecursiveCharacterTextSplitter(    
    chunk_size=100,    
    chunk_overlap=20
)

for i, chunk in enumerate(recursive.split_text(text), 1):
    print(f"\nChunk {i}:")    
    print(chunk)
```

The `chunk_overlap=20` setting means the splitter aims to retain up to 20 characters of shared text between adjacent chunks.

For example, conceptually:

`CHUNK 1`: The detective entered the house and found a letter.
`CHUNK 2`: found a letter. The letter mentioned a secret meeting.

Illustrative example: the highlighted text is shared context, not the exact output of your code.

Overlap can help when a fact starts in one chunk and continues into the next. It does not guarantee that every complete fact stays together, and it increases the amount of duplicated text that gets embedded and stored.

## Chunk size and overlap: what should you choose?

There is no single correct setting for every dataset.

| Setting       | Too small                    | Too large                                               |
| ------------- | ---------------------------- | ------------------------------------------------------- |
| Chunk size    | Context may be incomplete    | Multiple topics can get mixed together                  |
| Chunk overlap | Boundary context may be lost | More duplicated text, storage, and retrieval redundancy |

A useful starting point is to experiment with several chunk sizes and overlap values, then evaluate retrieval quality on realistic questions. Do not treat `100` characters as a general recommendation; the value in this lesson is intended for demonstration.

Also distinguish between three measurements:

- Characters: individual letters, spaces, and punctuation.
- Words: groups of text separated by whitespace.
- Tokens: units used by language models and often relevant to their context limits.

A 100-character chunk is not necessarily a 100-token chunk.

## How chunking fits into your RAG system

#### Load the source document 
PDF, text file, code, or transcript

#### Split into chunks
Fixed-size, paragraph, recursive, or semantic

#### Create embeddings
Convert each chunk into a vector

#### Store in Qdrant
Save vectors and chunk text as payload

#### Retrieve relevant chunks
Embed the user's question and search

#### Generate an answer
Pass retrieved context to the LLM

A poor chunking strategy can cause relevant information not to be retrieved, even when your embedding model and vector database are working correctly. Conversely, better chunk boundaries can make useful information easier to retrieve.

## Important questions

### What is chunking in RAG?

Chunking divides large source documents into smaller pieces that can be embedded, indexed, and retrieved independently.

### What is the difference between fixed-size and recursive chunking?

Fixed-size splitting follows a size boundary. Recursive splitting tries preferred separators first and progressively uses finer separators when necessary.

### What is chunk overlap?

Overlap is text shared between adjacent chunks. It can preserve context across boundaries but increases duplication.

### Is paragraph chunking always better than fixed-size chunking?

No. Paragraphs vary in length, and an oversized paragraph can produce a chunk that is too large. The best approach depends on the document and retrieval task.

### What is semantic chunking?

A technique that uses meaning or topic changes to decide where chunks should begin and end.

### Which chunking strategy is best for RAG?

There is no universal winner. Choose based on the data, query patterns, retrieval evaluation, and operational constraints.

### Does `chunk_size=100` mean 100 words?

No. In your examples, the default length measurement is characters.
