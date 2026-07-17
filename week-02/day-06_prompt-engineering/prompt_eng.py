import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("API key not found.")


client = Groq(api_key=my_api_key)
model = "openai/gpt-oss-20b"


def generate_answer(prompt):
    message = {"role": "user", "content": prompt}
    messages = [message]

    response = client.chat.completions.create(model=model, messages=messages)
    answer = response.choices[0].message.content
    return answer


bad_prompt = """
This is a user complaint: My laptop is not working.
Classify this.
"""

prompt = """
# ROLE
You are a support assistant at a mobile/laptop company.

# TASK
You have to classify an issue for the company.

# CONSTRAINTS
The classification of an issue can be one of the following categories: Billing, Technical, Return

# OUTPUT FORMAT
The output must be a single word which is one of the specified categories in constraints. 

# EXAMPLE
For instance if a user complaint says that he wants a refund then the category should be Refund.

# CONSTRAINTS
If the issue is unrelated to any of the categories mentioned in constraints, then the category should be Other.

User complaint: My laptop is not working.
Classify this.
"""

print(generate_answer(prompt))
