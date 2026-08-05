import json, os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel
from pypdf import PdfReader
from groq import Groq

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("No API key found.")

client = Groq(api_key=my_api_key)
model = "openai/gpt-oss-120b"


class Experience(BaseModel):
    company: str | None = None
    role: str | None = None
    duration: float | None = None
    description: str | None = None
    skills_used: list[str] = []


class Resume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    total_experience_years: float | None = None
    skills: list[str] = []
    experiences: list[Experience] = []
    projects: list[str] = []
    certifications: list[str] = []


class ChatRequest(BaseModel):
    question: str


# pdf text extraction
def read_pdf(file_path: Path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def parse_resume(resume_text):
    resume_schema = Resume.model_json_schema()
    message_system = {
        "role": "system",
        "content": f"""
        You are an Expert Resume Parser. 
        Extract information from the resume based on its meaning, not only based on exact section headings. Different resumes may use different headings.
        
        For example: 
        - Work Experience
        - Experience
        - Professional Experience
        - Employment History
        - Internships 

        All of the above may contain relevant experience information.
        
        Skills may also appear in the skills section, work experience, internships, projects, or certifications. Extract all skills mentioned in the resume.

        Return only valid JSON matching this schema: {resume_schema}

        IMPORTANT:
        1. Do not invent information. Only extract what is present in the resume.
        2. If a value is not mentioned, return null for that field.
        3. If information for a list is missing, return an empty list.
        4. Include internships in the experiences.
        5. Extract skills from all sections of the resume, including work experience, internships, projects, and certifications.
        """,
    }

    message_user = {
        "role": "user",
        "content": f"""
        Parse the following resume text and extract structured information from it:
        {resume_text}
        """,
    }

    messages = [message_system, message_user]
    response_format = {"type": "json_object"}

    response = client.chat.completions.create(
        model=model, messages=messages, response_format=response_format
    )
    raw_output = response.choices[0].message.content
    resume_data = json.loads(raw_output)
    resume = Resume(**resume_data)
    return resume


def ask_ai(question: str, resume: Resume):
    system_prompt = f"""
        You are an AI Assistant representing a candidate. Below is everything you need to know about the candidate:
        {resume}
        
        Rules:
        1. Answer only using the information.
        2. Never hallucinate.
        3. If the information is not available, tell that you don't have enough information to answer that question.
        4. Be professional.
        5. Answer as if you're talking to an HR.
        """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]
    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content
