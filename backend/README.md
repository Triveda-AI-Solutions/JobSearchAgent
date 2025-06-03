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
   pip install -r backend/requirements.txt
   ```

3. **Set up environment variables:**
   - Create a `.env` file in the `backend/` directory with your Perplexity API token:
     ```
     PERPLEXITY_API_TOKEN=your_token_here
     ```

4. **Run the FastAPI backend:**
   ```bash
   uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
   ```
   The server will start at `http://0.0.0.0:8000`.

### Docker

1. **Build the Docker image:**
   ```bash
   docker build -t job_search_backend ./backend
   ```

2. **Run the backend container:**
   ```bash
   docker run --env-file backend/.env -p 8000:8000 job_search_backend
   ```

## Usage

- Access the API documentation at `http://localhost:8000/docs` after starting the server.
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

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.