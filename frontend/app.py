# import streamlit as st
# import requests
# import re
# from io import BytesIO
# import os
# from dotenv import load_dotenv
# import PyPDF2

# # Load environment variables
# load_dotenv()
# BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000')

# def is_valid_github_url(url):
#     url = url.lstrip('@')
#     github_pattern = r'^https?://(?:www\.)?github\.com/[a-zA-Z0-9-]+(?:/[a-zA-Z0-9-_]+)*/?$'
#     if not re.match(github_pattern, url): return False
#     try:
#         parts = url.split('github.com/')
#         return bool(parts[1].split('/')[0]) if len(parts) == 2 else False
#     except: return False

# def validate_pdf(pdf_file):
#     try:
#         pdf_content = pdf_file.read()
#         pdf = PyPDF2.PdfReader(BytesIO(pdf_content))
#         if len(pdf.pages) < 1: return False, "Empty PDF"
#         pdf_file.seek(0)
#         return True, "Valid PDF"
#     except Exception as e:
#         return False, f"Invalid PDF: {str(e)}"

# def process_github_profile(github_url):
#     try:
#         response = requests.post(f"{BACKEND_API_URL}/api/process-github", json={"url": github_url})
#         return (True, response.json()) if response.status_code == 200 else (False, response.text)
#     except Exception as e:
#         return False, str(e)

# def get_job_matches(profile_data):
#     """Get job matches using full profile (for advanced matching)."""
#     try:
#         api_url = f"{BACKEND_API_URL}/api/match-jobs"

#         response = requests.post(
#             api_url,
#             json={"profile": profile_data}
#         )

#         if response.status_code == 200:
#             return True, response.json()
#         else:
#             try:
#                 return False, response.json()
#             except:
#                 return False, response.text

#     except requests.exceptions.ConnectionError:
#         return False, f"Could not connect to backend at {BACKEND_API_URL}"
#     except Exception as e:
#         return False, str(e)



# def generate_profile_improvement(resume_markdown_url, github_markdown_url, job_id):
#     try:
#         api_url = f"{BACKEND_API_URL}/api/improve-profile-advanced"
#         response = requests.post(api_url, json={
#             "resume_markdown_url": resume_markdown_url,
#             "github_markdown_url": github_markdown_url,
#             "job_id": job_id
#         })
#         if response.status_code == 200:
#             return True, response.json().get("suggestions", "")
#         else:
#             return False, response.text
#     except Exception as e:
#         return False, str(e)



# def format_bullet_section(title, items):
#     if not items:
#         return f"#### {title}\n_Not provided._"
    
#     bullet_points = "\n".join([f"- {item.strip().capitalize()}" for item in items if item.strip()])
#     return f"#### {title}\n{bullet_points}"





# def display_job_match(match):
#     job_id = match.get("job_id")
#     full_meta = fetch_full_job_details(job_id)

#     responsibilities = full_meta.get("responsibilities", "")
#     qualifications = full_meta.get("qualifications", "")
#     skills = match.get("skills", [])

#     with st.container():
#         with st.expander(f"🔍 **{match['job_title']} at {match['company']}** — Score: {match['similarity_score']:.2f}"):
#             st.markdown(f"""
#             ### 📌 Job Overview  
#             - **🏢 Company:** {full_meta.get('company', match['company'])}  
#             - **📍 Location:** {full_meta.get('location', match['location'])}  
#             - **💼 Type:** {full_meta.get('job_type', match['job_type'])}  
#             - **🕒 Mode:** {full_meta.get('work_mode', match['work_mode'])}  
#             - **🎯 Seniority:** {full_meta.get('seniority', match['seniority'])}  
#             - **💰 Salary:** {full_meta.get('salary', match['salary']) or 'Not Specified'}  
#             - **📅 Experience:** {full_meta.get('experience', match['experience']) or 'Not Specified'}  
#             - **📊 Match Category:** {match.get('match_category', 'unknown')}  
#             - **💡 Similarity Score:** `{match['similarity_score']:.2f}`
#             """, unsafe_allow_html=True)

#             st.markdown("---")
#             st.markdown(format_bullet_section("📋 Responsibilities", responsibilities.split(",")))
#             st.markdown(format_bullet_section("🎓 Qualifications", qualifications.split(",")))
#             st.markdown(format_bullet_section("🛠 Matching Skills", skills))
#             st.markdown("---")

            


#             # Combined button to generate both cover letter and improvement suggestions.
#             if st.button(f"📝 Generate Cover Letter & Feedback", key=f"generate_{job_id}"):
#                 with st.spinner("Generating cover letter and improvement suggestions..."):
#                     # Retrieve markdown URLs from session state
#                     resume_md_url = st.session_state.get("resume_markdown_url", "")
#                     github_md_url = st.session_state.get("github_markdown_url", "")
#                     success, combined_output = generate_feedback_and_cover_letter(resume_md_url, github_md_url, job_id)
#                     if success:
#                         st.markdown("### ✅ Generation Results")
#                         st.markdown(combined_output)
#                     else:
#                         st.error(f"❌ Error: {combined_output}")









# # def display_job_match(match):
# #     job_id = match.get("job_id")
# #     full_meta = fetch_full_job_details(job_id)

# #     responsibilities = full_meta.get("responsibilities", "")
# #     qualifications = full_meta.get("qualifications", "")
# #     skills = match.get("skills", [])

# #     with st.container():
# #         with st.expander(f"🔍 **{match['job_title']} at {match['company']}** — Score: {match['similarity_score']:.2f}"):
# #             st.markdown(f"""
# #             ### 📌 Job Overview  
# #             - **🏢 Company:** {full_meta.get('company', match['company'])}  
# #             - **📍 Location:** {full_meta.get('location', match['location'])}  
# #             - **💼 Type:** {full_meta.get('job_type', match['job_type'])}  
# #             - **🕒 Mode:** {full_meta.get('work_mode', match['work_mode'])}  
# #             - **🎯 Seniority:** {full_meta.get('seniority', match['seniority'])}  
# #             - **💰 Salary:** {full_meta.get('salary', match['salary']) or 'Not Specified'}  
# #             - **📅 Experience:** {full_meta.get('experience', match['experience']) or 'Not Specified'}  
# #             - **📊 Match Category:** {match.get('match_category', 'unknown')}  
# #             - **💡 Similarity Score:** `{match['similarity_score']:.2f}`
# #             """, unsafe_allow_html=True)

# #             st.markdown("---")
# #             st.markdown(format_bullet_section("📋 Responsibilities", responsibilities.split(",")))
# #             st.markdown(format_bullet_section("🎓 Qualifications", qualifications.split(",")))
# #             st.markdown(format_bullet_section("🛠 Matching Skills", skills))

# #             st.markdown("---")
# #             col1, col2 = st.columns(2)

# #             with col1:
# #                 if st.button(f"✉️ Generate Cover Letter", key=f"cover_{job_id}"):
# #                     st.success("🚀 Cover letter generation initiated!")

# #             with col2:
# #                 if st.button(f"📈 Improve Profile", key=f"profile_{job_id}"):
# #                     with st.spinner("Analyzing how to improve your profile..."):
# #                         profile_text = st.session_state.get("combined_profile_text", "")
# #                         job_description = full_meta.get("job_text", "")
# #                         success, suggestions = generate_profile_improvement(profile_text, job_description)
# #                         if success:
# #                             st.markdown("### ✅ Profile Improvement Suggestions")
# #                             with st.expander("🔧 See Suggestions"):
# #                                 st.markdown(suggestions)
# #                         else:
# #                             st.error(f"❌ Error generating suggestions: {suggestions}")





# def generate_feedback_and_cover_letter(resume_md_url, github_md_url, job_id):
#     try:
#         api_url = f"{BACKEND_API_URL}/api/generate-feedback-cover-letter"
#         # Fetch markdown content from the provided URLs
#         resume_resp = requests.get(resume_md_url)
#         if resume_resp.status_code != 200:
#             return False, f"Error fetching resume markdown: {resume_resp.text}"
#         resume_text = resume_resp.text

#         git_resp = requests.get(github_md_url)
#         if git_resp.status_code != 200:
#             return False, f"Error fetching GitHub markdown: {git_resp.text}"
#         github_text = git_resp.text

#         combined_profile = f"{resume_text}\n\n{github_text}"

#         # Fetch job details (assuming fetch_full_job_details returns a dict including "job_text")
#         job_details = fetch_full_job_details(job_id)
#         job_description = job_details.get("job_text", "")
#         if not job_description:
#             return False, "Job description not available"
            
#         payload = {
#             "profile_text": combined_profile,
#             "job_description": job_description
#         }
#         response = requests.post(api_url, json=payload)
#         if response.status_code == 200:
#             data = response.json()
#             combined_output = f"### Cover Letter\n{data.get('cover_letter', '')}\n\n### Improvement Suggestions\n{data.get('improvement_suggestions', '')}"
#             return True, combined_output
#         else:
#             return False, response.text
#     except Exception as e:
#         return False, str(e)









# def fetch_full_job_details(job_id):
#     try:
#         response = requests.get(f"{BACKEND_API_URL}/api/job-details/{job_id}")
#         if response.status_code == 200:
#             return response.json().get("metadata", {})
#         else:
#             return {}
#     except:
#         return {}




# def main():
#     st.set_page_config(page_title="SkillMatch AI", page_icon="🤖", layout="centered")
#     st.title("SkillMatch AI – Smart Resume & GitHub Job Matcher")
#     st.markdown("Upload your resume and GitHub URL to get personalized job matches powered by AI.")

#     github_url = st.text_input("🔗 GitHub Profile URL", placeholder="https://github.com/yourusername")
#     uploaded_file = st.file_uploader("📄 Upload Resume (PDF only)", type=["pdf"])

#     if st.button("🚀 Submit"):
#         if not github_url or not is_valid_github_url(github_url):
#             st.error("❌ Please enter a valid GitHub URL.")
#             return
#         if not uploaded_file:
#             st.error("❌ Please upload a resume.")
#             return

#         is_valid_pdf, pdf_msg = validate_pdf(uploaded_file)
#         if not is_valid_pdf:
#             st.error(f"❌ {pdf_msg}")
#             return

#         with st.spinner("⏳ Processing your profile..."):
#             github_success, github_result = process_github_profile(github_url)
#             if not github_success:
#                 st.error(github_result)
#                 return

#             files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
#             response = requests.post(f"{BACKEND_API_URL}/api/upload-resume", files=files, params={"github_url": github_url})

#             if response.status_code != 200:
#                 st.error("Resume processing failed.")
#                 return

#             data = response.json().get("data", {})
#             st.success("✅ Profile submitted successfully!")
#             st.balloons()


            
#             st.subheader("📊 Profile Summary")
#             st.markdown("### GitHub Info")
#             st.write(f"👤 Username: {github_result['data']['username']}")
#             st.write(f"📦 Repositories: {github_result['data']['repository_count']}")
#             st.write(f"📄 READMEs Processed: {github_result['data']['readme_count']}")
#             st.write(f"📝 GitHub Markdown: {github_result['data']['markdown_url']}")

            
          
#             st.markdown("### Resume Info")
#             st.write(f"📄 Filename: {data.get('filename')}")
#             st.write(f"☁️ S3 URL: {data.get('resume_url')}")
#             st.write(f"📜 Markdown URL: {data.get('markdown_url')}")


            

#             # Use the full user profile returned by the backend
#             user_profile = {
#                 "combined_embedding": data.get("embeddings_info", {}).get("embedding", []),
#                 "all_skills": data.get("embeddings_info", {}).get("skills", []),
#                 "experience_year": data.get("experience_year", ""),
#                 "qualification": data.get("qualification", "")
#             }

#             st.info("🔍 Finding job matches...")
#             match_success, match_result = get_job_matches(user_profile)


#             # 👇 Add this to visually inspect the match result JSON
#             st.subheader("🧪 Raw Match Result")
#             st.json(match_result)
            
#             if match_success and match_result.get("status") == "success":
#                 st.success(f"🎯 Found {match_result['total_matches']} job matches")
#                 for match in match_result["matches"]:
#                     display_job_match(match)
#             else:
#                 st.error(f"❌ Error matching jobs: {match_result.get('error', 'Unknown error')}")


# if __name__ == "__main__":
#     main()






# # import streamlit as st
# # import requests
# # import re
# # from io import BytesIO
# # import os
# # from dotenv import load_dotenv
# # import PyPDF2
# # from streamlit_extras.switch_page_button import switch_page

# # # Load environment variables
# # load_dotenv()
# # BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000')


# # def is_valid_github_url(url):
# #     url = url.lstrip('@')
# #     github_pattern = r'^https?://(?:www\.)?github\.com/[a-zA-Z0-9-]+(?:/[a-zA-Z0-9-_]+)*/?$'
# #     if not re.match(github_pattern, url): return False
# #     try:
# #         parts = url.split('github.com/')
# #         return bool(parts[1].split('/')[0]) if len(parts) == 2 else False
# #     except: return False


# # def validate_pdf(pdf_file):
# #     try:
# #         pdf_content = pdf_file.read()
# #         pdf = PyPDF2.PdfReader(BytesIO(pdf_content))
# #         if len(pdf.pages) < 1: return False, "Empty PDF"
# #         pdf_file.seek(0)
# #         return True, "Valid PDF"
# #     except Exception as e:
# #         return False, f"Invalid PDF: {str(e)}"


# # def process_github_profile(github_url):
# #     try:
# #         response = requests.post(f"{BACKEND_API_URL}/api/process-github", json={"url": github_url})
# #         return (True, response.json()) if response.status_code == 200 else (False, response.text)
# #     except Exception as e:
# #         return False, str(e)


# # def get_job_matches(profile_data):
# #     try:
# #         api_url = f"{BACKEND_API_URL}/api/match-jobs"
# #         response = requests.post(api_url, json={"profile": profile_data})
# #         return (True, response.json()) if response.status_code == 200 else (False, response.text)
# #     except Exception as e:
# #         return False, str(e)


# # def generate_profile_improvement(profile_text, job_description):
# #     try:
# #         api_url = f"{BACKEND_API_URL}/api/improve-profile"
# #         response = requests.post(api_url, json={
# #             "profile_text": profile_text,
# #             "job_description": job_description
# #         })
# #         if response.status_code == 200:
# #             return True, response.json().get("suggestions", "")
# #         else:
# #             return False, response.text
# #     except Exception as e:
# #         return False, str(e)


# # def fetch_full_job_details(job_id):
# #     try:
# #         response = requests.get(f"{BACKEND_API_URL}/api/job-details/{job_id}")
# #         if response.status_code == 200:
# #             return response.json().get("metadata", {})
# #         else:
# #             return {}
# #     except:
# #         return {}


# # def format_bullet_section(title, items):
# #     if not items:
# #         return f"#### {title}\n_Not provided._"
# #     bullet_points = "\n".join([f"- {item.strip().capitalize()}" for item in items if item.strip()])
# #     return f"#### {title}\n{bullet_points}"


# # def display_job_match(match):
# #     job_id = match.get("job_id")
# #     full_meta = fetch_full_job_details(job_id)

# #     responsibilities = full_meta.get("responsibilities", "")
# #     qualifications = full_meta.get("qualifications", "")
# #     skills = match.get("skills", [])

# #     with st.container():
# #         with st.expander(f"🔍 **{match['job_title']} at {match['company']}** — Score: {match['similarity_score']:.2f}"):
# #             st.markdown(f"""
# #             ### 📌 Job Overview  
# #             - **🏢 Company:** {full_meta.get('company', match['company'])}  
# #             - **📍 Location:** {full_meta.get('location', match['location'])}  
# #             - **💼 Type:** {full_meta.get('job_type', match['job_type'])}  
# #             - **🕒 Mode:** {full_meta.get('work_mode', match['work_mode'])}  
# #             - **🎯 Seniority:** {full_meta.get('seniority', match['seniority'])}  
# #             - **💰 Salary:** {full_meta.get('salary', match['salary']) or 'Not Specified'}  
# #             - **📅 Experience:** {full_meta.get('experience', match['experience']) or 'Not Specified'}  
# #             - **📊 Match Category:** {match.get('match_category', 'unknown')}  
# #             - **💡 Similarity Score:** `{match['similarity_score']:.2f}`
# #             """, unsafe_allow_html=True)

# #             st.markdown(format_bullet_section("📋 Responsibilities", responsibilities.split(",")))
# #             st.markdown(format_bullet_section("🎓 Qualifications", qualifications.split(",")))
# #             st.markdown(format_bullet_section("🛠 Matching Skills", skills))

# #             col1, col2 = st.columns(2)

# #             with col1:
# #                 if st.button(f"✉️ Generate Cover Letter", key=f"cover_{job_id}"):
# #                     st.success("🚀 Cover letter generation initiated!")

# #             with col2:
# #                 if st.button(f"📈 Improve Profile", key=f"profile_{job_id}"):
# #                     st.session_state["show_modal_for"] = job_id
# #                     st.session_state["modal_job_title"] = match["job_title"]
# #                     st.session_state["modal_company"] = match["company"]
# #                     st.session_state["modal_job_text"] = full_meta.get("job_text", "")


# # def main():
# #     st.set_page_config(page_title="SkillMatch AI", page_icon="🤖", layout="centered")
# #     st.title("SkillMatch AI – Smart Resume & GitHub Job Matcher")
# #     st.markdown("Upload your resume and GitHub URL to get personalized job matches powered by AI.")

# #     github_url = st.text_input("🔗 GitHub Profile URL", placeholder="https://github.com/yourusername")
# #     uploaded_file = st.file_uploader("📄 Upload Resume (PDF only)", type=["pdf"])

# #     if st.button("🚀 Submit"):
# #         if not github_url or not is_valid_github_url(github_url):
# #             st.error("❌ Please enter a valid GitHub URL.")
# #             return
# #         if not uploaded_file:
# #             st.error("❌ Please upload a resume.")
# #             return

# #         is_valid_pdf, pdf_msg = validate_pdf(uploaded_file)
# #         if not is_valid_pdf:
# #             st.error(f"❌ {pdf_msg}")
# #             return

# #         with st.spinner("⏳ Processing your profile..."):
# #             github_success, github_result = process_github_profile(github_url)
# #             if not github_success:
# #                 st.error(github_result)
# #                 return

# #             files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
# #             response = requests.post(f"{BACKEND_API_URL}/api/upload-resume", files=files, params={"github_url": github_url})

# #             if response.status_code != 200:
# #                 st.error("Resume processing failed.")
# #                 return

# #             data = response.json().get("data", {})
# #             st.success("✅ Profile submitted successfully!")
# #             st.balloons()

# #             st.subheader("📊 Profile Summary")
# #             st.markdown("### GitHub Info")
# #             st.write(f"👤 Username: {github_result['data']['username']}")
# #             st.write(f"📦 Repositories: {github_result['data']['repository_count']}")
# #             st.write(f"📄 READMEs Processed: {github_result['data']['readme_count']}")
# #             st.write(f"📝 GitHub Markdown: {github_result['data']['markdown_url']}")

# #             st.markdown("### Resume Info")
# #             st.write(f"📄 Filename: {data.get('filename')}")
# #             st.write(f"☁️ S3 URL: {data.get('resume_url')}")
# #             st.write(f"📜 Markdown URL: {data.get('markdown_url')}")

# #             # Store combined profile for feedback use
# #             st.session_state["combined_profile_text"] = (
# #                 data.get("extracted_text_preview", "") + "\n" +
# #                 github_result["data"].get("markdown_url", "")
# #             )

# #             user_profile = {
# #                 "combined_embedding": data.get("embeddings_info", {}).get("embedding", []),
# #                 "all_skills": data.get("embeddings_info", {}).get("skills", []),
# #                 "experience_year": data.get("experience_year", ""),
# #                 "qualification": data.get("qualification", "")
# #             }

# #             st.info("🔍 Finding job matches...")
# #             match_success, match_result = get_job_matches(user_profile)

# #             if match_success and match_result.get("status") == "success":
# #                 st.success(f"🎯 Found {match_result['total_matches']} job matches")
# #                 for match in match_result["matches"]:
# #                     display_job_match(match)
# #             else:
# #                 st.error(f"❌ Error matching jobs: {match_result.get('error', 'Unknown error')}")

# #     # Show modal after job rendering
# #     if st.session_state.get("show_modal_for"):
# #         with st.modal(f"📈 Improve Profile for {st.session_state['modal_job_title']} at {st.session_state['modal_company']}"):
# #             with st.spinner("🧠 Generating suggestions..."):
# #                 profile_text = st.session_state.get("combined_profile_text", "")
# #                 job_description = st.session_state.get("modal_job_text", "")
# #                 success, suggestions = generate_profile_improvement(profile_text, job_description)
# #                 if success:
# #                     st.markdown("### ✅ Profile Improvement Suggestions")
# #                     st.markdown(suggestions)
# #                 else:
# #                     st.error(f"❌ Error: {suggestions}")
# #             if st.button("Close"):
# #                 st.session_state["show_modal_for"] = None


# # if __name__ == "__main__":
# #     main()









# edited and removed

# def display_job_match(match: dict):
#     """
#     Display a single job match in an expandable container.
#     Adds a combined "Generate Cover Letter & Feedback" button for each job.
#     """
#     job_id = match.get("job_id")
#     full_meta = fetch_full_job_details(job_id)
    
#     responsibilities = full_meta.get("responsibilities", "")
#     qualifications = full_meta.get("qualifications", "")
#     skills = match.get("skills", [])

#     with st.container():
#         with st.expander(f"🔍 **{match.get('job_title', 'N/A')} at {match.get('company', 'N/A')}** — Score: {match.get('similarity_score', 0):.2f}"):
#             st.markdown(f"""
#             ### 📌 Job Overview  
#             - **🏢 Company:** {full_meta.get('company', match.get('company', 'N/A'))}  
#             - **📍 Location:** {full_meta.get('location', match.get('location', 'Unknown'))}  
#             - **💼 Type:** {full_meta.get('job_type', match.get('job_type', 'Unknown'))}  
#             - **🕒 Mode:** {full_meta.get('work_mode', match.get('work_mode', 'Unknown'))}  
#             - **🎯 Seniority:** {full_meta.get('seniority', match.get('seniority', 'Unknown'))}  
#             - **💰 Salary:** {full_meta.get('salary', match.get('salary', 'Not Specified'))}  
#             - **📅 Experience:** {full_meta.get('experience', match.get('experience', 'Not Specified'))}  
#             - **📊 Match Category:** {match.get('match_category', 'unknown')}  
#             - **💡 Similarity Score:** `{match.get('similarity_score', 0):.2f}`
#             """, unsafe_allow_html=True)

#             st.markdown("---")
#             st.markdown(format_bullet_section("📋 Responsibilities", responsibilities.split(",")))
#             st.markdown(format_bullet_section("🎓 Qualifications", qualifications.split(",")))
#             st.markdown(format_bullet_section("🛠 Matching Skills", skills))
#             st.markdown("---")
            
#             # Combined generate button for cover letter and feedback
#             if st.button(f"📝 Generate Cover Letter & Feedback", key=f"generate_{job_id}"):
#                 with st.spinner("Generating cover letter and improvement suggestions..."):
#                     # Retrieve resume and GitHub markdown URLs from session state (saved after profile processing)
#                     resume_md_url = st.session_state.get("resume_markdown_url", "")
#                     github_md_url = st.session_state.get("github_markdown_url", "")
#                     success, output = generate_feedback_and_cover_letter(resume_md_url, github_md_url, job_id)
#                     if success:
#                         st.markdown("### ✅ Generation Results")
#                         st.markdown(output)
#                     else:
#                         st.error(f"❌ Error: {output}")






# def generate_feedback_and_cover_letter(resume_md_url: str, github_md_url: str, job_id: str) -> (bool, str):
#     """
#     Retrieve the candidate's full markdown (by fetching resume and GitHub markdown from S3),
#     then query the backend endpoint /api/generate-feedback-cover-letter with a combined profile text
#     and the job description (fetched from the job details endpoint).
#     Returns a tuple (success: bool, result: str).
#     """
#     try:
#         # Fetch resume markdown text
#         resume_resp = requests.get(resume_md_url)
#         if resume_resp.status_code != 200:
#             return False, f"Error fetching resume markdown: {resume_resp.text}"
#         resume_text = resume_resp.text

#         # Fetch GitHub markdown text
#         git_resp = requests.get(github_md_url)
#         if git_resp.status_code != 200:
#             return False, f"Error fetching GitHub markdown: {git_resp.text}"
#         github_text = git_resp.text

#         # Combine the markdown contents into one profile text
#         combined_profile = f"{resume_text}\n\n{github_text}"

#         # Fetch job details to extract the job description (assume job_text holds the full description)
#         job_details = fetch_full_job_details(job_id)
#         job_description = job_details.get("job_text", "")
#         if not job_description:
#             return False, "Job description not available"

#         payload = {
#             "profile_text": combined_profile,
#             "job_description": job_description
#         }
#         api_url = f"{BACKEND_API_URL}/api/generate-feedback-cover-letter"
#         response = requests.post(api_url, json=payload)
#         if response.status_code == 200:
#             data = response.json()
#             combined_output = (
#                 "### Cover Letter\n" + data.get("cover_letter", "") +
#                 "\n\n### Improvement Suggestions\n" + data.get("improvement_suggestions", "")
#             )
#             return True, combined_output
#         else:
#             return False, response.text
#     except Exception as e:
#         return False, str(e)













# def display_job_match(match):
#     """
#     Display a single job match in an expandable container.
#     Adds a 'Generate Cover Letter & Feedback' button that records the clicked job in session_state.
#     """
#     job_id = match.get("job_id")
#     full_meta = fetch_full_job_details(job_id)

#     # Fallbacks to match dict if metadata is missing
#     company    = full_meta.get("company",    match.get("company",    "N/A"))
#     job_title  = match.get("job_title",      "N/A")
#     location   = full_meta.get("location",   match.get("location",   "Unknown"))
#     job_type   = full_meta.get("job_type",   match.get("job_type",   "Unknown"))
#     work_mode  = full_meta.get("work_mode",  match.get("work_mode",  "Unknown"))
#     seniority  = full_meta.get("seniority",  match.get("seniority",  "Unknown"))
#     salary     = full_meta.get("salary",     match.get("salary",     "Not Specified"))
#     experience = full_meta.get("experience", match.get("experience", "Not Specified"))
#     category   = match.get("similarity_category", match.get("match_category", "unknown"))
#     score      = match.get("similarity_score", 0.0)

#     responsibilities = full_meta.get("responsibilities", "")
#     qualifications   = full_meta.get("qualifications", "")
#     skills           = match.get("skills", [])

#     with st.container():
#         with st.expander(f"🔍 **{job_title}** at **{company}** — Score: {score:.2f}"):
#             st.markdown(f"""
#             ### 📌 Job Overview  
#             - **🏢 Company:** {company}  
#             - **📍 Location:** {location}  
#             - **💼 Type:** {job_type}  
#             - **🕒 Mode:** {work_mode}  
#             - **🎯 Seniority:** {seniority}  
#             - **💰 Salary:** {salary}  
#             - **📅 Experience:** {experience}  
#             - **📊 Match Category:** {category}  
#             - **💡 Similarity Score:** `{score:.2f}`
#             """, unsafe_allow_html=True)

#             st.markdown("---")
#             st.markdown(format_bullet_section("📋 Responsibilities", responsibilities.split(",")))
#             st.markdown(format_bullet_section("🎓 Qualifications",   qualifications.split(",")))
#             st.markdown(format_bullet_section("🛠 Matching Skills",   skills))
#             st.markdown("---")

#         # When clicked, record this job_id for later feedback generation
#         if st.button("📝 Generate Cover Letter & Feedback", key=f"btn_{job_id}"):
#             st.session_state.selected_job_for_feedback = job_id








# import logging
# import streamlit as st
# import requests
# import re
# from io import BytesIO
# import os
# from dotenv import load_dotenv
# import PyPDF2

# # Load environment variables
# load_dotenv()
# BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000')

# # Configure console logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # ─── Initialize session state ───────────────────────────────────
# if "selected_job_for_feedback" not in st.session_state:
#     st.session_state["selected_job_for_feedback"] = None

# # -----------------------------------------------------------------
# # Helper Functions
# # -----------------------------------------------------------------
# def is_valid_github_url(url: str) -> bool:
#     """
#     Validate if the provided URL is a valid GitHub profile URL.
#     """
#     url = url.lstrip('@')
#     github_pattern = r'^https?://(?:www\.)?github\.com/[a-zA-Z0-9-]+(?:/[a-zA-Z0-9-_]+)*/?$'
#     if not re.match(github_pattern, url):
#         return False
#     try:
#         parts = url.split('github.com/')
#         return bool(parts[1].split('/')[0]) if len(parts) == 2 else False
#     except Exception:
#         return False

# def validate_pdf(pdf_file) -> (bool, str):
#     """
#     Validate if the uploaded file is a valid PDF.
#     """
#     try:
#         pdf_content = pdf_file.read()
#         pdf = PyPDF2.PdfReader(BytesIO(pdf_content))
#         if len(pdf.pages) < 1:
#             return False, "Empty PDF"
#         pdf_file.seek(0)
#         return True, "Valid PDF"
#     except Exception as e:
#         return False, f"Invalid PDF: {str(e)}"

# def process_github_profile(github_url: str) -> (bool, dict):
#     """
#     Process GitHub profile using the backend.
#     """
#     try:
#         response = requests.post(f"{BACKEND_API_URL}/api/process-github", json={"url": github_url})
#         if response.status_code == 200:
#             return True, response.json()
#         else:
#             return False, response.text
#     except Exception as e:
#         return False, str(e)

# def get_job_matches(profile_data: dict) -> (bool, dict):
#     """
#     Get job matches using the full user profile (including combined embedding and skills) by calling the backend.
#     """
#     try:
#         api_url = f"{BACKEND_API_URL}/api/match-jobs"
#         response = requests.post(api_url, json={"profile": profile_data})
#         if response.status_code == 200:
#             return True, response.json()
#         else:
#             try:
#                 return False, response.json()
#             except Exception:
#                 return False, response.text
#     except requests.exceptions.ConnectionError:
#         return False, f"Could not connect to backend at {BACKEND_API_URL}"
#     except Exception as e:
#         return False, str(e)




# def generate_feedback_and_cover_letter(resume_md_url: str, github_md_url: str, job_id: str):
#     try:
#         # Fetch markdown content first
#         resume_md = requests.get(resume_md_url).text
#         github_md = requests.get(github_md_url).text
#         combined_profile = resume_md + "\n\n" + github_md

#         # Fetch job details (metadata containing responsibilities & qualifications)
#         job_details = requests.get(f"{BACKEND_API_URL}/api/job-details/{job_id}").json()
#         metadata = job_details.get("metadata", {})
#         job_description = metadata.get("responsibilities", "") + "\n\n" + metadata.get("qualifications", "")

#         payload = {
#             "profile_text": combined_profile,
#             "job_description": job_description
#         }

#         resp = requests.post(f"{BACKEND_API_URL}/api/generate-feedback-cover-letter", json=payload)
#         resp.raise_for_status()
#         return True, resp.json()

#     except Exception as e:
#         return False, str(e)















# def fetch_full_job_details(job_id: str) -> dict:
#     """
#     Fetch job details from the backend by job_id.
#     """
#     try:
#         response = requests.get(f"{BACKEND_API_URL}/api/job-details/{job_id}")
#         if response.status_code == 200:
#             return response.json().get("metadata", {})
#         else:
#             return {}
#     except Exception:
#         return {}

# def format_bullet_section(title: str, items: list) -> str:
#     """
#     Format a list of items as a bullet list under a header.
#     """
#     if not items:
#         return f"#### {title}\n_Not provided._"
#     bullet_points = "\n".join([f"- {item.strip().capitalize()}" for item in items if item.strip()])
#     return f"#### {title}\n{bullet_points}"







# def display_job_match(match):
#     """
#     Display a single job match in an expandable container, with a button
#     to generate cover letter & feedback. Logs every step for debugging.
#     """
#     job_id = match.get("job_id", "UNKNOWN")
#     full_meta = fetch_full_job_details(job_id)

#     # Extract fields with fallbacks
#     company    = full_meta.get("company",    match.get("company",    "N/A"))
#     job_title  = match.get("job_title",      "N/A")
#     location   = full_meta.get("location",   match.get("location",   "Unknown"))
#     job_type   = full_meta.get("job_type",   match.get("job_type",   "Unknown"))
#     work_mode  = full_meta.get("work_mode",  match.get("work_mode",  "Unknown"))
#     seniority  = full_meta.get("seniority",  match.get("seniority",  "Unknown"))
#     salary     = full_meta.get("salary",     match.get("salary",     "Not Specified"))
#     experience = full_meta.get("experience", match.get("experience", "Not Specified"))
#     category   = match.get("similarity_category", match.get("match_category", "unknown"))
#     score      = match.get("similarity_score", 0.0)

#     responsibilities = full_meta.get("responsibilities", "")
#     qualifications   = full_meta.get("qualifications", "")
#     skills           = match.get("skills", [])

#     # Container for the collapsible card
#     with st.container():
#         with st.expander(f"🔍 **{job_title}** at **{company}** — Score: {score:.2f}"):
#             st.markdown(f"""
#             ### 📌 Job Overview  
#             - **🏢 Company:** {company}  
#             - **📍 Location:** {location}  
#             - **💼 Type:** {job_type}  
#             - **🕒 Mode:** {work_mode}  
#             - **🎯 Seniority:** {seniority}  
#             - **💰 Salary:** {salary}  
#             - **📅 Experience:** {experience}  
#             - **📊 Match Category:** {category}  
#             - **💡 Similarity Score:** `{score:.2f}`
#             """, unsafe_allow_html=True)

#             st.markdown("---")
#             st.markdown(format_bullet_section("📋 Responsibilities", responsibilities.split(",")))
#             st.markdown(format_bullet_section("🎓 Qualifications",   qualifications.split(",")))
#             st.markdown(format_bullet_section("🛠 Matching Skills",   skills))
#             st.markdown("---")

#     # Placeholder to render the API results below the button
#     results_placeholder = st.container()

#     # The generate button: when clicked, we log and call the feedback API
#     if st.button("📝 Generate Cover Letter & Feedback", key=f"btn_{job_id}"):
#         # 1) Log click
#         logger.info(f"[DEBUG] Button clicked for job_id={job_id}")
#         st.write(f"🔧 DEBUG: Button clicked for job_id=`{job_id}`")

#         # 2) Retrieve markdown URLs from session_state
#         resume_md_url = st.session_state.get("resume_markdown_url")
#         github_md_url = st.session_state.get("github_markdown_url")
#         st.write(f"🔧 DEBUG: resume_markdown_url = `{resume_md_url}`")
#         st.write(f"🔧 DEBUG: github_markdown_url = `{github_md_url}`")

#         # 3) Sanity check
#         if not resume_md_url or not github_md_url:
#             st.error("🚨 ERROR: resume/github markdown URL missing in session_state")
#             logger.error("[ERROR] Missing resume_markdown_url or github_markdown_url in session_state")
#             return

#         # 4) Call the feedback API
#         with st.spinner("🕐 Calling feedback API…"):
#             try:
#                 payload = {
#                     "resume_markdown_url": resume_md_url,
#                     "github_markdown_url": github_md_url,
#                     "job_id": job_id
#                 }
#                 logger.info(f"[DEBUG] POST /api/generate-cover-letter-feedback payload={payload}")
#                 resp = requests.post(
#                     f"{BACKEND_API_URL}/api/generate-cover-letter-feedback",
#                     json=payload
#                 )
#                 st.write(f"🔧 DEBUG: HTTP {resp.status_code}")
#                 st.write(f"🔧 DEBUG: response.text =\n```\n{resp.text}\n```")
#                 logger.info(f"[DEBUG] Feedback API responded {resp.status_code}")

#                 resp.raise_for_status()
#                 result = resp.json()
#                 logger.info(f"[DEBUG] Parsed JSON: {result}")
#             except Exception as e:
#                 st.error(f"❌ Exception during API call: {e}")
#                 logger.exception(f"Exception calling feedback API for job {job_id}")
#                 return

#         # 5) Render results in the reserved placeholder
#         with results_placeholder:
#             st.markdown("### ✅ Generation Results")
#             st.markdown("#### 📄 Cover Letter")
#             st.markdown(result.get("cover_letter", "_No cover letter returned._"))
#             st.markdown("#### 💡 Feedback & Improvement Suggestions")
#             st.markdown(result.get("feedback", "_No feedback returned._"))






















# # -----------------------------------------------------------------
# # Main Frontend Workflow
# # -----------------------------------------------------------------
# def main():
#     st.set_page_config(page_title="SkillMatch AI", page_icon="🤖", layout="centered")
#     st.title("SkillMatch AI – Smart Resume & GitHub Job Matcher")
#     st.markdown("Upload your resume (PDF) and provide your GitHub profile URL to get personalized job matches and generate a tailored cover letter and profile improvement feedback.")

#     # Input fields for GitHub URL and PDF upload
#     github_url = st.text_input("🔗 GitHub Profile URL", placeholder="https://github.com/yourusername")
#     uploaded_file = st.file_uploader("📄 Upload Resume (PDF only)", type=["pdf"])

#     if st.button("🚀 Submit"):
#         # Validate inputs
#         if not github_url or not is_valid_github_url(github_url):
#             st.error("❌ Please enter a valid GitHub URL.")
#             return
#         if not uploaded_file:
#             st.error("❌ Please upload a resume.")
#             return

#         is_valid, pdf_msg = validate_pdf(uploaded_file)
#         if not is_valid:
#             st.error(f"❌ {pdf_msg}")
#             return

#         with st.spinner("⏳ Processing your profile..."):
#             # Process GitHub profile
#             github_success, github_result = process_github_profile(github_url)
#             if not github_success:
#                 st.error(github_result)
#                 return

#             # Process resume file via backend
#             files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
#             response = requests.post(f"{BACKEND_API_URL}/api/upload-resume", files=files, params={"github_url": github_url})
#             if response.status_code != 200:
#                 st.error("Resume processing failed.")
#                 return
            
#             data = response.json().get("data", {})
#             st.success("✅ Profile submitted successfully!")
#             st.balloons()

#             # Display profile summary
#             st.subheader("📊 Profile Summary")
#             st.markdown("### GitHub Info")
#             if github_result and "data" in github_result:
#                 st.write(f"👤 Username: {github_result['data'].get('username', 'N/A')}")
#                 st.write(f"📦 Repositories: {github_result['data'].get('repository_count', 'N/A')}")
#                 st.write(f"📄 READMEs Processed: {github_result['data'].get('readme_count', 'N/A')}")
#                 st.write(f"📝 GitHub Markdown: {github_result['data'].get('markdown_url', '')}")
#                 # Save GitHub markdown URL in session state for later use
#                 st.session_state["github_markdown_url"] = github_result['data'].get('markdown_url', '')
#             st.markdown("### Resume Info")
#             st.write(f"📄 Filename: {data.get('filename', '')}")
#             st.write(f"☁️ S3 URL: {data.get('resume_url', '')}")
#             st.write(f"📜 Markdown URL: {data.get('markdown_url', '')}")
#             # Save Resume markdown URL in session state for later use
#             st.session_state["resume_markdown_url"] = data.get("markdown_url", "")

#             # Prepare user profile for job matching (using combined embedding and skills)
#             user_profile = {
#                 "combined_embedding": data.get("embeddings_info", {}).get("embedding", []),
#                 "all_skills": data.get("embeddings_info", {}).get("skills", []),
#                 "experience_year": data.get("experience_year", ""),
#                 "qualification": data.get("qualification", "")
#             }
#             st.info("🔍 Finding job matches...")
#             matches_success, match_result = get_job_matches(user_profile)
            
#             # Display raw match result for debugging (optional)
#             st.subheader("🧪 Raw Match Result")
#             st.json(match_result)
            
#             if matches_success and match_result.get("status") == "success":
#                 st.success(f"🎯 Found {match_result.get('total_matches', 0)} job matches")
#                 st.subheader("Matching Jobs")
#                 for match in match_result.get("matches", []):
#                     display_job_match(match)
#                     # This is the part you need to update
#                     if st.button(f"📝 Generate Cover Letter & Feedback", key=f"btn_{match['job_id']}"):
#                         with st.spinner("Generating cover letter and improvement suggestions..."):
#                             # Fetch resume markdown and github markdown from session state
#                             resume_md_url = st.session_state.get("resume_markdown_url")
#                             github_md_url = st.session_state.get("github_markdown_url")
#                             job_id = match['job_id']  # Use the current match's job ID
                            
#                             success, combined_output = generate_feedback_and_cover_letter(resume_md_url, github_md_url, job_id)
#                             if success:
#                                 st.markdown("### ✅ Generation Results")
#                                 st.markdown(f"### 📄 Cover Letter\n{combined_output['cover_letter']}")
#                                 st.markdown(f"### 💡 Improvement Suggestions\n{combined_output['improvement_suggestions']}")
#                             else:
#                                 st.error(f"❌ Error: {combined_output}")

#                 # 2) *after* listing all jobs* check for a click
#                 job_to_run = st.session_state.selected_job_for_feedback
#                 if job_to_run:
#                     # clear it immediately so it only fires once
#                     st.session_state.selected_job_for_feedback = None

#                     with st.spinner("Generating cover letter and feedback…"):
#                         resume_md_url = st.session_state["resume_markdown_url"]
#                         github_md_url = st.session_state["github_markdown_url"]
#                         ok, result = generate_feedback_and_cover_letter(
#                             resume_md_url, github_md_url, job_to_run
#                         )

#                     st.markdown("---")
#                     if ok:
#                         st.markdown(f"## ✅ Results for Job `{job_to_run}`")
#                         st.markdown("### 📄 Cover Letter")
#                         st.markdown(result.get("cover_letter", "*(no cover letter returned)*"))
#                         st.markdown("### 💡 Feedback & Suggestions")
#                         st.markdown(result.get("feedback", "*(no feedback returned)*"))
#                     else:
#                         st.error(f"❌ Error generating feedback: {result}")
        
#             else:
#                 st.error(f"❌ Error matching jobs: {match_result.get('error', 'Unknown error')}")

# if __name__ == "__main__":
#     main()

































































# import logging
# import streamlit as st
# import requests
# import re
# from io import BytesIO
# import os
# from dotenv import load_dotenv
# import PyPDF2

# import logging

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# # Load environment variables
# load_dotenv()
# BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000')

# # Initialize session state if not already set
# if "resume_url" not in st.session_state:
#     st.session_state.resume_url = None
# if "github_url" not in st.session_state:
#     st.session_state.github_url = None
# if "generated_feedback" not in st.session_state:
#     st.session_state.generated_feedback = None

# # # Initialize session state
# # if "selected_job_for_feedback" not in st.session_state:
# #     st.session_state["selected_job_for_feedback"] = None

# # Helper Functions
# def is_valid_github_url(url: str) -> bool:
#     """
#     Validate if the provided URL is a valid GitHub profile URL.
#     """
#     url = url.lstrip('@')
#     github_pattern = r'^https?://(?:www\.)?github\.com/[a-zA-Z0-9-]+(?:/[a-zA-Z0-9-_]+)*/?$'
#     if not re.match(github_pattern, url):
#         return False
#     try:
#         parts = url.split('github.com/')
#         return bool(parts[1].split('/')[0]) if len(parts) == 2 else False
#     except Exception:
#         return False

# def validate_pdf(pdf_file) -> (bool, str):
#     """
#     Validate if the uploaded file is a valid PDF.
#     """
#     try:
#         pdf_content = pdf_file.read()
#         pdf = PyPDF2.PdfReader(BytesIO(pdf_content))
#         if len(pdf.pages) < 1:
#             return False, "Empty PDF"
#         pdf_file.seek(0)
#         return True, "Valid PDF"
#     except Exception as e:
#         return False, f"Invalid PDF: {str(e)}"

# def process_github_profile(github_url: str) -> (bool, dict):
#     """
#     Process GitHub profile using the backend.
#     """
#     try:
#         response = requests.post(f"{BACKEND_API_URL}/api/process-github", json={"url": github_url})
#         if response.status_code == 200:
#             return True, response.json()
#         else:
#             return False, response.text
#     except Exception as e:
#         return False, str(e)

# def get_job_matches(profile_data: dict) -> (bool, dict):
#     """
#     Get job matches using the full user profile (including combined embedding and skills) by calling the backend.
#     """
#     try:
#         api_url = f"{BACKEND_API_URL}/api/match-jobs"
#         response = requests.post(api_url, json={"profile": profile_data})
#         if response.status_code == 200:
#             return True, response.json()
#         else:
#             try:
#                 return False, response.json()
#             except Exception:
#                 return False, response.text
#     except requests.exceptions.ConnectionError:
#         return False, f"Could not connect to backend at {BACKEND_API_URL}"
#     except Exception as e:
#         return False, str(e)

# def generate_feedback_and_cover_letter(resume_md_url: str, github_md_url: str, job_id: str):
#     try:
#         logger.info(f"Making request to generate cover letter and feedback for job_id: {job_id}")
#         payload = {
#             "resume_markdown_url": resume_md_url,
#             "github_markdown_url": github_md_url,
#             "job_id": job_id
#         }
#         resp = requests.post(f"{BACKEND_API_URL}/api/generate-feedback-cover-letter", json=payload)
#         resp.raise_for_status()
#         return True, resp.json()
#     except Exception as e:
#         return False, str(e)

# def fetch_full_job_details(job_id: str) -> dict:
#     """
#     Fetch job details from the backend by job_id.
#     """
#     try:
#         response = requests.get(f"{BACKEND_API_URL}/api/job-details/{job_id}")
#         if response.status_code == 200:
#             return response.json().get("metadata", {})
#         else:
#             return {}
#     except Exception:
#         return {}

# def format_bullet_section(title: str, items: list) -> str:
#     """
#     Format a list of items as a bullet list under a header.
#     """
#     if not items:
#         return f"#### {title}\n_Not provided._"
#     bullet_points = "\n".join([f"- {item.strip().capitalize()}" for item in items if item.strip()])
#     return f"#### {title}\n{bullet_points}"

# def display_job_match(match):
#     """
#     Display a single job match in an expandable container, with a button to generate cover letter & feedback.
#     """
#     job_id = match.get("job_id", "UNKNOWN")
#     full_meta = fetch_full_job_details(job_id)

#     company = full_meta.get("company", match.get("company", "N/A"))
#     job_title = match.get("job_title", "N/A")
#     location = full_meta.get("location", match.get("location", "Unknown"))
#     job_type = full_meta.get("job_type", match.get("job_type", "Unknown"))
#     work_mode = full_meta.get("work_mode", match.get("work_mode", "Unknown"))
#     seniority = full_meta.get("seniority", match.get("seniority", "Unknown"))
#     salary = full_meta.get("salary", match.get("salary", "Not Specified"))
#     experience = full_meta.get("experience", match.get("experience", "Not Specified"))
#     score = match.get("similarity_score", 0.0)

#     responsibilities = full_meta.get("responsibilities", "")
#     qualifications = full_meta.get("qualifications", "")
#     skills = match.get("skills", [])

#     # Container for the collapsible card
#     with st.container():
#         with st.expander(f"🔍 **{job_title}** at **{company}** — Score: {score:.2f}"):
#             st.markdown(f"""
#             ### 📌 Job Overview  
#             - **🏢 Company:** {company}  
#             - **📍 Location:** {location}  
#             - **💼 Type:** {job_type}  
#             - **🕒 Mode:** {work_mode}  
#             - **🎯 Seniority:** {seniority}  
#             - **💰 Salary:** {salary}  
#             - **📅 Experience:** {experience}  
#             - **💡 Similarity Score:** `{score:.2f}`
#             """, unsafe_allow_html=True)
#             st.markdown("---")
#             st.markdown(format_bullet_section("📋 Responsibilities", responsibilities.split(",")))
#             st.markdown(format_bullet_section("🎓 Qualifications", qualifications.split(",")))
#             st.markdown(format_bullet_section("🛠 Matching Skills", skills))

#             # The generate button: when clicked, we log and call the feedback API
#             if st.button(f"📝 Generate Cover Letter & Feedback", key=f"btn_{job_id}"):
#                 with st.spinner("🕐 Calling feedback API…"):
#                     resume_md_url = st.session_state.get("resume_markdown_url")
#                     github_md_url = st.session_state.get("github_markdown_url")

#                     logger.info(f"[DEBUG] resume_md_url: {resume_md_url}")
#                     logger.info(f"[DEBUG] github_md_url: {github_md_url}")
                    
#                     # Ensure both URLs are available before calling the API
#                     if not resume_md_url or not github_md_url:
#                         st.error("🚨 ERROR: resume/github markdown URL missing in session_state")
#                         return

#                     success, result = generate_feedback_and_cover_letter(resume_md_url, github_md_url, job_id)
#                     logger.info(f"API response: {result}")
#                     logger.info(f"[DEBUG] API call success: {success}")


#                     if success:
#                         st.markdown("### ✅ Generation Results")
#                         st.markdown(f"### 📄 Cover Letter\n{result.get('cover_letter', '')}")
#                         st.markdown(f"### 💡 Feedback & Improvement Suggestions\n{result.get('improvement_suggestions', '')}")
#                     else:
#                         st.error(f"❌ Error: {result}")

# # Main Frontend Workflow
# def main():
#     st.set_page_config(page_title="SkillMatch AI", page_icon="🤖", layout="centered")
#     st.title("SkillMatch AI – Smart Resume & GitHub Job Matcher")
#     st.markdown("Upload your resume (PDF) and provide your GitHub profile URL to get personalized job matches and generate tailored cover letters & feedback.")

#     github_url = st.text_input("🔗 GitHub Profile URL", placeholder="https://github.com/yourusername")
#     uploaded_file = st.file_uploader("📄 Upload Resume (PDF only)", type=["pdf"])

#     if st.button("🚀 Submit"):
#         if not github_url or not is_valid_github_url(github_url):
#             st.error("❌ Please enter a valid GitHub URL.")
#             return
#         if not uploaded_file:
#             st.error("❌ Please upload a resume.")
#             return

#         valid, pdf_msg = validate_pdf(uploaded_file)
#         if not valid:
#             st.error(f"❌ {pdf_msg}")
#             return

#         with st.spinner("⏳ Processing your profile..."):
#             # Process GitHub profile
#             github_success, github_result = process_github_profile(github_url)
#             if not github_success:
#                 st.error(github_result)
#                 return

#             # Process resume file via backend
#             files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
#             response = requests.post(f"{BACKEND_API_URL}/api/upload-resume", files=files, params={"github_url": github_url})
#             if response.status_code != 200:
#                 st.error("Resume processing failed.")
#                 return
            
#             data = response.json().get("data", {})
#             st.success("✅ Profile submitted successfully!")
#             st.balloons()

#             # Show profile summary
#             st.subheader("📊 Profile Summary")
#             st.markdown("### GitHub Info")
#             if github_result and "data" in github_result:
#                 st.write(f"👤 Username: {github_result['data'].get('username', 'N/A')}")
#                 st.write(f"📦 Repositories: {github_result['data'].get('repository_count', 'N/A')}")
#                 st.write(f"📄 READMEs Processed: {github_result['data'].get('readme_count', 'N/A')}")
#                 st.write(f"📝 GitHub Markdown: {github_result['data'].get('markdown_url', '')}")
#                 st.session_state["github_markdown_url"] = github_result['data'].get('markdown_url', '')

#             st.markdown("### Resume Info")
#             st.write(f"📄 Filename: {data.get('filename', '')}")
#             st.write(f"☁️ S3 URL: {data.get('resume_url', '')}")
#             st.write(f"📜 Markdown URL: {data.get('markdown_url', '')}")
#             st.session_state["resume_markdown_url"] = data.get("markdown_url", "")

#             # Prepare user profile for job matching
#             user_profile = {
#                 "combined_embedding": data.get("embeddings_info", {}).get("embedding", []),
#                 "all_skills": data.get("embeddings_info", {}).get("skills", []),
#                 "experience_year": data.get("experience_year", ""),
#                 "qualification": data.get("qualification", "")
#             }

#             # Find job matches
#             st.info("🔍 Finding job matches…")
#             matches_success, match_result = get_job_matches(user_profile)

#             if matches_success and match_result.get("status") == "success":
#                 st.success(f"🎯 Found {match_result.get('total_matches', 0)} job matches")
#                 st.subheader("Matching Jobs")
#                 for match in match_result.get("matches", []):
#                     display_job_match(match)  # Display each matched job
#             else:
#                 st.error(f"❌ Error matching jobs: {match_result.get('error', 'Unknown error')}")

# if __name__ == "__main__":
#     main()































# import logging
# import streamlit as st
# import requests
# import re
# from io import BytesIO
# import os
# from dotenv import load_dotenv
# import PyPDF2

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# # Load environment variables
# load_dotenv()
# BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000')

# # Initialize session state if not already set
# if "resume_url" not in st.session_state:
#     st.session_state.resume_url = None
# if "github_url" not in st.session_state:
#     st.session_state.github_url = None
# if "generated_feedback" not in st.session_state:
#     st.session_state.generated_feedback = None
# if "job_results" not in st.session_state:
#     st.session_state.job_results = {}
# if "processing_jobs" not in st.session_state:
#     st.session_state.processing_jobs = set()

# # Helper Functions
# def is_valid_github_url(url: str) -> bool:
#     """
#     Validate if the provided URL is a valid GitHub profile URL.
#     """
#     url = url.lstrip('@')
#     github_pattern = r'^https?://(?:www\.)?github\.com/[a-zA-Z0-9-]+(?:/[a-zA-Z0-9-_]+)*/?$'
#     if not re.match(github_pattern, url):
#         return False
#     try:
#         parts = url.split('github.com/')
#         return bool(parts[1].split('/')[0]) if len(parts) == 2 else False
#     except Exception:
#         return False

# def validate_pdf(pdf_file) -> (bool, str):
#     """
#     Validate if the uploaded file is a valid PDF.
#     """
#     try:
#         pdf_content = pdf_file.read()
#         pdf = PyPDF2.PdfReader(BytesIO(pdf_content))
#         if len(pdf.pages) < 1:
#             return False, "Empty PDF"
#         pdf_file.seek(0)
#         return True, "Valid PDF"
#     except Exception as e:
#         return False, f"Invalid PDF: {str(e)}"

# def process_github_profile(github_url: str) -> (bool, dict):
#     """
#     Process GitHub profile using the backend.
#     """
#     try:
#         response = requests.post(f"{BACKEND_API_URL}/api/process-github", json={"url": github_url})
#         if response.status_code == 200:
#             return True, response.json()
#         else:
#             return False, response.text
#     except Exception as e:
#         return False, str(e)

# def get_job_matches(profile_data: dict) -> (bool, dict):
#     """
#     Get job matches using the full user profile (including combined embedding and skills) by calling the backend.
#     """
#     try:
#         api_url = f"{BACKEND_API_URL}/api/match-jobs"
#         response = requests.post(api_url, json={"profile": profile_data})
#         if response.status_code == 200:
#             return True, response.json()
#         else:
#             try:
#                 return False, response.json()
#             except Exception:
#                 return False, response.text
#     except requests.exceptions.ConnectionError:
#         return False, f"Could not connect to backend at {BACKEND_API_URL}"
#     except Exception as e:
#         return False, str(e)

# def generate_feedback_and_cover_letter(resume_md_url: str, github_md_url: str, job_id: str):
#     try:
#         logger.info(f"Making request to generate cover letter and feedback for job_id: {job_id}")
        
#         # Ensure URLs don't have spaces (which could cause API errors)
#         resume_md_url = resume_md_url.replace(" ", "%20")
#         github_md_url = github_md_url.replace(" ", "%20")
        
#         payload = {
#             "resume_markdown_url": resume_md_url,
#             "github_markdown_url": github_md_url,
#             "job_id": job_id
#         }
        
#         # Log the full payload for debugging
#         logger.info(f"API payload: {payload}")
        
#         resp = requests.post(f"{BACKEND_API_URL}/api/generate-feedback-cover-letter", json=payload)
        
#         # Log the response status and content for debugging
#         logger.info(f"API response status: {resp.status_code}")
#         logger.info(f"API response content: {resp.text[:200]}...")  # Log first 200 chars
        
#         resp.raise_for_status()
#         return True, resp.json()
#     except Exception as e:
#         logger.error(f"Error in generate_feedback_and_cover_letter: {str(e)}")
#         return False, str(e)

# def fetch_full_job_details(job_id: str) -> dict:
#     """
#     Fetch job details from the backend by job_id.
#     """
#     try:
#         response = requests.get(f"{BACKEND_API_URL}/api/job-details/{job_id}")
#         if response.status_code == 200:
#             return response.json().get("metadata", {})
#         else:
#             return {}
#     except Exception:
#         return {}

# def format_bullet_section(title: str, items: list) -> str:
#     """
#     Format a list of items as a bullet list under a header.
#     """
#     if not items:
#         return f"#### {title}\n_Not provided._"
#     bullet_points = "\n".join([f"- {item.strip().capitalize()}" for item in items if item.strip()])
#     return f"#### {title}\n{bullet_points}"

# def handle_generate_feedback(job_id):
#     """
#     Callback function for generating feedback and cover letter
#     """
#     # Mark this job as being processed
#     st.session_state.processing_jobs.add(job_id)
    
#     resume_md_url = st.session_state.get("resume_markdown_url")
#     github_md_url = st.session_state.get("github_markdown_url")
    
#     logger.info(f"[DEBUG] resume_md_url: {resume_md_url}")
#     logger.info(f"[DEBUG] github_md_url: {github_md_url}")
    
#     # Ensure both URLs are available before calling the API
#     if not resume_md_url or not github_md_url:
#         st.session_state.job_results[job_id] = {
#             "success": False,
#             "result": "🚨 ERROR: resume/github markdown URL missing in session_state"
#         }
#         st.session_state.processing_jobs.discard(job_id)
#         return

#     success, result = generate_feedback_and_cover_letter(resume_md_url, github_md_url, job_id)
#     logger.info(f"API response: {result}")
#     logger.info(f"[DEBUG] API call success: {success}")
    
#     # Store results in session state
#     st.session_state.job_results[job_id] = {
#         "success": success,
#         "result": result
#     }
    
#     # Mark this job as no longer being processed
#     st.session_state.processing_jobs.discard(job_id)

# def display_job_match(match):
#     """
#     Display a single job match in an expandable container, with a button to generate cover letter & feedback.
#     """
#     job_id = match.get("job_id", "UNKNOWN")
#     full_meta = fetch_full_job_details(job_id)

#     company = full_meta.get("company", match.get("company", "N/A"))
#     job_title = match.get("job_title", "N/A")
#     location = full_meta.get("location", match.get("location", "Unknown"))
#     job_type = full_meta.get("job_type", match.get("job_type", "Unknown"))
#     work_mode = full_meta.get("work_mode", match.get("work_mode", "Unknown"))
#     seniority = full_meta.get("seniority", match.get("seniority", "Unknown"))
#     salary = full_meta.get("salary", match.get("salary", "Not Specified"))
#     experience = full_meta.get("experience", match.get("experience", "Not Specified"))
#     score = match.get("similarity_score", 0.0)

#     responsibilities = full_meta.get("responsibilities", "")
#     qualifications = full_meta.get("qualifications", "")
#     skills = match.get("skills", [])

#     # Container for the collapsible card
#     with st.container():
#         with st.expander(f"🔍 **{job_title}** at **{company}** — Score: {score:.2f}"):
#             st.markdown(f"""
#             ### 📌 Job Overview  
#             - **🏢 Company:** {company}  
#             - **📍 Location:** {location}  
#             - **💼 Type:** {job_type}  
#             - **🕒 Mode:** {work_mode}  
#             - **🎯 Seniority:** {seniority}  
#             - **💰 Salary:** {salary}  
#             - **📅 Experience:** {experience}  
#             - **💡 Similarity Score:** `{score:.2f}`
#             """, unsafe_allow_html=True)
#             st.markdown("---")
#             st.markdown(format_bullet_section("📋 Responsibilities", responsibilities.split(",")))
#             st.markdown(format_bullet_section("🎓 Qualifications", qualifications.split(",")))
#             st.markdown(format_bullet_section("🛠 Matching Skills", skills))

#             # Check if this job is currently being processed
#             is_processing = job_id in st.session_state.processing_jobs
#             has_results = job_id in st.session_state.job_results
            
#             # Only show the generate button if not processing and no results yet
#             if not is_processing and not has_results:
#                 st.button(f"📝 Generate Cover Letter & Feedback", 
#                         key=f"btn_{job_id}", 
#                         on_click=handle_generate_feedback, 
#                         args=(job_id,))
            
#             # Show spinner if processing
#             if is_processing:
#                 with st.spinner("🕐 Calling feedback API…"):
#                     st.info("Processing your request. This may take a minute...")
            
#             # Display results if available
#             if has_results:
#                 job_result = st.session_state.job_results[job_id]
                
#                 if job_result["success"]:
#                     st.markdown("### ✅ Generation Results")
#                     st.markdown(f"### 📄 Cover Letter\n{job_result['result'].get('cover_letter', '')}")
#                     st.markdown(f"### 💡 Feedback & Improvement Suggestions\n{job_result['result'].get('improvement_suggestions', '')}")
                    
#                     # Add a button to regenerate if needed
#                     if st.button(f"🔄 Regenerate", key=f"regen_{job_id}"):
#                         # Remove the job from results and trigger regeneration
#                         st.session_state.job_results.pop(job_id, None)
#                         handle_generate_feedback(job_id)
#                 else:
#                     st.error(f"❌ Error: {job_result['result']}")
#                     if st.button(f"🔄 Try Again", key=f"retry_{job_id}"):
#                         # Remove the job from results and trigger regeneration
#                         st.session_state.job_results.pop(job_id, None)
#                         handle_generate_feedback(job_id)

# # Main Frontend Workflow
# def main():
#     st.set_page_config(page_title="SkillMatch AI", page_icon="🤖", layout="centered")
#     st.title("SkillMatch AI – Smart Resume & GitHub Job Matcher")
#     st.markdown("Upload your resume (PDF) and provide your GitHub profile URL to get personalized job matches and generate tailored cover letters & feedback.")

#     github_url = st.text_input("🔗 GitHub Profile URL", placeholder="https://github.com/yourusername")
#     uploaded_file = st.file_uploader("📄 Upload Resume (PDF only)", type=["pdf"])

#     if st.button("🚀 Submit"):
#         if not github_url or not is_valid_github_url(github_url):
#             st.error("❌ Please enter a valid GitHub URL.")
#             return
#         if not uploaded_file:
#             st.error("❌ Please upload a resume.")
#             return

#         valid, pdf_msg = validate_pdf(uploaded_file)
#         if not valid:
#             st.error(f"❌ {pdf_msg}")
#             return

#         with st.spinner("⏳ Processing your profile..."):
#             # Process GitHub profile
#             github_success, github_result = process_github_profile(github_url)
#             if not github_success:
#                 st.error(github_result)
#                 return

#             # Process resume file via backend
#             files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
#             response = requests.post(f"{BACKEND_API_URL}/api/upload-resume", files=files, params={"github_url": github_url})
#             if response.status_code != 200:
#                 st.error("Resume processing failed.")
#                 return
            
#             data = response.json().get("data", {})
#             st.success("✅ Profile submitted successfully!")
#             st.balloons()

#             # Show profile summary
#             st.subheader("📊 Profile Summary")
#             st.markdown("### GitHub Info")
#             if github_result and "data" in github_result:
#                 st.write(f"👤 Username: {github_result['data'].get('username', 'N/A')}")
#                 st.write(f"📦 Repositories: {github_result['data'].get('repository_count', 'N/A')}")
#                 st.write(f"📄 READMEs Processed: {github_result['data'].get('readme_count', 'N/A')}")
#                 st.write(f"📝 GitHub Markdown: {github_result['data'].get('markdown_url', '')}")
#                 st.session_state["github_markdown_url"] = github_result['data'].get('markdown_url', '')

#             st.markdown("### Resume Info")
#             st.write(f"📄 Filename: {data.get('filename', '')}")
#             st.write(f"☁️ S3 URL: {data.get('resume_url', '')}")
#             st.write(f"📜 Markdown URL: {data.get('markdown_url', '')}")
#             st.session_state["resume_markdown_url"] = data.get("markdown_url", "")

#             # Prepare user profile for job matching
#             user_profile = {
#                 "combined_embedding": data.get("embeddings_info", {}).get("embedding", []),
#                 "all_skills": data.get("embeddings_info", {}).get("skills", []),
#                 "experience_year": data.get("experience_year", ""),
#                 "qualification": data.get("qualification", "")
#             }

#             # Find job matches
#             st.info("🔍 Finding job matches…")
#             matches_success, match_result = get_job_matches(user_profile)

#             if matches_success and match_result.get("status") == "success":
#                 st.success(f"🎯 Found {match_result.get('total_matches', 0)} job matches")
#                 st.subheader("Matching Jobs")
#                 for match in match_result.get("matches", []):
#                     display_job_match(match)  # Display each matched job
#             else:
#                 st.error(f"❌ Error matching jobs: {match_result.get('error', 'Unknown error')}")

# if __name__ == "__main__":
#     main()










































###########################################################################################
###########################################################################################
###########################################################################################
###########################################################################################
###########################################################################################

# THis code works perfect dont change as of now 


###########################################################################################
###########################################################################################
###########################################################################################
###########################################################################################
###########################################################################################     








# import logging
# import streamlit as st
# import requests
# import re
# from io import BytesIO
# import os
# from dotenv import load_dotenv
# import PyPDF2
# import boto3
# from urllib.parse import urlparse

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# # Load environment variables
# load_dotenv()
# BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000')

# # Initialize session state if not already set
# if "resume_url" not in st.session_state:
#     st.session_state.resume_url = None
# if "github_url" not in st.session_state:
#     st.session_state.github_url = None
# if "generated_feedback" not in st.session_state:
#     st.session_state.generated_feedback = None
# if "job_results" not in st.session_state:
#     st.session_state.job_results = {}
# if "processing_jobs" not in st.session_state:
#     st.session_state.processing_jobs = set()

# # Helper Functions
# def is_valid_github_url(url: str) -> bool:
#     """
#     Validate if the provided URL is a valid GitHub profile URL.
#     """
#     url = url.lstrip('@')
#     github_pattern = r'^https?://(?:www\.)?github\.com/[a-zA-Z0-9-]+(?:/[a-zA-Z0-9-_]+)*/?$'
#     if not re.match(github_pattern, url):
#         return False
#     try:
#         parts = url.split('github.com/')
#         return bool(parts[1].split('/')[0]) if len(parts) == 2 else False
#     except Exception:
#         return False

# def validate_pdf(pdf_file) -> (bool, str):
#     """
#     Validate if the uploaded file is a valid PDF.
#     """
#     try:
#         pdf_content = pdf_file.read()
#         pdf = PyPDF2.PdfReader(BytesIO(pdf_content))
#         if len(pdf.pages) < 1:
#             return False, "Empty PDF"
#         pdf_file.seek(0)
#         return True, "Valid PDF"
#     except Exception as e:
#         return False, f"Invalid PDF: {str(e)}"

# def process_github_profile(github_url: str) -> (bool, dict):
#     """
#     Process GitHub profile using the backend.
#     """
#     try:
#         response = requests.post(f"{BACKEND_API_URL}/api/process-github", json={"url": github_url})
#         if response.status_code == 200:
#             return True, response.json()
#         else:
#             return False, response.text
#     except Exception as e:
#         return False, str(e)

# def get_job_matches(profile_data: dict) -> (bool, dict):
#     """
#     Get job matches using the full user profile (including combined embedding and skills) by calling the backend.
#     """
#     try:
#         api_url = f"{BACKEND_API_URL}/api/match-jobs"
#         response = requests.post(api_url, json={"profile": profile_data})
#         if response.status_code == 200:
#             return True, response.json()
#         else:
#             try:
#                 return False, response.json()
#             except Exception:
#                 return False, response.text
#     except requests.exceptions.ConnectionError:
#         return False, f"Could not connect to backend at {BACKEND_API_URL}"
#     except Exception as e:
#         return False, str(e)

# def fetch_from_s3(s3_url):
#     """
#     Fetch content from an S3 URL
#     """
#     try:
#         # Parse the S3 URL
#         parsed_url = urlparse(s3_url)
#         bucket_name = parsed_url.netloc
#         key = parsed_url.path.lstrip('/')
        
#         # Initialize S3 client
#         s3_client = boto3.client('s3')
        
#         # Get the object
#         response = s3_client.get_object(Bucket=bucket_name, Key=key)
        
#         # Read the content
#         content = response['Body'].read().decode('utf-8')
        
#         return content
#     except Exception as e:
#         logger.error(f"Error fetching from S3: {str(e)}")
#         return ""

# def generate_feedback_and_cover_letter(resume_md_url: str, github_md_url: str, job_id: str):
#     try:
#         logger.info(f"Making request to generate cover letter and feedback for job_id: {job_id}")
        
#         # Fetch job details to get the job description
#         job_details = fetch_full_job_details(job_id)
#         job_description = ""
        
#         # Construct job description from available fields
#         if job_details:
#             company = job_details.get("company", "")
#             job_title = job_details.get("job_title", "")
#             responsibilities = job_details.get("responsibilities", "")
#             qualifications = job_details.get("qualifications", "")
            
#             job_description = f"Job Title: {job_title}\nCompany: {company}\n\nResponsibilities:\n{responsibilities}\n\nQualifications:\n{qualifications}"
        
#         # Fetch the content from S3 URLs
#         logger.info(f"Fetching resume content from: {resume_md_url}")
#         resume_content = fetch_from_s3(resume_md_url)
        
#         logger.info(f"Fetching GitHub profile content from: {github_md_url}")
#         github_content = fetch_from_s3(github_md_url)
        
#         # Combine the profile content
#         profile_text = f"RESUME:\n{resume_content}\n\nGITHUB PROFILE:\n{github_content}"
        
#         # Ensure URLs don't have spaces (which could cause API errors)
#         resume_md_url = resume_md_url.replace(" ", "%20")
#         github_md_url = github_md_url.replace(" ", "%20")
        
#         payload = {
#             "resume_markdown_url": resume_md_url,
#             "github_markdown_url": github_md_url,
#             "job_id": job_id,
#             "profile_text": profile_text,
#             "job_description": job_description
#         }
        
#         # Log the payload structure (not the full content for privacy)
#         logger.info(f"API payload structure: {list(payload.keys())}")
#         logger.info(f"Profile text length: {len(profile_text)}")
#         logger.info(f"Job description length: {len(job_description)}")
        
#         resp = requests.post(f"{BACKEND_API_URL}/api/generate-feedback-cover-letter", json=payload)
        
#         # Log the response status and content for debugging
#         logger.info(f"API response status: {resp.status_code}")
#         if resp.status_code != 200:
#             logger.info(f"API error response: {resp.text[:200]}...")
        
#         resp.raise_for_status()
#         return True, resp.json()
#     except Exception as e:
#         logger.error(f"Error in generate_feedback_and_cover_letter: {str(e)}")
#         return False, str(e)

# def fetch_full_job_details(job_id: str) -> dict:
#     """
#     Fetch job details from the backend by job_id.
#     """
#     try:
#         response = requests.get(f"{BACKEND_API_URL}/api/job-details/{job_id}")
#         if response.status_code == 200:
#             return response.json().get("metadata", {})
#         else:
#             return {}
#     except Exception:
#         return {}

# def format_bullet_section(title: str, items: list) -> str:
#     """
#     Format a list of items as a bullet list under a header.
#     """
#     if not items:
#         return f"#### {title}\n_Not provided._"
#     bullet_points = "\n".join([f"- {item.strip().capitalize()}" for item in items if item.strip()])
#     return f"#### {title}\n{bullet_points}"

# def handle_generate_feedback(job_id):
#     """
#     Callback function for generating feedback and cover letter
#     """
#     # Mark this job as being processed
#     st.session_state.processing_jobs.add(job_id)
    
#     resume_md_url = st.session_state.get("resume_markdown_url")
#     github_md_url = st.session_state.get("github_markdown_url")
    
#     logger.info(f"[DEBUG] resume_md_url: {resume_md_url}")
#     logger.info(f"[DEBUG] github_md_url: {github_md_url}")
    
#     # Ensure both URLs are available before calling the API
#     if not resume_md_url or not github_md_url:
#         st.session_state.job_results[job_id] = {
#             "success": False,
#             "result": "🚨 ERROR: resume/github markdown URL missing in session_state"
#         }
#         st.session_state.processing_jobs.discard(job_id)
#         return

#     success, result = generate_feedback_and_cover_letter(resume_md_url, github_md_url, job_id)
#     logger.info(f"API response: {result}")
#     logger.info(f"[DEBUG] API call success: {success}")
    
#     # Store results in session state
#     st.session_state.job_results[job_id] = {
#         "success": success,
#         "result": result
#     }
    
#     # Mark this job as no longer being processed
#     st.session_state.processing_jobs.discard(job_id)

# def display_job_match(match):
#     """
#     Display a single job match in an expandable container, with a button to generate cover letter & feedback.
#     """
#     job_id = match.get("job_id", "UNKNOWN")
#     full_meta = fetch_full_job_details(job_id)

#     company = full_meta.get("company", match.get("company", "N/A"))
#     job_title = match.get("job_title", "N/A")
#     location = full_meta.get("location", match.get("location", "Unknown"))
#     job_type = full_meta.get("job_type", match.get("job_type", "Unknown"))
#     work_mode = full_meta.get("work_mode", match.get("work_mode", "Unknown"))
#     seniority = full_meta.get("seniority", match.get("seniority", "Unknown"))
#     salary = full_meta.get("salary", match.get("salary", "Not Specified"))
#     experience = full_meta.get("experience", match.get("experience", "Not Specified"))
#     score = match.get("similarity_score", 0.0)

#     responsibilities = full_meta.get("responsibilities", "")
#     qualifications = full_meta.get("qualifications", "")
#     skills = match.get("skills", [])

#     # Container for the collapsible card
#     with st.container():
#         with st.expander(f"🔍 **{job_title}** at **{company}** — Score: {score:.2f}"):
#             st.markdown(f"""
#             ### 📌 Job Overview  
#             - **🏢 Company:** {company}  
#             - **📍 Location:** {location}  
#             - **💼 Type:** {job_type}  
#             - **🕒 Mode:** {work_mode}  
#             - **🎯 Seniority:** {seniority}  
#             - **💰 Salary:** {salary}  
#             - **📅 Experience:** {experience}  
#             - **💡 Similarity Score:** `{score:.2f}`
#             """, unsafe_allow_html=True)
#             st.markdown("---")
#             st.markdown(format_bullet_section("📋 Responsibilities", responsibilities.split(",")))
#             st.markdown(format_bullet_section("🎓 Qualifications", qualifications.split(",")))
#             st.markdown(format_bullet_section("🛠 Matching Skills", skills))

#             # Check if this job is currently being processed
#             is_processing = job_id in st.session_state.processing_jobs
#             has_results = job_id in st.session_state.job_results
            
#             # Only show the generate button if not processing and no results yet
#             if not is_processing and not has_results:
#                 st.button(f"📝 Generate Cover Letter & Feedback", 
#                         key=f"btn_{job_id}", 
#                         on_click=handle_generate_feedback, 
#                         args=(job_id,))
            
#             # Show spinner if processing
#             if is_processing:
#                 with st.spinner("🕐 Calling feedback API…"):
#                     st.info("Processing your request. This may take a minute...")
            
#             # Display results if available
#             if has_results:
#                 job_result = st.session_state.job_results[job_id]
                
#                 if job_result["success"]:
#                     st.markdown("### ✅ Generation Results")
                    
#                     # Check the structure of the result and display accordingly
#                     if isinstance(job_result["result"], dict):
#                         if "cover_letter" in job_result["result"]:
#                             st.markdown(f"### 📄 Cover Letter\n{job_result['result'].get('cover_letter', '')}")
                        
#                         if "improvement_suggestions" in job_result["result"]:
#                             st.markdown(f"### 💡 Feedback & Improvement Suggestions\n{job_result['result'].get('improvement_suggestions', '')}")
                        
#                         # If neither key exists, display the whole result
#                         if "cover_letter" not in job_result["result"] and "improvement_suggestions" not in job_result["result"]:
#                             st.markdown(f"### 📄 Results\n{job_result['result']}")
#                     else:
#                         st.markdown(f"### 📄 Results\n{job_result['result']}")
                    
#                     # Add a button to regenerate if needed
#                     if st.button(f"🔄 Regenerate", key=f"regen_{job_id}"):
#                         # Remove the job from results and trigger regeneration
#                         st.session_state.job_results.pop(job_id, None)
#                         handle_generate_feedback(job_id)
#                 else:
#                     st.error(f"❌ Error: {job_result['result']}")
#                     if st.button(f"🔄 Try Again", key=f"retry_{job_id}"):
#                         # Remove the job from results and trigger regeneration
#                         st.session_state.job_results.pop(job_id, None)
#                         handle_generate_feedback(job_id)

# # Main Frontend Workflow
# def main():
#     st.set_page_config(page_title="SkillMatch AI", page_icon="🤖", layout="centered")
#     st.title("SkillMatch AI – Smart Resume & GitHub Job Matcher")
#     st.markdown("Upload your resume (PDF) and provide your GitHub profile URL to get personalized job matches and generate tailored cover letters & feedback.")

#     # Debug toggle for session state inspection
#     if st.sidebar.checkbox("Debug Session State"):
#         st.sidebar.write("Processing Jobs:", st.session_state.processing_jobs)
#         st.sidebar.write("Job Results Keys:", list(st.session_state.job_results.keys()))
#         for job_id, result in st.session_state.job_results.items():
#             st.sidebar.write(f"Job {job_id}: Success={result['success']}")
#             if result["success"] and isinstance(result["result"], dict):
#                 st.sidebar.write(f"Result keys: {list(result['result'].keys())}")

#     github_url = st.text_input("🔗 GitHub Profile URL", placeholder="https://github.com/yourusername")
#     uploaded_file = st.file_uploader("📄 Upload Resume (PDF only)", type=["pdf"])

#     if st.button("🚀 Submit"):
#         if not github_url or not is_valid_github_url(github_url):
#             st.error("❌ Please enter a valid GitHub URL.")
#             return
#         if not uploaded_file:
#             st.error("❌ Please upload a resume.")
#             return

#         valid, pdf_msg = validate_pdf(uploaded_file)
#         if not valid:
#             st.error(f"❌ {pdf_msg}")
#             return

#         with st.spinner("⏳ Processing your profile..."):
#             # Process GitHub profile
#             github_success, github_result = process_github_profile(github_url)
#             if not github_success:
#                 st.error(github_result)
#                 return

#             # Process resume file via backend
#             files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
#             response = requests.post(f"{BACKEND_API_URL}/api/upload-resume", files=files, params={"github_url": github_url})
#             if response.status_code != 200:
#                 st.error("Resume processing failed.")
#                 return
            
#             data = response.json().get("data", {})
#             st.success("✅ Profile submitted successfully!")
#             st.balloons()

#             # Show profile summary
#             st.subheader("📊 Profile Summary")
#             st.markdown("### GitHub Info")
#             if github_result and "data" in github_result:
#                 st.write(f"👤 Username: {github_result['data'].get('username', 'N/A')}")
#                 st.write(f"📦 Repositories: {github_result['data'].get('repository_count', 'N/A')}")
#                 st.write(f"📄 READMEs Processed: {github_result['data'].get('readme_count', 'N/A')}")
#                 st.write(f"📝 GitHub Markdown: {github_result['data'].get('markdown_url', '')}")
#                 st.session_state["github_markdown_url"] = github_result['data'].get('markdown_url', '')

#             st.markdown("### Resume Info")
#             st.write(f"📄 Filename: {data.get('filename', '')}")
#             st.write(f"☁️ S3 URL: {data.get('resume_url', '')}")
#             st.write(f"📜 Markdown URL: {data.get('markdown_url', '')}")
#             st.session_state["resume_markdown_url"] = data.get("markdown_url", "")

#             # Prepare user profile for job matching
#             user_profile = {
#                 "combined_embedding": data.get("embeddings_info", {}).get("embedding", []),
#                 "all_skills": data.get("embeddings_info", {}).get("skills", []),
#                 "experience_year": data.get("experience_year", ""),
#                 "qualification": data.get("qualification", "")
#             }

#             # Find job matches
#             st.info("🔍 Finding job matches…")
#             matches_success, match_result = get_job_matches(user_profile)

#             if matches_success and match_result.get("status") == "success":
#                 st.success(f"🎯 Found {match_result.get('total_matches', 0)} job matches")
#                 st.subheader("Matching Jobs")
#                 for match in match_result.get("matches", []):
#                     display_job_match(match)  # Display each matched job
#             else:
#                 st.error(f"❌ Error matching jobs: {match_result.get('error', 'Unknown error')}")

# if __name__ == "__main__":
#     main()




#####################################################################################################
#####################################################################################################
#####################################################################################################
#####################################################################################################
#####################################################################################################


# CODE ENDED


#####################################################################################################
#####################################################################################################
#####################################################################################################
#####################################################################################################
#####################################################################################################












































#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$  
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# THis is the code with cover letter and feed back

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$  
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


# import logging
# import streamlit as st
# import requests
# import re
# from io import BytesIO
# import os
# from dotenv import load_dotenv
# import PyPDF2
# import boto3
# from urllib.parse import urlparse

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# # Load environment variables
# load_dotenv()
# BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000')

# # Initialize session state for persistence across reruns
# for key, default in [
#     ("resume_markdown_url", ""),
#     ("github_markdown_url", ""),
#     ("matches", []),
#     ("processing_jobs", set()),
#     ("job_results", {})
# ]:
#     if key not in st.session_state:
#         st.session_state[key] = default

# # --- Helper Functions ---

# def is_valid_github_url(url: str) -> bool:
#     url = url.lstrip('@')
#     pattern = r'^https?://(?:www\.)?github\.com/[A-Za-z0-9-]+(?:/[A-Za-z0-9-_]+)*/?$'
#     if not re.match(pattern, url):
#         return False
#     try:
#         return bool(url.split('github.com/')[1].split('/')[0])
#     except:
#         return False

# def validate_pdf(pdf_file) -> (bool, str):
#     try:
#         content = pdf_file.read()
#         pdf = PyPDF2.PdfReader(BytesIO(content))
#         if not pdf.pages:
#             return False, "Empty PDF"
#         pdf_file.seek(0)
#         return True, "Valid PDF"
#     except Exception as e:
#         return False, f"Invalid PDF: {e}"

# def process_github_profile(github_url: str) -> (bool, dict):
#     try:
#         resp = requests.post(f"{BACKEND_API_URL}/api/process-github", json={"url": github_url})
#         if resp.status_code == 200:
#             return True, resp.json()
#         return False, resp.text
#     except Exception as e:
#         return False, str(e)

# def get_job_matches(profile: dict) -> (bool, dict):
#     try:
#         resp = requests.post(f"{BACKEND_API_URL}/api/match-jobs", json={"profile": profile})
#         if resp.status_code == 200:
#             return True, resp.json()
#         try:
#             return False, resp.json()
#         except:
#             return False, resp.text
#     except Exception as e:
#         return False, str(e)

# def fetch_from_s3(s3_url: str) -> str:
#     try:
#         parsed = urlparse(s3_url)
#         bucket = parsed.netloc
#         key = parsed.path.lstrip('/')
#         s3 = boto3.client('s3')
#         obj = s3.get_object(Bucket=bucket, Key=key)
#         return obj['Body'].read().decode('utf-8')
#     except Exception as e:
#         logger.error(f"S3 fetch error: {e}")
#         return ""

# def fetch_full_job_details(job_id: str) -> dict:
#     try:
#         resp = requests.get(f"{BACKEND_API_URL}/api/job-details/{job_id}")
#         if resp.status_code == 200:
#             return resp.json().get("metadata", {})
#     except:
#         pass
#     return {}

# def format_bullet_section(title: str, items: list) -> str:
#     if not items:
#         return f"#### {title}\n_No information provided._"
#     bullets = "\n".join(f"- {itm.strip().capitalize()}" for itm in items if itm.strip())
#     return f"#### {title}\n{bullets}"

# # --- Callbacks ---

# def handle_generate_feedback(job_id: str):
#     st.session_state.processing_jobs.add(job_id)
#     resume_md = st.session_state.resume_markdown_url
#     github_md = st.session_state.github_markdown_url

#     if not resume_md or not github_md:
#         st.session_state.job_results[job_id] = {
#             "success": False,
#             "result": "Missing resume or GitHub markdown URL"
#         }
#         st.session_state.processing_jobs.discard(job_id)
#         return

#     # Fetch profile markdown
#     resume_txt = fetch_from_s3(resume_md)
#     github_txt = fetch_from_s3(github_md)
#     profile_text = f"RESUME:\n{resume_txt}\n\nGITHUB:\n{github_txt}"

#     # Fetch job description
#     jd = fetch_full_job_details(job_id)
#     job_desc = "\n".join([
#         f"Title: {jd.get('job_title','')}",
#         f"Company: {jd.get('company','')}",
#         "Responsibilities:\n" + jd.get('responsibilities',''),
#         "Qualifications:\n" + jd.get('qualifications','')
#     ])

#     payload = {
#         "resume_markdown_url": resume_md,
#         "github_markdown_url": github_md,
#         "job_id": job_id,
#         "profile_text": profile_text,
#         "job_description": job_desc
#     }

#     try:
#         resp = requests.post(f"{BACKEND_API_URL}/api/generate-feedback-cover-letter", json=payload)
#         resp.raise_for_status()
#         st.session_state.job_results[job_id] = {
#             "success": True,
#             "result": resp.json()
#         }
#     except Exception as e:
#         logger.error(f"Feedback API error: {e}")
#         st.session_state.job_results[job_id] = {
#             "success": False,
#             "result": str(e)
#         }
#     finally:
#         st.session_state.processing_jobs.discard(job_id)

# # --- UI Components ---

# def display_job_match(match: dict):
#     job_id = match.get("job_id")
#     meta = fetch_full_job_details(job_id)
#     title = match.get("job_title", "N/A")
#     company = meta.get("company", "N/A")
#     score = match.get("similarity_score", 0.0)

#     with st.container():
#         with st.expander(f"🔍 {title} @ {company} — Score: {score:.2f}"):
#             st.markdown(f"""
#             - **Location:** {meta.get('location','N/A')}
#             - **Type:** {meta.get('job_type','N/A')}
#             - **Mode:** {meta.get('work_mode','N/A')}
#             - **Seniority:** {meta.get('seniority','N/A')}
#             - **Experience:** {meta.get('experience','N/A')}
#             """)
#             st.markdown("---")
#             st.markdown(format_bullet_section("Responsibilities", meta.get("responsibilities","").split(",")))
#             st.markdown(format_bullet_section("Qualifications", meta.get("qualifications","").split(",")))
#             st.markdown(format_bullet_section("Matching Skills", match.get("skills", [])))

#             processing = job_id in st.session_state.processing_jobs
#             has_res   = job_id in st.session_state.job_results

#             if not processing and not has_res:
#                 st.button(
#                     "📝 Generate Cover Letter & Feedback",
#                     key=f"btn_{job_id}",
#                     on_click=handle_generate_feedback,
#                     args=(job_id,)
#                 )

#             if processing:
#                 st.info("Generating... please wait.")
#                 st.spinner("⏳")

#             if has_res:
#                 jr = st.session_state.job_results[job_id]
#                 if jr["success"]:
#                     out = jr["result"]
#                     cl = out.get("cover_letter", "")
#                     fb = out.get("improvement_suggestions", "")
#                     if cl:
#                         st.markdown("### 📄 Cover Letter")
#                         st.write(cl)
#                     if fb:
#                         st.markdown("### 💡 Feedback & Suggestions")
#                         st.write(fb)
#                     if st.button("🔄 Regenerate", key=f"regen_{job_id}"):
#                         st.session_state.job_results.pop(job_id, None)
#                         handle_generate_feedback(job_id)
#                 else:
#                     st.error(f"Error: {jr['result']}")
#                     if st.button("🔄 Retry", key=f"retry_{job_id}"):
#                         st.session_state.job_results.pop(job_id, None)
#                         handle_generate_feedback(job_id)

# # --- Main App ---

# def main():
#     st.set_page_config(page_title="SkillMatch AI", page_icon="🤖", layout="centered")
#     st.title("SkillMatch AI – Resume & GitHub Job Matcher")
#     st.markdown("Upload your resume (PDF) and GitHub URL to find jobs and generate tailored cover letters & feedback.")

#     github_url = st.text_input("🔗 GitHub Profile URL", placeholder="https://github.com/username")
#     uploaded_file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])

#     if st.button("🚀 Submit"):
#         if not is_valid_github_url(github_url):
#             st.error("Invalid GitHub URL.")
#             return
#         if not uploaded_file:
#             st.error("Please upload a PDF resume.")
#             return

#         valid, msg = validate_pdf(uploaded_file)
#         if not valid:
#             st.error(msg)
#             return

#         with st.spinner("Processing profile..."):
#             # GitHub
#             ok, gh = process_github_profile(github_url)
#             if not ok:
#                 st.error(f"GitHub error: {gh}")
#                 return
#             gh_data = gh.get("data", {})
#             st.session_state.github_markdown_url = gh_data.get("markdown_url", "")

#             # Resume
#             files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
#             resp = requests.post(
#                 f"{BACKEND_API_URL}/api/upload-resume",
#                 files=files,
#                 params={"github_url": github_url}
#             )
#             if resp.status_code != 200:
#                 st.error("Resume processing failed.")
#                 return
#             data = resp.json().get("data", {})
#             st.session_state.resume_markdown_url = data.get("markdown_url", "")

#             st.success("Profile submitted!")
#             st.balloons()

#             # Prepare user profile for matching
#             profile = {
#                 "combined_embedding": data.get("embeddings_info", {}).get("embedding", []),
#                 "all_skills": data.get("embeddings_info", {}).get("skills", []),
#                 "experience_year": data.get("experience_year", ""),
#                 "qualification": data.get("qualification", "")
#             }

#             # Fetch matches
#             ok, mr = get_job_matches(profile)
#             if ok and mr.get("status") == "success":
#                 st.success(f"Found {mr.get('total_matches',0)} matches")
#                 st.session_state.matches = mr.get("matches", [])
#             else:
#                 st.error(f"Matching error: {mr.get('error','Unknown')}")

#     # Always show matches if present
#     if st.session_state.matches:
#         st.subheader("🔍 Matching Jobs")
#         for m in st.session_state.matches:
#             display_job_match(m)

# if __name__ == "__main__":
#     main()











#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$  
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# THis is the code with cover letter and feed back    ended
 
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$  
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$










































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
    job_title = match.get("job_title", "N/A")
    company = meta.get("company", "N/A")
    score = match.get("similarity_score", 0.0)
    match_category = match.get("match_category", match.get("similarity_category", "unknown")).capitalize()

    with st.container():
        with st.expander(f"🔍 {title} @ {company} Match: {match_category}"):
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
                    if st.button("🔄 More Suggestions", key=f"regen_{job_id}"):
                        # st.session_state.job_results.pop(job_id, None)
                        # handle_generate_feedback(job_id)
                        with st.spinner("Fetching more suggestions..."):
                            suggestions = fetch_more_suggestions(company, job_title)
                            display_more_suggestions(suggestions)
                else:
                    st.error(f"Error: {jr['result']}")
                    if st.button("🔄 Retry", key=f"retry_{job_id}"):
                        st.session_state.job_results.pop(job_id, None)
                        handle_generate_feedback(job_id)








def fetch_more_suggestions(company_name, job_title):
    try:
        response = requests.post(
            f"{BACKEND_API_URL}/api/webagent",
            json={"company": company_name, "job_query": job_title}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"❌ Error fetching suggestions: {str(e)}")
        return None

def display_more_suggestions(data):
    if data and data["status"] == "success":
        company_info = data.get("company_info", {})
        similar_jobs = data.get("similar_jobs", [])

        st.markdown("## 📌 Company Overview")
        st.write(company_info.get("overview", "No overview available."))

        st.markdown("## 🌐 Career Page")
        st.write(company_info.get("career_site_url", "Not available"))

        st.markdown("## 🧠 Company Culture")
        st.write(company_info.get("culture", "Not available"))

        st.markdown("## 🛠️ Tech Stack / Projects")
        st.write(company_info.get("technology", "Not available"))

        st.markdown("## 🏆 Achievements & Awards")
        st.write(company_info.get("achievements", "Not available"))

        st.markdown("## 🔍 Suggested Jobs")
        for job in similar_jobs:
            title = job.get("job_title", "Untitled Job")
        company = job.get("company", "N/A")
        location = job.get("location", "Unknown")
        job_type = job.get("job_type", "Unknown")
        work_mode = job.get("work_mode", "Unknown")
        responsibilities = job.get("responsibilities", "Not specified")
        skills = job.get("skills", [])

        st.markdown("---")
        st.markdown(f"""
        ### 🧳 {title}  
        **🏢 Company:** {company}  
        **📍 Location:** {location} | **🕒 Type:** {job_type} | **🏷️ Mode:** {work_mode}  

        **📋 Responsibilities:**  
        {format_bullet_list(responsibilities.split(','))}

        **🧠 Skills:**  
        {", ".join(skills)}
        """, unsafe_allow_html=True)
    else:
        st.error("❌ Failed to load suggestions.")

def format_bullet_list(items):
    return "\n".join([f"- {item.strip()}" for item in items if item.strip()])
# Assume this function is called after generating feedback or cover letters
def after_feedback_ui(company_name, job_title):
    if st.button("🔄 More Suggestions", key=f"more_suggestions_{company_name}_{job_title}"):
        with st.spinner("Fetching more job suggestions and company info..."):
            suggestion_data = fetch_more_suggestions(company_name, job_title)
            display_more_suggestions(suggestion_data)









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


            data = response.json().get("data", {})
            st.success("✅ Profile submitted successfully!")
            
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

            if match_success and match_result.get("status") == "success":
                st.success(f"🎯 Found {match_result['total_matches']} job matches")
                for match in match_result["matches"]:
                    display_job_match(match)
            else:
                st.error(f"Matching error: {mr.get('error','Unknown')}")

    # Always show matches if present
    if st.session_state.matches:
        st.subheader("🔍 Matching Jobs")
        for m in st.session_state.matches:
            display_job_match(m)

if __name__ == "__main__":
    main()
