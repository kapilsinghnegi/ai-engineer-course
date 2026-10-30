import json
import os
import re
import time
import uuid
from datetime import datetime

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

# Estimated pricing per 1M tokens (approximate; adjust as needed)
INPUT_COST_PER_1M = 0.50
OUTPUT_COST_PER_1M = 1.50


# ---------- Observability helpers ----------

def _now_ts():
    return datetime.utcnow().isoformat() + "Z"


def _cost(tokens_in: int, tokens_out: int) -> float:
    return tokens_in / 1_000_000 * INPUT_COST_PER_1M + tokens_out / 1_000_000 * OUTPUT_COST_PER_1M


def _norm_text(t: str) -> str:
    t = t.lower()
    t = t.replace("₹", "").replace(",", "")
    t = re.sub(r"\s+", " ", t)
    return t


def _contains_any(text: str, needles):
    t = _norm_text(text)
    return any(_norm_text(n) in t for n in needles)


# ---------- Guardrails ----------

# Keywords that trigger immediate chat termination
PROHIBITED_KEYWORDS = [
    # Cybersecurity / malware
    "malware", "virus", "ransomware", "exploit", "hack", "sql injection",
    "phishing", "keylogger", "trojan", "rootkit",
    # Sexual topics
    "sex", "sexual", "erotic", "porn", "onlyfans",
    # Weapons / violence
    "weapon", "gun", "knife", "bomb", "attack",
]

PROHIBITED_PREFIXES = ["how to make", "how to build", "tutorial for", "step by step for"]


def _is_prohibited_topic(text: str) -> bool:
    """Return True if the user input contains prohibited topics."""
    t = text.lower()
    for kw in PROHIBITED_KEYWORDS:
        if kw in t:
            return True
    # Check for instructional prefixes on prohibited topics
    for prefix in PROHIBITED_PREFIXES:
        if t.startswith(prefix):
            remaining = t[len(prefix):]
            for kw in PROHIBITED_KEYWORDS:
                if kw in remaining:
                    return True
    return False


def _same_name_customers(name: str) -> bool:
    """Return True if multiple customers share this exact name (case-insensitive)."""
    count = sum(1 for o in ORDERS if o["customer_name"].lower() == name.lower())
    return count > 1


def _is_order_history_query(text: str) -> bool:
    """Heuristic: does the user ask about an order, name, or history?

    Return True if the input appears to be an order-history inquiry.
    We treat it as an order query if:
    - It contains an order-ID pattern (A followed by 3-4 digits, e.g. A0001)
    - Or it contains a known customer name from our dataset
    Otherwise, it's likely extra/unrelated.
    """
    t = text.lower().strip()
    # Check for order-id pattern A followed by digits
    if re.search(r"\ba0?\d{3,4}\b", t):
        return True
    # Check against known customer names
    known_names = {o["customer_name"].lower() for o in ORDERS}
    for known in known_names:
        if known in t:
            return True
    return False


# ---------- Fake data for 5 customers ----------

ORDERS = [
    {
        "order_id": "A0001",
        "customer_name": "Rahul Sharma",
        "items": ["LED Bulb (9W)", "Extension Board"],
        "price": 850,
        "status": "delivered",
    },
    {
        "order_id": "A0002",
        "customer_name": "Priya Patel",
        "items": ["Ceiling Fan", "Fan Regulator"],
        "price": 3200,
        "status": "out for delivery",
    },
    {
        "order_id": "A0003",
        "customer_name": "Amit Verma",
        "items": ["Electric Kettle", "Power Strip"],
        "price": 2100,
        "status": "placed",
    },
    {
        "order_id": "A0004",
        "customer_name": "Sneha Iyer",
        "items": ["Table Lamp", "LED Tube Light (2ft)", "Switch Board"],
        "price": 1750,
        "status": "delivered",
    },
    {
        "order_id": "A0005",
        "customer_name": "Vikram Singh",
        "items": ["Mixer Grinder"],
        "price": 4500,
        "status": "out for delivery",
    },
]


def get_order_history(identifier: str) -> str:
    identifier = identifier.strip()
    matches = []
    for order in ORDERS:
        if order["order_id"].lower() == identifier.lower() or order[
            "customer_name"
        ].lower() == identifier.lower():
            matches.append(order)

    if not matches:
        return json.dumps({"found": False, "message": "No orders found for the given name or order id."})

    return json.dumps({"found": True, "orders": matches}, indent=2)


AVAILABLE_TOOLS = {"get_order_history": get_order_history}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_order_history",
            "description": "Get the order history for a customer using their name or order id (e.g. A0001).",
            "parameters": {
                "type": "object",
                "properties": {
                    "identifier": {
                        "type": "string",
                        "description": "The customer's name or the order id.",
                    }
                },
                "required": ["identifier"],
            },
        },
    }
]

SYSTEM_PROMPT = """
You are an assistant for an electric shop.
Users can give their name or order id.
If the user provides a name or order id, decide whether to call get_order_history and fetch their order history.
Once found, show the user the order history clearly.
Be concise. Do not volunteer unrelated information.
"""


def _run_agent(user_input: str):
    # ---------- Guardrail 1: Prohibited topics ----------
    if _is_prohibited_topic(user_input):
        return {
            "trace_id": str(uuid.uuid4()),
            "timestamp_utc": _now_ts(),
            "user_input": user_input,
            "final_answer": "I'm sorry, but I can't assist with that topic. The chat will now end.",
            "ended_early": True,
            "total_latency_ms": 0,
            "total_cost_usd": 0,
        }

    # ---------- Guardrail 2: Non-order-history inquiry check ----------
    # If the user is asking something other than order history, we still run the
    # agent but the system prompt constrains it. We track whether it's an order
    # query for reporting purposes.
    is_order_query = _is_order_history_query(user_input)

    trace_id = str(uuid.uuid4())
    start_wall = time.time()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]

    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_llm_latency_ms = 0.0
    total_tool_latency_ms = 0.0
    total_tool_cost = 0.0

    tool_calls_log = []

    for iteration in range(5):
        call_start = time.time()
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        call_latency_ms = (time.time() - call_start) * 1000

        # --- LLM usage ---
        usage = response.usage
        if usage:
            total_prompt_tokens += getattr(usage, "prompt_tokens", 0)
            total_completion_tokens += getattr(usage, "completion_tokens", 0)
        total_llm_latency_ms += call_latency_ms

        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            # Final answer phase
            final_answer = message.content or ""
            break

        # --- Tool calls ---
        for tool_call in message.tool_calls:
            tc_start = time.time()
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            if tool_name in AVAILABLE_TOOLS:
                # Execute tool & measure latency
                tool_start = time.time()
                result = AVAILABLE_TOOLS[tool_name](**arguments)
                tool_end = time.time()
                tool_latency_ms = (tool_end - tool_start) * 1000
                total_tool_latency_ms += tool_latency_ms

                tool_calls_log.append(
                    {
                        "name": tool_name,
                        "arguments": arguments,
                        "result": result,
                        "latency_ms": tool_latency_ms,
                    }
                )
            else:
                result = f"Unknown tool: {tool_name}"
                tool_calls_log.append(
                    {
                        "name": tool_name,
                        "arguments": arguments,
                        "result": result,
                        "latency_ms": 0.0,
                    }
                )

            messages.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": result}
            )

    else:
        # Loop finished without break -> iteration limit
        final_answer = "I couldn't complete the request within the iteration limit."

    total_wall = (time.time() - start_wall) * 1000  # ms
    total_cost = _cost(total_prompt_tokens, total_completion_tokens)

    # Build summary
    summary = {
        "trace_id": trace_id,
        "timestamp_utc": _now_ts(),
        "user_input": user_input,
        "final_answer": final_answer,
        "total_latency_ms": round(total_wall, 2),
        "total_cost_usd": round(total_cost, 6),
        "is_order_query": is_order_query,
        "ended_early": False,
        "llm": {
            "prompt_tokens": total_prompt_tokens,
            "completion_tokens": total_completion_tokens,
            "latency_ms": round(total_llm_latency_ms, 2),
        },
        "tools": tool_calls_log,
        "total_tool_latency_ms": round(total_tool_latency_ms, 2),
    }
    return summary


if __name__ == "__main__":
    print("=" * 60)
    print(" " * 18, "ELECTRIC SHOP AGENT (with Observability + Guardrails)")
    print("=" * 60)
    user_input = input("\nEnter your name or order id: ")
    summary = _run_agent(user_input)

    # Pretty-print the trace
    import json as _json
    print("\n--- TRACE ---")
    print(f"trace_id: {summary['trace_id']}")
    print(f"timestamp_utc: {summary['timestamp_utc']}")
    print(f"user_input: {summary['user_input']}")
    print(f"final_answer: {summary['final_answer']}")
    print(f"total_latency_ms: {summary['total_latency_ms']}")
    print(f"total_cost_usd: {summary['total_cost_usd']}")
    print(f"is_order_query: {summary['is_order_query']}")
    print(f"llm.prompt_tokens: {summary['llm']['prompt_tokens']}")
    print(f"llm.completion_tokens: {summary['llm']['completion_tokens']}")
    print(f"llm.latency_ms: {summary['llm']['latency_ms']}")
    print(f"total_tool_latency_ms: {summary['total_tool_latency_ms']}")
    print(f"tools.call_count: {len(summary['tools'])}")
    for tc in summary["tools"]:
        print(
            f"  tool: {tc['name']} args={_json.dumps(tc['arguments'])} result_snippet={str(tc['result'])[:80]} latency_ms={tc['latency_ms']}"
        )
    print("--- END TRACE ---")