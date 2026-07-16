# AI Mini Project — Resume Evaluator

## What We Are Building

Imagine an HR team has:

```text
Job Description
        +
1000 Resumes
        ↓
   AI Resume Evaluator
        ↓
┌─────────────────────┐
│ Candidate A → 87%   │
│ Candidate B → 79%   │
│ Candidate C → 61%   │
│ Candidate D → 42%   │
└─────────────────────┘
        ↓
Rank candidates
        ↓
Top candidates → HR review
```

Instead of manually reading every resume, the AI system performs the initial screening.

### Example

Suppose the JD requires:

- Bachelor's degree
- Python
- DSA
- AWS
- 2+ years experience

A resume might contain:

- B.Tech
- Python
- JavaScript
- AWS
- 1 year experience

The evaluator could produce something like:

```json
{
  "score": 72,
  "matching_skills": [
    "Python",
    "AWS"
  ],
  "missing_skills": [
    "DSA"
  ],
  "experience_requirement_met": false,
  "verdict": "Potential candidate, but experience requirement is not fully met."
}
```

The important idea is that the LLM doesn't simply return a paragraph.  
It returns **structured information that the program can process**.

---

## Project Architecture

The entire project can be understood as five major stages:

```text
                 ┌──────────────────┐
                 │  Job Description │
                 └────────┬─────────┘
                          ↓
                  Parse into JSON
                          ↓
                 ┌──────────────────┐
                 │ Structured Job  │
                 │      Schema     │
                 └────────┬─────────┘
                          │
                          │
┌─────────────┐           │
│ PDF / DOCX  │           │
└──────┬──────┘           │
       ↓                  │
Extract text              │
       ↓                  │
│   Resumes   │           │
Parse with LLM            │
       ↓                  │
Structured Resume ────────┤
                          ↓
                  Compare JD + Resume
                          ↓
                     Match Result
                          ↓
                     Score 0–100
                          ↓
                    Sort Candidates
                          ↓
                   Top / Bottom N
```

The instructor breaks the project into these major stages: JD schema, resume schema, resume reading, resume parsing, and final scoring.

---

## Part 1 — Parse the Job Description

### Why structure the Job Description?

A Job Description is initially just unstructured text:

```text
Software Development Engineer

We are looking for a candidate with...
Bachelor's degree...
Knowledge of Python...
Experience with AWS...
...
```

Working directly with this text makes comparison difficult.

Instead, convert it into a structured object:

```json
{
  "role": "Software Development Engineer",
  "required_skills": [
    "Python",
    "DSA"
  ],
  "preferred_skills": [
    "AWS",
    "Docker"
  ],
  "minimum_experience": 2,
  "education_requirements": [
    "Bachelor's degree"
  ],
  "responsibilities": [
    "Develop software",
    "Write tests"
  ]
}
```

This makes later comparison much easier.

---

### Designing the Job Description Schema

The project identifies common JD fields:

#### Role

What position is being advertised?

```text
Software Development Engineer
Software Test Engineer
Principal Engineer
...
```

#### Required Skills

Skills that are **mandatory**.

Examples:

```text
Python
Java
C++
Bachelor's degree
```

If the candidate doesn't satisfy a required condition, that can significantly affect their score.

#### Preferred Skills

These are desirable but **not mandatory**.

Examples:

```text
Docker
Kubernetes
Git
CI/CD
Linux
AI/ML
```

Think:

> **Required = Must have**  
> **Preferred = Good to have**

#### Minimum Experience

Examples:

```text
0 years
2 years
5 years
10 years
```

#### Educational Requirements

Examples:

```text
B.Tech
BCA
MCA
Bachelor's degree
Master's degree
```

#### Responsibilities

What will the candidate actually be expected to do?

---

### Use Pydantic for the Schema

Instead of treating the LLM response as arbitrary text, define a schema using **Pydantic**.

Conceptually:

```python
class JobDescription(BaseModel):
    role: str
    required_skills: list[str]
    preferred_skills: list[str]
    minimum_experience: int | None
    education_requirements: list[str]
    responsibilities: list[str]
```

The exact implementation can vary, but the principle is:

> **Define the structure first → ask the LLM to fill the structure.**

---

### Prompt Design

The system prompt should establish the LLM's role and instructions.

Conceptually:

```text
You are an expert HR assistant.

Analyze the provided job description.

Extract information according to the provided schema.

Return only valid JSON matching the schema.

Do not invent information.
Do not return unnecessary fields.
```

Then the user prompt supplies the actual JD:

```text
Analyze the following job description:

<JOB DESCRIPTION>
```

---

## Part 2 — Design the Resume Schema

This is more difficult than the JD schema.

Why?

Because **resumes are highly inconsistent**.

One resume might contain:

```text
Experience
Projects
Skills
Education
```

Another might contain:

```text
Work History
Technical Skills
Internships
Academic Background
```

Another may not contain experience at all.

Therefore, the schema must be flexible.

---

### Experience Schema

Create a reusable `Experience` structure.

Conceptually:

```python
class Experience(BaseModel):
    company: str
    role: str
    duration: str
    description: list[str]
    skills_used: list[str]
```

For example:

```json
{
  "company": "ABC Technologies",
  "role": "Software Developer",
  "duration": "2024-2026",
  "description": [
    "Developed REST APIs",
    "Built React applications"
  ],
  "skills_used": [
    "React",
    "Node.js",
    "MongoDB"
  ]
}
```

---

### Resume Schema

Then the main Resume schema can contain:

```python
class Resume(BaseModel):
    name: str
    email: str
    phone: str
    total_experience_years: float | None
    skills: list[str]
    experiences: list[Experience]
    projects: list[str]
    certifications: list[str]
    education: list[str]
```

The important design principle is:

> **Experience is a reusable object, while Resume contains a list of Experience objects.**

So:

```text
Resume
 ├── name
 ├── email
 ├── skills
 ├── experiences
 │     ├── Experience
 │     ├── Experience
 │     └── Experience
 ├── projects
 ├── certifications
 └── education
```

---

### Optional Fields

Not every resume contains every section.

For example:

```text
Candidate A → Has experience
Candidate B → No experience
Candidate C → Has certifications
Candidate D → No certifications
```

Therefore, many fields should be optional.

Conceptually:

```python
experience: list[Experience] | None
```

or appropriate defaults such as an empty list.

#### Key idea

> **Real-world input is messy. Your schema should handle missing information gracefully.**

---

## Part 3 — Extract Text from Resumes

Resumes may arrive as:

- PDF
- DOCX

The LLM cannot simply treat a local file path as the resume content.

First:

```text
PDF/DOCX
   ↓
Extract text
   ↓
Plain text
   ↓
LLM
```

---

### Reading PDF Files

The project uses a PDF reader to:

1. Open the PDF.
2. Iterate through pages.
3. Extract text from each page.
4. Combine the text.

Conceptually:

```python
def read_pdf(file_path):
    text = ""

    for page in pdf:
        text += extract_text(page)

    return text
```

---

### Reading DOCX Files

DOCX documents are slightly different.

Instead of pages, the document contains **paragraphs** and potentially **tables**.

So you need to extract:

```text
Paragraphs
+
Tables
```

---

### Important: Extract Tables Too

This is an easy detail to miss.

A resume might have an education table:

| Degree | Institution | CGPA | Year |
|---|---|---:|---:|
| 10th | School A | 90% | 2018 |
| 12th | School B | 88% | 2020 |

If you extract only paragraphs, this information may be lost.

Therefore:

```text
DOCX
 ├── Paragraphs
 └── Tables
```

Both should be extracted.

---

### Create a Unified `read_resume()` Function

Instead of making the rest of the program care about file formats:

```python
read_resume(file_path)
```

should internally decide:

```text
.pdf
  ↓
read_pdf()

.docx
  ↓
read_docx()

anything else
  ↓
ignore / return None
```

This is a good abstraction.

The rest of the application only needs:

```python
resume_text = read_resume(file_path)
```

It doesn't need to know whether the resume was PDF or DOCX.

---

## Part 4 — Parse Resumes Using an LLM

Now we have:

```text
Resume File
     ↓
Extract Text
     ↓
Resume Text
```

Next:

```text
Resume Text
     ↓
LLM
     ↓
Structured Resume JSON
```

---

### System Prompt

The LLM should be told something like:

```text
You are an expert resume parser.

Analyze the provided resume.

Extract information according to the Resume schema.

Different resumes may use different headings.

For example:
- Experience
- Work Experience
- Professional Experience
- Employment
- Internship

These may represent similar concepts.

Return only valid JSON matching the schema.

Do not invent information.
If information is unavailable, leave the field empty/null.
```

This is important because resumes use inconsistent terminology.

---

### User Prompt

The user prompt then supplies the actual resume:

```text
Analyze the following resume:

<RESUME TEXT>
```

The LLM returns structured data.

For example:

```json
{
  "name": "Kapil Negi",
  "email": "kapil@example.com",
  "skills": [
    "React",
    "Node.js",
    "MongoDB",
    "Python"
  ],
  "total_experience_years": 1,
  "experiences": [],
  "projects": [
    "KSN Drive",
    "AI Article Summarizer"
  ],
  "certifications": [],
  "education": [
    "B.Tech in Computer Science"
  ]
}
```

---

## Part 5 — Match Resume Against Job Description

At this point we have two structured objects:

### Job

```json
{
  "role": "Software Engineer",
  "required_skills": ["Python", "DSA"],
  "preferred_skills": ["AWS", "Docker"],
  "minimum_experience": 2
}
```

### Candidate

```json
{
  "name": "Candidate A",
  "skills": ["Python", "React", "AWS"],
  "total_experience_years": 3
}
```

Now the LLM compares them.

---

### Match Result Schema

Instead of returning only:

```text
82%
```

create a structured result.

Conceptually:

```python
class MatchResult(BaseModel):
    score: float
    details: dict
```

The `details` section can contain:

```json
{
  "candidate_name": "Candidate A",
  "matching_skills": [
    "Python",
    "AWS"
  ],
  "missing_skills": [
    "DSA",
    "Docker"
  ],
  "experience_requirement_met": true,
  "verdict": "Strong technical fit..."
}
```

---

### Why Return Details?

Suppose HR gets:

```text
Candidate A → 95
Candidate B → 72
Candidate C → 48
```

A score alone doesn't explain **why**.

HR needs to know:

```text
Why did Candidate A get 95?

Why did Candidate C get 48?

Which skills are missing?

Does the candidate meet the experience requirement?
```

Therefore:

> **Score + Explanation is much more useful than Score alone.**

---

## Rate Limiting

This is one of the most practical engineering lessons in the project.

Suppose you have:

```text
1000 resumes
```

and each resume requires:

```text
1 LLM call for parsing
+
1 LLM call for scoring
```

That's already approximately:

```text
1000 × 2 = 2000 LLM calls
```

If you send them too quickly, the API may reject requests because of **rate limits**.

---

### What Is Rate Limiting?

A service may impose limits such as:

```text
X requests / minute
X tokens / minute
X requests / second
```

This prevents a single user from overwhelming the service.

---

### Why Does Rate Limiting Exist?

One major reason is protection against abuse such as **Denial-of-Service (DoS)** attacks.

Conceptually:

```text
Normal:

User A → Request
User B → Request
User C → Request


Abusive:

Attacker
   ↓
Millions of requests
   ↓
Server
   ↓
Service becomes unavailable
```

Rate limiting restricts how quickly requests can arrive.

---

### Sleep Between Requests

The project uses a delay between LLM calls:

```python
time.sleep(5)
```

This is a simple demonstration of spacing out requests.

For a production system, however, a better approach would usually involve:

- Exponential backoff
- Retry handling
- Concurrency limits
- Queueing
- Provider-specific rate-limit handling
- Monitoring

---

## Ranking Candidates

After evaluating every resume, you might have:

```python
all_results = [
    {"name": "A", "score": 68},
    {"name": "B", "score": 45},
    {"name": "C", "score": 78},
    {"name": "D", "score": 58}
]
```

Sort by score:

```python
all_results.sort(
    key=lambda x: x["score"],
    reverse=True
)
```

Result:

```text
C → 78
A → 68
D → 58
B → 45
```

Then:

```python
top_candidates = all_results[:2]
bottom_candidates = all_results[-2:]
```

### Result

```text
Top 2:
1. Candidate C → 78
2. Candidate A → 68

Bottom 2:
1. Candidate D → 58
2. Candidate B → 45
```

---

## Important Prompt Engineering Lessons

This project teaches several important prompt-engineering principles.

### Give the LLM a Role

Instead of:

```text
Analyze this resume.
```

use:

```text
You are an expert resume evaluator...
```

This provides context for the task.

---

### Give a Schema

Don't simply say:

```text
Give me JSON.
```

Define what the JSON should contain.

```text
Name
Skills
Experience
Education
Projects
...
```

Better still, use a structured-output mechanism backed by a schema.

---

### Don't Ask for the Schema Itself

A common failure mode is the model returning something like:

```json
{
  "name": {
    "type": "string"
  },
  "skills": {
    "type": "array"
  }
}
```

That's the **schema definition**, not the extracted data.

You want:

```json
{
  "name": "John Doe",
  "skills": ["Python", "AWS"]
}
```

---

### Don't Return Unnecessary Fields

Tell the model:

```text
Do not return unnecessary fields.
```

This keeps the output clean and predictable.

---

### Don't Invent Information

This is one of the most important rules:

```text
DO NOT INVENT INFORMATION.
```

If the resume doesn't mention something:

```json
{
  "minimum_experience": null
}
```

or an appropriate empty value should be returned.

Do **not** allow the model to guess.

This reduces hallucination and improves reliability.

---

### Structured Output Makes LLMs Programmable

Without structured output:

```text
LLM
 ↓
paragraph
 ↓
developer manually parses it
```

With structured output:

```text
LLM
 ↓
JSON
 ↓
Python object
 ↓
application logic
```

This is a fundamental pattern in AI engineering.

---

## Key Python / Technical Concepts

### File Paths

The program iterates over a resume directory:

```text
resumes/
├── resume1.pdf
├── resume2.pdf
├── resume3.docx
└── ...
```

Then:

```python
for file_path in resume_folder.iterdir():
    ...
```

Each file is processed independently.

---

### File Extensions

The program checks the suffix:

```python
file_path.suffix
```

Possible results:

```text
.pdf
.docx
.txt
.png
```

Only supported formats are processed.

---

### JSON

The LLM response may arrive as raw JSON.

Python's `json` module can convert JSON text into Python objects:

```python
data = json.loads(raw_response)
```

Conceptually:

```text
JSON string
    ↓
json.loads()
    ↓
Python dictionary
```

---

### Pydantic

Pydantic provides structured models such as:

```python
class Resume(BaseModel):
    name: str
    skills: list[str]
```

It helps define and validate the expected data structure.

---

### Reusable Functions

The project separates responsibilities:

```text
read_pdf()
read_docx()
read_resume()
parse_resume()
final_score()
```

This is much better than putting everything inside one huge function.

---
