import os, time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("API key not found.")

client = Groq(api_key=my_api_key)
model = "openai/gpt-oss-20b"

JD = """
We are hiring a Python Backend Developer.

Requirements:
- Strong Python Knowledge
- FastAPI or Django
- PostgreSQL
- Docker
- AWS
- REST APIs
- 2+ years of experience
"""

RESUME = """
Name: Rahul Sharma

Experience:
3 years as a Software Developer.

Skills:
Python, FastAPI, MySQL, Docker,
REST APIs, Git

Projects:
Built a food delivery backend using
FastAPI and MySQL.

Deployed applications using Docker.
"""


def ask_llm(system_prompt, user_prompt):
    message_system = {"role": "system", "content": system_prompt}
    message_user = {"role": "user", "content": user_prompt}
    messages = [message_system, message_user]

    response = client.chat.completions.create(model=model, messages=messages)
    answer = response.choices[0].message.content
    return answer


def step1_resume_extract():
    print("-" * 100)
    print("STEP - 1: Extracting skills from the candidate's resume")
    # extract skills from resume
    system_prompt = """
    You are a professional HR assistant. Extract skills from the candidate's resume provided. Only return the skills, no other information. Do not invent any skills by yourself.
    
    Output Format: The output must only contain comma separated skills and no other filler information. 
    """
    user_prompt = f"Extract the skills from this resume {RESUME}"
    return ask_llm(system_prompt, user_prompt)


def step2_jd_extract():
    # extract skills from jd
    print("-" * 100)
    print("STEP - 2: Extracting skills from the job description")
    system_prompt = """
    You are a professional HR assistant. Extract skills from the job description provided. Only return the skills, no other information. Do not invent any skills by yourself.
    
    Output Format: The output must only contain comma separated skills and no other filler information.
    """
    user_prompt = f"Extract the skills from this job description {JD}"
    return ask_llm(system_prompt, user_prompt)


def step3_match_skills(candidate, jd):
    print("-" * 100)
    print(
        "STEP - 3: Matching both skills and generating the final score and my verdict."
    )
    system_prompt = f"""
    You are an HR Assistant. Compare the skills of the candidate and the skills from the job description and generate a final score between 1 and 100. Also produce a short verdict whether the candidate is a good fit for this role or not.
    """
    user_prompt = f"""
    Compare and match the skills:
    Candidate: {candidate}
    Job Description: {jd}
    """

    return ask_llm(system_prompt, user_prompt)


candidate = step1_resume_extract()
print(candidate)
time.sleep(2)
jd = step2_jd_extract()
print(jd)
time.sleep(2)
score = step3_match_skills(candidate, jd)
print(score)
