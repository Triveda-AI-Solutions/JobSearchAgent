FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY src/ ./src/

COPY .env .env

# Command to run the FastAPI application
CMD export $(grep -v '^#' .env | xargs) && uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload