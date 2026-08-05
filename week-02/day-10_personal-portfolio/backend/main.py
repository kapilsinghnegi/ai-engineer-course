from pathlib import Path
from fastapi import FastAPI
from parse_resume import read_pdf, parse_resume, ask_ai, ChatRequest

app = FastAPI()


@app.get("/")
def home():
    return {"status": 200, "message": "Server is up and running."}


@app.post("/chat")
def chat(request: ChatRequest):
    resume_text = read_pdf(Path("data/resume.pdf"))
    resume = parse_resume(resume_text)
    answer = ask_ai(request.question, resume)
    return {"status": 200, "answer": answer}
