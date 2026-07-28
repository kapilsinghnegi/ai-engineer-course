# Streaming

## What is Streaming?

When an LLM generates a response, there are two main ways to deliver that response to the user:

### Non-streaming

The application waits until the **entire response has been generated** and then sends it to the user.

```text
User
  ↓
LLM generates entire response
  ↓
Complete response
  ↓
User receives everything
```

For example, if the LLM takes 10 seconds to generate a long answer:

```text
0s ─────────────── 10s
                    ↓
             Complete answer
```

The user sees **nothing during those 10 seconds**.

---

### Streaming

Instead of waiting for the entire response, the LLM sends the response in **small pieces as they become available**.

```text
User
  ↓
LLM
  ↓
Chunk 1 → User
Chunk 2 → User
Chunk 3 → User
Chunk 4 → User
...
```

The user can start reading while the rest of the response is still being generated.

---

## Why Do LLMs Use Streaming?

The main reason is **better perceived performance and user experience**.

Suppose an LLM needs 10 seconds to generate a response.

### Without streaming

```text
User waits...
User waits...
User waits...
User waits...
User waits...

          ↓

Complete response appears
```

The user may think:

> "Why is this taking so long?"

### With streaming

```text
User
 ↓
Chunk 1 appears
 ↓
Chunk 2 appears
 ↓
Chunk 3 appears
 ↓
Chunk 4 appears
 ↓
...
```

The total generation time may still be approximately the same, but the **user doesn't feel like they are waiting for the entire response**.

This is an important distinction:

> **Streaming usually improves perceived latency, not necessarily the model's actual generation speed.**

---

## Streaming vs Non-Streaming

| Feature | Non-Streaming | Streaming |
|---|---|---|
| Response delivery | All at once | Incrementally |
| User sees first output | After full generation | As soon as first chunk arrives |
| Perceived latency | Higher | Lower |
| UX | User waits | User can start reading |
| Best for | Machine-to-machine processing | Human-facing applications |
| Typical ChatGPT UI | ❌ | ✅ |

---

## What is a Chunk?

A **chunk** is a small piece of the overall response delivered during streaming.

For example, imagine the final response is:

```text
The Internet is a global network of interconnected computers...
```

The LLM might deliver it approximately as:

```text
Chunk 1 → "The Internet"
Chunk 2 → " is a global"
Chunk 3 → " network of"
Chunk 4 → " interconnected"
Chunk 5 → " computers..."
```

The exact size and boundaries of chunks depend on the API/provider and implementation.

### Important

A chunk is **not necessarily one word or one sentence**.

It can contain a small piece of generated output.

Think:

```text
Complete Response
       ↓
 ┌─────┬─────┬─────┬─────┐
 │ C1  │ C2  │ C3  │ C4  │
 └─────┴─────┴─────┴─────┘
```

---

## How Streaming Improves User Experience

Consider a restaurant where you order:

- Starter — 10 minutes
- Main course — 30 minutes
- Dessert — 5 minutes

### Approach A: No streaming

The restaurant waits until **everything is ready**.

```text
10 min → Starter ready
30 min → Main course ready
5 min  → Dessert ready

Total waiting ≈ 30 min

Everything arrives together.
```

You may think:

> "This restaurant is slow."

### Approach B: Streaming

The restaurant sends each item as soon as it is ready.

```text
10 min → Starter arrives
30 min → Main course arrives
35 min → Dessert arrives
```

The total process still takes time, but you started receiving something after only 10 minutes.

The same concept applies to LLM responses.

### LLM equivalent

```text
LLM generates chunk 1
        ↓
User receives chunk 1

LLM generates chunk 2
        ↓
User receives chunk 2

LLM generates chunk 3
        ↓
User receives chunk 3
```

The user is **occupied and receiving useful output immediately**.

---

## When Should You Use Streaming?

Streaming is particularly useful when the **end user is a human who is reading the response**.

### Good use cases

#### 1. Chatbots

```text
User → "Explain system design"
                 ↓
             LLM
                 ↓
       Stream response
                 ↓
             Human
```

This is one of the most obvious use cases.

#### 2. AI assistants

Examples:

- Coding assistants
- Customer-support chatbots
- Personal AI assistants
- Educational AI applications

#### 3. Long-form responses

If an answer takes several seconds to generate, streaming can make the application feel much more responsive.

#### 4. ChatGPT-like interfaces

The familiar effect:

```text
Generating...
The
The Internet
The Internet is
The Internet is a
...
```

is achieved using streaming.

---

## When Should You NOT Use Streaming?

This is extremely important.

**Don't automatically enable streaming everywhere.**

The key question is:

> **Who or what is consuming the response?**

If another program needs the **complete response**, streaming can make processing more complicated.

---

### Example: JSON output

Suppose the LLM must generate:

```json
{
  "name": "Kapil",
  "email": "example@gmail.com"
}
```

A downstream program may need the **complete valid JSON object** before it can process it.

If you stream pieces:

```text
Chunk 1:
{
  "name":

Chunk 2:
"Kapil",

Chunk 3:
"email":

Chunk 4:
"example@gmail.com"
}
```

At intermediate points, the response is incomplete.

For example:

```json
{
  "name": "Kapil",
```

This is not yet the complete object.

Therefore, if your application expects a structured response that another program will consume, **non-streaming is often simpler and safer**.

---

### Human vs Machine

A useful rule:

```text
Human is reading?
       ↓
   Streaming ✅


Machine is processing?
       ↓
   Usually complete response first
```

This isn't an absolute rule, but it's a very useful engineering heuristic.

---

## Implementing Streaming with an LLM

The basic API concept is usually something like:

```python
stream=False
```

for normal responses.

To enable streaming:

```python
stream=True
```

Conceptually:

```python
response = client.chat.completions.create(
    model="...",
    messages=messages,
    stream=True
)
```

Now `response` represents a **stream of chunks**, rather than one complete response.

Instead of:

```python
print(response.choices[0].message.content)
```

you generally iterate over the stream:

```python
for chunk in response:
    ...
```

---

## Important Code Concepts

The exact API syntax can differ between providers and SDK versions, but the underlying pattern is:

```python
stream = client.some_llm_call(
    model=model,
    messages=messages,
    stream=True
)

for chunk in stream:
    content = chunk...
    
    if content:
        print(content, end="", flush=True)
```

Let's understand the important parts.

---

### `stream=True`

```python
stream=True
```

tells the LLM API:

> "Don't wait for the complete response. Send generated output incrementally."

Without it:

```python
stream=False
```

the application receives the completed response.

---

### Iterating over the stream

```python
for chunk in stream:
```

Each iteration gives you another piece of the response.

Think:

```text
stream
 │
 ├── chunk 1
 ├── chunk 2
 ├── chunk 3
 ├── chunk 4
 └── ...
```

---

### Extracting content

In the example from the lesson, the generated text is extracted from the chunk using a structure equivalent to:

```python
chunk.choices[0].delta.content
```

Conceptually:

```text
chunk
  ↓
choices[0]
  ↓
delta
  ↓
content
```

This differs from a normal completed response, where you typically access the completed message content.

---

### `flush=True`

When printing streamed content:

```python
print(content, end="", flush=True)
```

`flush=True` tells Python to **flush the output immediately** rather than waiting for its normal output buffering behavior.

This helps make the terminal display the chunks as soon as they arrive.

The lesson explicitly uses immediate flushing so that the streamed output appears progressively rather than being buffered. Pasted text(20261004-131111)

---

## Streaming vs Actual Latency

This is an important interview concept.

Suppose:

```text
Time to generate complete response = 10 seconds
```

### Non-streaming

```text
0s ───────────────────────── 10s
                              ↓
                       First output
```

### Streaming

Suppose the first chunk is ready after 1 second:

```text
0s ── 1s ── 2s ── 3s ── ... ── 10s
      ↓
   Chunk 1
             ↓
          Chunk 2
                    ↓
                 Chunk 3
```

The **total generation time may remain close to 10 seconds**.

But:

```text
Time To First Token (TTFT)
```

is much lower.

### Remember

> **Streaming primarily improves Time-to-First-Token and perceived responsiveness, not necessarily total generation time.**

---

## Interview Questions

### Q1. What is streaming in an LLM?

**Answer:**

Streaming is the process of sending an LLM's generated response incrementally in small chunks instead of waiting for the complete response before sending it to the client.

---

### Q2. Why is streaming useful?

Because it improves **perceived latency and user experience**.

The user can start reading the response as soon as the first chunk is available.

---

### Q3. Does streaming make the LLM generate faster?

**Not necessarily.**

It primarily allows the application to **display the output earlier**.

The total generation time may remain similar.

---

### Q4. What is a chunk?

A chunk is a small piece of a streamed response delivered incrementally by the LLM API.

---

### Q5. When should you use streaming?

Use it primarily when:

> **A human is waiting for and reading the response.**

Examples:

- Chatbots
- AI assistants
- ChatGPT-like applications
- Interactive coding assistants

---

### Q6. When should you avoid streaming?

When the response is intended to be consumed programmatically as a complete structured result.

For example:

```json
{
  "name": "Kapil",
  "email": "example@gmail.com"
}
```

A downstream program may be better served by receiving the complete valid JSON.

---

### Q7. What does `stream=True` do?

It tells the LLM API to return the generated response incrementally rather than as one completed response.

---

### Q8. What does `flush=True` do?

It forces Python to flush buffered output immediately, allowing streamed content to appear in the terminal as soon as it is received.

---