# perplexity-app

## Overview
This project is a FastAPI application designed to provide a robust and efficient API for various functionalities. FastAPI is a modern web framework for building APIs with Python 3.6+ based on standard Python type hints.

## Project Structure
```
perplexity-app
├── src
│   ├── main.py          # Entry point of the FastAPI application
│   └── __init__.py      # Marks the directory as a Python package
├── requirements.txt      # Lists the dependencies required for the project
├── Dockerfile            # Instructions to build a Docker image for the FastAPI application
└── README.md             # Documentation for the project
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd perplexity-app
   ```

2. **Install dependencies:**
   You can install the required dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   You can run the FastAPI application using the following command:
   ```bash
   uvicorn src.main:app --reload
   ```
   This will start the server at `http://127.0.0.1:8000`.

## Usage
Once the application is running, you can access the API documentation at `http://127.0.0.1:8000/docs`.

## Docker Instructions
To build and run the Docker container, use the following commands:

1. **Build the Docker image:**
   ```bash
   docker build -t perplexity-app .
   ```

2. **Run the Docker container:**
   ```bash
   docker run -d -p 8000:8000 perplexity-app
   ```

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.