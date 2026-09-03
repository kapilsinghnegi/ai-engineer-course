# Episode 18: Build Your First AI Agent — Tool Calling from Scratch

The lesson introduces an agent built with Groq, a Tavily web-search API, and a Python calculator. It also prepares you for LangGraph, which helps orchestrate more complex, multi-step agent workflows.

## What is an AI agent?

An AI agent is an application in which an LLM can choose and use tools to accomplish a task, rather than only generating a text response.

A simplified model is:

**Agent = LLM + Tools + Execution Loop**

- **LLM:** Understands the user's request and decides what action may help.
- **Tools:** Functions or APIs that perform actions, such as calculations, searching the web, or accessing a database.
- **Execution loop:** Sends the request to the LLM, executes requested tools, returns the results to the LLM, and continues until the LLM produces a final answer or the loop reaches its limit.

For example, consider these two questions:

- “What is `10 * 21`?” — use a calculator.
- “Who is the current Prime Minister of India?” — search for up-to-date information on the web.

The LLM chooses the appropriate tool based on the question and the tool descriptions provided to it.

### LLM vs. AI agent

| LLM alone | LLM-powered agent |
|---|---|
| Generates text from its learned knowledge and supplied context | Can request external tools to gather information or perform operations |
| May make arithmetic mistakes when calculating directly | Can delegate arithmetic to a calculator |
| May have outdated knowledge | Can use web search for current information |
| Usually responds directly | Can follow a multi-step tool-use loop |

**Important distinction:** An agent is not simply an LLM with a tool list. It also needs application code to execute the requested tools and return their results. Tool calling is the model's request to perform an action; your Python program performs the actual action.

## What is a tool?

In ordinary Python, a tool can be a function. From the agent's perspective, that function is a capability the model can request.

Examples:

| Tool | Purpose |
|---|---|
| `calculate` | Perform supported mathematical calculations |
| `web_search` | Retrieve information from the web |
| `send_email` | Send an email through an authorized email API |
| `query_database` | Retrieve records from a database |
| `book_flight` | Interact with a booking service, if an appropriate API is available |

A tool usually has two important parts:

1. **Its implementation:** The actual Python function or API integration.
2. **Its definition/schema:** A description of the tool and the parameters it accepts, supplied to the LLM so it can choose and call it correctly.

The LLM doesn't need to know the implementation's internal details. It needs a clear description of what the tool does, when to use it, and how to supply valid arguments.

---

## Understanding the two tools in this episode

### Tool 1 — Web search

The code uses Tavily, a web-search service, to retrieve information relevant to a query.

```python
def web_search(query: str) -> str:
    """Search the web for current information."""
    try:
        response = tavily.search(
            query=query,
            max_results=3,
            search_depth="basic"
        )

        results = []

        for result in response["results"]:
            results.append(
                f"Title: {result['title']}\n"
                f"URL: {result['url']}\n"
                f"Content: {result['content']}"
            )

        return "\n\n".join(results)

    except Exception as e:
        return f"Search failed: {e}"
```

**How it works:**

1. Accepts a search query as a string.
2. Calls Tavily's search API.
3. Requests up to three results.
4. Extracts each result's title, URL, and content.
5. Joins the results into one string and returns it.
6. If an exception occurs, returns an error message.

The function returns search results; it does not itself decide which result is authoritative or whether the results fully answer the user's question. The LLM can use the returned information to formulate an answer.

### Tool 2 — Calculator

The supplied code is:

```python
def calculate(expression: str) -> str:
    """Perform a mathematical calculation."""

    try:
        return str(
            eval(
                expression,
                {"__builtins__": {}},
                {}
            )
        )
    except Exception as e:
        return f"Calculation failed: {e}"
```

It accepts a mathematical expression, evaluates it, and converts the result to a string.

For example:

- `10 * 21` → `"210"`
- `100 / 4` → `"25.0"`
- `2 + 3 * 4` → `"14"`

The third example also illustrates operator precedence: multiplication happens before addition.

**Security caveat:** `eval()` is dangerous when used on untrusted input. Removing `__builtins__` reduces access to Python built-ins, but it is not a sufficient security boundary for a production calculator. A safer approach is to parse expressions with Python's `ast` module and explicitly allow only numeric constants and approved arithmetic operators. The transcript mentions an AST-based approach in the code walkthrough, but the code you supplied for this episode still uses `eval()`.

## Environment setup

The code imports the libraries needed to access Groq, Tavily, and environment variables.

```python
import os
import json

from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

load_dotenv()

groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
```

Install the dependencies using `uv`:

```bash
uv add groq python-dotenv tavily
```

Create a `.env` file in the project directory:

```dotenv
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

- `python-dotenv` loads environment variables from `.env`.
- `GROQ_API_KEY` authenticates requests to Groq.
- `TAVILY_API_KEY` authenticates requests to Tavily.
- `json` is used to parse the JSON arguments supplied with tool calls.

Keep `.env` out of Git by adding it to `.gitignore`. Do not print or commit your API keys.

The code should also check that both keys are present before initializing the clients. Otherwise, a missing key can cause a confusing failure later.

## Tool registry: connecting tool names to Python functions

The code defines:

```python
AVAILABLE_TOOLS = {
    "web_search": web_search,
    "calculate": calculate,
}
```

This is a **tool registry**: a mapping between the tool names the model may request and the Python functions that implement them.

For example:

```python
AVAILABLE_TOOLS["web_search"]
```

returns a reference to the `web_search` function. It does not execute the function yet.

Later, when the model requests `web_search`, the agent looks up the function in this dictionary and invokes it with the supplied arguments.

The registry separates the model's decision from the application's execution logic.

### Why is this separation useful?

The model doesn't need to write Python code to search the web. It only needs to request a named tool and provide valid arguments. Your program is responsible for deciding whether that tool exists and then executing its implementation.

It also means the application can reject unknown tool names instead of attempting to execute arbitrary code requested by the model.

---

## Tool definitions: how the LLM learns to use tools

This is one of the most important concepts in the episode.

In the intended implementation, `tools` contains schemas describing `web_search` and `calculate`.

A simplified example of a tool definition is:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the web for current information "
                "and recent events."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "A concise web search query."
                        )
                    }
                },
                "required": ["query"]
            }
        }
    }
]
```

This example defines only the web-search tool to keep the structure clear. The calculator requires its own corresponding definition.

A function tool definition typically contains the following fields:

| Field | Meaning |
|---|---|
| `type` | Identifies the tool as a function tool |
| `name` | The exact tool name the model can request |
| `description` | Explains what the tool does and when it should be used |
| `parameters` | Describes the arguments accepted by the function |
| `properties` | Defines each argument, including its type and description |
| `required` | Lists the arguments that must be supplied |

### Why descriptions matter

Suppose the model sees these descriptions:

- `web_search`: “Search the web for current information and recent events.”
- `calculate`: “Evaluate a basic mathematical expression.”

If the user asks for the current price of a product, web search is the natural choice. If the user asks to multiply two numbers, the calculator is the natural choice.

The descriptions help the model decide which tool is appropriate. Poor or vague descriptions make that decision less reliable.

### Why parameters matter

Consider the calculator tool. It expects an `expression` string, such as `"25 * 15"`.

The tool definition should tell the model that:

- The parameter is named `expression`.
- Its type is `string`.
- It represents a mathematical expression.
- It is required.

The model can then request a call with arguments such as:

```json
{
  "expression": "25 * 15"
}
```

The function implementation and the schema must agree. If the schema advertises `expression` but the function expects a differently named parameter, the tool call may fail.

**Key lesson:** Tool descriptions explain *when and why* to use a tool; parameter schemas explain *how* to call it.

---

## The system prompt: defining the agent's behaviour

This should be filled with instructions explaining the agent's role and the tools it can use.

For example:

```python
SYSTEM_PROMPT = """
    You are an AI research assistant.
    
    Rules:
    1. Use web_search for current or changing information.
    2. Use calculate for mathematical calculations.
    3. You may use tools multiple times.
    4. When you have enough information, answer the user.
    5. Include useful source URLs from web search results.
    """
```

The system prompt provides general behaviour instructions, while the tool schemas define the callable tools and their argument formats.

These are related but distinct:

- **System prompt:** Guides the agent's overall behaviour.
- **Tool definitions:** Tell the model what tools exist and how to request them.
- **Tool registry:** Maps requested tool names to actual Python implementations.
- **Agent loop:** Executes the calls and sends their results back to the model.

A system prompt alone does not grant the model access to a Python function. The function must be exposed through the API's tool definitions, and the application must implement the execution loop.

---

## The agent loop: the heart of tool calling

The core function is:

```python
def run_agent(question: str, max_iterations: int = 5):
```

It accepts the user's question and a maximum iteration count.

The loop allows the LLM to request tools, receive their results, and decide what to do next. Let's break it down.

### Step 1 — Create the conversation history

```python
messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    },
    {
        "role": "user",
        "content": question
    }
]
```

The message history starts with two messages:

1. The system instructions.
2. The user's question.

The history is important because the LLM needs the original request and subsequent tool results to continue the task.

### Step 2 — Ask the LLM what to do

```python
response = groq.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)
```

The application sends the conversation and available tool definitions to Groq.

- `model` selects the model used for the request.
- `messages` contains the conversation history.
- `tools` advertises the available functions.
- `tool_choice="auto"` allows the model to decide whether to request a tool or respond directly, subject to the model and API's supported behaviour.

For example, the model might request `calculate` for a math question, request `web_search` for a current fact, or return an answer directly if no tool is needed.

### Step 3 — Extract the model's message

```python
message = response.choices[0].message
messages.append(message)
```

The first choice's message is added to the history. It may contain a final text response, one or more tool calls, or both text and tool-call information depending on the response format.

Appending the assistant message is essential: when the tool results arrive, the next model call needs the context of what it requested.

### Step 4 — Check whether the model requested a tool

```python
if not message.tool_calls:
    print("\nFINAL ANSWER:")
    print(message.content)
    return message.content
```

If there are no tool calls, the program treats the message as the final answer and returns its content.

Otherwise, the code proceeds to execute the requested tool calls.

### Step 5 — Read each tool call

```python
for tool_call in message.tool_calls:
    tool_name = tool_call.function.name
    arguments = json.loads(
        tool_call.function.arguments
    )
```

A tool call includes the requested function name and its arguments. The arguments arrive as a JSON-formatted string, so `json.loads()` converts that string into a Python dictionary.

For example, the model could request:

```json
{
  "query": "current Prime Minister of India"
}
```

After parsing, Python receives:

```python
{"query": "current Prime Minister of India"}
```

The code can then pass this dictionary to the corresponding function.

### Step 6 — Find and execute the Python function

```python
if tool_name not in AVAILABLE_TOOLS:
    result = f"Unknown tool: {tool_name}"
else:
    result = AVAILABLE_TOOLS[tool_name](**arguments)
```

This is where the model's request becomes an actual action.

- An unknown name is rejected.
- A known name is looked up in `AVAILABLE_TOOLS`.
- `**arguments` unpacks the dictionary into keyword arguments.

For example:

```python
{"query": "current Prime Minister of India"}
```

is equivalent to:

```python
web_search(
    query="current Prime Minister of India"
)
```

The function executes and returns a result.

**Important:** The LLM does not directly execute your Python function. Your program does that after interpreting the tool-call request.

### Step 7 — Send the tool result back to the model

```python
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": result
})
```

The result is added to the conversation as a tool message. `tool_call_id` links the result to the specific tool call that requested it.

The next iteration sends this history back to the LLM. The model can now use the returned result to generate an answer or request another tool.

### Step 8 — Stop when the model finishes or the limit is reached

```python
print("\nMaximum iterations reached.")

return (
    "I couldn't complete the task "
    "within the iteration limit."
)
```

If the loop completes all allowed iterations without receiving a final answer, the function returns a fallback message.

This prevents the program from looping indefinitely. However, the limit in this code is a limit on **LLM-loop iterations**, not a strict limit on the total number of tool calls: one iteration can contain multiple tool calls.

---

## The complete workflow

**1. User submits a question**

Example: “What is 25 × 15?”

**2. LLM receives the prompt and tool schemas**

Decides whether to respond or request a tool

- **Calculator** · Math expression → numeric result
- **Web search** · Query → search results

**3. Python executes the requested tool**

The result is appended to conversation history

**4. LLM receives the result**

Produces a final answer or requests another tool

This cycle is commonly called a **tool-calling loop**. In the transcript, the instructor explains that a larger task may require several iterations because the agent must complete subtasks sequentially.

## What is an iteration, and why do agents need one?

An iteration is one pass through the main agent loop: the application sends the conversation to the LLM, receives its response, and processes the response.

Suppose you ask:

> Find a person's YouTube channel, then tell me how many subscribers it has.

The agent might need to:

1. Search for the person.
2. Use the search results to identify the correct YouTube channel.
3. Search for the channel's current subscriber count.
4. Produce a final answer.

The exact number of iterations depends on the model's decisions and the quality of the search results. A single iteration can also request multiple tools.

### Why set `max_iterations`?

Your function defaults to:

```python
def run_agent(question: str, max_iterations: int = 5):
```

Without a limit, the application could keep making LLM calls and using tools without reaching a satisfactory answer. Each call can consume model tokens, and external APIs may have usage limits or costs.

The limit provides a stopping condition, but it is not a guarantee that the task will finish within five iterations. If the task is too complex, the agent may return the fallback message.

Also, the code's `for` loop counts LLM iterations. To limit total tool executions separately, you would need an additional tool-call counter.

---

## How does this relate to ReAct and LangGraph?

The lesson uses a manual loop that alternates between reasoning, tool requests, tool execution, and observation of the results. This resembles the **ReAct** pattern, which combines reasoning and acting, though the supplied code does not explicitly implement a separate ReAct prompt format.

The instructor's motivation for introducing LangGraph is that manual orchestration becomes harder as the number of tools, agents, and possible paths increases.

| Manual agent loop | LangGraph-style orchestration |
|---|---|
| You write the loop and routing logic yourself | You define a graph of states and transitions |
| Tool execution is managed in your own code | Tools and workflow steps can be represented as graph nodes |
| Complex branching can become difficult to maintain | Branches and conditional transitions can be made explicit |
| You implement additional state handling yourself | The framework provides abstractions for stateful workflows |

LangGraph does not automatically make an agent intelligent or guarantee correct tool use. It provides orchestration abstractions that can make complex workflows easier to manage, test, and maintain.

## Important questions and answers

**Q1. What is an AI agent?**

An LLM-powered application that can select and use tools to accomplish tasks. Its application code executes the tools and returns results to the model.

**Q2. What is function or tool calling?**

It is a mechanism through which a model requests a named function with structured arguments. The application validates and executes that request, then returns the result to the model.

**Q3. What is the difference between a tool schema and a tool implementation?**

A schema tells the model the function's name, purpose, and parameter format. The implementation is the actual code that performs the operation.

**Q4. What is `tool_choice="auto"`?**

It allows the model to decide whether to request an available tool or respond without one, according to the model and API's supported behaviour.

**Q5. Why does the agent append tool results to `messages`?**

So the model can see the results of its requested action and use them to produce a final answer or decide on the next action.

**Q6. Why is `tool_call_id` important?**

It associates a tool result with the corresponding tool request, especially when the model requests multiple tools in one response.

**Q7. Why should an agent have an iteration limit?**

To prevent unbounded loops, excessive model usage, unnecessary API calls, and wasted time when the agent cannot complete the task.

**Q8. Why is `eval()` unsafe for a calculator tool?**

It evaluates Python expressions and can execute more than ordinary arithmetic. Restricting built-ins is not a sufficient security boundary. Use a restricted parser and allow only supported arithmetic operations.

**Q9. What is the difference between an agent and a fixed workflow?**

An agent can use model-driven decisions to select actions dynamically. A fixed workflow follows predetermined steps. Real systems can combine both approaches.

**Q10. Why use LangGraph?**

To organize complex, stateful agent workflows with explicit nodes, transitions, and branching instead of maintaining increasingly complicated orchestration logic manually.

## Quick revision

- An **LLM** interprets the request and chooses a response or action.
- A **tool** gives the agent access to a function or external capability.
- A **tool schema** tells the model what the tool does and which arguments it accepts.
- A **tool registry** maps function names to Python implementations.
- `tool_choice="auto"` lets the model decide whether to request a tool.
- `json.loads()` parses the tool arguments.
- `AVAILABLE_TOOLS[tool_name](**arguments)` executes the selected Python function.
- A tool result is added to the conversation using its `tool_call_id`.
- The agent repeats the loop until it finishes or reaches its limit.
- `max_iterations` limits loop passes, not necessarily the total number of tools executed.
- Tool calling is not the same as the model executing arbitrary code.
- Safe execution, argument validation, error handling, and API limits are essential for reliable agents.