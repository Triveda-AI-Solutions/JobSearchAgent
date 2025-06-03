from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi import Form
from pydantic import BaseModel
from typing import List, Optional
import requests
import json
import os
import dotenv
import PyPDF2
# Load environment variables from .env file
dotenv.load_dotenv()
PERPLEXITY_API_TOKEN = os.getenv("PERPLEXITY_API_TOKEN")

app = FastAPI()

# --- Models ---

class ModelRequest(BaseModel):
    model: str
    user_input: Optional[str] = None


class TechFormat(BaseModel):
    list_of_tech: List[str]

class Job(BaseModel):
    job_title: str
    company_name: str
    job_location: str
    job_url: str
    job_description: str

class JobListFormat(BaseModel):
    jobs: List[Job]

# --- Perplexity API Call ---

PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"

def model_call(model: str, user_input: str, response_class: BaseModel):
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
    return {"message": "Welcome to the FastAPI application!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "query": q}


@app.post("/jobs", response_model=JobListFormat)
def fetch_jobs_from_prompt(request: ModelRequest):
    """
    Fetch all job listings based on the user's search preferences.
    model: The model to use for the request. Allowed values are "sonar", "sonar-pro", "llama-3.1-sonar-huge-128k-online"
    user_input: The user's input text containing job search preferences.
    """
    return model_call(request.model, 
                      f"""My skills are : {request.user_input}
                         Search all job listings based on my preferences and skills.
                         Please give me the top 10 job listings based on my skills""", 
                      response_class=JobListFormat)


@app.post("/from_pdf_resume", response_model=JobListFormat)
def fetch_jobs_from_pdf(
    model: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Convert a PDF file to text.
    file: The PDF file in binary format.
    """
    try:
        reader = PyPDF2.PdfReader(file.file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    technology_list = model_call(model, 
                      f"""Fetch all top 10 technologies from the resume content. 
                         Just give me the keywords of the technology like wordpress, Python, Java etc.. 
                         Please give me the top 10 technologies from the resume.
                         Do not give me any explanation or any other text.
                       The content is : {text}""",
                      response_class=TechFormat)
    request = ModelRequest(model=model, user_input=", ".join(technology_list["list_of_tech"]))
    job_list = fetch_all_jobs(request)
    return job_list