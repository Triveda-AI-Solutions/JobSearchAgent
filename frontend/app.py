import PyPDF2
import streamlit as st
import requests

st.set_page_config(layout="wide")
st.markdown("<h1 style='color:#4F8BF9; text-align:center;'>Job Search AI Agent</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>Introducing AI-Powered Job Search Engine</h3>", unsafe_allow_html=True)

API_BASE_URL = "http://0.0.0.0:8000"

def fetch_all_jobs(model, user_input):
    response = requests.post(
        f"{API_BASE_URL}/jobs",
        json={"model": model,"user_input": user_input},
        timeout=60
    )
    response.raise_for_status()
    return response.json()

def fetch_all_technologies(model, user_input):
    response = requests.post(
        f"{API_BASE_URL}/technologies",
        json={"model": model,  "user_input": user_input},
        timeout=60
    )
    response.raise_for_status()
    return response.json()


def display_job(job):
    """
    Function to display job details in the Streamlit app.
    """
    st.markdown(
        f"""
        <div style="border:2px solid #4F8BF9; border-radius:10px; padding:16px; margin-bottom:16px; background-color:#f7fafd;">
            <h4 style="margin-top:0;">{job['job_title']}</h4>
            <p><strong>Company Name:</strong> {job['company_name']}</p>
            <p><strong>Job Location:</strong> {job['job_location']}</p>
            <p><strong>Job URL:</strong> <a href="{job['job_url']}" target="_blank">{job['job_url']}</a></p>
            <p><strong>Job Description:</strong> {job['job_description']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def main():
    job_list = {}
    col1, col2 = st.columns([3, 1])
    with col1:
        job_preferences = st.text_area("Ask Like", 
                                    height=100, 
                                    placeholder="Looking for a job in delhi 7 years exp 10 LPA.",
                                    help="Describe your ideal job, location, salary, and other preferences.")
        model_options = ["sonar", "sonar-pro", "llama-3.1-sonar-huge-128k-online"]
        selected_model = st.pills(" ", model_options, selection_mode="single", default="sonar")
    with col2:
        if st.button("Search Jobs", disabled=not job_preferences, 
                    help="Please enter your job preferences to search for jobs.",type="primary"):
            job_list = fetch_all_jobs(model=selected_model,
                                        user_input=job_preferences)
            
    st.markdown("""
                <div style="display: flex; align-items: center; margin: 24px 0;">
                <hr style="flex: 1; border: none; border-top: 2px solid #ccc; margin: 0;">
                <span style="padding: 0 16px; font-weight: bold; color: #333;">OR</span>
                <hr style="flex: 1; border: none; border-top: 2px solid #ccc; margin: 0;">
                </div>
                """, unsafe_allow_html=True)

    col3, col4 = st.columns([3, 1])
    technology_list = None
    with col3:
        uploaded_file = st.file_uploader("Upload your resume for Job search", type=["pdf"], label_visibility="collapsed")

    if uploaded_file is not None:
        st.write("**Resume Uploaded successfully:**")
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
        except Exception as e:
            st.error(f"Could not read PDF: {e}")

        technology_list = fetch_all_technologies(model=selected_model,
                                        user_input=text
                                        )
        
        with st.expander("Technologies in your resume", expanded=False):
            for t in technology_list["list_of_tech"]:
                st.markdown(f"- {t}")


    with col4:
        if st.button("Search Jobs", disabled=not technology_list, 
                    help="Please upload your resume to search for jobs.",type="primary"):
            job_list = fetch_all_jobs(model=selected_model,
                                        user_input=( ", ".join(technology_list["list_of_tech"])))
    if job_list != {}:
        cols = st.columns(3)
        for i, job in enumerate(job_list["jobs"]):
            with cols[i % 3]:
                display_job(job)


if __name__ == "__main__":
    main()