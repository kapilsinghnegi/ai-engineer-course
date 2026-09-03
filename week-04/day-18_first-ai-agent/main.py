import json, os
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not all([GROQ_API_KEY, TAVILY_API_KEY]):
    raise ValueError("Missing required API key")

groq = Groq(api_key=GROQ_API_KEY)
tavily = TavilyClient(api_key=TAVILY_API_KEY)

# Tool 1: Web Search


def web_search(query: str) -> str:
    try:
        response = tavily.search(query=query, max_results=3, search_depth="basic")

        results = []

        for result in response["results"]:
            results.append(
                f"Title: {result['title']}\n"
                f"URL: {result["url"]}\n"
                f"Content: {result["content"]}"
            )
        return "\n\n".join(results)
    except Exception as e:
        return f"Search failed: {e}"


# Tool 2: Calculator


def calculate(expression: str) -> str:
    try:
        return str(eval(expression, {"__bulletins__": {}}, {}))
    except Exception as e:
        return f"Calculation failed: {e}"


# Tool Registry

AVAILABLE_TOOLS = {"web_search": web_search, "calculate": calculate}

# Tool Definitions for LLM

tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information, news, recent events, prices, statistics, or facts that may have changed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A specific and concise web search query.",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform mathematical calculations such as percentages, multiplications, division, or arithmetic",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A mathematical expression such as '2500 * 0.15'.",
                    }
                },
                "required": ["expression"],
            },
        },
    },
]

# Agent Instructions

SYSTEM_PROMPT = """
    You are a research assistant.
    
    Rules:
    1. Use web_search for current or changing information.
    2. Use calculate for mathematical calculations.
    3. You may use tools multiple times.
    4. When you have enough information, answer the user.
    5. Include useful source URLs from web search results. 
"""


# Agent Loop
def run_agent(question: str, max_iterations: int = 5):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    for iteration in range(max_iterations):
        response = groq.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            print("\n Final Answer:")
            print(message.content)
            return message.content

        print(f"\n--- Iteration {iteration + 1} ---")

        # Tool Call(s)
        print(f"LLM requested {len(message.tool_calls)} tool(s)")

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            print(f"Tool: {tool_name}")
            print(f"Arguments: {arguments}")

            if tool_name not in AVAILABLE_TOOLS:
                result = f"Unknown tool: {tool_name}"
            else:
                result = AVAILABLE_TOOLS[tool_name](**arguments)

            print("Tool result received.")

            messages.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": result}
            )

    print("\nMaximum iterations reached.")
    return "I couldn't complete the task within the iteration limit."


print("=" * 60)
print(" " * 20, "AI RESEARCH AGENT")
print("=" * 60)

question = input("\nAsk me anything: ")
run_agent(question)
