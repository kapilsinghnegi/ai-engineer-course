# Pydantic + JSON — Structured Outputs

## Why Structured Output Is Needed

So far, an LLM interaction usually looks like:

```text
User → Prompt → LLM → Text Response
```

For example:

```text
Prompt:
"Extract the customer's name, email, phone number and issue."
```

The LLM might respond:

```text
Sure! I'd be happy to help.

The customer's name is Kapil.
His email is kapil@example.com.
His phone number is 9876543210.
The issue is that his iPhone stopped working.
```

For a human, this is easy to understand.

For another **program**, however, this is inconvenient.

The next program needs to somehow determine:

* Where does the name start?
* Where does the email start?
* Which number is the phone number?
* Where does the issue begin?
* What if the LLM changes the wording?

This creates a **parsing problem**.

### The core problem

> **Humans are good at understanding natural language. Programs are much better at consuming predictable structures.**

This becomes especially important when an LLM's output is going directly into another piece of software.

---

## The Problem with Plain Text Output

Imagine an AI customer-support system receives this email:

```text
Hi,

My name is Kapil and I bought an iPhone from your store.
It stopped working yesterday.

Please contact me at:
kapil@example.com
9876543210

Thanks,
Kapil
```

We want the LLM to extract:

```text
name
email
phone
issue
```

A normal LLM response might be:

```text
Sure! Here's the information I found:

Name: Kapil
Email: kapil@example.com
Phone: 9876543210
Issue: iPhone stopped working.
```

The information is correct, but the format isn't guaranteed.

Another response could be:

```text
The customer is Kapil. You can reach him at
kapil@example.com or 9876543210. His iPhone
appears to have stopped working.
```

A third response could be:

```text
Customer Details:

👤 Kapil
📧 kapil@example.com
📱 9876543210

Problem:
The customer's iPhone is not working.
```

All three contain the same information, but a program would need different parsing logic for each.

---

## Structured vs Unstructured Output

### Unstructured Output

Natural language without a fixed format.

Example:

```text
Kapil contacted support because his iPhone stopped working.
You can reach him at kapil@example.com.
```

The structure is implicit.

The program has to figure it out.

---

### Structured Output

Information follows a predefined structure.

Example:

```json
{
  "name": "Kapil",
  "email": "kapil@example.com",
  "phone": "9876543210",
  "issue": "iPhone stopped working"
}
```

Now the program knows exactly where each piece of information is.

---

## What Is JSON?

**JSON = JavaScript Object Notation**

Despite its name, JSON is not limited to JavaScript.

It is a lightweight data-interchange format widely used by:

* APIs
* Web applications
* Backend services
* Databases
* AI applications
* Microservices

A JSON object looks like:

```json
{
  "name": "Kapil",
  "email": "kapil@example.com",
  "phone": "9876543210"
}
```

It consists of **key-value pairs**.

```text
key → value
```

For example:

```text
"name" → "Kapil"
"email" → "kapil@example.com"
"phone" → "9876543210"
```

---

## Why JSON Is Useful for AI Applications

Suppose an AI agent processes **1 million customer complaints**.

You cannot realistically have a human read every LLM response.

Instead:

```text
Customer Complaint
        ↓
      LLM
        ↓
Structured JSON
        ↓
Backend Program
        ↓
Database / Decision / Action
```

For example:

```json
{
  "category": "electronics",
  "priority": "high",
  "customer_email": "kapil@example.com",
  "issue": "iPhone stopped working"
}
```

Your backend can now do:

```python
if ticket["priority"] == "high":
    escalate_ticket()
```

This is much easier than trying to interpret a paragraph.

---

## What Is Pydantic?

**Pydantic is a Python library used for data validation and structured data modeling.**

In AI applications, Pydantic is particularly useful for defining:

> **What structure do I expect from the LLM?**

For example, suppose we want:

```text
name     → string
email    → string
issue    → string
```

We can represent that structure with a Pydantic model.

Conceptually:

```python
from pydantic import BaseModel

class Ticket(BaseModel):
    name: str
    email: str
    issue: str
```

This tells our program:

```text
A Ticket must contain:

name  → string
email → string
issue → string
```

---

## Pydantic Models and Schemas

A **schema** is essentially a specification describing what data should look like.

Think of it as a contract.

For example:

```python
class Ticket(BaseModel):
    name: str
    email: str
    issue: str
```

The schema says:

```text
Ticket
 ├── name  : string
 ├── email : string
 └── issue : string
```

### Mental model

Think of Pydantic as a **form template**.

Suppose you create a form:

```text
Customer Complaint

Name:   __________
Email:  __________
Issue:  __________
```

You don't want someone submitting:

```text
My father's name is Rahul.
My Aadhaar number is XXXXX.
I live in Delhi.
My favorite food is pizza.
```

You only care about the fields your application requires.

Pydantic helps define those expected fields.

---

## Combining Pydantic with an LLM

The basic idea is:

```text
                 ┌───────────────┐
User Input ─────→│      LLM      │
                 └───────┬───────┘
                         ↓
                 Structured Data
                         ↓
                 Pydantic Schema
                         ↓
                    Application
```

A typical implementation conceptually contains four pieces:

### Define the model

```python
class Ticket(BaseModel):
    name: str
    email: str
    issue: str
```

### Create a schema

The schema communicates the expected structure.

### Tell the LLM to return the required structure

For example:

```text
Extract the customer information.

Return the result as JSON according to the provided schema.
Do not include additional fields.
```

### Parse the response

The application receives structured data rather than relying on manually parsing prose.

---

## Reading JSON in Python

Python provides a built-in `json` module.

```python
import json
```

Suppose the LLM returns:

```json
{
  "name": "Kapil",
  "email": "kapil@example.com",
  "issue": "iPhone stopped working"
}
```

You can parse JSON with:

```python
data = json.loads(raw_json)
```

Then access fields directly:

```python
print(data["name"])
print(data["email"])
print(data["issue"])
```

Output:

```text
Kapil
kapil@example.com
iPhone stopped working
```

### Important distinction

```python
json.loads()
```

converts a **JSON string → Python object**.

While:

```python
json.dumps()
```

converts a **Python object → JSON string**.

Easy memory trick:

```text
loads  → load JSON into Python
dumps  → dump Python into JSON
```

---

## Practical Example: Customer Complaint Extraction

Let's design a simple ticket extraction system.

### Input

```text
Hi, my name is Kapil.

I purchased an iPhone from your store and
it stopped working yesterday.

Please contact me at kapil@example.com.

My address is Delhi.
My father's name is Rahul.
```

We only need:

```text
name
email
issue
```

### Pydantic model

```python
from pydantic import BaseModel

class Ticket(BaseModel):
    name: str
    email: str
    issue: str
```

### Expected output

```json
{
  "name": "Kapil",
  "email": "kapil@example.com",
  "issue": "iPhone stopped working"
}
```

Notice that:

```text
address
father's name
```

are ignored because they aren't part of our schema.

That's the power of defining a strict output structure.

---

## Interview Questions

### Q1. Why is structured output important in LLM applications?

Because LLMs naturally generate flexible natural-language responses, while software applications need predictable data structures that can be reliably consumed by code.

---

### Q2. What is JSON?

JSON (JavaScript Object Notation) is a lightweight text-based format for representing structured data using objects, arrays, key-value pairs, and primitive values.

---

### Q3. What is Pydantic?

Pydantic is a Python library for defining data models and validating data against those models.

---

### Q4. What is a schema?

A schema defines the expected structure, fields, and data types of some data.

Example:

```text
Ticket
 ├── name  : string
 ├── email : string
 └── issue : string
```

---

### Q5. What problem does Pydantic solve in an LLM application?

It helps define and validate the structure of data expected from the LLM, making the output easier and safer for downstream application code to consume.

---

### Q6. What is the difference between structured and unstructured output?

**Unstructured:**

```text
The customer is Kapil and his phone isn't working.
```

**Structured:**

```json
{
  "name": "Kapil",
  "issue": "Phone isn't working"
}
```

---

### Q7. What is `json.loads()`?

It parses a JSON string into a Python object.

```python
data = json.loads(raw_json)
```

---

### Q8. What is `json.dumps()`?

It serializes a Python object into a JSON-formatted string.

```python
json_string = json.dumps(data)
```

---
