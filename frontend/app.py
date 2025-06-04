import PyPDF2
import streamlit as st
import requests

# Set Streamlit page configuration and custom headers
st.set_page_config(layout="wide")
st.markdown("<h1 style='color:#4F8BF9; text-align:center;'>Job Search AI Agent</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>Introducing AI-Powered Job Search Engine</h3>", unsafe_allow_html=True)

# Base URL for the backend API
API_BASE_URL = "http://0.0.0.0:8000"

def fetch_all_jobs(model, user_input):
    """
    Sends a POST request to the backend to fetch jobs based on user input and selected model.
    Args:
        model (str): The AI model to use for job search.
        user_input (str): User's job preferences.
    Returns:
        dict: JSON response containing job listings.
    """
    response = requests.post(
        f"{API_BASE_URL}/jobs",
        json={"model": model,"user_input": user_input},
        timeout=60
    )
    response.raise_for_status()
    return response.json()

def fetch_jobs_from_pdf(model, file_obj):
    """
    Sends a POST request to the backend to fetch jobs based on the uploaded PDF resume.
    Args:
        model (str): The AI model to use for job search.
        file_obj (file-like): Uploaded PDF file object.
    Returns:
        dict: JSON response containing job listings.
    """
    files = {
        "file": (file_obj.name, file_obj, "application/pdf"),
    }
    data = {
        "model": model,
    }
    response = requests.post(
        f"{API_BASE_URL}/from_pdf_resume",
        data=data,
        files=files,
        timeout=60
    )
    response.raise_for_status()
    return response.json()

def display_job(job):
    """
    Renders job details in a styled card format using Streamlit markdown.
    Args:
        job (dict): Dictionary containing job details.
    """
    st.markdown(
        f"""
        <div style="border:2px solid #4F8BF9; border-radius:10px; padding:16px; margin-bottom:16px; background-color:#f7fafd;">
            <h4 style="margin-top:0;">{job['job_title']}</h4>
            <p><strong>Company Name:</strong> {job['company_name']}</p>
            <p><strong>Job Location:</strong> {job['job_location']}</p>
            <p><strong>Job Status:</strong> {requests.get(job['job_url'], timeout=5).status_code}</p>
            <p><strong>Job URL:</strong> <a href="{job['job_url']}" target="_blank">{job['job_url']}</a></p>
            <p><strong>Job Description:</strong> {job['job_description']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def main():
    """
    Main function to render the Streamlit UI and handle user interactions.
    Allows users to search for jobs by entering preferences or uploading a resume.
    Displays job results in a grid layout.
    """
    job_list = {}
    # Layout for job preference input and model selection
    col1, col2 = st.columns([3, 1])
    with col1:
        job_preferences = st.text_area("Ask Like", 
                                    height=100, 
                                    placeholder="Looking for a job in delhi 7 years exp 10 LPA.",
                                    help="Describe your ideal job, location, salary, and other preferences.")
        model_options = ["sonar", "sonar-pro", "llama-3.1-sonar-huge-128k-online"]
        selected_model = st.pills(" ", model_options, selection_mode="single", default="sonar")
    with col2:
        # Button to search jobs based on preferences
        if st.button("Search Jobs", disabled=not job_preferences, 
                    help="Please enter your job preferences to search for jobs.",type="primary"):
            job_list = fetch_all_jobs(model=selected_model,
                                        user_input=job_preferences)
            
    # Divider with "OR" for alternative resume upload option
    st.markdown("""
                <div style="display: flex; align-items: center; margin: 24px 0;">
                <hr style="flex: 1; border: none; border-top: 2px solid #ccc; margin: 0;">
                <span style="padding: 0 16px; font-weight: bold; color: #333;">OR</span>
                <hr style="flex: 1; border: none; border-top: 2px solid #ccc; margin: 0;">
                </div>
                """, unsafe_allow_html=True)

    # Layout for resume upload
    col3, col4 = st.columns([3, 1])
    with col3:
        uploaded_file = st.file_uploader("Upload your resume for Job search", type=["pdf"], label_visibility="collapsed")

    if uploaded_file is not None:
        st.write("**Resume Uploaded successfully:**")
        
    with col4:
        # Button to search jobs based on uploaded resume
        if st.button("Search Jobs", disabled=not uploaded_file,
                    help="Please upload your resume to search for jobs.", type="primary"):
            job_list = fetch_jobs_from_pdf(model=selected_model, file_obj=uploaded_file)
    # Display job results in a 3-column grid
    if job_list != {}:
        cols = st.columns(3)
        for i, job in enumerate(job_list["jobs"]):
            with cols[i % 3]:
                display_job(job)

# Entry point for the Streamlit app
if __name__ == "__main__":
    main()