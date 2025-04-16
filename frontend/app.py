# import streamlit as st
# import requests
# import re
# from io import BytesIO
# import os
# from dotenv import load_dotenv
# import PyPDF2

# # Load environment variables
# load_dotenv()

# # Get backend API URL from environment variables
# BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000')

# def is_valid_github_url(url):
#     """Validate if the provided URL is a valid GitHub profile URL."""
#     # Remove @ symbol if present at the start
#     url = url.lstrip('@')
    
#     # Basic GitHub URL pattern that handles both profile and repository URLs
#     github_pattern = r'^https?://(?:www\.)?github\.com/[a-zA-Z0-9-]+(?:/[a-zA-Z0-9-_]+)*/?$'
    
#     # Check if URL matches the pattern
#     if not re.match(github_pattern, url):
#         return False
        
#     # Additional validation: must have github.com/ in the URL
#     if 'github.com/' not in url:
#         return False
        
#     # Get the username part (first segment after github.com/)
#     try:
#         parts = url.split('github.com/')
#         if len(parts) != 2:
#             return False
#         username = parts[1].split('/')[0]
#         if not username:  # Username cannot be empty
#             return False
#     except:
#         return False
        
#     return True

# def validate_pdf(pdf_file):
#     """Validate if the uploaded file is a valid PDF."""
#     try:
#         # Read the PDF content
#         pdf_content = pdf_file.read()
#         # Try to create a PDF reader object
#         pdf = PyPDF2.PdfReader(BytesIO(pdf_content))
#         # Check if PDF has at least one page
#         if len(pdf.pages) < 1:
#             return False, "The PDF file appears to be empty"
#         # Reset file pointer for later use
#         pdf_file.seek(0)
#         return True, "Valid PDF"
#     except Exception as e:
#         return False, f"Invalid PDF file: {str(e)}"

# def process_github_profile(github_url):
#     """Process GitHub profile using backend API."""
#     try:
#         # API endpoint
#         api_url = f"{BACKEND_API_URL}/api/process-github"
        
#         # Make POST request to backend
#         response = requests.post(
#             api_url,
#             json={"url": github_url}
#         )
        
#         if response.status_code == 200:
#             return True, response.json()
#         else:
#             error_detail = "Unknown error"
#             try:
#                 error_data = response.json()
#                 error_detail = error_data.get('detail', str(error_data))
#             except:
#                 error_detail = response.text
#             return False, f"Error processing GitHub profile: {error_detail}"
            
#     except requests.exceptions.ConnectionError:
#         return False, f"Could not connect to the backend server at {BACKEND_API_URL}"
#     except Exception as e:
#         return False, f"An error occurred: {str(e)}"

# def get_job_matches(resume_skills, github_skills):
#     """Get job matches based on skills."""
#     try:
#         api_url = f"{BACKEND_API_URL}/api/match-jobs"
        
#         response = requests.post(
#             api_url,
#             json={
#                 "resume_skills": resume_skills,
#                 "github_skills": github_skills
#             }
#         )
        
#         if response.status_code == 200:
#             return True, response.json()
#         else:
#             error_detail = "Unknown error"
#             try:
#                 error_data = response.json()
#                 error_detail = error_data.get('detail', str(error_data))
#             except:
#                 error_detail = response.text
#             return False, f"Error getting job matches: {error_detail}"
            
#     except requests.exceptions.ConnectionError:
#         return False, f"Could not connect to the backend server at {BACKEND_API_URL}"
#     except Exception as e:
#         return False, f"An error occurred: {str(e)}"

# def display_job_match(match):
#     """Display a single job match in an expandable section."""
#     with st.expander(f"🔍 {match['job_title']} at {match['company']} (Score: {match['similarity_score']:.2f})"):
#         st.markdown(f"""
#         ### 🏢 Company: {match['company']}
#         ### 📍 Location: {match['location']}
#         ### 💼 Job Type: {match['job_type']}
#         ### 🕒 Work Mode: {match['work_mode']}
#         ### 🎯 Seniority: {match['seniority']}
#         ### 💰 Salary: {match['salary']}
#         ### 📅 Experience: {match['experience']}
        
#         #### 📋 Responsibilities
#         {match['responsibilities']}
        
#         #### 🎓 Qualifications
#         {match['qualifications']}
        
#         #### 🛠 Skills
#         {match['skills']}
#         """)

# def main():
#     st.set_page_config(
#         page_title="Profile Upload",
#         page_icon="📄",
#         layout="centered"
#     )

#     st.title("Upload Your Profile")
#     st.markdown("""
#     Please provide your GitHub profile URL and upload your resume in PDF format.
#     This information will be used to analyze your skills and find matching jobs.
#     """)

#     # GitHub URL input
#     github_url = st.text_input("GitHub Profile URL", placeholder="https://github.com/username")
    
#     # File uploader for PDF
#     uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=['pdf'])

#     if st.button("Submit", type="primary"):
#         if not github_url:
#             st.error("Please enter your GitHub profile URL")
#             return
            
#         if not uploaded_file:
#             st.error("Please upload your resume")
#             return

#         # Validate GitHub URL
#         if not is_valid_github_url(github_url):
#             st.error("Please enter a valid GitHub profile URL")
#             return

#         # Validate PDF before sending to backend
#         is_valid_pdf, pdf_message = validate_pdf(uploaded_file)
#         if not is_valid_pdf:
#             st.error(f"Invalid PDF file: {pdf_message}")
#             return

#         try:
#             with st.spinner("Processing your profile..."):
#                 # First process GitHub profile
#                 st.info("Processing GitHub profile...")
#                 github_success, github_result = process_github_profile(github_url)
                
#                 if not github_success:
#                     st.error(github_result)
#                     return
                
#                 # Then process resume
#                 st.info("Processing resume...")
#                 # Create form data for multipart upload
#                 files = {
#                     'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')
#                 }
                
#                 # API endpoint for resume
#                 api_url = f"{BACKEND_API_URL}/api/upload-resume"
                
#                 # Make POST request to backend
#                 response = requests.post(
#                     api_url,
#                     files=files,
#                     params={'github_url': github_url}
#                 )
                
#                 # Check response
#                 if response.status_code == 200:
#                     response_data = response.json()
                    
#                     if response_data.get('status') == 'success' and 'data' in response_data:
#                         st.success("Profile submitted successfully!")
#                         st.balloons()
                        
#                         # Display the submitted information
#                         st.subheader("Submitted Information:")
                        
#                         # GitHub Information
#                         st.write("### GitHub Profile")
#                         github_data = github_result['data']
#                         st.write(f"Username: {github_data['username']}")
#                         st.write(f"Repositories: {github_data['repository_count']}")
#                         st.write(f"READMEs Processed: {github_data['readme_count']}")
#                         st.write(f"GitHub Markdown: {github_data['markdown_url']}")
                        
#                         # Resume Information
#                         st.write("### Resume")
#                         st.write(f"Filename: {response_data['data']['filename']}")
#                         st.write(f"Resume S3 URL: {response_data['data']['resume_url']}")
#                         st.write(f"Resume Markdown: {response_data['data']['markdown_url']}")
                        
#                         # Extract skills from embeddings info
#                         resume_skills = []
#                         github_skills = []
                        
#                         if 'embeddings_info' in response_data['data']:
#                             resume_skills = response_data['data']['embeddings_info'].get('skills', [])
                        
#                         if 'github_info' in response_data['data'] and 'embeddings_info' in response_data['data']['github_info']:
#                             github_skills = response_data['data']['github_info']['embeddings_info'].get('skills', [])
                        
#                         # Get job matches
#                         st.info("Finding matching jobs...")
#                         matches_success, matches_result = get_job_matches(resume_skills, github_skills)
                        
#                         if matches_success and matches_result.get('status') == 'success':
#                             st.success(f"Found {matches_result['total_matches']} matching jobs!")
                            
#                             # Display job matches
#                             st.subheader("Matching Jobs")
#                             for match in matches_result['matches']:
#                                 display_job_match(match)
#                         else:
#                             st.error(f"Error finding job matches: {matches_result.get('error', 'Unknown error')}")
#                     else:
#                         st.error("Unexpected response format from server")
#                         st.json(response_data)
#                 else:
#                     error_detail = "Unknown error"
#                     try:
#                         error_data = response.json()
#                         error_detail = error_data.get('detail', str(error_data))
#                     except:
#                         error_detail = response.text
                    
#                     st.error(f"Error submitting profile: {error_detail}")
                    
#         except requests.exceptions.ConnectionError:
#             st.error(f"Could not connect to the backend server at {BACKEND_API_URL}. Please make sure the backend is running.")
#         except Exception as e:
#             st.error(f"An error occurred: {str(e)}")
#             st.error("Full error details for debugging:")
#             st.exception(e)

# if __name__ == "__main__":
#     main()



import streamlit as st
import requests
import re
from io import BytesIO
import os
from dotenv import load_dotenv
import PyPDF2

# Load environment variables
load_dotenv()
BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000')

def is_valid_github_url(url):
    url = url.lstrip('@')
    github_pattern = r'^https?://(?:www\.)?github\.com/[a-zA-Z0-9-]+(?:/[a-zA-Z0-9-_]+)*/?$'
    if not re.match(github_pattern, url): return False
    try:
        parts = url.split('github.com/')
        return bool(parts[1].split('/')[0]) if len(parts) == 2 else False
    except: return False

def validate_pdf(pdf_file):
    try:
        pdf_content = pdf_file.read()
        pdf = PyPDF2.PdfReader(BytesIO(pdf_content))
        if len(pdf.pages) < 1: return False, "Empty PDF"
        pdf_file.seek(0)
        return True, "Valid PDF"
    except Exception as e:
        return False, f"Invalid PDF: {str(e)}"

def process_github_profile(github_url):
    try:
        response = requests.post(f"{BACKEND_API_URL}/api/process-github", json={"url": github_url})
        return (True, response.json()) if response.status_code == 200 else (False, response.text)
    except Exception as e:
        return False, str(e)

def get_job_matches(profile_data):
    """Get job matches using full profile (for advanced matching)."""
    try:
        api_url = f"{BACKEND_API_URL}/api/match-jobs"

        response = requests.post(
            api_url,
            json={"profile": profile_data}
        )

        if response.status_code == 200:
            return True, response.json()
        else:
            try:
                return False, response.json()
            except:
                return False, response.text

    except requests.exceptions.ConnectionError:
        return False, f"Could not connect to backend at {BACKEND_API_URL}"
    except Exception as e:
        return False, str(e)


# def display_job_match(match):
#     job_id = match.get("job_id")
#     full_meta = fetch_full_job_details(job_id)

#     with st.expander(f"🔍 {match['job_title']} at {match['company']} (Score: {match['similarity_score']:.2f})"):
#         st.markdown(f"""
#         ### 🏢 Company: {full_meta.get('company', match['company'])}
#         ### 📍 Location: {full_meta.get('location', match['location'])}
#         ### 💼 Job Type: {full_meta.get('job_type', match['job_type'])}
#         ### 🕒 Work Mode: {full_meta.get('work_mode', match['work_mode'])}
#         ### 🎯 Seniority: {full_meta.get('seniority', match['seniority'])}
#         ### 💰 Salary: {full_meta.get('salary', match['salary'])}
#         ### 📅 Experience: {full_meta.get('experience', match['experience'])}
#         ### 📊 Match Category: {match.get('match_category', 'unknown')}
#         ### 💡 Similarity Score: {match['similarity_score']:.2f}

#         #### 📋 Responsibilities
#         {full_meta.get('responsibilities', 'Not Specified')}

#         #### 🎓 Qualifications
#         {full_meta.get('qualifications', 'Not Specified')}

#         #### 🛠 Matching Skills
#         {", ".join(match['skills']) if match['skills'] else "Not available"}
#         """)





def format_bullet_section(title, items):
    if not items:
        return f"#### {title}\n_Not provided._"
    
    bullet_points = "\n".join([f"- {item.strip().capitalize()}" for item in items if item.strip()])
    return f"#### {title}\n{bullet_points}"







def display_job_match(match):
    job_id = match.get("job_id")
    full_meta = fetch_full_job_details(job_id)

    responsibilities = full_meta.get("responsibilities", "")
    qualifications = full_meta.get("qualifications", "")
    skills = match.get("skills", [])

    with st.container():
        with st.expander(f"🔍 **{match['job_title']} at {match['company']}** — Score: {match['similarity_score']:.2f}"):
            st.markdown(f"""
            ### 📌 Job Overview  
            - **🏢 Company:** {full_meta.get('company', match['company'])}  
            - **📍 Location:** {full_meta.get('location', match['location'])}  
            - **💼 Type:** {full_meta.get('job_type', match['job_type'])}  
            - **🕒 Mode:** {full_meta.get('work_mode', match['work_mode'])}  
            - **🎯 Seniority:** {full_meta.get('seniority', match['seniority'])}  
            - **💰 Salary:** {full_meta.get('salary', match['salary']) or 'Not Specified'}  
            - **📅 Experience:** {full_meta.get('experience', match['experience']) or 'Not Specified'}  
            - **📊 Match Category:** {match.get('match_category', 'unknown')}  
            - **💡 Similarity Score:** `{match['similarity_score']:.2f}`
            """, unsafe_allow_html=True)

            st.markdown("---")

            # Format and display responsibilities
            formatted_responsibilities = format_bullet_section("📋 Responsibilities", responsibilities.split(","))
            st.markdown(formatted_responsibilities)

            # Format and display qualifications
            formatted_qualifications = format_bullet_section("🎓 Qualifications", qualifications.split(","))
            st.markdown(formatted_qualifications)

            # Format and display skills
            formatted_skills = format_bullet_section("🛠 Matching Skills", skills)
            st.markdown(formatted_skills)

            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"✉️ Generate Cover Letter", key=f"cover_{job_id}"):
                    st.success("🚀 Cover letter generation initiated!")

            with col2:
                if st.button(f"📈 Improve Profile", key=f"profile_{job_id}"):
                    st.success("🧠 Profile improvement analysis started!")






def fetch_full_job_details(job_id):
    try:
        response = requests.get(f"{BACKEND_API_URL}/api/job-details/{job_id}")
        if response.status_code == 200:
            return response.json().get("metadata", {})
        else:
            return {}
    except:
        return {}




def main():
    st.set_page_config(page_title="SkillMatch AI", page_icon="🤖", layout="centered")
    st.title("SkillMatch AI – Smart Resume & GitHub Job Matcher")
    st.markdown("Upload your resume and GitHub URL to get personalized job matches powered by AI.")

    github_url = st.text_input("🔗 GitHub Profile URL", placeholder="https://github.com/yourusername")
    uploaded_file = st.file_uploader("📄 Upload Resume (PDF only)", type=["pdf"])

    if st.button("🚀 Submit"):
        if not github_url or not is_valid_github_url(github_url):
            st.error("❌ Please enter a valid GitHub URL.")
            return
        if not uploaded_file:
            st.error("❌ Please upload a resume.")
            return

        is_valid_pdf, pdf_msg = validate_pdf(uploaded_file)
        if not is_valid_pdf:
            st.error(f"❌ {pdf_msg}")
            return

        with st.spinner("⏳ Processing your profile..."):
            github_success, github_result = process_github_profile(github_url)
            if not github_success:
                st.error(github_result)
                return

            files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
            response = requests.post(f"{BACKEND_API_URL}/api/upload-resume", files=files, params={"github_url": github_url})

            if response.status_code != 200:
                st.error("Resume processing failed.")
                return

            data = response.json().get("data", {})
            st.success("✅ Profile submitted successfully!")
            st.balloons()

            st.subheader("📊 Profile Summary")
            st.markdown("### GitHub Info")
            st.write(f"👤 Username: {github_result['data']['username']}")
            st.write(f"📦 Repositories: {github_result['data']['repository_count']}")
            st.write(f"📄 READMEs Processed: {github_result['data']['readme_count']}")
            st.write(f"📝 GitHub Markdown: {github_result['data']['markdown_url']}")

            st.markdown("### Resume Info")
            st.write(f"📄 Filename: {data.get('filename')}")
            st.write(f"☁️ S3 URL: {data.get('resume_url')}")
            st.write(f"📜 Markdown URL: {data.get('markdown_url')}")

            # Use the full user profile returned by the backend
            user_profile = {
                "combined_embedding": data.get("embeddings_info", {}).get("embedding", []),
                "all_skills": data.get("embeddings_info", {}).get("skills", []),
                "experience_year": data.get("experience_year", ""),
                "qualification": data.get("qualification", "")
            }

            st.info("🔍 Finding job matches...")
            match_success, match_result = get_job_matches(user_profile)


            # 👇 Add this to visually inspect the match result JSON
            st.subheader("🧪 Raw Match Result")
            st.json(match_result)

            if match_success and match_result.get("status") == "success":
                st.success(f"🎯 Found {match_result['total_matches']} job matches")
                for match in match_result["matches"]:
                    display_job_match(match)
            else:
                st.error(f"❌ Error matching jobs: {match_result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
