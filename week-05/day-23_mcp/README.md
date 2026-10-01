# Model Context Protocol (MCP)

## What problem does MCP solve?

Before understanding MCP, let's revisit what we built when learning AI agents.

An AI agent generally consists of:

- **LLM:** Understands the user's request and decides what action to take.
- **Tools:** Allow the LLM to interact with external systems and perform tasks.

For example, our earlier agent had two tools:

1. Web search using Tavily.
2. Calculator for mathematical operations.

To connect Tavily with our agent, we wrote a Python function that called the Tavily API.

Conceptually:

```python
def web_search(query):
    response = tavily_client.search(query)
    return response
```

The function needs to know how Tavily's API works: its endpoint, arguments, authentication requirements, and expected response.

This approach works, but it introduces problems when the number of tools increases.

### Problem 1: Every integration requires custom code

Imagine Claude wants to support:

- GitHub
- Gmail
- Google Drive
- Slack
- Tavily
- YouTube
- Other external services

Without a common integration standard, Claude's developers would need to implement and maintain separate integrations for these services.

Each service might have different:

- API structures
- Authentication mechanisms
- Function names
- Arguments
- Response formats

The integration workload increases as more tools are supported.

### Problem 2: API changes can break integrations

Suppose Tavily initially provides an API that accepts three arguments:

```python
search(query, max_results, topic)
```

Later, Tavily changes its API to accept two arguments:

```python
search(query, search_depth)
```

The existing integration might stop working.

The application using Tavily would need to update its integration code to accommodate the new API.

This creates maintenance problems because the application and the external service are tightly coupled.

**The core problem:** Different tools have different integration methods, and every AI application would otherwise need to understand those individual methods.

---

## What is MCP?

**MCP - Model Context Protocol**

MCP is an open protocol that standardizes how AI applications discover and interact with external tools and context sources.

MCP was introduced by Anthropic in November 2024.

Use this analogy to learn its purpose:

Imagine hiring three people:

- A driver who speaks French.
- A cook who speaks Japanese.
- A cleaner who speaks German.

You would need to learn three different languages to communicate with them.

Instead, everyone agrees to use one common language: English.

Now communication becomes easier.

Let's compare this common language to MCP.

In this analogy:

| Analogy | MCP concept |
|---|---|
| Driver, cook, cleaner | External tools and services |
| Different languages | Different API and integration methods |
| Common language | MCP protocol |
| Person communicating with workers | AI application |
| Company providing workers | Tool provider |

The important idea is that AI applications and tool providers follow a shared protocol rather than implementing a completely different communication method for every integration.

---

## Why do we need MCP?

Let's compare the two approaches.

### Without MCP

Suppose an AI application wants to integrate with Tavily.

```text
AI Application
      |
      v
Custom Tavily Function
      |
      v
Tavily API
```

The application developer must understand Tavily's API and write the integration.

If the application also needs Gmail, GitHub, and Slack, it needs additional integrations.

```text
                 AI Application
                  /     |     \
                 /      |      \
                v       v       v
          Tavily API  Gmail API  GitHub API
```

Each integration has its own implementation and maintenance requirements.

### With MCP

Instead, each service can expose its functionality through an MCP server.

```text
             AI Application
                    |
                    v
                MCP Client
                    |
          Standard MCP Protocol
                    |
        +-----------+-----------+
        |           |           |
        v           v           v
    Tavily MCP  Gmail MCP   GitHub MCP
     Server      Server      Server
        |           |           |
        v           v           v
    Tavily API  Gmail API   GitHub API
```

The AI application communicates through the common MCP protocol.

The individual MCP servers handle communication with their respective services.

This reduces the need for every AI application to implement every provider's API independently.

---

## How does MCP work?

The instructor explains a basic interaction sequence.

Let's use Tavily as an example.

Suppose a user asks:

*"Search the web for the latest developments in AI agents."*

The process looks like this:

1. **AI application requests available tools** · The MCP client connects to the Tavily MCP server and discovers which tools it provides.
2. **MCP server provides tool descriptions** · The server describes its available tools, their purpose, and their input schemas.
3. **LLM decides which tool to use** · The application makes the available tool information accessible to the model. The model decides whether Tavily search is appropriate.
4. **Tool invocation** · The client sends a request to invoke the selected tool with the required arguments.
5. **MCP server executes the tool** · The server handles the underlying Tavily integration and returns the result.
6. **Result reaches the AI application** · The application passes the tool result back to the LLM, which can formulate a response to the user.

### Example of tool discovery

Imagine a Tavily MCP server exposes two tools:

| Tool | Purpose |
|---|---|
| `tavily_search` | Search the web |
| `tavily_extract` | Extract content from web pages |

The server also provides descriptions and input schemas.

A simplified conceptual schema might look like this:

```json
{
  "name": "tavily_search",
  "description": "Search the web for relevant information",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string"
      }
    },
    "required": ["query"]
  }
}
```

This is an illustrative example of a tool description, not a complete MCP protocol message.

The AI application can discover the tool and its required arguments without hardcoding Tavily's API implementation into its own code.

### What happens when Tavily changes?

Suppose Tavily changes its internal API.

The Tavily MCP server can be updated to handle the new API while continuing to expose a compatible MCP interface.

The AI application can continue using the server through the protocol, subject to compatibility and any changes to the exposed tool contract.

**Important nuance:** MCP does not guarantee that integrations never break. If a server changes its tool names, input schema, authentication requirements, or behavior incompatibly, clients may still need adjustments.

---

## What is an MCP server?

An MCP server is a program that exposes capabilities to MCP clients through the MCP protocol.

It can expose different types of capabilities:

| Capability | Purpose | Example |
|---|---|---|
| Tools | Perform actions | Search the web, send an email |
| Resources | Provide data or context | Documents, files, database records |
| Prompts | Provide reusable prompt templates | Research or analysis templates |

### What is an MCP client?

An MCP client is the component in an AI application that communicates with an MCP server.

For example:

- An AI desktop application can act as an MCP host.
- The host manages MCP client connections.
- Each MCP client communicates with an MCP server.

These terms are worth distinguishing:

| Term | Meaning |
|---|---|
| MCP Host | Application that manages the AI experience and MCP connections |
| MCP Client | Protocol participant that communicates with an MCP server |
| MCP Server | Program exposing tools, resources, or prompts |

An important distinction: an MCP server is not necessarily a separate physical computer. It is a software process that communicates through the protocol. It can run locally or remotely.

---

## The restaurant analogy

Imagine visiting KFC, Domino's, or any other restaurant.

Each restaurant has its own menu and dishes.

But the ordering process is generally similar:

1. Ask for the menu.
2. Select a dish.
3. Place the order.
4. Receive the food and pay.

You do not need to learn a completely different ordering system every time you visit a restaurant.

This shared ordering process is compared to a protocol.

In MCP:

| Restaurant example | MCP equivalent |
|---|---|
| Restaurant | MCP server |
| Menu | Available tools and descriptions |
| Dish | A particular tool |
| Placing an order | Invoking a tool |
| Order details | Tool arguments |
| Food received | Tool result |

The important lesson is that individual restaurants can offer different dishes while following a familiar ordering process.

Similarly, different MCP servers can expose different capabilities while following the same communication protocol.

---

## MCP vs traditional tool calling

This is one of the most important distinctions from the lesson.

| Aspect | Traditional tool integration | MCP-based integration |
|---|---|---|
| Integration | Custom implementation for each service | Common protocol |
| Tool discovery | Often hardcoded or provider-specific | Server can expose tool information |
| Tool execution | Application calls the provider's API | MCP client invokes the server |
| API changes | Application integration may need changes | Server can absorb internal API changes |
| Reusability | Integration code may be application-specific | MCP servers can be reused by compatible clients |
| Maintenance | Can become difficult with many integrations | Separates provider integration from client |

### Does MCP replace function calling?

No.

This is a critical concept.

**Function calling** is a capability through which an LLM can request that a function or tool be executed.

**MCP** is a protocol that standardizes how an application discovers and communicates with external capabilities.

They solve different problems and can work together.

For example:

1. MCP client discovers tools from an MCP server.
2. The AI application makes those tools available to the LLM.
3. The LLM requests a tool call.
4. The application invokes the corresponding MCP tool.
5. The result is returned to the LLM.

So MCP and function calling are complementary, not competing technologies.

---

## Benefits and limitations

### Benefits

1. **Standardization:** A common communication protocol across compatible AI clients and tool servers.
2. **Reusability:** An MCP server can potentially be used by multiple compatible AI applications.
3. **Separation of concerns:** The server manages the external service integration; the client manages communication with the server.
4. **Easier discovery:** Clients can discover the tools exposed by a server.
5. **Reduced integration duplication:** Developers do not need to independently recreate every provider integration for every application.

### Limitations and important considerations

- MCP does not automatically make every API compatible; someone still needs to implement and maintain the MCP server.
- Authentication and authorization still need to be handled.
- Tool descriptions and schemas must be accurate.
- External tool results must be treated as untrusted input.
- Poorly secured servers can expose sensitive data or perform unintended actions.
- Network latency and server availability can affect tool execution.
- MCP does not eliminate the need to validate tool arguments or handle errors.

---

## Important questions and answers

**What is MCP?**

Model Context Protocol is an open protocol that standardizes communication between AI applications and external systems that expose capabilities such as tools, resources, and prompts.

**Who introduced MCP and when?**

Anthropic introduced MCP in November 2024.

**Why was MCP introduced?**

To reduce the need for custom integrations between every AI application and every external tool provider, and to make tool discovery and communication more standardized.

**What is an MCP server?**

A program that exposes capabilities such as tools, resources, and prompts through the MCP protocol.

**What is an MCP client?**

A component in an AI application that communicates with an MCP server using the MCP protocol.

**Does MCP replace function calling?**

No. Function calling lets an LLM request tool execution. MCP standardizes how an application discovers and communicates with external capabilities. They can work together.

**Does every MCP server run on a separate physical machine?**

No. An MCP server is a software process. It may run locally or remotely.

**What happens if an external API changes?**

The MCP server can be updated to accommodate changes in the underlying API while preserving its exposed interface, provided the server maintains compatibility.

**What are the three main MCP capabilities?**

Tools, resources, and prompts.

---

## Quick revision

**Remember these points**
- MCP = Model Context Protocol.
- Introduced by Anthropic in November 2024.
- It standardizes communication between AI applications and external services.
- MCP servers expose tools, resources, and prompts.
- MCP clients communicate with MCP servers.
- The server handles the integration with the underlying service.
- MCP and LLM function calling are complementary.
- MCP reduces duplicated integration work; it does not eliminate integration maintenance.
