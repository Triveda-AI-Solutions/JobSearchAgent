import requests
import json
import streamlit as st
url = "https://api.perplexity.ai/chat/completions"

@st.cache_data(show_spinner="Fetching user technology listings", ttl=3600)
def fetch_all_technologies(token, user_input):
    """
    Function to fetch all technologies from the resume content using Perplexity AI.
    This function sends a request to the Perplexity API and returns the list of technologies.
    """
    return model_call(token,user_input)

@st.cache_data(show_spinner="Searching all job listings", ttl=3600)
def fetch_all_jobs(token, user_input):
    """
    Function to fetch all job listings based on the user's search preferences.
    This function sends a request to the Perplexity API and returns the list of jobs.
    """
    return model_call(token, user_input) 

@st.cache_data
def model_call(token, user_input):
    """
    Function to call the Perplexity AI model with a specific payload and headers.
    This function sends a POST request to the Perplexity API and returns the response.
    """
    # Define the payload and headers for the API request
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "Be precise and concise."
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    return response.json() if response.status_code == 200 else {"error": f"Request failed with status code {response.status_code}"}