
import logging
import streamlit as st
import requests
import re
from io import BytesIO
import os
from dotenv import load_dotenv
import PyPDF2
import boto3
from urllib.parse import urlparse
 
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
 
# Load environment variables
load_dotenv()
BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000')
 
# Initialize session state for persistence across reruns
for key, default in [
    ("resume_markdown_url", ""),
    ("github_markdown_url", ""),
    ("matches", []),
    ("processing_jobs", set()),
    ("job_results", {})
]:
    if key not in st.session_state:
        st.session_state[key] = default
 
# --- Helper Functions ---
 
def is_valid_github_url(url: str) -> bool:
    url = url.lstrip('@')
    pattern = r'^https?://(?:www\.)?github\.com/[A-Za-z0-9-]+(?:/[A-Za-z0-9-_]+)*/?$'
    if not re.match(pattern, url):
        return False
    try:
        return bool(url.split('github.com/')[1].split('/')[0])
    except:
        return False
 
def validate_pdf(pdf_file) -> (bool, str):
    try:
        content = pdf_file.read()
        pdf = PyPDF2.PdfReader(BytesIO(content))
        if not pdf.pages:
            return False, "Empty PDF"
        pdf_file.seek(0)
        return True, "Valid PDF"
    except Exception as e:
        return False, f"Invalid PDF: {e}"
 
def process_github_profile(github_url: str) -> (bool, dict):
    try:
        resp = requests.post(f"{BACKEND_API_URL}/api/process-github", json={"url": github_url})
        if resp.status_code == 200:
            return True, resp.json()
        return False, resp.text
    except Exception as e:
        return False, str(e)
 
def get_job_matches(profile: dict) -> (bool, dict):
    try:
        resp = requests.post(f"{BACKEND_API_URL}/api/match-jobs", json={"profile": profile})
        if resp.status_code == 200:
            return True, resp.json()
        try:
            return False, resp.json()
        except:
            return False, resp.text
    except Exception as e:
        return False, str(e)
 
def fetch_from_s3(s3_url: str) -> str:
    try:
        parsed = urlparse(s3_url)
        bucket = parsed.netloc
        key = parsed.path.lstrip('/')
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket=bucket, Key=key)
        return obj['Body'].read().decode('utf-8')
    except Exception as e:
        logger.error(f"S3 fetch error: {e}")
        return ""
 
def fetch_full_job_details(job_id: str) -> dict:
    try:
        resp = requests.get(f"{BACKEND_API_URL}/api/job-details/{job_id}")
        if resp.status_code == 200:
            return resp.json().get("metadata", {})
    except:
        pass
    return {}
 
def format_bullet_section(title: str, items: list) -> str:
    if not items:
        return f"#### {title}\n_No information provided._"
    bullets = "\n".join(f"- {itm.strip().capitalize()}" for itm in items if itm.strip())
    return f"#### {title}\n{bullets}"
 
# --- Callbacks ---
 
def handle_generate_feedback(job_id: str):
    st.session_state.processing_jobs.add(job_id)
    resume_md = st.session_state.resume_markdown_url
    github_md = st.session_state.github_markdown_url
 
    if not resume_md or not github_md:
        st.session_state.job_results[job_id] = {
            "success": False,
            "result": "Missing resume or GitHub markdown URL"
        }
        st.session_state.processing_jobs.discard(job_id)
        return
 
    # Fetch profile markdown
    resume_txt = fetch_from_s3(resume_md)
    github_txt = fetch_from_s3(github_md)
    profile_text = f"RESUME:\n{resume_txt}\n\nGITHUB:\n{github_txt}"
 
    # Fetch job description
    jd = fetch_full_job_details(job_id)
    job_desc = "\n".join([
        f"Title: {jd.get('job_title','')}",
        f"Company: {jd.get('company','')}",
        "Responsibilities:\n" + jd.get('responsibilities',''),
        "Qualifications:\n" + jd.get('qualifications','')
    ])
 
    payload = {
        "resume_markdown_url": resume_md,
        "github_markdown_url": github_md,
        "job_id": job_id,
        "profile_text": profile_text,
        "job_description": job_desc
    }
 
    try:
        resp = requests.post(f"{BACKEND_API_URL}/api/generate-feedback-cover-letter", json=payload)
        resp.raise_for_status()
        st.session_state.job_results[job_id] = {
            "success": True,
            "result": resp.json()
        }
    except Exception as e:
        logger.error(f"Feedback API error: {e}")
        st.session_state.job_results[job_id] = {
            "success": False,
            "result": str(e)
        }
    finally:
        st.session_state.processing_jobs.discard(job_id)
 
# --- UI Components ---
 
def display_job_match(match: dict):
    job_id = match.get("job_id")
    meta = fetch_full_job_details(job_id)
    title = match.get("job_title", "N/A")
    company = meta.get("company", "N/A")
    score = match.get("similarity_score", 0.0)
 
    with st.container():
        with st.expander(f"🔍 {title} @ {company} — Score: {score:.2f}"):
            st.markdown(f"""
            - **Location:** {meta.get('location','N/A')}
            - **Type:** {meta.get('job_type','N/A')}
            - **Mode:** {meta.get('work_mode','N/A')}
            - **Seniority:** {meta.get('seniority','N/A')}
            - **Experience:** {meta.get('experience','N/A')}
            """)
            st.markdown("---")
            st.markdown(format_bullet_section("Responsibilities", meta.get("responsibilities","").split(",")))
            st.markdown(format_bullet_section("Qualifications", meta.get("qualifications","").split(",")))
            st.markdown(format_bullet_section("Matching Skills", match.get("skills", [])))
 
            processing = job_id in st.session_state.processing_jobs
            has_res   = job_id in st.session_state.job_results
 
            if not processing and not has_res:
                st.button(
                    "📝 Generate Cover Letter & Feedback",
                    key=f"btn_{job_id}",
                    on_click=handle_generate_feedback,
                    args=(job_id,)
                )
 
            if processing:
                st.info("Generating... please wait.")
                st.spinner("⏳")
 
            if has_res:
                jr = st.session_state.job_results[job_id]
                if jr["success"]:
                    out = jr["result"]
                    cl = out.get("cover_letter", "")
                    fb = out.get("improvement_suggestions", "")
                    if cl:
                        st.markdown("### 📄 Cover Letter")
                        st.write(cl)
                    if fb:
                        st.markdown("### 💡 Feedback & Suggestions")
                        st.write(fb)
                    if st.button("🔄 Regenerate", key=f"regen_{job_id}"):
                        st.session_state.job_results.pop(job_id, None)
                        handle_generate_feedback(job_id)
                else:
                    st.error(f"Error: {jr['result']}")
                    if st.button("🔄 Retry", key=f"retry_{job_id}"):
                        st.session_state.job_results.pop(job_id, None)
                        handle_generate_feedback(job_id)
 
# --- Main App ---
 
def main():
    st.set_page_config(page_title="SkillMatch AI", page_icon="🤖", layout="centered")
    st.title("SkillMatch AI – Resume & GitHub Job Matcher")
    st.markdown("Upload your resume (PDF) and GitHub URL to find jobs and generate tailored cover letters & feedback.")
 
    github_url = st.text_input("🔗 GitHub Profile URL", placeholder="https://github.com/username")
    uploaded_file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])
 
    if st.button("🚀 Submit"):
        if not is_valid_github_url(github_url):
            st.error("Invalid GitHub URL.")
            return
        if not uploaded_file:
            st.error("Please upload a PDF resume.")
            return
 
        valid, msg = validate_pdf(uploaded_file)
        if not valid:
            st.error(msg)
            return
 
        with st.spinner("Processing profile..."):
            # GitHub
            ok, gh = process_github_profile(github_url)
            if not ok:
                st.error(f"GitHub error: {gh}")
                return
            gh_data = gh.get("data", {})
            st.session_state.github_markdown_url = gh_data.get("markdown_url", "")
 
            # Resume
            files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
            resp = requests.post(
                f"{BACKEND_API_URL}/api/upload-resume",
                files=files,
                params={"github_url": github_url}
            )
            if resp.status_code != 200:
                st.error("Resume processing failed.")
                return
            data = resp.json().get("data", {})
            st.session_state.resume_markdown_url = data.get("markdown_url", "")
 
            st.success("Profile submitted!")
            st.balloons()
 
            # Prepare user profile for matching
            profile = {
                "combined_embedding": data.get("embeddings_info", {}).get("embedding", []),
                "all_skills": data.get("embeddings_info", {}).get("skills", []),
                "experience_year": data.get("experience_year", ""),
                "qualification": data.get("qualification", "")
            }
 
            # Fetch matches
            ok, mr = get_job_matches(profile)
            if ok and mr.get("status") == "success":
                st.success(f"Found {mr.get('total_matches',0)} matches")
                st.session_state.matches = mr.get("matches", [])
            else:
                st.error(f"Matching error: {mr.get('error','Unknown')}")
 
    # Always show matches if present
    if st.session_state.matches:
        st.subheader("🔍 Matching Jobs")
        for m in st.session_state.matches:
            display_job_match(m)
 
if __name__ == "__main__":
    main()
 
