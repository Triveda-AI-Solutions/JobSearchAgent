JOB_SEARCH_PROMPT = """
My skills are: {skills}
Based on my skills and preferences, search for the top relevant job listings.
For each job, provide:
- job_title
- company_name
- job_location
- job_url (must be a valid URL)
- job_description

Return only a JSON array of jobs, with all fields filled.
"""

TECH_EXTRACTION_PROMPT = """
Analyze the following resume content and extract the top 10 most relevant technologies, programming languages, frameworks, or tools mentioned.
Return only a JSON array of technology keywords (e.g., ["Python", "Java", "WordPress"]).
Do not include any explanation or extra text—only the JSON array.
Resume content:
{resume_text}
"""