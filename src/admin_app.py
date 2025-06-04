import streamlit as st
import os
import dotenv
dotenv.load_dotenv()
PASSWORD = os.getenv("st_admin_password")

def check_password():
    def password_entered():
        if st.session_state["password"] == PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Remove password from session state
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if not check_password():
    st.stop()

# Set the folder path
RESUMES_FOLDER = os.path.join(os.path.dirname(__file__), "all_resumes")

st.title("Admin Dashboard")

if not os.path.exists(RESUMES_FOLDER):
    st.error(f"Folder not found: {RESUMES_FOLDER}")
else:
    files = os.listdir(RESUMES_FOLDER)
    if not files:
        st.info("No files found in the folder.")
    else:
        st.write("### Uploaded Resumes:")
        for file in files:
            st.write(f"- {file}")