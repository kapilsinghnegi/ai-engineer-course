import os, sys
import numpy as np
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API key not found.")

client = Groq(api_key=my_api_key)
groq_model = "openai/gpt-oss-120b"

model = SentenceTransformer("all-MiniLM-L6-v2")


documents = [
    "Employees receive 24 days of paid leave per year.",
    "Employees work from office on Tuesday, Wednesday, and Thursday.",
    "Monday and Friday are optional work-from-home days.",
    "Employees receive Rs 3000 per month gym reimbursement.",
    "Employees can claim Rs 2000 per month for home internet.",
    "Employees have a 90 day notice period.",
]

document_embeddings = model.encode(documents)
print(sys.getsizeof(document_embeddings))


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def retrieve(query_embedding):
    scores = []
    for i, document_embedding in enumerate(document_embeddings):
        score = cosine_similarity(query_embedding, document_embedding)
        scores.append((score, documents[i]))
    scores.sort(reverse=True)
    return scores[0]


def ask_llm(question, context):
    message_system = {
        "role": "system",
        "content": f"""Answer in one-line only. Answer only based on the context provided to you. Don't hallucinate. Context: {context}""",
    }
    message_user = {"role": "user", "content": question}
    messages = [message_system, message_user]
    response = client.chat.completions.create(model=groq_model, messages=messages)
    answer = response.choices[0].message.content
    return answer


query = "How many days of vacation do I get?"
query_embedding = model.encode(query)
score, context = retrieve(query_embedding)
print(ask_llm(query, context))
