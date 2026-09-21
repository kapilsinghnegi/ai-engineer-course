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