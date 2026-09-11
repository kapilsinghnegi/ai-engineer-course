# LangGraph Fundamentals — State, Nodes, Edges, and Conditional Routing

## What is LangGraph?

LangGraph is a framework for building stateful, multi-step applications and AI-agent workflows as graphs.

A graph consists of:

- **State:** The data shared across workflow steps.
- **Nodes:** Functions that perform work or make decisions.
- **Edges:** Connections that determine which node runs next.
- **Conditional edges:** Routing rules that select the next node based on the current state.
- **Entry point:** The node where execution begins.
- **End:** A special marker indicating that execution should stop.

For example, an AI research agent might use a graph like this:

`User question → Search → Evaluate results → Answer or search again → End`

Your current example is simpler:

`Start → Double → Check condition → Double again OR Finish → End`

The underlying principle is the same: execution follows the graph, and the state carries information between steps.

## State: the data moving through the graph

Your code defines:

```python
from typing import TypedDict

class State(TypedDict):
    number: int
```

### What is `TypedDict`?

`TypedDict` lets you describe the expected structure of a dictionary using type annotations.

Here, `State` specifies that the graph's state contains a `number` key whose value is expected to be an integer.

An example state is:

```python
{"number": 5}
```

After doubling, it might become:

```python
{"number": 10}
```

And later:

```python
{"number": 20}
```

Conceptually, state is the shared data passed through the graph. Nodes can read values from it and return updates to it.

**Important distinction:** `TypedDict` provides type information; it does not automatically validate every runtime value. Also, LangGraph does not require every state field to be an integer or even use `TypedDict` in every workflow. It supports other state schemas, depending on the application.

## Nodes: functions that perform work

In LangGraph, a node is a function registered under a name. A node receives the current state and typically returns a dictionary containing state updates.

Your graph has two nodes.

### Node 1 — `double()`

```python
def double(state: State) -> dict:
    board_num = state["number"]
    new_num = board_num * 2
    print("in double: ", new_num)
    return {"number": new_num}
```

For example, if the incoming state is `{"number": 5}`, the function returns `{"number": 10}`.

One small naming issue: `board_num` appears to be a typo for `number` or `current_num`. It does not affect execution, but a clearer variable name improves readability.

### Node 2 — `finish()`

```python
def finish(state: State) -> dict:
    board_num = state["number"]
    print("in finish: ", board_num)
    return {"number": board_num}
```

This node prints the final number and returns the same number without modifying it.

If the state contains `{"number": 160}`, it prints `160` and returns `{"number": 160}`.

Why return the number again? The node's main purpose here is to demonstrate a final processing step. It could instead return an empty update if it did not need to change state, or return some additional result if the state schema were expanded.

## Conditional routing: `decision()`

```python
def decision(state: State) -> str:
    if state["number"] < 100:
        return "double"
    else:
        return "finish"
```

This function decides which node should execute next.

- If `number` is less than `100`, return `"double"`.
- Otherwise, return `"finish"`.

Notice that this function **does not double the number**. It only chooses a route.

This is a useful separation of responsibilities:

- `double()` performs an operation.
- `decision()` determines the next step.
- LangGraph follows the selected edge.

For the initial number `5`, the sequence of decisions will be:

| Current number | Condition | Next node |
|---:|---|---|
| 10 | \(10 < 100\) | `double` |
| 20 | \(20 < 100\) | `double` |
| 40 | \(40 < 100\) | `double` |
| 80 | \(80 < 100\) | `double` |
| 160 | \(160 < 100\) is false | `finish` |

The condition is evaluated after `double()` returns its update. This is why the decision sees `10` on the first pass, not the original `5`.

---

## Building the graph

Now let's examine how the functions are connected.

### Step 1 — Create a graph builder

```python
builder = StateGraph(State)
```

`StateGraph(State)` creates a graph builder that uses the `State` schema you defined earlier.

At this stage, you've created the graph structure, but you haven't added the nodes or connections yet.

### Step 2 — Register the nodes

```python
builder.add_node("double", double)
builder.add_node("finish", finish)
```

Each call associates a name with a Python function:

- `"double"` maps to `double()`.
- `"finish"` maps to `finish()`.

The node name is the identifier used when defining edges and routing.

### Step 3 — Set the entry point

```python
builder.set_entry_point("double")
```

This tells LangGraph to begin execution at the `double` node.

The initial state is supplied later when invoking the graph. Setting the entry point does not itself run the node.

### Step 4 — Add conditional edges

```python
builder.add_conditional_edges(
    "double",
    decision,
    {"double": "double", "finish": "finish"}
)
```

This is the key line in the example.

The arguments are:

1. `"double"` — the node after which routing is evaluated.
2. `decision` — the routing function.
3. The mapping — connects each returned routing label to a destination node.

The mapping can be read as:

```python
{
    "double": "double",
    "finish": "finish"
}
```

When `decision()` returns `"double"`, LangGraph routes execution back to the `double` node. When it returns `"finish"`, execution moves to the `finish` node.

This creates a loop in the graph. LangGraph can execute the same node repeatedly until the condition selects another route.

### Step 5 — Connect the final node to the end

```python
builder.add_edge("finish", END)
```

`END` is a special LangGraph marker meaning the graph execution should terminate after `finish` completes.

It is not another Python function you need to define.

### Step 6 — Compile the graph

```python
graph = builder.compile()
```

Compilation turns the configured builder into a runnable graph. The graph is now ready to be invoked with an initial state.

### Step 7 — Execute the graph

```python
if __name__ == "__main__":
    result = graph.invoke({"number": 5})
```

`graph.invoke()` starts execution with the initial state `{"number": 5}`.

The `if __name__ == "__main__":` guard means this code runs when the file is executed as a script, but not when the file is imported as a module.

The result is assigned to `result`. Your current code doesn't print it, so the final state won't be displayed automatically just because the variable was assigned.

You can add:

```python
print("Final state:", result)
```

to see the returned state.

---

## Visualize the workflow

**Start**

**`double`**

Multiply number by 2

**`decision`**

Is the updated number less than 100?

- Yes · **`double`** · Repeat the operation
- No · **`finish`** · Print the final number

**`END`**

Return the final graph state

The diagram shows the main structure. The `"double"` route loops back to the same node, while the `"finish"` route proceeds to the terminal node.

## Full execution walkthrough

Let's trace `graph.invoke({"number": 5})` step by step.

**Execution trace** · 5 doubling operations

Final state

The expected console output, excluding the final-state print unless you add it, is:

```text
in double:  10
in double:  20
in double:  40
in double:  80
in double:  160
in finish:  160
```

The final returned state is:

```python
{"number": 160}
```

## How LangGraph updates state

One particularly important concept is that nodes can return **partial state updates**.

Your `double()` node returns:

```python
return {"number": new_num}
```

LangGraph applies that update to the graph's state. Because `number` is the only state field, the resulting state is straightforward.

In a larger application, the state might contain several fields:

```python
class State(TypedDict):
    question: str
    search_results: str
    answer: str
```

A search node could return only:

```python
{"search_results": "Retrieved information..."}
```

The other state fields are not necessarily overwritten simply because the node omitted them. For a normal `TypedDict` state without custom reducers, LangGraph updates the returned keys and preserves the other existing keys.

This lets different nodes focus on their own responsibilities rather than rebuilding the entire state every time.

## Common mistakes to avoid

| Mistake | Why it matters |
|---|---|
| Confusing a node with an edge | Nodes perform work; edges control execution flow. |
| Assuming `decision()` changes the state | It only chooses a route in this example. |
| Forgetting the entry point | The graph needs a defined starting node. |
| Forgetting `END` | A terminal route should explicitly stop the graph. |
| Assuming `compile()` executes the graph | Compilation prepares the graph; `invoke()` runs it. |
| Expecting `result` to print automatically | Assigning a return value to a variable does not display it. |
| Forgetting the node runs before the condition | The initial value `5` is doubled to `10` before the first routing decision. |

### A small improvement to your code

You can make the variable names and return type more precise:

```python
def double(state: State) -> dict[str, int]:
    current_num = state["number"]
    new_num = current_num * 2

    print("in double:", new_num)

    return {"number": new_num}

def finish(state: State) -> dict[str, int]:
    current_num = state["number"]

    print("in finish:", current_num)

    return {"number": current_num}
```

The graph logic remains the same; this just makes the code easier to understand.

One more detail: this particular workflow terminates because the number doubles and eventually reaches the threshold. In other graphs, conditional routes can accidentally create infinite cycles. LangGraph has a recursion limit to help prevent runaway execution, but you should design explicit stopping conditions rather than rely on that limit.

## Important questions and answers

**Q1. What is a graph in LangGraph?**

A graph is a workflow composed of nodes and edges. Nodes perform operations, and edges determine the order in which those operations execute.

**Q2. What is state in LangGraph?**

State is the data shared between graph nodes. Nodes read from it and return updates that the graph applies during execution.

**Q3. What is the difference between a normal edge and a conditional edge?**

A normal edge connects a node to a predetermined next node. A conditional edge uses a routing function to select the next node based on the current state.

**Q4. What does `StateGraph(State)` do?**

It creates a graph builder that uses the specified state schema.

**Q5. What does `compile()` do?**

It compiles the configured graph into a runnable object.

**Q6. What is the purpose of `END`?**

It marks the termination of graph execution.

**Q7. Why does this example finish at `160`?**

Because the graph doubles `80` to `160`, then checks whether `160 < 100`. The condition is false, so the graph routes to `finish`.

**Q8. Can a graph execute the same node multiple times?**

Yes. An edge can route execution back to a previously executed node, creating a loop. The loop should have a valid stopping condition.

**Q9. Does a node need to return the complete state?**

No. Nodes can return partial updates. LangGraph applies those updates according to the state's update and reducer semantics.

**Q10. Why is this useful for AI agents?**

An agent can use conditional edges to decide whether to search again, call a tool, evaluate retrieved evidence, ask for clarification, or produce a final answer.
