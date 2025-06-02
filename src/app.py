import PyPDF2
import json
import streamlit as st
from utils import perplexity

st.set_page_config(layout="wide")
st.markdown("<h1 style='color:#4F8BF9; text-align:center;'>Job Search AI Agent</h1>", unsafe_allow_html=True)
st.markdown("<h3>Welcome to your personalized job search AI assistant!</h3>", unsafe_allow_html=True)
st.markdown("<p style='color:gray;'>Upload your resume and specify your job preferences to get tailored job listings.</p>", unsafe_allow_html=True)

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
    # User input for chat messages
    with st.sidebar:
        st.header("User Configuration")
        st.session_state.perplexity_token = st.text_input("Perplexity Token", type="password")
        st.divider()
        uploaded_file = st.file_uploader("Upload your resume for Job search", type=["pdf"], label_visibility="collapsed")

        if uploaded_file is not None:
            st.divider()
            st.write("**Resume Uploaded successfully:**")
            st.write(f"**File name:** {uploaded_file.name}")
            st.write(f"**File size:** {uploaded_file.size} bytes")
    if not st.session_state.perplexity_token:
        st.error("Please enter your Perplexity token in the sidebar to proceed.")
        return
    if not uploaded_file:
        st.warning("Please upload your resume to start the job search.")
        return

    if uploaded_file is not None and st.session_state.perplexity_token:
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            technology_list = perplexity.fetch_all_technologies(st.session_state.perplexity_token,
                                           f"""Fetch all top 10 technologies from the resume content. 
                                           Just give me the keywords of the technology like wordpress, Python, Java etc.. 
                                           Please give me in numbered list format.
                                             Do not give me any explanation or any other text.
                                           The content is : {text}""")
            technology_list = technology_list["choices"][0]["message"]["content"]
            st.write("**Technologies found in your resume:**")
            st.write(technology_list)

        except Exception as e:
            st.error(f"Could not read PDF: {e}")

        st.divider()
        job_preferences = st.text_area("Write your Job preferences : ", 
                                       height=200, 
                                       placeholder="e.g. I am looking for a job with remote work options with 50k salary per month.",
                                       help="Describe your ideal job, location, salary, and other preferences.")
        if st.button("Search Jobs", disabled=not job_preferences, 
                     help="Please enter your job preferences to search for jobs.",type="primary"):
            job_list = perplexity.fetch_all_jobs(st.session_state.perplexity_token,
                                           f"""I have experience in : {technology_list}.
                                           My preferences are  : {job_preferences}
                                           Search all job listings based on my preferences.
                                           Give me json response with the following keys:
                                           job_title, job_url, company_name, job_location, job_description.""")

            try:
                extracted_job_list = (job_list["choices"][0]["message"]["content"]).split("```json")[1].split("```")[0]
                extracted_job_list = json.loads(extracted_job_list)
                cols = st.columns(3)
                for i, job in enumerate(extracted_job_list):
                    with cols[i % 3]:
                        display_job(job)
            except Exception as e:
                for job in job_list["search_results"]:
                    st.write(job["title"])
                    st.write(job["url"])
                    st.divider()


if __name__ == "__main__":
    main()