# Job Search Backend (FastAPI)

## Overview
This project is a FastAPI backend for the Job Search AI Agent. It provides API endpoints for extracting technologies from resumes and searching for jobs using Perplexity AI.

## Project Structure
```
backend/
├── Dockerfile
├── README.md
├── requirements.txt
└── src/
    ├── __init__.py
    └── main.py      # FastAPI backend for job and technology extraction
```

## Setup Instructions

### Local Setup

1. **Create and activate a new environment:**
   ```bash
   conda create -n job_search_agent python=3.12
   conda activate job_search_agent
   ```

2. **Install backend dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the FastAPI backend:**
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```
   The server will start at `http://0.0.0.0:8000`.

### Docker

1. **Build the Docker image:**
   ```bash
   docker build -t job_search_backend .
   ```

2. **Run the backend container:**
   ```bash
   docker run -p 8000:8000 job_search_backend
   ```

## Usage

- Access the API documentation at `http://localhost:8000/docs` after starting the server.
- Main endpoints:
  - `POST /technologies` — Extract technologies from resume content.
  - `POST /jobs` — Search for jobs based on user preferences.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.