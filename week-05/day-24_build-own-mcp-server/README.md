# Day 24 — Build Your First MCP Server

## What are we building?

We will build a custom calculator tool and make it accessible to Claude through MCP.

Normally, if you ask Claude:

> Add 10 and 30.

Claude might calculate the answer itself or use another calculator tool.

But we want Claude to use our own Python function.

Our custom function will deliberately add `100` to the result. This helps us verify that Claude actually called our tool rather than calculating the answer independently.

For example:

| Input | Normal result | Our MCP tool |
|---|---:|---:|
| 10 + 30 | 40 | 140 |
| 40 + 30 | 70 | 170 |
| 5 + 5 | 10 | 110 |

**Our architecture**

**User**

"Add 40 and 30"

**Claude Desktop**

AI application / MCP host

**MCP Client**

Communicates with our MCP server

Our implementation

**Add_Hundred_Calculator MCP Server**

Exposes the add_hundred tool

**40 + 30 + 100 = 170**

**Tool result returned to Claude**

---

## Project setup

The instructor creates a project folder for the MCP server.

Example structure:

```text
week-six/
└── my-mcp-server/
    ├── .venv/
    ├── pyproject.toml
    ├── uv.lock
    └── mcp_server.py
```

### Install the MCP package

```bash
uv add "mcp[cli]"
```

The `[cli]` extra provides CLI development utilities. This distinction matters because the installed package must actually expose the import and CLI commands used in your code.

---

## Understanding the MCP server code

```python
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("Add_Hundred_Calculator")

@mcp.tool()
def add_hundred(a: int, b: int) -> int:
    """Add two numbers using custom calculator"""
    return a + b + 100  # deliberate debug proves claude is using our tool

if __name__ == "__main__":
    mcp.run()
```

Let's understand each part.

### Importing MCPServer

```python
from mcp.server.mcpserver import MCPServer
```

This imports the `MCPServer` class from the installed MCP package.

We use this class to create an MCP server that can expose tools to compatible MCP clients.

Think of it as creating the kitchen in our restaurant analogy from Day 23.

### Creating the MCP server

```python
mcp = MCPServer("Add_Hundred_Calculator")
```

Here, we create an MCP server instance.

- `MCPServer` is the class.
- `mcp` is the object created from that class.
- `"Add_Hundred_Calculator"` is the server's name.

The name helps identify the server.

It is not the name of an individual tool.

### Registering a tool

```python
@mcp.tool()
def add_hundred(a: int, b: int) -> int:
```

This is the most important part of the implementation.

`@mcp.tool()` is a Python decorator.

It registers the function as a tool exposed by the MCP server.

Without this decorator, the function would simply be an ordinary Python function. It would not automatically become an MCP tool.

The function accepts two parameters:

- `a`: First number.
- `b`: Second number.

Both are annotated as integers.

The return type annotation indicates that the function returns an integer.

### Tool description

```python
"""Add two numbers using custom calculator"""
```

This is a Python docstring.

It describes what the function does.

The MCP SDK can use function metadata, including its name, description, and parameter information, when exposing the tool to clients.

This is important because the AI application needs to understand what the tool does and when it might be useful.

### Tool implementation

```python
return a + b + 100
```

This is our actual business logic.

For example:

```python
add_hundred(40, 30)
```

Returns:

```text
170
```

The extra `100` is intentional.

It acts as a debugging signal: if Claude returns `170` for the request to add 40 and 30, that indicates the custom function was executed.

### Running the server

```python
if __name__ == "__main__":
    mcp.run()
```

This is Python's main-module guard.

It ensures that `mcp.run()` executes when the file is run directly.

For example:

```bash
python mcp_server.py
```

When this happens, the MCP server starts.

The exact transport and runtime behavior depend on the SDK version and server implementation.

---

## How does `@mcp.tool()` work?

Let's understand why this decorator is useful.

In a traditional Python application, you might define a function:

```python
def add_hundred(a: int, b: int) -> int:
    return a + b + 100
```

You can call it directly:

```python
result = add_hundred(10, 30)
```

But Claude cannot automatically call every Python function on your computer.

It needs a way to discover the function, understand its parameters, and request its execution.

The decorator registers the function with the MCP server:

```python
@mcp.tool()
def add_hundred(a: int, b: int) -> int:
    """Add two numbers using custom calculator"""
    return a + b + 100
```

Conceptually, the server can now expose information like:

| Metadata | Value |
|---|---|
| Tool name | `add_hundred` |
| Description | Add two numbers using custom calculator |
| Parameter `a` | Integer |
| Parameter `b` | Integer |
| Return value | Integer |

The MCP server SDK handles much of the protocol-related work.

**Important:** The instructor says we do not need to manually write a separate function schema or explain the API syntax to Claude. The SDK derives tool metadata from the registered function, including its annotations and docstring.

This is one of the main advantages of using an MCP SDK.

---

## Running and testing the MCP server

Before connecting the server to Claude, we can test it independently.

This is a good development practice: verify that the server exposes the expected tools before introducing another application into the debugging process.

### Step 1: Start the MCP development interface

The transcript demonstrates:

```bash
uv run mcp dev mcp_server.py
```

This launches an MCP development interface in the browser.

The development interface lets you:

1. Connect to your MCP server.
2. Discover the tools it exposes.
3. Inspect tool descriptions and input parameters.
4. Execute a tool with test arguments.
5. Inspect the returned result.

This is useful because you can test your server without first configuring Claude Desktop.

### Step 2: Test the tool

Select the `add_hundred` tool and provide:

```json
{
  "a": 10,
  "b": 30
}
```

Expected result:

```text
140
```

Why?

```text
10+30+100=140
```

If the result is `140`, your function is behaving as expected.

---

## Connecting the MCP server to Claude Desktop

Once the server has been tested, the next step is connecting it to Claude Desktop.

The instructor uses the Claude Desktop configuration file:

`claude_desktop_config.json`

This configuration tells Claude Desktop:

- Which MCP server to start.
- Which command to execute.
- Which directory contains the project.
- Which Python file starts the server.

The transcript demonstrates adding an MCP server configuration under the `mcpServers` object.

### Configuration example from the lesson

```json
{
  "mcpServers": {
    "Add_Hundred_Calculator": {
      "command": "UV_PATH",
      "args": [
        "--directory",
        "PATH_TO_WORKING_DIR",
        "run",
        "mcp_server.py"
      ]
    }
  }
}
```

The values in this example are placeholders. Replace them with your actual paths.

### Understanding each field

| Field | Purpose |
|---|---|
| `mcpServers` | Contains the MCP servers configured in Claude Desktop |
| `Add_Hundred_Calculator` | Custom name used to identify the server |
| `command` | Executable used to launch the server |
| `args` | Arguments passed to that executable |
| `--directory` | Specifies the project directory |
| `run` | Tells `uv` to run the project command |
| `mcp_server.py` | Python file that starts the server |

### Find the location of `uv.exe`

On Windows, the instructor uses:

```powershell
where.exe uv
```

This returns the location of the `uv` executable.

For example:

```text
C:\Users\YourUsername\.local\bin\uv.exe
```

Put the returned path in the `command` field.

On macOS or Linux, use:

```bash
which uv
```

### Find your project directory

Navigate to your MCP project folder:

```bash
cd path/to/my-mcp-server
```

Then run:

```bash
pwd
```

This prints the absolute path of your working directory.

Use that path as the value of `--directory`.

### Pay attention to Windows path escaping

JSON uses backslashes as escape characters.

For Windows paths, use doubled backslashes:

```json
"C:\\Users\\YourUsername\\Projects\\my-mcp-server"
```

Alternatively, forward slashes can be used in many Windows application paths:

```json
"C:/Users/YourUsername/Projects/my-mcp-server"
```

A missing character in the path can prevent Claude from launching the server.

### Restart Claude Desktop

After saving the configuration:

1. Completely close Claude Desktop.
2. Make sure its background process has exited.
3. Open Claude Desktop again.
4. Check the connectors or available MCP integrations.

The instructor demonstrates that the newly configured server appears in Claude Desktop.

---

## How do we verify Claude is using our tool?

This is the most interesting part of the demonstration.

Ask Claude:

> Use the add_hundred tool and add 40 and 30.

A normal calculation would return:

```
40+30=70
```
But our MCP tool returns:

```
40+30+100=170
```

**Expected verification**

Normal calculation · **70**

Custom MCP tool · **170**

Custom tool execution signal

The extra 100 confirms that the custom function's logic affected the result.

This is a simple debugging technique.

However, in a real application, you should also inspect Claude's tool-use indicator or execution logs. A model could theoretically produce `170` without calling the tool if it guessed the expected behavior.

---

## Complete execution flow

Let's connect all the concepts into one flow.

**MCP tool execution lifecycle**

1. **Build the server** · Create a Python MCP server using the SDK.
2. **Register tools** · Use `@mcp.tool()` to expose Python functions.
3. **Start the server** · Run the Python file through `uv`.
4. **Configure Claude Desktop** · Add the server's executable, project directory, and Python entry point to its configuration.
5. **Discover available tools** · Claude's MCP client communicates with the server and discovers its registered tools and input schemas.
6. **Select and invoke a tool** · Claude decides to use `add_hundred` and provides `a=40`, `b=30`.
7. **Execute Python function** · The MCP server executes the function and returns `170`.
8. **Generate the response** · Claude receives the tool result and communicates it to the user.

### What if we add another tool?

Suppose we want to expose a subtraction tool too.

We can register another function:

```python
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract the second number from the first."""
    return a - b
```

Now the server exposes two tools:

- `add_hundred`
- `subtract`

The client can discover both tools from the same MCP server.

This demonstrates how one MCP server can expose multiple capabilities.

---

## Important technical corrections and caveats

There are a few details worth understanding before implementing this yourself.

### `MCPServer` vs `FastMCP`

Your code uses:

```python
from mcp.server.mcpserver import MCPServer
```

And:

```python
mcp = MCPServer("Add_Hundred_Calculator")
```

The commonly documented official Python MCP SDK interface uses `FastMCP`:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Add_Hundred_Calculator")
```

The decorator pattern remains similar:

```python
@mcp.tool()
def add_hundred(a: int, b: int) -> int:
    """Add two numbers using custom calculator."""
    return a + b + 100
```

For a standard Claude Desktop integration over standard input/output (stdio), the entry point is:

```python
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

So, don't assume the transcript's `MCPServer` import will work with every version of the official SDK. Check the installed package and SDK version before running the instructor's exact code.

### Why is stdio important?

In this setup, Claude Desktop launches the MCP server as a local process and communicates with it using standard input and output.

This means:

- Claude starts the server.
- Requests are sent through standard input.
- Responses are returned through standard output.
- The server can be stopped when the client no longer needs it.

**Important:** Avoid printing debugging messages directly to standard output in an MCP server using stdio. Such messages can interfere with protocol communication. Use Python logging, typically directed to standard error, instead.

### MCP doesn't mean Claude automatically understands everything

The MCP server exposes tool metadata, including descriptions and input schemas.

Claude's application uses that information to make the tools available to the model.

The model still decides whether to call a tool based on the user's request and the application's tool-selection behavior.

---

## Important questions and answers

**What is the purpose of @mcp.tool()?**

It registers a Python function as a tool exposed by the MCP server. The SDK can derive the tool's name, description, and input schema from the function.


**What is the difference between an MCP server and an MCP client?**

The server exposes capabilities, while the client communicates with the server to discover and invoke those capabilities.


**Why do we use a docstring in an MCP tool?**

It provides a description of the tool's purpose, helping clients and models understand when the tool should be used.


**What is the purpose of claude_desktop_config.json?**

It tells Claude Desktop how to launch and connect to configured MCP servers, including their executable, arguments, and project directories.


**What does --directory do in the uv command?**

It specifies the project directory in which uv should execute the requested command.


**Why should we test an MCP server before connecting it to Claude?**

To verify that the server starts, exposes the expected tools, accepts the correct inputs, and returns the expected outputs independently of the AI application.


**Can one MCP server expose multiple tools?**

Yes. Multiple functions can be registered as tools on the same server.


**What is stdio transport?**

A communication method in which the client and server exchange protocol messages through standard input and standard output.


---

## Quick revision

| Concept | Remember |
|---|---|
| `MCPServer` / `FastMCP` | Creates an MCP server, depending on SDK interface |
| `@mcp.tool()` | Registers a Python function as an MCP tool |
| Function docstring | Describes the tool |
| Type annotations | Describe input and return types |
| `mcp.run()` | Starts the server |
| MCP Inspector | Tests and inspects MCP servers |
| `claude_desktop_config.json` | Configures MCP servers in Claude Desktop |
| `uv` | Runs the Python project and manages dependencies |
| stdio | Local process communication through standard input/output |