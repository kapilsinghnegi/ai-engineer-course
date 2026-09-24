# Multi-Agent Systems

## What is an AI Agent?

An AI agent combines an LLM with tools that allow it to perform actions.

For example, a tool-using agent might have:
- An LLM that decides what to do.
- A web-search tool to retrieve current information.
- A calculator tool to perform arithmetic.
- A Python function to process data.

The LLM can decide which tool to call based on the user's request, receive the result, and continue reasoning.

## Single-agent vs Multi-agent Systems

### Single-agent System

Imagine that you need to automate a daily NVIDIA stock-price report:

1. Search for the latest stock data.
2. Create a graph of the historical prices.
3. Write and send an email containing the report.

One agent could have all three tools available:

```
One LLM / Agent
├── Web Search
├── Graph Creation
└── Email
```

The same agent decides when to search, when to generate the graph, and when to send the email. It can use the result of one tool as input to another.

### Multi-agent System

Now split the work between specialist agents and introduce a manager, also called a supervisor, coordinator, or orchestrator.

```
Manager / Orchestrator - Plans the sequence, delegates tasks, tracks results
├── Search Agent
|   └── Searches for data
├── Graph Creation
|   └── Processes data
└── Email
    └── Prepares or sends email
```

The manager might delegate the search task first, pass the returned data to the graph agent, and then pass the graph or its analysis to the email agent.

The specialist agents have narrowly defined responsibilities. In the instructor's example, the manager itself has no tools and delegates all execution to the specialist agents.

Important distinction: different agents don't require different models
A multi-agent system can use:
- The same model for all agents, with different prompts and tools.
- Different models for different agents.
- A combination of models, chosen according to the requirements.

The manager might delegate the search task first, pass the returned data to the graph agent, and then pass the graph or its analysis to the email agent.

The specialist agents have narrowly defined responsibilities. In the instructor's example, the manager itself has no tools and delegates all execution to the specialist agents.

### Important distinction: different agents don't require different models

A multi-agent system can use:

- The same model for all agents, with different prompts and tools.
- Different models for different agents.
- A combination of models, chosen according to the requirements.

For example, a research agent could use a stronger reasoning model, while an email-formatting agent uses a cheaper model.

**Agent** refers to a role and its decision-making/tool-use setup; it doesn't automatically mean a separate model provider or a different underlying model.

### Compare the two architectures

| Aspect | Single agent | Multi-agent |
|---|---|---|
| LLM roles | One agent handles the overall task | Several agents have specialized roles |
| Tool access | One agent may access all tools | Tools can be divided by responsibility |
| Coordination | Mostly internal to one agent | Agents exchange tasks and results |
| Context | One agent's context accumulates task history | Context can be scoped to individual agents |
| Complexity | Usually simpler | More orchestration and failure points |
| Cost | Often lower | Can be higher due to extra calls and handoffs |

Neither architecture is automatically better. The correct choice depends on the task and measured performance. 

## How a multi-agent system works

Let's look at the architecture through a educational YouTube production team: a teacher creates the content, an editor prepares the final video, and an uploader publishes it. A manager coordinates the work.

The important concept is **task dependency**: an editor cannot edit a video that hasn't been created, and an uploader shouldn't publish a video before editing is complete.

The same logic applies to AI agents.

### Example: Search agent + maths agent + manager

Suppose the user asks:

> Find the height of the Eiffel Tower and the Burj Khalifa in metres. Calculate what percentage of the Burj Khalifa's height the Eiffel Tower is, and how many Eiffel Towers stacked together would equal the Burj Khalifa's height.

The workflow can be:

**Step 1 — Manager receives the request**

It identifies that current or reliable height information is needed before calculations can be performed.

**Step 2 — Search agent**

It searches for both heights and returns the facts it found. It doesn't need to handle the later calculations.

**Step 3 — Manager tracks the results**

It retains the returned heights and decides which task should happen next.

**Step 4 — Maths agent**

It uses the calculator tool to calculate the percentage and height ratio from the supplied figures.

**Step 5 — Manager returns the answer**

It combines the search results and calculations into one response.

### Why does the manager keep notes?

The manager needs to remember what the specialist agents returned. In a simple implementation, this can be represented by a variable, a message history, or a structured object.

For example:

```python
notes = {
    "eiffel_tower_height_m": None,
    "burj_khalifa_height_m": None,
    "percentage": None,
    "height_ratio": None,
}
```

The search agent supplies the first two values. The maths agent calculates the last two. The manager uses those results to build the final answer.

This example illustrates **shared workflow state**. The notes don't have to be a physical file; they can live in memory or in a graph's state object.

## Why use multiple agents?

The instructor's central point is that multi-agent architecture is useful when tasks are sufficiently distinct to benefit from specialization.

### Reason 1: Logical separation of responsibilities

Web research, mathematical calculation, code execution, and email composition have different requirements.

A search agent can focus on gathering relevant facts. A maths agent can focus on correct calculations. A manager can focus on task ordering and delegation.

This can make responsibilities easier to define, test, and debug.

### Reason 2: More controlled tool access

You can limit each agent's available tools to the ones it needs.

For example:

- Search agent: web-search tool only.
- Maths agent: calculator tool only.
- Manager: no execution tools; it delegates to the specialist agents.

This follows the principle of **least privilege**: give each component only the capabilities it needs. It also reduces the number of tool choices a specialist has to consider.

However, restricted tools do not guarantee correct behavior. Each agent still needs clear instructions, input validation, and error handling.

### Reason 3: Different model requirements

Some tasks require more reasoning than others.

| Task | Possible model strategy |
|---|---|
| Complex research and synthesis | Stronger reasoning model |
| Simple arithmetic | Lightweight model plus a calculator tool |
| Formatting an email | Cheaper model, if quality is sufficient |
| Coordinating a complex workflow | A model capable of following the delegation rules |

This is a potential optimization, not a guarantee. A manager that makes poor routing decisions can undermine the whole system, so model selection should be tested empirically.

### Reason 4: Managing context

An LLM has a finite context window: it can process only a limited amount of input and output tokens in one context.

As a workflow grows, the conversation may accumulate:

- The original user request.
- Tool definitions and tool outputs.
- Earlier reasoning and intermediate results.
- Repeated instructions and error messages.

Separating work can reduce how much irrelevant history each specialist needs to process.

**Technical clarification:** the instructor calls this concern “context overflow.” More precisely, context-window exhaustion can occur when the total input exceeds the model's supported limit. Before that happens, a long history may also make it harder to keep relevant details salient. A multi-agent architecture can help manage context, but it doesn't automatically prevent context exhaustion; each agent has its own context limits, and the manager's context can still grow. 

## Disadvantages: calls, communication, cost, and complexity

A multi-agent system introduces handoffs. Every handoff can require an agent to receive instructions, interpret supplied data, and return a result.

Consider the difference:

- **Single agent:** search → calculate → answer.
- **Multi-agent:** manager → search agent → manager → maths agent → manager → answer.

The multi-agent version can involve additional LLM calls and repeated input/output tokens. Those calls can increase latency and API cost.

### What does token usage measure?

- **Input tokens:** prompts, instructions, history, and data sent to a model.
- **Output tokens:** text or tool-call arguments generated by a model.
- **Total tokens:** input tokens plus output tokens.

If each agent receives a long history or repeats data that another agent already processed, token usage may rise substantially.

## Code Implementation

The implementation exercise compares two approaches **without LangGraph**, so you can understand the orchestration logic before introducing a framework.

### Approach A: Single agent

The single-agent implementation has:

- One `ask_llm()` function.
- A web-search tool using Tavily.
- A Python calculator tool.
- A model that decides which tool to call.
- A maximum-attempt limit to stop repeated tool calls.
- Token-usage tracking.

The important property is that **one agent makes the tool-selection decisions for the whole task**. It can search, use the search results in a calculation, and continue if it needs more information.

### Approach B: Multi-agent without LangGraph

The instructor describes three LLM-call functions:

| Function | Responsibility | Tool access |
|---|---|---|
| `ask_manager()` | Choose the next specialist and track progress | No execution tools in the intended design |
| `ask_search()` | Find requested information | Web search |
| `ask_maths()` | Perform calculations | Calculator |

The manager must keep track of the user's request, the results returned by the specialist agents, and which steps remain.

### Why use a maximum-attempt limit?

This helps prevent an agent from repeatedly calling tools without completing the task.

A robust implementation should also handle:

- Repeated calls with the same arguments.
- Invalid tool names or arguments.
- Empty or irrelevant search results.
- API rate limits and timeouts.
- A manager that repeatedly selects the same specialist.
- Incomplete answers when the attempt limit is reached.

A maximum-attempt limit is a safeguard, not a guarantee that the task will be completed correctly.

### How should token usage be compared?

The instructor's experiment compares the single-agent and multi-agent runs on a task requiring both search and calculation. A fair comparison should use the same question, equivalent tools, the same underlying model where appropriate, and equivalent success criteria.

Record at least:

| Metric | What it tells you |
|---|---|
| Input tokens | How much information was sent to the models |
| Output tokens | How much the models generated |
| Total LLM calls | How many model requests were made |
| Tool calls | How often external functions were executed |
| Completion success | Whether the task was answered correctly |
| Latency | How long the workflow took |
| Cost | The actual cost under the applicable pricing |

## Important Questions and Answers

**Q1 What is a multi-agent system?**
A system in which multiple agents have defined responsibilities and coordinate to complete a task. They may use the same underlying model or different models.

**Q2 What is the difference between a single-agent and a multi-agent system?**
A single agent can manage the task and use multiple tools. A multi-agent system distributes responsibilities across agents and coordinates their work.

**Q3 What is an orchestrator or supervisor agent?**
An agent responsible for deciding which specialist should handle a task, tracking results, and coordinating the workflow. 

**Q4 Why might you use multi-agent?**
When responsibilities are logically distinct, tool access should be restricted by role, or different tasks benefit from different models or contexts. 

**Q5 Why can multi-agent systems be more expensive?**
They may introduce extra LLM calls, handoffs, repeated context, and longer outputs. The actual difference depends on implementation and workload.

**Q6 Do multi-agent systems require different LLM models?**
No. Different agents can use the same model with different instructions and tool access, or use different models when requirements justify it.

**Q7 Does using multiple agents guarantee better accuracy?**
No. Specialization can help, but coordination mistakes and error propagation can reduce accuracy. Evaluate both architectures on representative tasks.

**Q8 How do you prevent an agent from looping indefinitely?**
Use maximum iteration limits, timeouts, repeated-action detection, tool-call limits, and explicit completion conditions.

**Q9 When should you introduce multi-agent architecture?**
Start with a single agent, measure its performance, identify a concrete limitation, and test whether delegation improves the relevant metrics enough to justify its cost.
