# Job Search AI Agent

This project is an AI-powered job search dashboard built using Streamlit. It allows users to search for jobs based on their preferences or by uploading their resume, leveraging Perplexity AI for intelligent job and technology extraction.

## Project Structure

```
job_search_agent/
├── backend/
│   ├── Dockerfile
│   ├── README.md
│   ├── requirements.txt
│   └── src/
│       ├── __init__.py
│       └── main.py      # FastAPI backend for job and technology extraction
├── frontend/
│   ├── app.py           # Main entry point for the Streamlit application
│   ├── requirements.txt
```

## Setup Instructions

### Backend

#### Option 1: Local Setup

1. **Create and activate a new environment:**
   ```
   conda create -n job_search_agent python=3.12
   conda activate job_search_agent
   ```

2. **Install backend dependencies:**
   ```
   pip install -r backend/requirements.txt
   ```

3. **Set up environment variables:**
   - Create a `.env` file in the `backend/` directory with your Perplexity API token:
     ```
     PERPLEXITY_API_TOKEN=your_token_here
     ```

4. **Run the FastAPI backend:**
   ```
   uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Option 2: Docker

1. **Build the Docker image:**
   ```
   docker build -t job_search_backend ./backend
   ```

2. **Run the backend container:**
   ```
   docker run --env-file backend/.env -p 8000:8000 job_search_backend
   ```

### Frontend

1. **Install frontend dependencies:**
   ```
   pip install -r frontend/requirements.txt
   ```

2. **Run the Streamlit application:**
   ```
   streamlit run frontend/app.py
   ```

## Features

- Search for jobs by entering preferences (location, experience, salary, etc.)
- Upload your resume (PDF) to extract top technologies and search for relevant jobs
- Uses Perplexity AI for intelligent extraction and job search
- Modern, user-friendly Streamlit interface

## Usage

- Access the API documentation at `http://localhost:8000/docs` after starting the backend server.
- Main endpoints:
  - `POST /technologies` — Extract technologies from resume content.
  - `POST /jobs` — Search for jobs based on user preferences.

### Example API Request

**POST /technologies**
```json
{
  "model": "sonar",
  "user_input": "Resume content here..."
}
```

**POST /jobs**
```json
{
  "model": "sonar",
  "user_input": "Looking for a job in Berlin, 5 years experience, Python developer."
}
```

---

Feel free to explore and modify the code to suit your needs!