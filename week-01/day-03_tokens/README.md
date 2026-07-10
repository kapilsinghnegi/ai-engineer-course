# Tokens Explained

## What Is a Token?

A **token** is a piece of text that an LLM processes as an input/output unit.

A token can be:

* A complete word
* Part of a word
* Multiple characters
* Punctuation
* Whitespace or whitespace-associated text
* Special characters

The exact way text is divided into tokens depends on the **tokenizer used by the model**.

## Why Do LLMs Need Tokens?

An LLM is ultimately a computational system operating on numerical representations.

It cannot directly process:

```text
Hello, how are you?
```

as raw human language.

Instead, the text goes through a pipeline roughly like:

```text
Human Text
    ↓
Tokenizer
    ↓
Tokens
    ↓
Token IDs / Numerical Representation
    ↓
LLM
    ↓
Output Token IDs
    ↓
Detokenization
    ↓
Human-Readable Text
```

### Example

Suppose we send:

```text
Hello
```

The tokenizer converts it into one or more tokens.

Those tokens are mapped to numerical IDs, which the model processes.

The model then predicts output tokens, which are converted back into text.

### Important distinction

The model doesn't simply "understand English directly."

A simplified conceptual flow is:

```text
Text → Tokens → Token IDs → Model Computation → Token IDs → Text
```

---

## Why Character-Level Encoding Is Not Practical

One early idea would be:

> Convert every character into a number.

For example:

```text
HELLO
```

could theoretically become something like:

```text
H → number
E → number
L → number
L → number
O → number
```

Character encoding systems such as **ASCII** demonstrate that characters can indeed be represented numerically.

For example:

```text
A → 65
B → 66
a → 97
b → 98
```

But using individual characters as the basic unit creates problems.

### Problem 1: Huge sequences

A long document contains a huge number of characters.

For example:

```text
A 5,000-line source-code file
```

could contain hundreds of thousands of individual characters.

Processing every character separately would create very long sequences.

### Problem 2: Inefficient representation

Common words would repeatedly be represented as many individual character units.

For example:

```text
programming
```

would need to be represented character by character.

This is inefficient for an LLM.

---

## Why Word-Level Encoding Is Not Enough

The next obvious idea is:

> Instead of characters, make every complete word a token.

For example:

```text
hello → 1
world → 2
apple → 3
```

This seems much better.

However, it creates another major problem.

### The vocabulary problem

Natural language has an enormous number of possible word forms.

People don't only use dictionary words.

They also use:

* Names
* Brand names
* Slang
* Misspellings
* Abbreviations
* Technical terms
* Newly invented words
* Combined words
* Domain-specific terminology

For example:

```text
Zomato
```

may not behave like an ordinary dictionary word.

Similarly, someone could invent:

```text
Alexfin
```

or:

```text
Pratyushification
```

A word-level tokenizer would have to deal with an ever-growing vocabulary.

---

## The Idea Behind Tokenization

This leads to the key idea:

> **Instead of treating every complete word as a token, break text into reusable pieces.**

These pieces are called **tokens**.

A tokenizer tries to create a vocabulary of useful text pieces that can be combined to represent a very large variety of text.

### Mental model

Think of LEGO.

You don't need a separate LEGO piece for every possible object.

Instead, you need reusable building blocks.

Similarly:

```text
Reusable text pieces
        ↓
Combine them
        ↓
Represent many different words
```

This is the core intuition behind modern tokenization.

---

## Tokens Are Not Necessarily Words

A token can be:

```text
1 word
```

but it can also be:

```text
part of a word
```

or:

```text
multiple characters
```

Therefore:

> **1 word ≠ 1 token**

And:

> **4 characters ≠ necessarily 1 token**

The number of tokens depends on the tokenizer and the actual text.

---

## Subword Tokenization

Modern LLM tokenizers commonly use approaches based on **subword tokenization**.

The basic idea is:

```text
Common text patterns → reusable tokens
Rare/unusual words → split into smaller pieces
```

### Example

Imagine the tokenizer knows:

```text
play
walk
eat
```

It may also recognize useful pieces such as:

```text
-ing
```

Then it can represent:

```text
playing
walking
eating
```

using reusable components.

```text
play → playing
walk → walking
eat → eating
```

Instead of memorizing every possible word form independently, reusable patterns can be learned.

### Another conceptual example

A rare word might be split approximately like:

```text
unusualword
↓
un + usual + word
```

The exact split depends on the tokenizer.

---

## Tokenization Example

Consider a word that is extremely common:

```text
airplane
```

A tokenizer may potentially represent it efficiently as a single token or a small number of tokens.

But a rare or invented word such as:

```text
Pratyushification
```

may be broken into several pieces.

Conceptually:

```text
Pratyushification
        ↓
Pratyush + ification
```

or perhaps even smaller pieces.

The exact result depends on the tokenizer.

### Key rule

**Common text tends to have efficient token representations, while rare/unseen text may require more tokens.**

This is why token count cannot be determined simply by counting words or characters.

---

## Input Tokens vs Completion Tokens

When interacting with an LLM, there are generally two important token categories.

### Input Tokens

These are the tokens contained in what you send to the model.

For example:

```text
Explain machine learning in simple terms.
```

The tokenizer converts your prompt into input tokens.

These are often called:

```text
Prompt Tokens
```

or:

```text
Input Tokens
```

---

### Completion Tokens

These are the tokens generated by the model in its response.

For example:

```text
Machine learning is a field of AI...
```

The generated response is also represented as tokens.

These are often called:

```text
Completion Tokens
```

or, in some APIs:

```text
Output Tokens
```

---

### Total Tokens

The total token usage can be thought of as:

```text
Total Tokens
=
Input Tokens
+
Output/Completion Tokens
```

### Example

Suppose:

```text
Input Tokens = 100
Output Tokens = 200
```

Then:

```text
Total Tokens = 100 + 200
             = 300
```

This is important because token usage affects:

* Cost
* Context-window usage
* Application performance
* Maximum response length

---

## Why Tokens Matter for Cost

LLM APIs generally charge based on **tokens**, not simply the number of words.

This means:

```text
More tokens
    ↓
More computation
    ↓
Potentially higher cost
```

### Important consequence

Two texts containing roughly the same number of words may have different token counts.

For example:

```text
Common text
```

may tokenize efficiently.

Whereas:

```text
Rare names + unusual spelling + code
```

may produce more tokens.

Therefore:

> **Token count is more relevant than word count when estimating LLM usage and cost.**

---

## Maximum Tokens

LLM APIs often provide a parameter that limits how many tokens the model can generate.

Conceptually:

```python
max_tokens = 100
```

means:

> Do not generate more than approximately 100 output tokens.

### Why is this useful?

Suppose you're building an AI agent for a company.

Your manager says:

> "The response must stay below 100 output tokens."

You can enforce an output limit.

This helps with:

* Cost control
* Response length
* Latency
* UI constraints
* Predictable application behavior

---

### Important distinction

`max_tokens` is an **output-generation limit** in APIs that expose it in this way.

It should not be confused with the model's entire context window.

For example:

```text
Input
+
Generated Output
```

must still fit within the model's supported context constraints.

---

## Finish Reason

Another useful piece of information returned by an LLM API is the **finish reason**.

It tells you why generation stopped.

### `stop`

This generally means:

> The model finished generating naturally.

For example:

```text
finish_reason = "stop"
```

means the model reached a natural stopping point.

---

### `length`

This generally means:

> Generation stopped because it reached the configured output/token limit.

For example:

```text
max_tokens = 50
```

If the model still had more to say but reached the limit:

```text
finish_reason = "length"
```

### Example

Suppose you ask:

```text
Write a 1000-word essay about Machine Learning.
```

but configure:

```text
max_tokens = 50
```

The model may be forced to stop before completing the essay.

You might therefore see:

```text
finish_reason = "length"
```

---

## Practical Python Example

A simplified structure looks like this:

```python
response = client.chat.completions.create(
    model="YOUR_MODEL",
    messages=[
        {
            "role": "user",
            "content": "Explain machine learning."
        }
    ]
)

print(response.usage.prompt_tokens)
print(response.usage.completion_tokens)
print(response.usage.total_tokens)
```

The important fields are:

```python
response.usage.prompt_tokens
```

→ Number of input/prompt tokens.

```python
response.usage.completion_tokens
```

→ Number of generated/output tokens.

```python
response.usage.total_tokens
```

→ Total token usage.

---

## Example: Limiting Output

A request can also specify an output-token limit, depending on the API/model:

```python
response = client.chat.completions.create(
    model="YOUR_MODEL",
    messages=[
        {
            "role": "user",
            "content": "Explain machine learning."
        }
    ],
    max_tokens=100
)
```

If the response hits the limit before naturally finishing, inspect:

```python
response.choices[0].finish_reason
```

You may get something conceptually like:

```text
"length"
```

If it finishes naturally:

```text
"stop"
```

> **API parameter names can vary between providers and newer API interfaces, so always check the specific model/provider documentation.**

---

## Interview Questions

### Q1. What is a token?

A token is a unit of text generated by a tokenizer. It can represent a complete word, part of a word, punctuation, whitespace-associated text, or another text fragment.

---

### Q2. Is one word always one token?

**No.**

A word can be:

* One token
* Multiple tokens

depending on the tokenizer and how common/structured the word is.

---

### Q3. Why don't LLMs simply tokenize every character?

Character-level tokenization creates very long sequences and is computationally inefficient for large amounts of text.

---

### Q4. Why don't LLMs simply use complete words as tokens?

Because natural language has:

* Huge vocabulary
* Rare words
* Names
* Misspellings
* New words
* Slang
* Domain-specific terminology

Subword tokenization provides a better compromise.

---

### Q5. What is tokenization?

Tokenization is the process of converting text into a sequence of tokens that the model can process.

```text
Text → Tokens
```

---

### Q6. What are input tokens?

Tokens representing the input/prompt sent to the model.

---

### Q7. What are completion tokens?

Tokens generated by the model as its response.

---

### Q8. How is total token usage calculated?

Conceptually:

```text
Total Tokens
=
Input Tokens
+
Output Tokens
```

---

### Q9. Why are tokens important for AI engineers?

Because token usage affects:

* API cost
* Context-window consumption
* Output length
* Latency
* Application design
* Performance

---

### Q10. What does `max_tokens` do?

It limits the amount of output the model can generate, subject to the API/model's specific semantics.

---

### Q11. What does `finish_reason = "stop"` generally mean?

The model finished generating naturally.

---

### Q12. What does `finish_reason = "length"` generally mean?

Generation stopped because the configured length/token limit was reached.

---