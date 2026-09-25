# AI Agent Evaluation: Levels, Testing Methods, and Golden Datasets

This lesson focuses on **how to evaluate an AI agent after building it**.

Until now, you've learned how to build agents, give them tools, use LangGraph, and create multi-agent systems. But building an agent is only half the job. You also need to determine whether it:

- Produces the correct result.
- Uses tools in an appropriate way.
- Avoids unnecessary or repeated tool calls.
- Handles individual components correctly.
- Follows the expected workflow for different scenarios.

The lesson covers five interview-oriented topics:

1. Why is evaluating AI agents difficult?
2. What are the levels of AI agent evaluation?
3. What is trajectory evaluation?
4. Who or what can evaluate an AI agent?
5. What is a golden dataset, and how do you create one?

## Why is AI agent evaluation difficult?

To understand this, first compare traditional software with AI agents.

### Traditional software is generally deterministic

Consider a payment application such as Paytm.

Suppose you transfer ₹100 to another person.

Expected behaviour:

1. ₹100 should be deducted from your account.
2. ₹100 should be credited to the recipient's account.
3. The transaction should be recorded correctly.

If the money is deducted but never reaches the recipient, the system has failed.

We know what the expected result should be. We can write test cases and compare the actual result against the expected result.

This is deterministic behaviour: for a given valid input and system state, the program is expected to follow defined rules and produce a predictable outcome.

### AI agents are not fully deterministic

An AI agent consists of an LLM with access to tools.

For example:

- LLM: decides what action to perform.
- Web search: retrieves information.
- Calculator: performs calculations.
- Other tools: perform external operations.

Unlike a conventional function, an LLM may produce different responses when given the same question multiple times.

For example, ask an LLM:

> Who is Pratyush Narain?

One response might describe his professional background. Another might emphasize his social-media presence.

Both answers might be correct, even though their wording and details differ.

This creates a testing challenge:

- Two different responses can both be correct.
- A response can be partially correct.
- A response can sound convincing but contain incorrect information.
- The agent may reach a correct answer using an inefficient or inappropriate sequence of tool calls.

Therefore, comparing an AI agent's response against one exact expected string is often insufficient.

### Why traditional testing alone isn't enough

| Traditional software | AI agents |
|---|---|
| Often follows explicitly defined rules | Uses probabilistic model outputs |
| Expected outputs can often be specified exactly | Multiple responses may be acceptable |
| Function behaviour can be tested directly | Tool selection and reasoning paths also matter |
| Output comparison is often straightforward | Semantic evaluation may be required |

**Interview answer: Why is AI agent evaluation difficult?**

AI agent evaluation is challenging because LLM-based systems are non-deterministic. The same input can produce different valid outputs, and correctness depends not only on the final response but also on tool selection, tool arguments, and the execution trajectory. Consequently, exact-output testing alone is not sufficient.

---

## Levels of AI agent evaluation

The instructor explains three evaluation levels using a hotel-booking example.

Suppose you give an AI agent this task:

> Book a three-star hotel in a city that has a beach.

The agent has two tools:

- A tool to find cities with beaches.
- A tool to search for and book hotels.

How do we evaluate whether the agent did its job correctly?

### Level 0 — Final outcome evaluation

What was the result?

At this level, you only check whether the final task was completed successfully.

You don't care how the agent completed it yet.

For the hotel example, two conditions must be satisfied:

1. The hotel must be three-star.
2. The hotel must be in a city with a beach.

Consider these outcomes:

| Actual booking | Result |
|---|---|
| Three-star hotel in Chennai | Pass, assuming the hotel and beach conditions are verified |
| Five-star hotel in Chennai | Fail |
| Three-star hotel in Patna | Fail |
| No booking made | Fail |

The point is simple: **Did the agent accomplish the requested task or not?**

This is also called outcome-based evaluation.

### Level 1 — Trajectory evaluation

How did it reach the result?

Suppose the agent successfully booked a three-star hotel in Chennai.

Level 0 says the task succeeded.

But now we want to inspect the process that led to that result.

This is called the agent's **trajectory**.

A trajectory is the sequence of actions, tool calls, observations, and decisions made by the agent while completing a task.

For example, consider two possible approaches.

**Approach A — Find the city first**

1. Search for cities that have beaches.
2. Select a suitable city.
3. Search for three-star hotels in that city.
4. Book a hotel.

**Approach B — Find hotels first**

1. Search for three-star hotels across a very large geographical area.
2. Collect a huge list of hotels.
3. Check which hotels are in cities with beaches.
4. Book a hotel.

Both approaches might produce a successful booking. However, Approach A may be much more efficient because it narrows down the search space before searching for hotels.

This is why checking the final outcome alone isn't enough.

#### What should you inspect in a trajectory?

**1. Tool selection**

Did the agent call the correct tools?

For example, did it use the city-search tool before searching for hotels?

**2. Tool arguments**

Did it pass appropriate arguments?

For example, did it search for three-star hotels in the selected beach city rather than searching without geographical restrictions?

**3. Repeated tool calls**

Did it call the same tool unnecessarily?

Example:

```text
Call 1: Search cities with beaches
Result: Chennai, Goa, Mumbai

Call 2: Search cities with beaches
Result: Chennai, Goa, Mumbai

Call 3: Search cities with beaches
Result: Chennai, Goa, Mumbai

Call 4: Search hotels in Chennai
```

The first call already returned the required information. Repeating it without a reason wastes time and resources.

**4. Infinite loops or excessive retries**

Did the agent keep repeating actions without making progress?

**5. Efficiency of the execution path**

Could the agent have completed the task with fewer tool calls or a better sequence of operations?

**The difference between Level 0 and Level 1**

- **Level 0** · **WHAT?** · Did the agent complete the task successfully?
- **Level 1** · **HOW?** · Did it use an appropriate and efficient trajectory?

This is similar to DSA problem-solving:

- First, check whether the solution passes the test cases.
- Then, check whether the solution uses an efficient algorithm or brute force.

### Level 2 — Individual component evaluation

Is each component working?

The instructor's third level focuses on testing individual tools or components independently.

This is similar to unit testing in traditional software engineering.

Consider a calculator tool:

```python
def calculate(a, b):
    return a + b
```

You can easily test it:

```python
assert calculate(3, 5) == 8
assert calculate(10, 20) == 30
```

The expected output is known, so normal code-based tests are sufficient.

Now consider a more complex component: a resume parser.

Its job is to:

1. Accept a PDF resume.
2. Extract the information.
3. Convert the information into JSON.
4. Return the structured data.

There are several possible failure points:

- The PDF may not be readable.
- The name may be extracted incorrectly.
- The email address may be missing.
- The JSON structure may be invalid.
- Important information may be omitted.

You should test the resume parser independently to verify that the component itself works correctly.

For example:

```python
result = parse_resume("resume.pdf")

assert result["name"] is not None
assert result["email"] is not None
assert isinstance(result, dict)
```

These checks test basic properties of the output. You would also compare extracted fields against known expected values using representative sample resumes.

**Important:** A component passing its individual tests doesn't guarantee that the complete agent will work. The LLM might still select the wrong tool or pass incorrect arguments to it.

### A note about the level numbering

---

## Who or what evaluates an AI agent?

The instructor introduces three evaluation approaches.

### Code-based evaluation

Use ordinary Python code or automated tests when the expected result is deterministic.

Examples:

- Calculator output.
- JSON schema validation.
- Required fields in extracted data.
- Whether a tool returned a valid status code.
- Whether a transaction amount matches the expected value.

Example:

```python
def test_calculator():
    assert calculate(2, 2) == 4
    assert calculate(10, 5) == 15
    assert calculate(8, 3) == 11
```

This approach is fast, repeatable, and inexpensive.

**Use it when the expected behaviour can be defined precisely.**

### LLM-as-a-Judge

LLM evaluates another LLM's output

Some outputs are difficult to evaluate using exact string comparisons.

For example, imagine a web-search tool that answers:

> Who is Pratyush Narain?

The response might be phrased differently each time. Writing fixed string comparisons for every acceptable response would be impractical.

Instead, another LLM can act as an evaluator.

You provide it with:

- The original question.
- The generated answer.
- Relevant reference information or evaluation criteria.

Then ask it to judge the answer.

Conceptual example:

```python
evaluation_prompt = """
You are an AI evaluator.

Question:
{question}

Reference information:
{reference}

Agent answer:
{answer}

Evaluate whether the answer is:
1. Relevant
2. Factually supported
3. Complete

Return a structured evaluation.
"""
```

The judge can return a score or structured feedback.

For example:

```json
{
  "relevant": true,
  "supported": true,
  "complete": false,
  "reason": "The answer omitted an important detail."
}
```

LLM-as-a-Judge is useful for semantic evaluation, but it is not infallible. The judge can also make mistakes or exhibit bias. For important applications, calibrate it against human-reviewed examples.

### Human review

Some evaluations require human judgment.

For example:

- Was the agent's overall strategy sensible?
- Did it follow the expected business workflow?
- Did it unnecessarily repeat actions?
- Did it handle an unusual customer situation appropriately?

A human can inspect the agent's trajectory and decide whether the execution was acceptable.

This is particularly useful when the expected behaviour involves business rules, judgment, or complex workflows.

### Comparison of evaluation methods

| Method | Best suited for | Example |
|---|---|---|
| Code-based tests | Deterministic behaviour | Calculator, JSON validation |
| LLM-as-a-Judge | Semantic or flexible outputs | Web-search answer evaluation |
| Human review | Complex decisions and workflows | Reviewing agent trajectories |

**The key lesson:** You don't need to choose only one. A good evaluation system can combine all three methods. 

---

## Golden dataset

### What is a golden dataset?

A golden dataset is a collection of predefined test scenarios that describe how you expect your AI agent to behave.

Think of it as an evaluation reference for your agent.

Before evaluating the agent, you define:

- What input or scenario should be tested?
- Which tools should the agent use?
- What arguments should it pass to those tools?
- What conditions must be satisfied for the task to count as successful?

You then run your agent against these test cases and compare its actual behaviour with your expectations.

### Four important fields

According to the instructor, a golden dataset contains four main elements.

| Field | Meaning |
|---|---|
| Input | The user's request or scenario |
| Expected tools | Which tools should be called |
| Expected arguments | What arguments should be passed to those tools |
| Success check | How to determine whether the task succeeded |

Let's understand each one.

**1. Input**

This is the scenario you want to test.

Example:

```text
I received cold food and want a ₹300 refund.
My order ID is ORD123.
```

Input doesn't have to be plain text. It could also include images, PDFs, or other relevant information.

**2. Expected tools**

Define which tools the agent is expected to use.

For the refund example, imagine company policy requires human approval before issuing a refund.

Expected tools:

```text
1. Contact human support
2. Process refund (only after approval)
```

If the agent directly issues a refund without requesting approval, it has violated the expected workflow.

**3. Expected arguments**

Define what information should be passed to the selected tools.

For example:

```json
{
  "order_id": "ORD123",
  "refund_amount": 300,
  "reason": "Customer received cold food"
}
```

The agent must not confuse a refund request with an order-cancellation request.

**4. Success check**

Define what successful completion means.

For example:

- Human approval was requested.
- The correct order ID was supplied.
- The refund was not issued without approval.
- If approval was granted, the refund was processed successfully.
- The customer received an appropriate response.

### Complete golden dataset example

Let's combine these fields into one example.

**Golden test case #001** · Refund request

**Input**

"I received cold food. Please refund ₹300 for order ORD123."

**Expected tools**
1. `contact_human_support`
2. `process_refund` — only after approval
**Expected arguments**
```json
{
"order_id": "ORD123",
"amount": 300,
"reason": "Cold food received"
}
```
**Success check**
- Correct order ID supplied.
- Human approval requested.
- Refund processed only after approval.
- Customer receives confirmation.

This test case now becomes a reference against which you can evaluate your agent.

### Why do we need a golden dataset?

Imagine you've developed a Zomato customer-support agent.

Customers can:

- Request refunds.
- Cancel orders.
- Reschedule orders.
- Complain about delivery.
- Ask to speak to a human.
- Ask unrelated questions.

You need to anticipate different scenarios and define how your agent should respond.

You might start with 10 test cases, then expand to 100 or 1,000 as the system becomes more complex.

The purpose isn't to imagine every possible situation. It's to build a representative collection of important scenarios and expected behaviours.

### How is a golden dataset used?

**Golden dataset**

Inputs + expected tools + arguments + success criteria

**Run AI agent on each test case**

**Collect actual outputs and trajectories**

**Compare actual behaviour with expected behaviour**

- **Pass**
- **Fail**

The evaluation can use code, an LLM judge, or human review depending on what needs to be checked.

### Example golden dataset in Python

Here's a simple structure you could use in a real project:

```python
golden_dataset = [
    {
        "id": "test_001",
        "input": (
            "I received cold food. "
            "Please refund Rs. 300 for order ORD123."
        ),
        "expected_tools": [
            "contact_human_support",
            "process_refund"
        ],
        "expected_arguments": {
            "order_id": "ORD123",
            "amount": 300,
            "reason": "Cold food received"
        },
        "success_check": {
            "human_approval_required": True,
            "refund_only_after_approval": True,
            "customer_confirmation": True
        }
    }
]
```

One useful distinction: the expected tools don't necessarily have to be called in precisely the same order in every valid workflow. Your evaluation criteria should allow legitimate alternative trajectories where appropriate, while still enforcing essential business rules.

---

## Putting all the concepts together

Let's say you have built a Zomato customer-support AI agent.

A customer requests a refund.

How would you evaluate it using everything learned today?

| Evaluation concept | What you check |
|---|---|
| Level 0 — Outcome | Was the refund handled correctly? |
| Level 1 — Trajectory | Did the agent contact human support before processing the refund? |
| Level 2 — Component | Does the refund tool work correctly when called with valid arguments? |
| Code-based evaluation | Is the refund amount and order ID correct? |
| LLM-as-a-Judge | Is the final customer response relevant and appropriate? |
| Human review | Was the workflow followed correctly in unusual situations? |
| Golden dataset | Does the agent behave as expected across predefined scenarios? |

This is the central idea of AI agent evaluation: you don't just test the final answer. You evaluate the overall system and its individual components.

---

## Important questions and answers

**1. Why is AI agent evaluation difficult?**

Because LLM-based agents are non-deterministic. The same input may produce different valid outputs, and correctness can depend on the final result, tool calls, arguments, and execution trajectory.

**2. What is trajectory evaluation?**

Trajectory evaluation examines the sequence of actions an agent takes to complete a task, including tool selection, tool arguments, repeated calls, and execution efficiency.

**3. What is the difference between outcome and trajectory evaluation?**

Outcome evaluation checks whether the task succeeded. Trajectory evaluation checks how the agent achieved that result.

**4. What is LLM-as-a-Judge?**

It uses an LLM to evaluate another model's output against a question, reference information, or evaluation criteria, especially when exact string comparison is unsuitable.

**5. When should you use code-based evaluation?**

When the expected result is deterministic and can be checked precisely, such as calculator results, required JSON fields, or schema validation.

**6. What is human evaluation?**

A human reviews outputs or execution traces when correctness or quality requires contextual judgment, such as reviewing complex agent workflows.

**7. What is a golden dataset?**

A collection of predefined evaluation scenarios containing the input, expected tools, expected tool arguments, and success criteria.

**8. Why do we need expected tool arguments?**

To verify that the agent passes the correct information to each tool, rather than merely checking whether it called the correct tool.

**9. Can a component pass its unit tests while the complete agent still fails?**

Yes. A tool can work correctly in isolation, but the agent may select the wrong tool, provide incorrect arguments, or use the wrong execution sequence.

---