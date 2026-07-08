import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API key not found.")

client = Groq(api_key=my_api_key)
model = "openai/gpt-oss-20b"

message_system = {
    "role": "system",
    "content": "You are brand manager who suggests name for my clothing company. Name should contains only single word.",
}
message_user = {"role": "user", "content": "Suggest a name for my clothing Company"}
messages = [message_system, message_user]

response = client.chat.completions.create(
    model=model, messages=messages, temperature=0.5
)
answer = response.choices[0].message.content
print(answer)
