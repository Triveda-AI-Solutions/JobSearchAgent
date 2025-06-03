from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import requests
import json

app = FastAPI()

# --- Models ---

class ModelRequest(BaseModel):
    model: str
    token: str
    user_input: str

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

def model_call(model: str, token: str, user_input: str, response_class: BaseModel):
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
        "Authorization": f"Bearer {token}",
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

@app.post("/technologies", response_model=TechFormat)
def fetch_all_technologies(request: ModelRequest):
    """
    Fetch all technologies from the resume content using Perplexity AI.
    """
    return model_call(request.model, request.token, request.user_input, response_class=TechFormat)

@app.post("/jobs", response_model=JobListFormat)
def fetch_all_jobs(request: ModelRequest):
    """
    Fetch all job listings based on the user's search preferences.
    """
    return model_call(request.model, request.token, request.user_input, response_class=JobListFormat)