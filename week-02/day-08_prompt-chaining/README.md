# Prompt Chaining

## What is Prompt Chaining?

**Prompt Chaining** is a technique where a complex task is broken into multiple smaller tasks, and each task is handled by a separate LLM call.

The output of one LLM call becomes the input to the next LLM call.

### Simple flow

```text
Complex Task
     ↓
Prompt 1 → Output 1
             ↓
Prompt 2 → Output 2
             ↓
Prompt 3 → Output 3
             ↓
Prompt 4 → Final Output
```

### Core idea

> **One prompt → One focused task → Output → Next prompt**

Instead of asking an LLM to complete everything in one huge prompt, we create a sequence of smaller, controlled steps.

---

## Why Prompt Chaining is Needed

Imagine you need to build a house.

You could give one person a giant instruction:

```text
Buy land → design house → get permission → construct →
paint → furnish → deliver final house
```

Or you can break the work into stages:

```text
Step 1 → Buy land
Step 2 → Design the house
Step 3 → Get construction plan
Step 4 → Build
Step 5 → Paint
```

The second approach is easier to:

- understand
- debug
- modify
- test
- control

The same principle applies to LLM applications.

### Without Prompt Chaining

```text
Huge Prompt
    ↓
LLM
    ↓
Final Answer
```

The LLM has to perform many operations inside one call.

### With Prompt Chaining

```text
Prompt 1 → LLM → Result 1
                    ↓
Prompt 2 → LLM → Result 2
                    ↓
Prompt 3 → LLM → Result 3
                    ↓
Prompt 4 → LLM → Final Result
```

This gives the developer much more control over the workflow.

---

## Example: Resume Evaluator

We'll use a **resume evaluation system** as the main example.

### Goal

Given:

- a candidate's resume
- a job description

the system should determine whether the candidate is a good fit.

A simplified workflow could be:

```text
Resume
   ↓
Extract Candidate Skills
   ↓
Job Description
   ↓
Extract Required Skills
   ↓
Compare Skills
   ↓
Generate Score
   ↓
Make Hiring Decision
```

Instead of doing everything in one LLM call, we create multiple calls.

---

### Step 1 — Extract Candidate Skills

Input:

```text
Candidate Resume
```

Prompt:

```text
Extract the skills from this resume.
Return only the skills.
Do not invent any skills.
```

Output:

```text
Python
REST API
Docker
Git
AWS
Django
```

---

### Step 2 — Extract Job Description Skills

Input:

```text
Job Description
```

Prompt:

```text
Extract the skills required by this job description.
Return only the required skills.
Do not invent any skills.
```

Output:

```text
Python
REST API
Django
PostgreSQL
Docker
AWS
```

---

### Step 3 — Compare the Skills

Now we pass the outputs from Steps 1 and 2 to another LLM call.

```text
Candidate Skills:
Python
REST API
Docker
Git
AWS

Required Skills:
Python
REST API
Django
PostgreSQL
Docker
AWS
```

Prompt:

```text
Compare the candidate's skills with the required skills.

Generate:
1. Matching skills
2. Missing skills
3. A score between 1 and 100
4. A short verdict
```

Possible output:

```text
Matching:
Python
REST API
Docker
AWS

Missing:
Django
PostgreSQL

Score:
70

Verdict:
Fair fit with a strong foundation.
```

---

### Step 4 — Take an Action

Now we can apply business logic.

```text
if score >= 60:
    → Contact HR / proceed to interview
else:
    → Send rejection email
```

So the entire workflow becomes:

```text
Resume
  ↓
[LLM Call 1]
Extract Candidate Skills
  ↓
Candidate Skills

Job Description
  ↓
[LLM Call 2]
Extract Required Skills
  ↓
Required Skills

Candidate + JD Skills
  ↓
[LLM Call 3]
Compare + Score
  ↓
Score
  ↓
[Business Logic / LLM Call 4]
Decision
  ↓
Interview / Rejection
```

This is **Prompt Chaining**.

---

## How Prompt Chaining Works

The most important pattern to remember is:

```text
Input
  ↓
Prompt A
  ↓
Output A
  ↓
Prompt B
  ↓
Output B
  ↓
Prompt C
  ↓
Output C
```

The output of one step becomes the input of another.

### Example

```python
candidate_skills = extract_resume_skills(resume)

job_skills = extract_job_skills(job_description)

score = compare_skills(candidate_skills, job_skills)

decision = make_decision(score)
```

Each function represents an individual step in the chain.

### Think of it as a pipeline

```text
Data → Transform → Transform → Transform → Result
```

This is similar to a traditional software pipeline, except some transformations are performed by LLMs.

---

## Benefits of Prompt Chaining

There are several important reasons to use Prompt Chaining in production AI systems.

---

### Debugging

This is one of the **biggest advantages**.

Suppose your final resume score is unexpectedly **30**, but you expected **80**.

If everything happens in one huge prompt:

```text
Resume → Huge Prompt → Score = 30
```

Where did the problem occur?

Possibilities:

- Resume extraction failed
- JD extraction failed
- Skill matching failed
- Scoring failed
- Decision logic failed

You have to inspect the entire process.

#### With Prompt Chaining

You can inspect each stage independently:

```text
Step 1 → Candidate Skills ✓
Step 2 → JD Skills ✓
Step 3 → Matching ✗
Step 4 → Scoring
```

Now you immediately know that **Step 3** is the problem.

You only need to fix Step 3.

#### Key idea

> **Break a complex AI workflow into observable stages so each stage can be tested independently.**

---

### Modularity

Prompt chaining makes the system **modular**.

For example:

```text
Step 1 → Resume Extraction
Step 2 → JD Extraction
Step 3 → Skill Matching
Step 4 → Scoring
```

If the matching logic is broken, you don't need to rewrite the entire application.

You only modify:

```text
Step 3
```

Similarly:

```text
Extraction problem → Fix extraction module
Matching problem   → Fix matching module
Scoring problem    → Fix scoring module
```

#### Think of software modules

```text
┌───────────────┐
│ Resume Parser │
└───────┬───────┘
        ↓
┌───────────────┐
│ JD Parser     │
└───────┬───────┘
        ↓
┌───────────────┐
│ Skill Matcher │
└───────┬───────┘
        ↓
┌───────────────┐
│ Scorer        │
└───────────────┘
```

Each component has a specific responsibility.

---

### Using Different Models

Prompt chaining also allows you to use **different models for different tasks**.

Not every task requires the most powerful and expensive model.

For example:

| Task | Model Requirement |
|---|---|
| Complex reasoning | Powerful/expensive model |
| Resume understanding | Medium/strong model |
| Simple classification | Smaller/cheaper model |
| Formatting | Small/cheap model |
| Simple comparison | Cheap model |

#### Example

```text
Step 1: Resume extraction
        ↓
      Cheap model

Step 2: JD extraction
        ↓
      Cheap model

Step 3: Complex skill analysis
        ↓
      Powerful model

Step 4: Send email
        ↓
      Simple model / normal code
```

This can significantly reduce **LLM/API costs**.

#### Important principle

> **Use the strongest model where intelligence is actually required, not everywhere.**

---

### Retrying Individual Steps

Another advantage is that individual steps can be retried.

Suppose:

```text
Step 1 → Incorrect extraction
```

You can retry only Step 1.

For example:

```text
Step 1
  ↓
Bad output
  ↓
Retry with refined prompt
  ↓
Better output
```

There is no need to execute the entire workflow again.

This is particularly useful when working with probabilistic LLM outputs.

---

## Prompt Chaining vs ReAct

This distinction is **very important for AI Engineer interviews**.

Both can involve multiple LLM/tool operations, but **who controls the workflow is different**.

---

### ReAct

**ReAct = Reasoning + Action**

In a ReAct-style agent:

> The LLM decides what action/tool to take next.

You provide the model with available tools.

For example:

```text
Available tools:
- PDF Reader
- Search
- Calculator
- Email
- Database
```

The LLM decides:

```text
I need to read the PDF.
        ↓
Use PDF Reader

Now I need to calculate something.
        ↓
Use Calculator

Now I need to send an email.
        ↓
Use Email
```

The sequence is dynamically determined by the model.

---

### Prompt Chaining

In Prompt Chaining:

> **The developer decides the sequence.**

For example:

```text
Step 1 → Extract resume skills
Step 2 → Extract JD skills
Step 3 → Compare skills
Step 4 → Calculate score
Step 5 → Take action
```

The model doesn't decide the overall workflow.

---

### ReAct vs Prompt Chaining

| Feature | ReAct | Prompt Chaining |
|---|---|---|
| Full form | Reasoning + Action | — |
| Who decides next step? | LLM/Agent | Developer |
| Workflow | Dynamic | Predetermined |
| Tools | Important | Optional |
| Best for | Open-ended tasks | Known workflows |
| Control | Lower | Higher |
| Debugging | More complex | Easier |
| Example | AI agent | Resume pipeline |

#### Easy way to remember

> **ReAct → "LLM, you decide what to do next."**

> **Prompt Chaining → "I, the developer, decide what happens next."**

---

## Implementation Example

The architecture can be simplified to:

```python
def ask_llm(system_prompt, user_prompt):
    # Make LLM API call
    return response
```

Then create individual functions.

### Step 1

```python
def extract_resume_skills(resume):
    system_prompt = """
    You are a professional HR assistant.
    Extract skills from the candidate's resume.
    Return only the skills.
    Do not invent skills.
    """

    user_prompt = f"""
    Extract the skills from this resume:

    {resume}
    """

    return ask_llm(system_prompt, user_prompt)
```

### Step 2

```python
def extract_job_skills(job_description):
    system_prompt = """
    You are a professional HR assistant.
    Extract the skills required by the job description.
    Return only the skills.
    """

    user_prompt = f"""
    Extract the skills from this job description:

    {job_description}
    """

    return ask_llm(system_prompt, user_prompt)
```

### Step 3

```python
def compare_skills(candidate_skills, job_skills):
    system_prompt = """
    You are a professional HR assistant.

    Compare candidate skills with job requirements.
    Generate a score between 1 and 100.
    Also provide a short verdict.
    """

    user_prompt = f"""
    Candidate Skills:
    {candidate_skills}

    Required Skills:
    {job_skills}
    """

    return ask_llm(system_prompt, user_prompt)
```

### Chain them

```python
candidate_skills = extract_resume_skills(resume)

job_skills = extract_job_skills(job_description)

result = compare_skills(
    candidate_skills,
    job_skills
)
```

---

## Key Takeaways

### Prompt Chaining

Break a complex AI task into multiple smaller LLM calls.

```text
Task
 ↓
Prompt 1
 ↓
Prompt 2
 ↓
Prompt 3
 ↓
Result
```

### Each prompt should have a focused responsibility

Bad:

```text
Extract → Analyze → Score → Decide → Email
```

all inside one giant prompt.

Better:

```text
Extract
  ↓
Analyze
  ↓
Score
  ↓
Decide
  ↓
Email
```

### Outputs become inputs

```text
Output 1 → Input 2
Output 2 → Input 3
Output 3 → Input 4
```

###  Prompt chaining improves debugging

You can inspect each stage separately.

### Prompt chaining improves modularity

Individual steps can be modified without rewriting the entire workflow.

### Different models can be used

Use:

- powerful models for complex tasks
- cheaper models for simple tasks

### Steps can be retried independently

If one step fails, retry that step instead of the entire pipeline.

### Prompt Chaining ≠ ReAct

The key distinction:

```text
Prompt Chaining → Developer controls workflow
ReAct           → LLM controls workflow
```

---

## Important Questions

### Q1. What is Prompt Chaining?

**Answer:**

Prompt Chaining is a technique for breaking a complex task into multiple smaller LLM calls, where the output of one call is passed as input to the next call.

---

### Q2. Why use Prompt Chaining instead of one large prompt?

Because it provides:

- easier debugging
- modularity
- better control
- easier testing
- ability to retry individual steps
- ability to use different models for different tasks
- potentially lower cost

---

### Q3. How is Prompt Chaining different from ReAct?

In Prompt Chaining, the **developer defines the sequence of steps**.

In ReAct, the **LLM dynamically decides which action/tool to take next** based on the current situation.

---

### Q4. Give a real-world example of Prompt Chaining.

A resume evaluation system:

```text
Resume
 ↓
Extract candidate skills
 ↓
Extract job requirements
 ↓
Compare skills
 ↓
Generate score
 ↓
Make hiring decision
```

Each stage can be implemented as a separate LLM call.

---

### Q5. What is the biggest debugging advantage?

You can identify **which specific stage produced the incorrect result** instead of debugging one massive LLM response.

---

### Q6. Why use different models in a prompt chain?

Different tasks have different complexity requirements.

Using an expensive model for every step increases cost unnecessarily. A cheaper model can handle simple tasks while a powerful model handles complex reasoning.

---