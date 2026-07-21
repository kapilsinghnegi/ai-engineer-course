# ReAct — Introduction to AI Agents

## What is ReAct?

**ReAct = Reasoning + Action**

ReAct is a pattern where an LLM:

1. **Reasons** about the user's problem.
2. **Decides** what action/tool is needed.
3. **Executes** that tool.
4. **Observes** the result.
5. Uses the observation to decide the **next action**.
6. Repeats until it can produce the final answer.

---

## Why ReAct Was Needed

### The limitation of a normal LLM

An LLM is trained on historical data.

For example, suppose a model's training data ends around a particular date.

It may know:

- historical facts
- programming concepts
- general knowledge
- information present in its training data

But it cannot automatically know information that changes **after its knowledge cutoff**.

Examples:

- Today's weather
- Current hotel prices
- Current flight prices
- Today's news
- Current sports results
- Current product prices

> "What is the temperature today?"

or

> "What is the hotel price in Dubai today?"

Historical training data cannot reliably answer such questions because the information is **current and dynamic**.

---

## LLM vs AI Agent

### Traditional LLM

A simple LLM interaction looks like:

```text
User → Prompt → LLM → Answer
```

Example:

```text
User:
How do I build a website?

       ↓

LLM:
You can use HTML, CSS and JavaScript...
```

The LLM mainly generates a response.

---

### AI Agent

An AI agent can interact with external tools and perform actions.

For example, an agent could:

- check weather
- search flights
- check hotel prices
- search products
- send emails
- retrieve documents
- perform calculations
- check order status
- process refunds

So the flow becomes:

```text
User
 ↓
AI Agent
 ↓
Reason
 ↓
Choose Tool
 ↓
Execute Tool
 ↓
Observe Result
 ↓
Reason Again
 ↓
Choose Another Tool
 ↓
...
 ↓
Final Answer
```

---

## The Problem with Tools

Giving an LLM tools solves one problem but creates another.

Suppose an AI agent has **20 tools**.

For an Amazon-like customer-support agent, tools might include:

- `get_order_status`
- `track_delivery`
- `return_item`
- `refund_order`
- `search_product`
- `update_address`
- etc.

Now the question becomes:

> **Which tool should the LLM use for a particular user request?**

---

### Example

User:

> "Where is my order?"

Possible tools:

```text
get_order_status
track_delivery
return_item
refund_order
search_product
update_address
...
```

The agent must figure out that it may need:

```text
get_order_status
       ↓
track_delivery
```

It should **not** unnecessarily call:

```text
refund_order
return_item
update_address
```

---

### The problem becomes more complex

Consider:

> "I ordered a product, but it hasn't arrived at my address. Check what's wrong and update my address if necessary."

Now the agent may need to:

```text
1. Check order status
        ↓
2. Check delivery status
        ↓
3. Check address
        ↓
4. Decide whether address needs updating
        ↓
5. Update address
```

The exact sequence depends on the information returned by earlier tools.

Therefore, hard-coding every possible sequence with `if/else` becomes extremely difficult as the number of tools increases.

---

## What is the ReAct Loop?

ReAct solves this dynamic tool-selection problem.

The LLM continuously performs:

```text
Reason → Act → Observe → Reason → Act → Observe → ...
```

until the task is complete.

### The three key concepts

| Concept | Meaning |
|---|---|
| **Reasoning** | Decide what needs to happen next |
| **Action** | Select and execute a tool |
| **Observation** | Read the tool's result |

The loop continues until the LLM has enough information to provide the final answer.

---

## ReAct Example: Buying an iPhone

Let's take a simple example:

> "I have ₹5,000. What is the price of an iPhone 17, and how much money will I have left after buying it?"

At first glance, this looks like simple arithmetic.

But an agent needs **two different capabilities**.

### Step 1 — Find the iPhone price

The price is dynamic.

So the agent needs:

```text
get_product_price()
```

Suppose the tool returns:

```text
iPhone 17 = ₹1,000
```

### Step 2 — Calculate remaining money

The user has:

```text
₹5,000
```

The phone costs:

```text
₹1,000
```

The agent therefore uses a calculator:

```text
5000 - 1000
```

Result:

```text
₹4,000
```

### Final answer

```text
iPhone 17 costs ₹1,000.
You will have ₹4,000 remaining.
```

---

## ReAct Flow

```text
User Prompt
     ↓
"I have ₹5000..."
     ↓
Reason
     ↓
Need iPhone 17 price
     ↓
Action
     ↓
get_product_price("iPhone 17")
     ↓
Observation
     ↓
₹1000
     ↓
Reason
     ↓
Need remaining money
     ↓
Action
     ↓
calculator("5000 - 1000")
     ↓
Observation
     ↓
₹4000
     ↓
Reason
     ↓
Task complete
     ↓
Final Answer
```

This is the **ReAct loop** in its simplest form.

---

### ReAct Example: Planning a Dubai Trip

Consider the user request:

> "I want to go to Dubai. I'll stay in a 3-star hotel and travel by a non-stop flight from Delhi. How much will it cost?"

The agent needs multiple tools.

#### Step 1

Find the price of a 3-star hotel in Dubai.

```text
Hotel Tool
   ↓
Hotel Price
```

#### Step 2

Find a non-stop flight from Delhi to Dubai.

```text
Flight Tool
   ↓
Flight Price
```

#### Step 3

Calculate total cost.

```text
Hotel Price + Flight Price
             ↓
       Calculator
             ↓
        Total Cost
```

The developer does not need to manually write:

```text
if user asks about Dubai:
    call hotel tool
    call flight tool
    call calculator
```

Instead, the LLM determines the required sequence.

This dynamic sequence is the core idea behind ReAct.

---

## Core ReAct Workflow

### Step 1 — Understand the problem

The LLM receives the user's prompt.

```text
What does the user actually want?
```

### Step 2 — Decide the next task

Break the problem into the next useful step.

```text
What should I solve first?
```

### Step 3 — Select a tool

Choose from the available tools.

```text
Which available tool can solve this step?
```

### Step 4 — Execute the tool

Call the selected tool.

```text
Tool → Result
```

### Step 5 — Observe

Read the tool result.

```text
Observation = Tool Result
```

### Step 6 — Decide the next action

Use the observation as new information.

```text
What should I do now?
```

### Step 7 — Repeat

Continue until the task is complete.

### Step 8 — Return final answer

Once enough information has been collected:

```text
Final Answer
```

---

## Implementing ReAct

There is **no special "ReAct package" required** for the basic implementation shown.

Instead, the developer provides:

1. Tools
2. A system prompt
3. A loop
4. Tool execution logic
5. Conversation/history management

---

### Tools in the Example

The example creates two simple Python tools.

#### Tool 1 — Get Product Price

Conceptually:

```python
get_product_price(product)
```

Example:

```text
get_product_price("iPhone 17")
→ ₹1000
```

The demo contains predefined prices for products such as:

```text
iPhone 17 → ₹1000
iPhone 15 → ₹500
```

---

#### Tool 2 — Calculator

The second tool evaluates a mathematical expression.

Example:

```text
calculator("5000 - 1000")
→ 4000
```

So the agent has:

```text
Tools
├── get_product_price
└── calculator
```

The tools are stored in a dictionary so the agent can access the corresponding Python function.

---

### System Prompt for ReAct

The **system prompt is extremely important**.

The LLM needs to understand:

- what role it has
- what tools are available
- how each tool should be called
- what arguments each tool expects
- how the ReAct process works
- when it should stop
- what format its response should follow

---

#### Example role

The agent is instructed:

```text
You are a shopping assistant.
```

Then it is told:

```text
You have these tools:
- get_product_price
- calculator
```

The system prompt also explains the expected arguments.

For example:

```text
get_product_price
→ expects a product name

calculator
→ expects a mathematical expression
```

This is important because the model needs to know **how to interact with the tools correctly**.

---

### Action and Observation

These are two terms you should remember very clearly.

#### Action

An **action** means the agent decides to call a tool.

Example:

```text
Action:
get_product_price("iPhone 17")
```

The tool then executes.

---

#### Observation

The **observation** is the result returned by the tool.

Example:

```text
Observation:
₹1000
```

Then the agent uses that observation for its next reasoning step.

---

### Complete example

```text
Reason:
I need the price of iPhone 17.

Action:
get_product_price("iPhone 17")

Observation:
₹1000

Reason:
The user has ₹5000.
I need to calculate the remaining amount.

Action:
calculator("5000 - 1000")

Observation:
₹4000

Final Answer:
₹4000 will remain.
```

---

## Maintaining Memory Between Tool Calls

This is a very important implementation detail.

Suppose the first tool returns:

```text
₹1000
```

The LLM needs to remember that value during the next iteration.

How?

The tool result is added back into the **message history**.

Conceptually:

```text
User
 ↓
Assistant → Action
 ↓
Tool → Observation
 ↓
Assistant → Next Action
```

The previous assistant/tool interaction becomes part of the next model call.

This allows the model to know:

```text
iPhone 17 price = ₹1000
```

when it performs the next calculation.

---

### Why this matters

Without preserving the previous result:

```text
Step 1:
iPhone 17 = ₹1000

Step 2:
???
```

The model would not necessarily know what happened in Step 1.

With conversation history:

```text
Step 1:
iPhone 17 = ₹1000

Step 2:
I already know the price is ₹1000.
Now calculate 5000 - 1000.
```

---

## Understanding the Code Flow

The implementation follows roughly this architecture:

```text
                 ┌─────────────────┐
                 │   User Prompt   │
                 └────────┬────────┘
                          ↓
                 ┌─────────────────┐
                 │   System Prompt │
                 │   + Tools       │
                 └────────┬────────┘
                          ↓
                 ┌─────────────────┐
                 │       LLM       │
                 └────────┬────────┘
                          ↓
                 ┌─────────────────┐
                 │ Thought + Action│
                 └────────┬────────┘
                          ↓
                    Execute Tool
                          ↓
                 ┌─────────────────┐
                 │   Observation   │
                 └────────┬────────┘
                          ↓
                   Add to History
                          ↓
                       LLM Again
                          ↓
                    Next Action
                          ↓
                        ...
                          ↓
                    Final Answer
```

---

## Iteration limit

The example uses a loop such as:

```python
for _ in range(5):
```

This means the demo assumes the task can be completed within **five tool-use iterations**, this number is a design decision.

For a more complex agent, you could potentially allow:

```text
2 iterations
5 iterations
20 iterations
100 iterations
```

depending on the complexity of the application.

---

## Why Detailed System Prompts Matter

> **Don't assume the LLM automatically understands your desired workflow.**

You need to clearly explain:

- its role
- available tools
- tool syntax
- arguments
- decision-making process
- stopping conditions
- output format

For example, the system prompt tells the model:

### Rule 1

Decide what you need to do next.

### Rule 2

Select the appropriate tool.

### Rule 3

Call only one tool at a time.

### Rule 4

After taking an action, stop and wait for the observation.

### Rule 5

Never invent a tool result.

### Rule 6

Use the actual observation returned by the tool.

### Rule 7

After receiving the observation, decide the next action.

### Rule 8

Repeat until the task is complete.

### Rule 9

When complete, return the final answer.

This explicit instruction helps the model follow the desired ReAct structure.

---

## Important Concepts to Remember

### ReAct is a loop

Don't think of ReAct as:

```text
Reason once → Action once → Done
```

Think:

```text
Reason
 ↓
Action
 ↓
Observation
 ↓
Reason
 ↓
Action
 ↓
Observation
 ↓
...
 ↓
Final Answer
```

---

### Tools give LLMs external capabilities

An LLM alone may not know:

```text
Today's weather
Current flight price
Current hotel price
Current product price
```

Tools/APIs can provide that information.

---

### ReAct decides which tools to use

The developer provides the tools.

The LLM determines:

> **Which tool should I use, and when?**

---

### Tool outputs can become inputs

This is extremely important.

```text
Tool A
 ↓
Output
 ↓
Tool B
```

Example:

```text
Get Product Price
       ↓
     ₹1000
       ↓
Calculator
       ↓
5000 - 1000
       ↓
₹4000
```

So one tool's output can influence the next tool call.

---

### ReAct is especially useful for complex tasks

The more tools and possible workflows your agent has, the more difficult it becomes to hard-code every possible sequence.

ReAct allows the LLM to dynamically determine the sequence.

---

## Quick Revision

### What is ReAct?

**ReAct = Reasoning + Action**

---

### What problem does it solve?

It helps an LLM dynamically decide:

> **Which tool should I use, when should I use it, and what should I do after seeing its result?**

---

### Basic loop

```text
Reason
 ↓
Action
 ↓
Observation
 ↓
Reason
 ↓
Action
 ↓
Observation
 ↓
Final Answer
```

---

### Action vs Observation

| Term | Meaning | Example |
|---|---|---|
| **Reason** | Decide what needs to happen | "I need the product price." |
| **Action** | Call a tool | `get_product_price("iPhone 17")` |
| **Observation** | Tool result | `₹1000` |
| **Final Answer** | Answer user | "You will have ₹4000 left." |

---

### LLM vs Agent

```text
LLM:
Prompt → Answer

Agent:
Prompt
  ↓
Reason
  ↓
Tool
  ↓
Observation
  ↓
Reason
  ↓
Tool
  ↓
...
  ↓
Answer
```

---

### Most important implementation pieces

```text
1. Tools
2. System Prompt
3. User Prompt
4. LLM Call
5. Action Extraction
6. Tool Execution
7. Observation
8. Message History
9. Loop
10. Final Answer
```

---
