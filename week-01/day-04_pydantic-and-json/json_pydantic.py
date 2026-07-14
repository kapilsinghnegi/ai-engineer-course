import os
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
import json

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API key not found")

client = Groq(api_key=my_api_key)


class Ticket(BaseModel):
    name: str
    email: str
    issue: str


schema = Ticket.model_json_schema()

system_prompt = f"""
Extract the personal information from the ticket, strictly based on this schema {schema}. The output must be in json format only.
"""

message_system = {
    "role": "system",
    "content": system_prompt,
}

text = "Hello, my name is Kapil. I am from Delhi. I travel to different places for my work on day-to-day basis. I have an iPhone that is not working at all. This is causing a lot of trouble in my work. This issue needs to be fixed ASAP. Help me solve this issue. You can contact me on this email - kapil@example.com"
user_prompt = f"""
This is a customer ticket. Extract the personal information from this. {text}
"""
message_user = {"role": "user", "content": user_prompt}

model = "openai/gpt-oss-20b"
messages = [message_system, message_user]
response_format = {"type": "json_object"}

response = client.chat.completions.create(
    model=model, messages=messages, response_format=response_format
)
answer = response.choices[0].message.content
print(answer)

# extract from json
raw_json = answer
data_file = json.loads(raw_json)
ticket = Ticket(**data_file)

print(ticket.name)
print(ticket.email)
print(ticket.issue)
