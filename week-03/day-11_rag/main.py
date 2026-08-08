import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("API key not found.")

client = Groq(api_key=my_api_key)
model = "openai/gpt-oss-20b"

# step - 1: Create knowledge base
knowledge_base = {
    "age": "Kapil is 23 years old currently.",
    "interests": "His interests include Full-Stack Development, AI Engineering, MMA and other sports",
}


# step - 2: Retrieval
def retrieve_info(question):
    question = question.lower()
    if "age" in question:
        return knowledge_base["age"]
    elif "interest" in question:
        return knowledge_base["interests"]
    return None


def ask_llm(question):
    context = retrieve_info(question)
    message_system = {
        "role": "system",
        "content": f"""Answer in one line only and answer only based on the given context. Don't hallucinate.
        Context: {context}""",
    }
    message_user = {"role": "user", "content": question}
    messages = [message_system, message_user]
    response = client.chat.completions.create(model=model, messages=messages)
    answer = response.choices[0].message.content
    return answer


question = "How old is Kapil?"
print(ask_llm(question))
