# Job Search Agent (FastAPI + Streamlit)

## Overview
This project consists of a FastAPI backend and a Streamlit frontend for the Job Search AI Agent. It provides API endpoints for extracting technologies from resumes and searching for jobs using Perplexity AI.

## Project Structure
```
.
├── Dockerfile
├── README.md
├── frontend/
│   ├── app.py              # Streamlit frontend
│   └── requirements.txt
└── src/
    ├── __init__.py
    ├── main.py             # FastAPI backend for job and technology extraction
    ├── requirements.txt
    └── all_resumes/
        └── wordpress_resume.pdf
```

## Setup Instructions

### Local Setup

#### Backend

1. **Create and activate a new environment:**
   ```bash
   conda create -n job_search_agent python=3.9
   conda activate job_search_agent
   ```

2. **Install backend dependencies:**
   ```bash
   pip install -r src/requirements.txt
   ```

3. **Set up environment variables:**
   - Create a `.env` file in the root directory with your Perplexity API token:
     ```
     PERPLEXITY_API_TOKEN=your_token_here
     ```

4. **Run the FastAPI backend:**
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```
   The server will start at `http://0.0.0.0:8000`.

#### Frontend

1. **Install frontend dependencies:**
   ```bash
   pip install -r frontend/requirements.txt
   ```

2. **Run the Streamlit frontend:**
   ```bash
   streamlit run frontend/app.py
   ```

### Docker

1. **Build the Docker image:**
   ```bash
   docker build -t job_search_backend .
   ```

2. **Run the backend container:**
   ```bash
   docker run --env-file .env -p 8000:8000 job_search_backend
   ```

## Usage

- Access the API documentation at `http://localhost:8000/docs` after starting the backend server.
- Main endpoints:
  - `POST /jobs` — Search for jobs based on user preferences.
  - `POST /jobs_from_resume` — Search for jobs by uploading a resume (PDF or DOCX).
  - `GET /get_uploaded_resumes_list` — List all uploaded resumes.

### Example API Requests

**POST /jobs**
```json
{
  "model": "sonar",
  "user_input": "Looking for a job in Berlin, 5 years experience, Python developer."
}
```

**POST /jobs_from_resume** (multipart/form-data)
- Fields:
  - `model`: e.g., "sonar"
  - `file`: PDF or DOCX resume file

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.