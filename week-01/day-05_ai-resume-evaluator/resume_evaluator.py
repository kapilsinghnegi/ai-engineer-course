import os, json, time
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
from pypdf import PdfReader
from docx import Document

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("API key not found.")

job_description = """
Description
Do you want to solve real customer problems through innovative technology? Do you enjoy working on scalable services in a collaborative team environment? Do you want to see your code directly impact millions of customers worldwide?

At Amazon, we hire the best minds in technology to innovate and build on behalf of our customers. Customer obsession is part of our company DNA, which has made us one of the world's most beloved brands.

Our Software Development Engineers (SDEs) use modern technology to solve complex problems while seeing their work's impact first-hand. The challenges SDEs solve at Amazon are meaningful and influence millions of customers, sellers, and products globally. We seek individuals passionate about creating new products, features, and services while managing ambiguity in an environment where development cycles are measured in weeks, not years.

At Amazon, we believe in ownership at every level. As an SDE-I, you'll own the entire lifecycle of your code - from design through deployment and ongoing operations. This ownership mindset, combined with our commitment to operational excellence, ensures we deliver the highest quality solutions for our customers.

We're looking for curious minds who think big and want to define tomorrow's technology. At Amazon, you'll grow into the high-impact engineer you know you can be, supported by a culture of learning and mentorship. Every day brings exciting new challenges and opportunities for personal growth.
Key job responsibilities
• Collaborate and communicate effectively with experienced cross-disciplinary Amazonians to design, build, and operate innovative products and services that delight our customers, while participating in technical discussions to drive solutions forward.
• Design and develop scalable solutions using cloud-native architectures and microservices in a large distributed computing environment.
• Participate in code reviews and contribute to technical documentation.
• Build and maintain resilient distributed systems that are scalable, fault-tolerant, and cost-effective.
• Leverage and contribute to the development of GenAI and AI-powered tools to enhance development productivity while staying current with emerging technologies.
• Write clean, maintainable code following best practices and design patterns.
• Work in an agile environment practicing CI/CD principles while participating in operational responsibilities including on-call duties.
• Demonstrate operational excellence through monitoring, troubleshooting, and resolving production issues.
Basic Qualifications
- Experience with at least one general-purpose programming language such as Java, Python, C++, C#, Go, Rust, or TypeScript
- Experience with data structure implementation, basic algorithm development, and/or object-oriented design principles
- Currently has, or is in the process of obtaining a bachelor’s degree in Computer Science, Computer Engineering, Data Science, Information Systems, or related STEM fields
- Must be 18 years of age of older
Preferred Qualifications
- Experience from previous technical internship(s) or demonstrated project experience
- Experience with one or more of the following: AI tools for development productivity, Cloud platforms (preferably AWS), Database systems (SQL and NoSQL), Contributing to open-source projects, Version control systems, Debugging and troubleshooting complex systems
- Demonstrated ability to learn and adapt to new technologies quickly
- Basic understanding of software development lifecycle (SDLC)
- Strong problem-solving and analytical skills
- Excellent written and verbal communication skills
"""


class JobDesc(BaseModel):
    role: str
    required_skills: list[str]
    preferred_skills: list[str]
    minimum_experience: float | None
    educational_requirements: list[str]
    responsibilities: list[str]


jd_schema = JobDesc.model_json_schema()

message_system = {
    "role": "system",
    "content": f"""
    You are an expert HR Assistant. 
    Your job is to analyze job descriptions and extract structured information from them. 
    Return only valid JSON matching this schema: {jd_schema}

    IMPORTANT:
    1. Do not return the schema itself.
    2. Do not return fields like "properties", "title", or "type".
    3. Fill the schema with actual information extracted from the job description.
    4. If minimum experience is not mentioned, return null for that field.
    5. If information for a list is missing, return an empty list.
    6. Do not invent information. Only extract what is present in the job description.
""",
}

message_user = {
    "role": "user",
    "content": f"""
    Analyse the following job description: {job_description}
    """,
}

client = Groq(api_key=my_api_key)
model = "openai/gpt-oss-120b"
messages = [message_system, message_user]
response_format = {"type": "json_object"}

response = client.chat.completions.create(
    model=model, messages=messages, response_format=response_format
)
answer = response.choices[0].message.content

raw_json = answer

job_data = json.loads(raw_json)
job = JobDesc(**job_data)


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


class MatchResult(BaseModel):
    score: float
    details: dict


def read_pdf(filepath):
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text


def read_docx(filepath):
    document = Document(filepath)
    text = ""
    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text += paragraph.text + "\n"

        for table in document.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text += cell.text + "\n"
    return text


def read_resume(filepath):
    if filepath.suffix.lower() == ".pdf":
        return read_pdf(filepath)
    elif filepath.suffix.lower() == ".docx":
        return read_docx(filepath)
    else:
        return None


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

    response = client.chat.completions.create(
        model=model, messages=messages, response_format=response_format
    )
    raw_output = response.choices[0].message.content
    resume_data = json.loads(raw_output)
    resume = Resume(**resume_data)
    return resume


def final_score(job, resume):
    match_schema = MatchResult.model_json_schema()
    message = {
        "role": "user",
        "content": f"""
        You are an HR recruiter. 
        Compare the candidate's resume with the job description.

        JOB DESCRIPTION:
        {job.model_dump_json(indent=2)}

        CANDIDATE RESUME:
        {resume.model_dump_json(indent=2)}
        
        Return a JSON object matching this schema: {match_schema}

        Give me: 
        1. Candidate's name
        2. Matching skills
        3. Missing important skills
        4. Whether experience requirement is met
        5. Overall match percentage score (0-100) 
        6. A short final verdict

        Keep the response concise and easy to read.
        """,
    }
    messages = [message]
    response = client.chat.completions.create(
        model=model, messages=messages, response_format=response_format
    )
    result_json = response.choices[0].message.content
    result_data = json.loads(result_json)
    result = MatchResult(**result_data)
    return result


resume_folder = Path("resumes")
all_results = []

for file_path in resume_folder.iterdir():
    if file_path.suffix.lower() not in [".pdf", ".docx"]:
        print(f"Skipping unsupported file format: {file_path.name}")
        continue
    print("\n Processing resume:", file_path.name)
    resume_text = read_resume(file_path)
    parsed_resume = parse_resume(resume_text)
    time.sleep(5)
    result = final_score(job, parsed_resume)
    time.sleep(5)
    print("Score:", result.score)
    all_results.append(
        {"name": parsed_resume.name, "score": result.score, "details": result.details}
    )

all_results.sort(key=lambda candidate: candidate["score"], reverse=True)
top_2 = all_results[:2]

print("\nTop 2 Candidates:")
for candidate in top_2:
    print(candidate["name"], "-", candidate["score"], "%")
    print(candidate["details"])

# worst_2 = all_results[-2:]

# print("LOWEST 2 CANDIDATES")
# for candidate in worst_2:
# print(candidate["name"], "-", candidate["score"], "%")
# print(candidate["details"])
