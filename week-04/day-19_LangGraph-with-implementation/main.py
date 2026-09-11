from typing import TypedDict
from langgraph.graph import END, StateGraph


class State(TypedDict):
    number: int


def double(state: State) -> dict:
    board_num = state["number"]
    new_num = board_num * 2
    print("in double: ", new_num)
    return {"number": new_num}


def finish(state: State) -> dict:
    board_num = state["number"]
    print("in finish: ", board_num)
    return {"number": board_num}


def decision(state: State) -> str:
    if state["number"] < 100:
        return "double"
    else:
        return "finish"


builder = StateGraph(State)
builder.add_node("double", double)
builder.add_node("finish", finish)

# entry point
builder.set_entry_point("double")

builder.add_conditional_edges(
    "double", decision, {"double": "double", "finish": "finish"}
)

builder.add_edge("finish", END)
graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke({"number": 5})
