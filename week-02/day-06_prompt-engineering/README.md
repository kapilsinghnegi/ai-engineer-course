# Prompt Engineering

## What is Prompt Engineering?

**Prompt Engineering** is the practice of designing clear and structured instructions for an LLM so that it produces **more useful, consistent, controlled, and predictable outputs**.

> **Prompt Engineering = Improving the instructions given to an LLM to get better results.**

It is not about writing complicated prompts.

The core idea is **clarity + control**.

For example, this is vague:

```text
Classify this.
My laptop is not working.
```

The LLM has to guess:

- What role should it play?
- What exactly should it classify?
- Which categories are allowed?
- What format should the answer have?
- What should happen if the input doesn't fit?

A better prompt answers these questions explicitly.

---

## Why Prompt Engineering Matters

LLMs are **probabilistic systems**, not traditional deterministic programs.

For a normal program:

```text
2 + 2 → 4
```

You expect exactly the same result every time.

With an LLM, the same prompt can potentially produce slightly different responses.

For example:

```text
Tell me about yourself.
```

may produce different wording each time.

This becomes a problem in **production systems**.

### Example

Imagine an AI system classifies customer complaints.

Your backend expects:

```text
billing
technical
return
```

Then your code processes the result:

```text
LLM → classification → backend logic
```

If the LLM returns:

```text
technical
```

everything works.

But if it suddenly returns:

```text
The customer appears to be experiencing a hardware malfunction...
```

your backend may not know what to do.

#### Therefore:

> **Prompt Engineering helps constrain the LLM so its output is suitable for downstream code.**

This is especially important when:

- LLM output is consumed by another program
- You need structured output
- You are building AI agents
- You are building customer-support bots
- You need predictable classifications
- You need to prevent unrelated requests
- You need safe fallback behavior

---

## The Problem with Vague Prompts

Consider:

```text
This is a user complaint.

My laptop is not working.

Handle this.
```

This is a **vague prompt**.

The LLM doesn't know:

- What "handle" means
- Whether it should classify or solve the problem
- Which categories exist
- What response format is expected
- What to do with unrelated requests

It might respond:

```text
I'm sorry to hear that your laptop isn't working.
Could you tell me whether the device powers on?
...
```

That might be a perfectly reasonable conversational response, but it is **not necessarily what your application needs**.

The developer may need:

```text
technical
```

and nothing else.

### Key lesson

> **Never assume the LLM knows what you want. Explicitly define what it should do.**

---

## The 6 Building Blocks of a Good Prompt

| # | Component | Main Question |
|---|---|---|
| 1 | **Role** | Who are you? |
| 2 | **Task** | What should you do? |
| 3 | **Constraints** | What are the boundaries? |
| 4 | **Output Format** | What should the answer look like? |
| 5 | **Examples / Shots** | Can you show examples? |
| 6 | **Fallback** | What should happen when the input doesn't fit? |

### Easy way to remember

> **Role → Task → Constraints → Format → Examples → Fallback**

Think:

**Who → Do what → Within what limits → Return how → Learn from examples → What if it doesn't fit?**

---

## Role

### What is a Role?

The **role** tells the LLM what kind of assistant it is supposed to behave as.

For example:

```text
You are a customer support assistant for a laptop company.
```

This gives the model context about its responsibility.

#### Good role

```text
You are a customer support assistant for a laptop company.
```

Even better:

```text
You are a customer support assistant responsible for classifying customer issues for a laptop company.
```

This combines:

- **Domain:** laptop customer support
- **Responsibility:** issue classification

---

### Role should be relevant to the task

A role should generally describe a relevant **domain or responsibility**.

#### Good

```text
You are a Python developer responsible for reviewing Python code.
```

#### Not useful

```text
You are a genius engineer.
```

Calling an LLM "genius" does **not magically increase its intelligence or capabilities**.

The role provides **context**, not additional model intelligence.

#### Important distinction

> **Prompting can guide a model's behavior, but it cannot turn a weaker model into a fundamentally more capable model.**

---

## Task

The **task** tells the LLM exactly what action it needs to perform.

For example:

```text
Classify the customer's issue.
```

Instead of:

```text
Handle this.
```

The second instruction is ambiguous.

The first is specific.

### Example

```text
Task:
Classify the customer's issue into one of the supported categories.
```

Possible tasks include:

- classify
- summarize
- extract
- translate
- generate
- compare
- rewrite
- analyze
- answer
- transform

### Rule

> **Give the LLM a clear action instead of a vague instruction.**

---

## Constraints

Constraints define the **boundaries** within which the LLM must operate.

Think of constraints as a fence around the model's possible output.

Suppose your application supports only three categories:

```text
Billing
Technical
Return
```

Tell the model:

```text
The issue must be classified into exactly one of these categories:

- Billing
- Technical
- Return
```

Now the model has a limited set of valid outcomes.

Without constraints, it might invent:

```text
Hardware
Account
HR
General Support
Delivery
```

even though your application doesn't support them.

---

### Why constraints matter

Constraints improve:

- consistency
- predictability
- downstream processing
- safety
- reliability

### Mental model

Without constraints:

```text
LLM
 ↓
Anything
```

With constraints:

```text
LLM
 ↓
Billing | Technical | Return
```

---

## Output Format

Even if the model knows what to do, you should specify **how the result should be returned**.

For example:

```text
Your answer must be exactly one word.
```

And:

```text
The word must be one of:
Billing
Technical
Return
```

Now the expected output is:

```text
Technical
```

Instead of:

```text
The customer's laptop appears to have a technical issue.
I would classify this as a technical problem.
```

---

## Output format vs constraints

These concepts are related but different.

### Constraint

Defines **what values are allowed**.

```text
Only Billing, Technical, or Return are allowed.
```

### Output format

Defines **how the answer should be structured**.

```text
Return exactly one word.
```

Together:

```text
Constraint:
Choose one of Billing, Technical, Return.

Output format:
Return exactly one word.
```

---

## Zero-Shot, One-Shot & Few-Shot

**Shot** refers to the number of examples you provide to the model.

---

### Zero-Shot

You provide **no examples**.

```text
Classify the issue as Billing, Technical, or Return.

Input:
My laptop is not working.
```

There are no examples demonstrating the expected behavior.

This is **zero-shot prompting**.

---

### One-Shot

You provide **one example**.

```text
Example:

Input:
I was charged more than expected.

Output:
Billing

Now classify:

Input:
My laptop is not working.
```

The example demonstrates the expected behavior.

This is **one-shot prompting**.

---

### Few-Shot

You provide **multiple examples**.

```text
Example 1:
Input: I was charged extra.
Output: Billing

Example 2:
Input: My laptop won't turn on.
Output: Technical

Example 3:
Input: I want a refund.
Output: Return
```

Then provide the actual input.

This is **few-shot prompting**.

---

### Why examples help

Examples show the model:

- what inputs look like
- what outputs should look like
- how to map inputs to outputs
- what level of detail is expected

#### Important principle

> **When instructions alone are ambiguous, examples can demonstrate the desired behavior more clearly.**

---

## Fallback

This is one of the most important concepts for **production AI systems**.

A fallback defines what the model should do when the input **doesn't fit the expected categories or task**.

Suppose your system supports:

```text
Billing
Technical
Return
```

What happens if the user says:

```text
My marriage is broken.
```

This doesn't fit any category.

Without a fallback, the model might force the input into one of the categories:

```text
Billing
```

That is incorrect.

---

### Add a fallback

For example:

```text
If the issue does not fit any of the categories,
return:

Other
```

Now:

```text
Input:
My marriage is broken.

Output:
Other
```

This is much safer.

---

### Why fallback is important

Real-world systems don't receive only the inputs you expect.

Users will:

- misunderstand the system
- ask unrelated questions
- intentionally test the system
- enter unexpected data
- provide incomplete information
- try to make the model perform unrelated tasks

Therefore:

> **A production system should explicitly define what happens when the expected path fails.**

---

## How the Six Components Work Together

Let's build the prompt step by step.

### Step 1 — Role

```text
You are a customer support assistant for a laptop company.
```

---

### Step 2 — Task

```text
Classify the customer's issue.
```

---

### Step 3 — Constraints

```text
The issue must belong to exactly one of these categories:

Billing
Technical
Return
```

---

### Step 4 — Output Format

```text
Return exactly one word.
```

---

### Step 5 — Example

```text
Example:

Input:
I was charged more than expected.

Output:
Billing
```

---

### Step 6 — Fallback

```text
If the issue does not fit any category, return:

Other
```

---

### Final engineered prompt

```text
Role:
You are a customer support assistant for a laptop company.

Task:
Classify the customer's issue.

Constraints:
The issue must belong to exactly one of:
- Billing
- Technical
- Return

Output Format:
Return exactly one word.

Example:
Input: I was charged more than expected.
Output: Billing

Fallback:
If the issue does not fit any category, return:
Other
```

Now the LLM has much less room for ambiguity.

---

## Bad Prompt vs Engineered Prompt

### ❌ Bad Prompt

```text
This is a user complaint.

My laptop is not working.

Handle this.
```

Problems:

- No role
- Vague task
- No allowed categories
- No output format
- No examples
- No fallback

---

### ✅ Better Prompt

```text
You are a customer support assistant for a laptop company.

Task:
Classify the customer's issue.

Constraints:
The issue must be one of:
- Billing
- Technical
- Return

Output:
Return exactly one word.

Example:
Input: I was charged extra.
Output: Billing

Fallback:
If the issue does not fit any category, return Other.

Customer issue:
My laptop is not working.
```

Expected output:

```text
Technical
```

---

## Prompt Engineering in Production

Prompt engineering becomes especially important when the LLM is part of a larger software system.

A common architecture is:

```text
User
  ↓
Application
  ↓
Prompt
  ↓
LLM
  ↓
Structured Output
  ↓
Backend Logic
  ↓
Action
```

For example:

```text
Customer message
      ↓
AI classifier
      ↓
Billing / Technical / Return / Other
      ↓
Route to appropriate team
```

If the LLM output is unpredictable, the rest of the application can break.

---

### Example: Customer Support Agent

Suppose:

```text
Billing → Billing Team
Technical → Engineering Team
Return → Returns Team
Other → Human Support
```

Then your backend can implement:

```text
if category == "Billing":
    send_to_billing()

elif category == "Technical":
    send_to_engineering()

elif category == "Return":
    send_to_returns()

else:
    send_to_human_support()
```

This is why **controlled LLM output matters**.

---

## Important Concepts to Remember

### LLMs are probabilistic

Don't assume:

```text
Same prompt → Always exactly same output
```

Instead, design your system so that small variations don't break the application.

---

### Prompt engineering doesn't increase model intelligence

This:

```text
You are a genius AI.
```

doesn't magically upgrade the model.

Prompting primarily provides:

- context
- instructions
- boundaries
- examples
- desired behavior

---

### More specific instructions are usually better

Compare:

```text
Handle this.
```

with:

```text
Classify the customer's complaint into Billing,
Technical, or Return and return exactly one category.
```

The second gives the model much less ambiguity.

---

### Constraints are boundaries

Think:

> **Constraints = Fence around the LLM**

They restrict what the model is allowed to return.

---

### Output format is critical for code integration

If another program consumes the LLM's response, specify the format explicitly.

For example:

```text
Return only JSON.
```

or:

```text
Return exactly one category name.
```

or, where appropriate, use structured-output features supported by the model/API.

---

### Fallback handles unexpected input

Never assume:

> "Users will only ask what I expect."

They won't.

Always consider:

```text
Expected input
        ↓
Normal processing
        ↓
Unexpected input
        ↓
Fallback
```

---

## Important Questions

### Q1. What is Prompt Engineering?

**Answer:**

Prompt engineering is the process of designing and refining instructions given to an LLM to obtain more accurate, consistent, controlled, and useful outputs.

---

### Q2. Why is prompt engineering important in production?

Because LLM outputs are probabilistic and may vary. Production systems often depend on predictable outputs, so prompts need to constrain and structure model behavior.

---

### Q3. What are the six prompt-engineering components discussed here?

1. Role
2. Task
3. Constraints
4. Output Format
5. Zero-shot / One-shot / Few-shot examples
6. Fallback

---

### Q4. What is the difference between role and task?

**Role** defines **who the model is / what domain or responsibility it has**.

**Task** defines **what the model needs to do**.

Example:

```text
Role:
You are a customer-support assistant.

Task:
Classify the customer's complaint.
```

---

### Q5. What are constraints?

Constraints define boundaries on the model's behavior or output.

Example:

```text
Only return:
Billing
Technical
Return
```

---

### Q6. What is zero-shot prompting?

Giving the model a task **without examples**.

---

### Q7. What is one-shot prompting?

Giving the model **one example** before asking it to perform the task.

---

### Q8. What is few-shot prompting?

Providing **multiple examples** to demonstrate the desired behavior.

---

### Q9. Why is fallback important?

Because real-world inputs can be unexpected or unrelated. A fallback gives the model a defined behavior instead of forcing an invalid answer.

---

### Q10. Does saying "You are a genius engineer" make an LLM more intelligent?

**No.**

A role can guide behavior and provide context, but it does not fundamentally increase the model's underlying capabilities.

---


## Final Mental Model

> **A good prompt tells the model WHO it is, WHAT it should do, WHAT it is allowed to do, HOW it should respond, SHOWS examples when useful, and WHAT to do when the input doesn't fit.**

```text
┌───────────────┐
│     ROLE      │ → Who are you?
├───────────────┤
│     TASK      │ → What do you do?
├───────────────┤
│  CONSTRAINTS  │ → What are the boundaries?
├───────────────┤
│ OUTPUT FORMAT │ → How should you respond?
├───────────────┤
│    EXAMPLES   │ → Show me what good looks like
├───────────────┤
│    FALLBACK   │ → What if nothing matches?
└───────────────┘
```
