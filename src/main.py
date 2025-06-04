from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
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
    model: str
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
    jobs: List[Job]

# --- Perplexity API Call Helper ---

PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"

def model_call(model: str, user_input: str, response_class: BaseModel):
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

@app.get("/")
def read_root():
    """
    Root endpoint for health check.
    """
    return {"message": "Welcome to the JobSearchAgent!"}

@app.post("/jobs", response_model=JobListFormat)
async def fetch_jobs_from_prompt(request: ModelRequest):
    """
    Fetch job listings based on the user's search preferences.
    - model: The model to use for the request.
    - user_input: The user's input text containing job search preferences.
    """
    pre_text = "My request is : " if request.type == "prompt" else "I am looking for a Job. My technical skills are : "
    return model_call(
        request.model, 
        f"""{pre_text} {request.user_input}
           Search all job listings based on my preferences and skills.
           Please give me the top 50 job listings based on my skills""", 
        response_class=JobListFormat
    )

# Ensure the directory for storing resumes exists
from datetime import datetime 
if not os.path.exists("all_resumes"):
    os.makedirs("all_resumes")

async def upload_resume(
    file: UploadFile = File(...)
):
    """
    Upload a resume file to the server.
    - file: The resume file in binary format.
    Returns the filename and storage location.
    """
    try:
        content_type = file.content_type
        if content_type == "application/pdf":
            file_extension = ".pdf"
        elif content_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            file_extension = ".docx"
        else:
            file_extension = ""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_location = f"all_resumes/{file.filename}_{timestamp}{file_extension}"
        with open(file_location, "wb") as f:
            f.write(await file.read())
        return {"filename": file.filename, "location": file_location}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/jobs_from_resume", response_model=JobListFormat)
async def fetch_jobs_from_resume(
    model: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Extracts text from a PDF or DOCX resume, identifies top technologies,
    and fetches job listings based on those technologies.
    - model: The model to use for the request.
    - file: The resume file in binary format.
    """
    try:
        content_type = file.content_type
        text = ""
        file_bytes = await file.read()
        file_stream = BytesIO(file_bytes)
        if content_type == "application/pdf":
            reader = PyPDF2.PdfReader(file_stream)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif content_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            doc = Document(file_stream)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # Save the uploaded resume
    upload_resume(file=file)
    # Extract top technologies from resume text
    technology_list = model_call(
        model, 
        f"""Fetch all top 10 technologies from the resume content. 
           Just give me the keywords of the technology like wordpress, Python, Java etc.. 
           Please give me the top 10 technologies from the resume.
           Do not give me any explanation or any other text.
           The content is : {text}""",
        response_class=TechFormat
    )
    # Use extracted technologies to fetch job listings
    request = ModelRequest(model=model, user_input=", ".join(technology_list["list_of_tech"]), type="tech_list")
    job_list = await fetch_jobs_from_prompt(request)
    return job_list

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