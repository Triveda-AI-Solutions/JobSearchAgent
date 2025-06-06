from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form, Body
from pydantic import BaseModel
from typing import List, Optional
import requests
import json
import os
import dotenv
import PyPDF2
from docx import Document
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file
dotenv.load_dotenv()
PERPLEXITY_API_TOKEN = os.getenv("PERPLEXITY_API_TOKEN")

app = FastAPI()

# Enable CORS for all origins (for development/demo purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---

class ModelRequest(BaseModel):
    """
    Request model for job search prompts.
    """
    model: str = "sonar-pro"
    user_input: Optional[str] = "I am looking for a Job. I am open to all job types. "
    type: Optional[str] = "prompt"

class TechFormat(BaseModel):
    """
    Response model for extracted technologies from resume.
    """
    list_of_tech: List[str]

class Job(BaseModel):
    """
    Model representing a single job listing.
    """
    job_title: str
    company_name: str
    job_location: str
    job_url: str
    salary: str
    skills: List[str]
    job_type: str
    education_qualification: str
    job_description: str

class JobListFormat(BaseModel):
    """
    Response model for a list of job listings.
    """
    output_text: Optional[str] = None
    technology_list: Optional[List[str]] = None
    jobs: List[Job]
    jobs_count: int
    
# Ensure the directory for storing resumes exists
from datetime import datetime 
if not os.path.exists("all_resumes"):
    os.makedirs("all_resumes")

# --- Perplexity API Call Helper ---

PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"

def perplexity_model_call(model: str, user_input: str, response_class: BaseModel):
    """
    Calls the Perplexity API with the given model and user input.
    Returns the response parsed as the specified response_class.
    """
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Be precise and concise. Do not give any explanation or any other text."
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"schema": response_class.model_json_schema()}
        }
    }
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(PERPLEXITY_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return json.loads(data["choices"][0]["message"]["content"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- FastAPI Endpoints ---

@app.post("/fetch_jobs", response_model=JobListFormat)
async def fetch_jobs(
    model: str = Form("sonar-pro"),
    user_input: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    """
    Fetch job listings based on user prompt or uploaded resume.
    - If 'file' is provided, extract technologies from resume and search jobs.
    - If 'user_input' is provided, search jobs based on prompt.
    """
    if file:
        try:
            content_type = file.content_type
            text = ""
            file_bytes = await file.read()
            file_stream = BytesIO(file_bytes)
            if content_type == "application/pdf":
                reader = PyPDF2.PdfReader(file_stream)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                file_extension = ".pdf"
            elif content_type in [
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/msword"
            ]:
                doc = Document(file_stream)
                for para in doc.paragraphs:
                    text += para.text + "\n"
                file_extension = ".docx"
            else:
                raise HTTPException(status_code=400, detail="Unsupported file type")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        # Save the uploaded resume
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_location = f"all_resumes/{file.filename}_{timestamp}{file_extension}"
        with open(file_location, "wb") as f_out:
            f_out.write(file_bytes)
        # Extract top technologies from resume text
        technology_list = perplexity_model_call(
            model,
            f"""Fetch all top 10 technologies from the resume content. 
               Just give me the keywords of the technology like wordpress, Python, Java etc.. 
               Please give me the top 10 technologies from the resume.
               Do not give me any explanation or any other text.
               The content is : {text}""",
            response_class=TechFormat
        )["list_of_tech"]
        technology_string = ", ".join(technology_list)
        pre_text = f"I am looking for a Job. My technical skills are : {technology_string}."
        output_text = f"Based on your technologies from the resume: {technology_string}"
    if user_input and not file:
        pre_text = f"My request is : {user_input}."
        output_text = f"Based on your request: {user_input}"
        technology_list = []
    if user_input and file:
        pre_text = pre_text + f" My request is : {user_input}."
        output_text = f"Based on your request: {user_input} and technologies from the resume: {technology_string}"
    if not user_input and not file:
        raise HTTPException(status_code=400, detail="Either user_input or file must be provided.")
    jobs = perplexity_model_call(
        model,
        f"""{pre_text}
           Search all job listings based on my preferences and skills.
           I need the following details for each job:
           job_title: str
           company_name: str
           job_location: str
           job_url: str
           salary: str
           skills: List[str]
           job_type: str
           education_qualification: str
           job_description: str
           Please give me any other top 5 job listings based on my skills.""",
        response_class=JobListFormat
    )["jobs"]

    return {
        "output_text": output_text,
        "technology_list": technology_list,
        "jobs": jobs, 
        "jobs_count": len(jobs)
        }


@app.post("/question_on_jobs", response_model=JobListFormat)
async def question_on_jobs(
    model: str = Form("sonar-pro"),
    user_input: str = Form(None),
    known_jobs: List[Job] = Body(None),
):
    output_text = f"Based on your request: {user_input}" 
    jobs = perplexity_model_call(
        model,
        f"""I already know about these jobs: {known_jobs}.
            My request is : {user_input}
            Give me a list of jobs that match my request.""",
        response_class=JobListFormat
    )["jobs"]

    return {"output_text": output_text,
            "jobs": jobs,
            "jobs_count": len(jobs)
            }


@app.get("/get_uploaded_resumes_list")
async def get_uploaded_resumes():
    """
    Get a list of all uploaded resumes stored on the server.
    """
    try:
        files = os.listdir("all_resumes")
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))