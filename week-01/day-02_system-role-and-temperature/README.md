# Ep 03: System Role + Temperature

## Big Picture

Two important concepts when working with LLM APIs are:

* **System Role** → controls **how the model should behave / what role it should play**
* **Temperature** → controls the **degree of randomness/creativity in the model's output**

A simple way to remember:

> **System Role = Who are you?**
> **Temperature = How creatively should you answer?**

### Example

Suppose we send:

> `I love you`

The response can differ depending on the system instruction.

| System instruction           | Expected behavior               |
| ---------------------------- | ------------------------------- |
| You are my girlfriend        | Romantic response               |
| You are my manager           | Professional/workplace response |
| You are a teacher            | Educational response            |
| You are a software architect | Technical response              |

The **message is the same**, but the model's behavior changes because its **role/context changes**.

---

## How LLM Messages Work

LLM APIs generally work with messages that contain two important parts:

```text
Role + Content
```

For example:

```text
Role: user
Content: Explain recursion in JavaScript.
```

Common message roles include:

### 1. User

Represents the person/application requesting something from the model.

```text
user → "Explain REST APIs."
```

### 2. Assistant

Represents the model's response.

```text
assistant → "A REST API is..."
```

### 3. System

Provides high-level instructions/context that guide the model's behavior.

```text
system → "You are a senior software architect."
```

Then:

```text
user → "Design an API for an e-commerce application."
```

The model should answer from the perspective established by the system instruction.

---

## System Role

### What is a System Role?

A **system role** provides instructions that establish the model's behavior, identity, responsibilities, or constraints for the conversation.

For example:

```text
system:
"You are a senior software architect."

user:
"How should I design this application?"
```

The model is instructed to approach the problem like a senior software architect.

### Simple mental model

Think of the system message as the model's **job description**.

```text
System Role
     ↓
Defines who/what the AI is supposed to be
     ↓
Influences how it interprets and answers user requests
```

---

### Why System Role Matters

Without role/context, an LLM may provide a relatively general answer.

With a system role, we can create specialized AI behavior.

For example:

```text
You are a senior backend engineer.
```

vs.

```text
You are a product manager.
```

The same question can produce answers with different priorities.

#### Example

User:

> "How should I build this application?"

**Senior Backend Engineer**

May focus on:

* APIs
* databases
* authentication
* scalability
* backend architecture

**System Architect**

May focus on:

* overall architecture
* service boundaries
* scalability
* reliability
* security
* maintainability

**Product Manager**

May focus on:

* user requirements
* business goals
* MVP scope
* prioritization
* user experience

The **system role changes the perspective from which the model approaches the problem.**

---

### Example

Consider:

```python
message_system = {
    "role": "system",
    "content": "You are my loving girlfriend."
}

message_user = {
    "role": "user",
    "content": "I love you."
}
```

The system instruction establishes the relationship/context before the user message is processed.

If we instead use:

```python
message_system = {
    "role": "system",
    "content": "You are my strict office manager."
}
```

The same user message can receive a completely different response.

### Important

The system instruction should generally be provided **before** the user request so that the model has the intended context when interpreting the request.

---

## Real-World Use Case

System roles become especially useful when building **AI agents**.

Imagine a company wants multiple AI agents.

Instead of using one generic AI for everything, we can create specialized agents:

```text
                LLM
                 │
       ┌─────────┼─────────┐
       ↓         ↓         ↓
   Architect  Developer  Tester
```

Each agent can receive a different system instruction.

### Architect Agent

```text
You are a senior software architect.
Focus on scalability, security, reliability,
and maintainability.
```

### Developer Agent

```text
You are a software developer.
Focus on implementing clean and correct code.
```

### Testing Agent

```text
You are a QA engineer.
Focus on finding bugs, edge cases, and
testing strategies.
```

The underlying LLM may be the same, but the **assigned role and instructions differ**.

---

## Temperature

### What is Temperature?

**Temperature is a generation parameter that influences the randomness of the model's output.**

In simple terms:

> **Lower temperature → more predictable output**
> **Higher temperature → more varied/random output**

It is commonly used when calling an LLM API.

For example:

```python
temperature=0
```

or:

```python
temperature=1
```

The exact supported range depends on the model/API.

> **Important:** The video demonstrates a `0–2` range for the Groq model/API being used. Do not assume every LLM provider or model supports exactly the same range.

---

### How LLMs Generate Answers

An LLM is not simply a database that looks up the correct answer.

At a high level, it generates text by predicting what token is likely to come next based on:

* the input
* the conversation context
* the model's learned patterns
* probabilities over possible next tokens

For example:

```text
The capital of France is ...
```

The model assigns a very high probability to:

```text
Paris
```

The generation process then continues token by token.

This is why LLMs are better thought of as **generative/predictive models**, rather than simple "truth machines."

---

### How Temperature Influences Generation

Suppose the model has several possible next tokens:

```text
Token A → 70%
Token B → 20%
Token C → 8%
Token D → 2%
```

With a lower temperature, generation tends to favor the more probable choices.

With a higher temperature, less-probable choices become more likely to be selected.

#### Simplified mental model

```text
Low Temperature
      ↓
More predictable
      ↓
Less variation

High Temperature
      ↓
More variation
      ↓
More creative/random
```

> This is a conceptual explanation. Temperature mathematically modifies the model's probability distribution; it does not directly "turn creativity on" like a switch.

---

## Low vs High Temperature

### Temperature ≈ 0

The model generally favors highly probable outputs.

Characteristics:

* More deterministic/predictable
* Less variation
* Better suited to tasks where consistency matters
* Less useful when you specifically want diverse ideas

Example:

```text
Give me the name of a food brand.
```

A low-temperature model might repeatedly produce conventional names.

---

### Moderate Temperature

The model has more freedom to select alternatives.

Characteristics:

* Some variation
* More diverse answers
* Still relatively coherent
* Useful for brainstorming and ideation

---

### Higher Temperature

The model is encouraged to explore lower-probability alternatives.

Characteristics:

* More variation
* More unusual outputs
* Greater creativity
* Potentially less predictable
* Potentially less reliable for precision-oriented tasks

---

## Temperature Example

Suppose we ask:

> "Suggest a name for my food company."

### Low temperature

Possible output:

```text
Savor
```

A conventional, semantically obvious name.

### Higher temperature

Possible outputs could become more unusual:

```text
Testio
Zomato-like coined names
other invented brand names
```

The important idea isn't the specific names.

The idea is:

> **Increasing temperature allows the model to explore a wider range of possible outputs.**

---

## Real-World Use Cases

The appropriate temperature depends heavily on the application.

### Use Case 1: Medical/Information-Oriented Assistant

Suppose an AI assistant helps doctors retrieve or reason about medical information.

You generally want:

* consistency
* precision
* predictable outputs
* minimal unnecessary randomness

Therefore, a **lower temperature** is generally more appropriate.

However:

> Temperature alone does **not** make an AI system medically safe or factually correct.

Other mechanisms are required, such as reliable sources, retrieval, validation, guardrails, and human oversight.

---

### Use Case 2: Storytelling AI

Suppose you're building an AI storyteller.

You want:

* creative ideas
* different narratives
* unexpected combinations
* varied language

A **higher temperature** can be useful.

Example:

```text
Write a horror story about an abandoned railway station.
```

A more varied generation process can produce more interesting story ideas.

---

### Use Case 3: Brand Name Generator

Suppose you're building an AI tool that generates startup or product names.

You may want the model to explore many possibilities.

Therefore, a higher temperature can be useful during the **ideation phase**.

---

## System Role vs Temperature

This is one of the most important concepts from the lecture.

| Concept      | System Role                       | Temperature                                |
| ------------ | --------------------------------- | ------------------------------------------ |
| Main purpose | Defines model behavior/role       | Controls generation randomness             |
| Answers      | **Who should you be?**            | **How varied should your answers be?**     |
| Changes      | Role, instructions, perspective   | Probability distribution during generation |
| Example      | "You are a senior developer"      | `temperature=0.8`                          |
| Main effect  | Specialized behavior              | More/less predictable output               |
| Useful for   | AI agents, specialized assistants | Creativity, consistency, diversity         |

---

## Important Questions

### Q1. What is a system role in an LLM?

A system role provides high-level instructions that establish how the model should behave, what role it should perform, or what perspective it should use when responding.

---

### Q2. What are common LLM message roles?

Common roles include:

* `system`
* `user`
* `assistant`

---

### Q3. What is the difference between system and user messages?

A **user message** generally represents the user's request.

A **system message** establishes instructions/context that guide how the model should handle requests.

Example:

```text
System:
You are a senior backend engineer.

User:
Design an authentication system.
```

---

### Q4. What is temperature in an LLM?

Temperature is a generation parameter that controls the degree of randomness/variation in the model's output.

---

### Q5. What happens when temperature is decreased?

The output generally becomes:

* More predictable
* More consistent
* Less varied

---

### Q6. What happens when temperature is increased?

The output generally becomes:

* More varied
* More unpredictable
* Potentially more creative

But it can also become less reliable or coherent for some tasks.

---

### Q7. Why would you use a low temperature?

For tasks where consistent and predictable responses are valuable.

Examples:

* Structured extraction
* Classification
* Certain information retrieval workflows
* Deterministic-style application behavior

---

### Q8. Why would you use a higher temperature?

For tasks where diversity and ideation are valuable.

Examples:

* Storytelling
* Brainstorming
* Creative writing
* Brand-name generation

---

### Q9. Can temperature make an LLM factually correct?

**No.**

Temperature controls generation behavior; it does not guarantee factual accuracy.

---

### Q10. What is the difference between system role and temperature?

**System role defines the model's role/behavior.**

**Temperature controls the randomness/variation of generation.**

Example:

```text
System:
"You are a senior architect."

Temperature:
0.2
```

means:

> Act as a senior architect and generate relatively predictable responses.

---

## Quick Revision

### System Role

```text
System Role
     ↓
Defines role / behavior / instructions
     ↓
Specialized AI behavior
```

Examples:

```text
"You are a senior developer."
"You are a software architect."
"You are a QA engineer."
"You are a product manager."
```

---

### Temperature

```text
Temperature
     ↓
Controls randomness/variation
     ↓
Low → predictable
High → varied
```

---

### Real-World Mapping

| Application                       | Typical tendency     |
| --------------------------------- | -------------------- |
| Structured information extraction | Lower temperature    |
| Classification                    | Lower temperature    |
| Coding assistant                  | Often lower/moderate |
| General chatbot                   | Low/moderate         |
| Brainstorming                     | Moderate/higher      |
| Storytelling                      | Higher               |
| Creative writing                  | Higher               |
| Brand-name ideation               | Moderate/higher      |

These are **general tendencies**, not universal rules.

---