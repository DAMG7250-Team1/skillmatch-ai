





# import os
# import sys
# import json
# import logging
# import string
# import hashlib
# import re
# import boto3
# from botocore.exceptions import ClientError
# from datetime import datetime
# from pathlib import Path
# from dotenv import load_dotenv
# from typing import List, Dict, Any, Optional, Union

# # Load environment variables
# load_dotenv()

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# # Add parent directory to path for importing other modules (avoid self‐import)
# sys.path.append(str(Path(__file__).parent.parent))

# from openai import OpenAI
# from pinecone import Pinecone

# class UserEmbeddingProcessor:
#     """
#     Processes a user's profile from resume and GitHub markdown files.
#     It extracts comprehensive skills, computes detailed experience (senority) from the EXPERIENCE section only,
#     extracts education/qualification data from the EDUCATION section,
#     generates a combined embedding for the profile, and produces GitHub feedback with improvement suggestions.
    
#     The combined profile is saved as a JSON file to S3, and the embedding is upserted to Pinecone under a specific namespace.
    
#     The Pinecone metadata includes:
#       - combined_markdown_url: S3 URL where the combined profile is saved.
#       - git_repo: GitHub repository URL.
#       - github_feedback: Feedback summary for the GitHub profile.
#       - github_skills: List of skills extracted from GitHub.
#       - qualification: Education details extracted from the EDUCATION section.
#       - resume_s3: S3 URL of the resume markdown.
#       - resume_skills: List of skills extracted from the resume.
#       - senority: A JSON string that contains the total experience (in months, years) and level,
#                    extracted only from the EXPERIENCE section.
#       - source: "userprofile"
#       - user_id: the user’s ID.
#       - combined_text_hash: MD5 hash of the combined text.
#     """
    
#     def __init__(self):
#         # Initialize S3 client.
#         self.aws_bucket_name = os.getenv('AWS_BUCKET_NAME', 'skillmatchai')
#         self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
#         self.s3_client = boto3.client(
#             's3',
#             aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#             aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
#             region_name=self.aws_region
#         )
#         # Initialize OpenAI client.
#         self.openai_api_key = os.getenv('OPENAI_API_KEY')
#         if not self.openai_api_key:
#             raise ValueError("OpenAI API key not found in environment variables")
#         self.openai_client = OpenAI(api_key=self.openai_api_key)
        
#         # Initialize Pinecone client.
#         self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
#         if not self.pinecone_api_key:
#             raise ValueError("Pinecone API key not found in environment variables")
#         self.pc = Pinecone(api_key=self.pinecone_api_key)
#         self.pinecone_index_name = os.getenv('PINECONE_INDEX_NAME', 'skillmatch')
#         self.index = self.pc.Index(self.pinecone_index_name)
        
#         # Use a specific namespace for user profiles.
#         self.pinecone_user_namespace = os.getenv('PINECONE_USER_NAMESPACE', 'userprofile')
#         logger.info(f"Connected to Pinecone index: {self.pinecone_index_name}, using namespace: {self.pinecone_user_namespace}")

#     def _read_markdown_from_s3(self, s3_url: str) -> str:
#         """Read markdown content from an S3 URL."""
#         try:
#             s3_url_clean = s3_url.replace("s3://", "")
#             parts = s3_url_clean.split("/", 1)
#             bucket = parts[0]
#             key = parts[1]
#             logger.info(f"Fetching from bucket: {bucket}, key: {key}")
#             response = self.s3_client.get_object(Bucket=bucket, Key=key)
#             text = response['Body'].read().decode('utf-8')
#             logger.info(f"Successfully fetched markdown from {s3_url} (size: {len(text)} bytes)")
#             return text
#         except ClientError as e:
#             logger.error(f"Error reading from S3: {str(e)}")
#             raise
#         except Exception as e:
#             logger.error(f"Unexpected error reading from S3: {str(e)}")
#             raise

#     def extract_all_skills_from_text(self, text: str) -> List[str]:
#         """Extract all technical skills from the given text using an LLM prompt."""
#         prompt = f"""
# Extract all technical skills, tools, frameworks, and programming languages from the text below.
# Consider sections such as "TECHNICAL SKILLS", "EXPERIENCE", and "PROJECTS".
# Return ONLY a comma-separated list with no extra commentary.
# Example: Python, JavaScript, React, SQL, Docker

# Text:
# {text}
#         """
#         try:
#             response = self.openai_client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "Extract all technical skills accurately."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.0,
#                 max_tokens=250
#             )
#             skills_text = response.choices[0].message.content.strip()
#             skills_list = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
#             logger.info(f"Extracted {len(skills_list)} skills from text")
#             return skills_list
#         except Exception as e:
#             logger.error(f"Error extracting skills: {str(e)}")
#             return []
    
#     def get_combined_embedding(self, resume_text: str, github_text: Optional[str] = None) -> List[float]:
#         """Generate a combined embedding for the user's profile by concatenating resume and GitHub texts."""
#         combined_text = resume_text + " " + (github_text or "")
#         try:
#             response = self.openai_client.embeddings.create(
#                 model="text-embedding-3-large",
#                 input=combined_text
#             )
#             embedding = response.data[0].embedding
#             logger.info("Generated combined embedding for user profile")
#             return embedding
#         except Exception as e:
#             logger.error(f"Error generating combined embedding: {str(e)}")
#             raise

#     def _extract_section(self, text: str, section_title: str) -> str:
#         """
#         Extract the section of the text that follows a given section header.
#         Assumes headers start with '#' and are on their own line.
#         Returns the section text until the next header or end of text.
#         """
#         # Split text into lines.
#         lines = text.splitlines()
#         capture = False
#         section_lines = []
#         header_pattern = re.compile(r"^#")
#         for line in lines:
#             if capture:
#                 # Stop capturing if a new header is found.
#                 if header_pattern.match(line.strip()):
#                     break
#                 section_lines.append(line)
#             else:
#                 if section_title.lower() in line.lower():
#                     capture = True
#         section_text = "\n".join(section_lines).strip()
#         logger.info(f"Extracted section '{section_title}' with {len(section_text)} characters")
#         return section_text

#     def extract_experience_details(self, resume_text: str) -> Dict[str, Union[float, str]]:
#         """
#         Extract detailed professional experience from the EXPERIENCE section of the resume.
#         Sums referenced durations (e.g., "9 months", "1 year") and classifies the senority level.
        
#         Rules:
#           - Entry Level: less than 24 months.
#           - Mid Level: 24 to 60 months.
#           - Senior Level: more than 60 months.
          
#         Returns a dictionary containing:
#           "total_experience_months", "total_experience_years", and "level".
#         """
#         experience_section = self._extract_section(resume_text, "EXPERIENCE")
#         if not experience_section:
#             logger.warning("No EXPERIENCE section found; defaulting to zero experience.")
#             return {"total_experience_months": 0, "total_experience_years": 0, "level": "Entry Level"}
        
#         prompt = f"""
# Analyze the EXPERIENCE section of the resume below and identify all references to durations of professional experience 
# (e.g., "9 months", "1 year", "2 years 3 months") that pertain to job positions.
# Sum these durations to calculate the total months of experience.
# Then convert the total months into years (ignoring remainders) and classify the senority level as follows:
# - Entry Level: less than 24 months.
# - Mid Level: between 24 and 60 months.
# - Senior Level: more than 60 months.
# Return a JSON string with keys:
#     "total_experience_months": <number>,
#     "total_experience_years": <number>,
#     "level": <string>
# If no valid duration is found, return {{"total_experience_months": 0, "total_experience_years": 0, "level": "Entry Level"}}.
# EXPERIENCE Section:
# {experience_section}
#         """
#         try:
#             response = self.openai_client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "Extract and sum up job experience durations from the EXPERIENCE section."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.0,
#                 max_tokens=100
#             )
#             result_text = response.choices[0].message.content.strip()
#             try:
#                 details = json.loads(result_text)
#                 total_months = float(details.get("total_experience_months", 0))
#                 total_years = int(details.get("total_experience_years", total_months // 12))
#                 level = details.get("level", "Entry Level")
#             except Exception:
#                 total_months, total_years, level = 0, 0, "Entry Level"
#             logger.info(f"Extracted experience (from EXPERIENCE section): {total_months} months ({total_years} years), level: {level}")
#             return {"total_experience_months": total_months, "total_experience_years": total_years, "level": level}
#         except Exception as e:
#             logger.error(f"Error extracting experience details: {str(e)}")
#             return {"total_experience_months": 0, "total_experience_years": 0, "level": "Entry Level"}

#     def extract_education_details(self, resume_text: str) -> str:
#         """
#         Extract qualification details from the EDUCATION section of the resume.
#         This should include degree(s) being pursued or earned, institution names,
#         and any relevant academic achievements.
        
#         Returns a string summary (or empty string if none found).
#         """
#         education_section = self._extract_section(resume_text, "EDUCATION")
#         if not education_section:
#             logger.warning("No EDUCATION section found.")
#             return ""
        
#         prompt = f"""
# Extract a concise summary of the education details from the EDUCATION section below.
# Include details such as degree(s), institution names, and completion or expected dates if available.
# Return the summary as plain text.

# EDUCATION Section:
# {education_section}
#         """
#         try:
#             response = self.openai_client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "Extract education qualification details from the EDUCATION section."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.0,
#                 max_tokens=150
#             )
#             education_details = response.choices[0].message.content.strip()
#             logger.info("Extracted education details from resume")
#             return education_details
#         except Exception as e:
#             logger.error(f"Error extracting education details: {str(e)}")
#             return ""
    
#     def generate_github_feedback(self, github_text: str) -> str:
#         """
#         Generate concise, constructive feedback for the GitHub profile,
#         including suggestions for improvement.
#         """
#         prompt = f"""
# Provide a concise and constructive feedback summary for the GitHub profile described in the text below.
# Your feedback should include:
#   - Strengths observed,
#   - Areas for improvement,
#   - Suggestions for enhancing the profile (e.g., adding more project details, improving documentation, or writing technical blogs).
# Return only a one- or two-sentence summary.

# Text:
# {github_text}
#         """
#         try:
#             response = self.openai_client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "Provide detailed and constructive feedback for a GitHub profile."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.2,
#                 max_tokens=150
#             )
#             feedback = response.choices[0].message.content.strip()
#             logger.info("Generated GitHub feedback with improvement suggestions")
#             return feedback
#         except Exception as e:
#             logger.error(f"Error generating GitHub feedback: {str(e)}")
#             return ""
    
#     def save_combined_profile_to_s3(self, user_id: str, combined_text: str, embedding: List[float]) -> str:
#         """
#         Save the combined markdown text and its embedding to S3 as a JSON file.
#         The file is stored under:
#             user_profiles/{user_id}/{timestamp}_combined.json
#         Returns the S3 URL of the saved file.
#         """
#         try:
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             key = f"user_profiles/{user_id}/{timestamp}_combined.json"
#             data = {
#                 "combined_text": combined_text,
#                 "embedding": embedding,
#                 "timestamp": datetime.now().isoformat()
#             }
#             json_data = json.dumps(data, ensure_ascii=False)
#             self.s3_client.put_object(
#                 Bucket=self.aws_bucket_name,
#                 Key=key,
#                 Body=json_data.encode('utf-8'),
#                 ContentType='application/json'
#             )
#             s3_url = f"s3://{self.aws_bucket_name}/{key}"
#             logger.info(f"Saved combined profile to {s3_url}")
#             return s3_url
#         except Exception as e:
#             logger.error(f"Error saving combined profile to S3: {str(e)}")
#             raise
    
#     def upsert_profile_to_pinecone(self, user_id: str, combined_text: str, embedding: List[float],
#                                      extra_metadata: Dict[str, Any]) -> None:
#         """
#         Upsert the user's combined embedding to Pinecone under the specified namespace.
#         The vector ID is generated using the user_id and an MD5 hash of the combined text (to reduce duplication).
#         For non-primitive metadata values, such as the experience dictionary, the value is stored as a JSON string.
#         """
#         try:
#             text_hash = hashlib.md5(combined_text.encode('utf-8')).hexdigest()
#             vector_id = f"{user_id}_{text_hash}"
#             # Merge extra metadata with basic fields and convert non-primitive types to strings.
#             metadata = {
#                 "combined_markdown_url": extra_metadata.get("combined_markdown_url", ""),
#                 "git_repo": extra_metadata.get("git_repo", ""),
#                 "github_feedback": extra_metadata.get("github_feedback", ""),
#                 "github_skills": extra_metadata.get("github_skills", []),
#                 "qualification": extra_metadata.get("qualification", []),
#                 "resume_s3": extra_metadata.get("resume_s3", ""),
#                 "resume_skills": extra_metadata.get("resume_skills", []),
#                 "senority": json.dumps(extra_metadata.get("senority", {})),  # store as JSON string
#                 "source": "userprofile",
#                 "user_id": user_id,
#                 "combined_text_hash": text_hash
#             }
#             self.index.upsert(
#                 vectors=[(vector_id, embedding, metadata)],
#                 namespace=self.pinecone_user_namespace
#             )
#             logger.info(f"Upserted vector for user {user_id} with ID {vector_id} into Pinecone namespace '{self.pinecone_user_namespace}'")
#         except Exception as e:
#             logger.error(f"Error upserting profile to Pinecone: {str(e)}")
#             raise

#     def process_user_data(self, resume_url: str, github_url: Optional[str] = None,
#                           git_repo: str = "", qualification: Optional[List[str]] = None) -> Dict[str, Any]:
#         """
#         Process user data from resume and optional GitHub markdown URLs.
#         It:
#           - Reads resume and GitHub markdown from S3.
#           - Extracts skills from both sources and deduplicates them.
#           - Generates a combined embedding.
#           - Saves the combined profile to S3.
#           - Upserts the embedding to Pinecone (with additional metadata).
#           - Extracts detailed experience from the EXPERIENCE section only.
#           - Extracts education qualification details from the EDUCATION section.
#           - Generates GitHub feedback.
#         Returns a dictionary containing:
#           - combined_embedding: The profile embedding.
#           - all_skills: Deduplicated list of skills.
#           - senority: Detailed experience information.
#           - qualification: Education details.
#           - github_feedback: GitHub feedback.
#           - sources: Extraction info from each source.
#           - combined_profile_url: S3 URL where the combined profile is stored.
#         """
#         try:
#             resume_text = self._read_markdown_from_s3(resume_url)
#             github_text = self._read_markdown_from_s3(github_url) if github_url else ""
            
#             # Extract skills.
#             resume_skills = self.extract_all_skills_from_text(resume_text)
#             github_skills = self.extract_all_skills_from_text(github_text) if github_text else []
#             all_skills = list({skill for skill in resume_skills + github_skills})
            
#             # Generate the combined embedding.
#             combined_embedding = self.get_combined_embedding(resume_text, github_text)
            
#             # Prepare combined text.
#             combined_text = resume_text + "\n" + github_text
            
#             # Save the combined profile to S3.
#             user_id = "test_user_123"  # Adjust as needed.
#             combined_profile_url = self.save_combined_profile_to_s3(user_id, combined_text, combined_embedding)
            
#             # Prepare extra metadata.
#             extra_metadata = {
#                 "combined_markdown_url": combined_profile_url,
#                 "git_repo": git_repo,
#                 "github_feedback": self.generate_github_feedback(github_text) if github_text else "",
#                 "github_skills": github_skills,
#                 "qualification": self.extract_education_details(resume_text),  # New extraction for EDUCATION details.
#                 "resume_s3": resume_url,
#                 "resume_skills": resume_skills,
#                 "senority": self.extract_experience_details(resume_text)  # From EXPERIENCE section only.
#             }
            
#             # Upsert the embedding to Pinecone.
#             self.upsert_profile_to_pinecone(user_id, combined_text, combined_embedding, extra_metadata)
            
#             user_data = {
#                 "combined_embedding": combined_embedding,
#                 "all_skills": all_skills,
#                 "senority": extra_metadata["senority"],
#                 "qualification": extra_metadata["qualification"],
#                 "github_feedback": extra_metadata["github_feedback"],
#                 "sources": [
#                     {"type": "resume", "extracted_skills": resume_skills},
#                     {"type": "github", "extracted_skills": github_skills}
#                 ],
#                 "combined_profile_url": combined_profile_url
#             }
#             logger.info(f"User data processed with {len(all_skills)} unique skills, experience: {extra_metadata['senority']}, and qualification: {extra_metadata['qualification']}")
#             return user_data
#         except Exception as e:
#             logger.error(f"Error processing user data: {str(e)}")
#             raise
    
#     def extract_education_details(self, resume_text: str) -> str:
#         """
#         Extract a summary of educational qualifications from the EDUCATION section of the resume.
#         Returns a summary string (or an empty string if not found).
#         """
#         education_section = self._extract_section(resume_text, "EDUCATION")
#         if not education_section:
#             logger.warning("No EDUCATION section found.")
#             return ""
#         prompt = f"""
# Extract a concise summary of the educational qualifications from the EDUCATION section below.
# Include details such as the degree being pursued or earned, the institution(s), and any relevant dates.
# Return the summary as plain text.

# EDUCATION Section:
# {education_section}
#         """
#         try:
#             response = self.openai_client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "Extract education qualification details from the EDUCATION section."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.0,
#                 max_tokens=150
#             )
#             education_details = response.choices[0].message.content.strip()
#             logger.info("Extracted education details from resume")
#             return education_details
#         except Exception as e:
#             logger.error(f"Error extracting education details: {str(e)}")
#             return ""
    
#     def _extract_section(self, text: str, section_title: str) -> str:
#         """
#         Extract a section from the text based on the given section header.
#         Assumes section headers start with '#' and are on their own line.
#         Returns the content of the section until the next header or end of text.
#         """
#         lines = text.splitlines()
#         capture = False
#         section_lines = []
#         for line in lines:
#             if capture:
#                 if line.strip().startswith("#"):
#                     break
#                 section_lines.append(line)
#             elif section_title.lower() in line.lower():
#                 capture = True
#         section_text = "\n".join(section_lines).strip()
#         logger.info(f"Extracted '{section_title}' section with {len(section_text)} characters")
#         return section_text

#     def generate_github_feedback(self, github_text: str) -> str:
#         """(Already defined above) Generate GitHub feedback."""
#         prompt = f"""
# Provide a concise and constructive feedback summary for the GitHub profile described in the text below.
# Your feedback should include:
#   - Strengths observed,
#   - Areas for improvement,
#   - Suggestions for enhancing the profile (e.g., adding more project details, improving documentation, or writing technical blogs).
# Return only a one- or two-sentence summary.

# Text:
# {github_text}
#         """
#         try:
#             response = self.openai_client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "Provide detailed and constructive feedback for a GitHub profile."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.2,
#                 max_tokens=150
#             )
#             feedback = response.choices[0].message.content.strip()
#             logger.info("Generated GitHub feedback with improvement suggestions")
#             return feedback
#         except Exception as e:
#             logger.error(f"Error generating GitHub feedback: {str(e)}")
#             return ""
    
#     def save_combined_profile_to_s3(self, user_id: str, combined_text: str, embedding: List[float]) -> str:
#         """
#         Save the combined markdown text and its embedding to S3 as a JSON file.
#         The file is stored under: user_profiles/{user_id}/{timestamp}_combined.json
#         Returns the S3 URL.
#         """
#         try:
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             key = f"user_profiles/{user_id}/{timestamp}_combined.json"
#             data = {
#                 "combined_text": combined_text,
#                 "embedding": embedding,
#                 "timestamp": datetime.now().isoformat()
#             }
#             json_data = json.dumps(data, ensure_ascii=False)
#             self.s3_client.put_object(
#                 Bucket=self.aws_bucket_name,
#                 Key=key,
#                 Body=json_data.encode('utf-8'),
#                 ContentType='application/json'
#             )
#             s3_url = f"s3://{self.aws_bucket_name}/{key}"
#             logger.info(f"Saved combined profile to {s3_url}")
#             return s3_url
#         except Exception as e:
#             logger.error(f"Error saving combined profile to S3: {str(e)}")
#             raise
    
#     def upsert_profile_to_pinecone(self, user_id: str, combined_text: str, embedding: List[float],
#                                      extra_metadata: Dict[str, Any]) -> None:
#         """
#         Upsert the user's combined embedding to Pinecone under the specified namespace.
#         The vector ID is generated as "{user_id}_{md5_hash}" and extra metadata (including senority and qualification)
#         is stored. Non-primitive metadata (such as senority) is converted to a JSON string.
#         """
#         try:
#             text_hash = hashlib.md5(combined_text.encode('utf-8')).hexdigest()
#             vector_id = f"{user_id}_{text_hash}"
#             metadata = {
#                 "combined_markdown_url": extra_metadata.get("combined_markdown_url", ""),
#                 "git_repo": extra_metadata.get("git_repo", ""),
#                 "github_feedback": extra_metadata.get("github_feedback", ""),
#                 "github_skills": extra_metadata.get("github_skills", []),
#                 "qualification": extra_metadata.get("qualification", ""),
#                 "resume_s3": extra_metadata.get("resume_s3", ""),
#                 "resume_skills": extra_metadata.get("resume_skills", []),
#                 "senority": json.dumps(extra_metadata.get("senority", {})),  # convert to JSON string
#                 "source": "userprofile",
#                 "user_id": user_id,
#                 "combined_text_hash": text_hash
#             }
#             self.index.upsert(
#                 vectors=[(vector_id, embedding, metadata)],
#                 namespace=self.pinecone_user_namespace
#             )
#             logger.info(f"Upserted vector for user {user_id} with ID {vector_id} into Pinecone namespace '{self.pinecone_user_namespace}'")
#         except Exception as e:
#             logger.error(f"Error upserting profile to Pinecone: {str(e)}")
#             raise
    
#     def process_user_data(self, resume_url: str, github_url: Optional[str] = None,
#                           git_repo: str = "", qualification: Optional[List[str]] = None) -> Dict[str, Any]:
#         """
#         Process user data from resume and optional GitHub markdown URLs.
#         It reads the markdown from S3, extracts skills, generates a combined embedding, extracts detailed experience from the EXPERIENCE section,
#         extracts education details from the EDUCATION section, generates GitHub feedback, saves the combined profile to S3, upserts the embedding to Pinecone, 
#         and returns a dictionary with the combined embedding, all skills, experience (senority), qualification (education summary),
#         GitHub feedback, source extraction info, and the S3 URL of the combined profile.
#         """
#         try:
#             resume_text = self._read_markdown_from_s3(resume_url)
#             github_text = self._read_markdown_from_s3(github_url) if github_url else ""
            
#             # Extract skills.
#             resume_skills = self.extract_all_skills_from_text(resume_text)
#             github_skills = self.extract_all_skills_from_text(github_text) if github_text else []
#             all_skills = list({skill for skill in resume_skills + github_skills})
            
#             # Generate combined embedding.
#             combined_embedding = self.get_combined_embedding(resume_text, github_text)
            
#             # Prepare combined text.
#             combined_text = resume_text + "\n" + github_text
            
#             # Save combined profile to S3.
#             user_id = "test_user_123"  # Adjust as needed.
#             combined_profile_url = self.save_combined_profile_to_s3(user_id, combined_text, combined_embedding)
            
#             # Prepare extra metadata.
#             extra_metadata = {
#                 "combined_markdown_url": combined_profile_url,
#                 "git_repo": git_repo,
#                 "github_feedback": self.generate_github_feedback(github_text) if github_text else "",
#                 "github_skills": github_skills,
#                 # For qualification, extract details from the EDUCATION section.
#                 "qualification": self.extract_education_details(resume_text),
#                 "resume_s3": resume_url,
#                 "resume_skills": resume_skills,
#                 # Extract experience details from the EXPERIENCE section only.
#                 "senority": self.extract_experience_details(resume_text)
#             }
            
#             # Upsert the user profile embedding into Pinecone.
#             self.upsert_profile_to_pinecone(user_id, combined_text, combined_embedding, extra_metadata)
            
#             user_data = {
#                 "combined_embedding": combined_embedding,
#                 "all_skills": all_skills,
#                 "senority": extra_metadata["senority"],
#                 "qualification": extra_metadata["qualification"],
#                 "github_feedback": extra_metadata["github_feedback"],
#                 "sources": [
#                     {"type": "resume", "extracted_skills": resume_skills},
#                     {"type": "github", "extracted_skills": github_skills}
#                 ],
#                 "combined_profile_url": combined_profile_url
#             }
#             logger.info(f"User data processed with {len(all_skills)} unique skills, experience: {extra_metadata['senority']}, and qualification: {extra_metadata['qualification']}")
#             return user_data
#         except Exception as e:
#             logger.error(f"Error processing user data: {str(e)}")
#             raise
    
#     def extract_education_details(self, resume_text: str) -> str:
#         """
#         Extract a summary of education qualifications from the EDUCATION section of the resume.
#         This should include degree(s), institution name(s), and relevant dates.
#         Returns a summary string or an empty string if not found.
#         """
#         education_section = self._extract_section(resume_text, "EDUCATION")
#         if not education_section:
#             logger.warning("No EDUCATION section found.")
#             return ""
#         prompt = f"""
# Extract a concise summary of the educational qualifications from the EDUCATION section below.
# Include details such as the degree being pursued or earned, the institution(s), and the completion/expected date.
# Return the summary as plain text.

# EDUCATION Section:
# {education_section}
#         """
#         try:
#             response = self.openai_client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "Extract education qualification details from the EDUCATION section."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.0,
#                 max_tokens=150
#             )
#             education_details = response.choices[0].message.content.strip()
#             logger.info("Extracted education details from resume")
#             return education_details
#         except Exception as e:
#             logger.error(f"Error extracting education details: {str(e)}")
#             return ""
    
#     def _extract_section(self, text: str, section_title: str) -> str:
#         """
#         Extract a section from the text based on the given section header.
#         Looks for a line containing the section title (case-insensitive) and returns all following lines until a new header is found.
#         """
#         lines = text.splitlines()
#         capture = False
#         section_lines = []
#         for line in lines:
#             if capture:
#                 if line.strip().startswith("#"):
#                     break
#                 section_lines.append(line)
#             elif section_title.lower() in line.lower():
#                 capture = True
#         section_text = "\n".join(section_lines).strip()
#         logger.info(f"Extracted '{section_title}' section with {len(section_text)} characters")
#         return section_text

# if __name__ == "__main__":
#     # Example usage when running this module directly.
#     resume_url = "s3://skillmatchai/resume/markdown/20250411_200621_AUM-JS-python-Doc.md"
#     github_url = "s3://skillmatchai/github/markdown/20250411_200617_Aumpatelarjun_github_profile.md"
#     git_repo = "https://github.com/Aumpatelarjun"
#     qualification = []  # Will be filled from EDUCATION section.
    
#     processor = UserEmbeddingProcessor()
#     user_profile = processor.process_user_data(resume_url, github_url, git_repo, qualification)
#     print(json.dumps(user_profile, indent=2))



# import os
# import sys
# import json
# import logging
# import string
# import hashlib
# import re
# import boto3
# from botocore.exceptions import ClientError
# from datetime import datetime
# from pathlib import Path
# from dotenv import load_dotenv
# from typing import List, Dict, Any, Optional, Union

# # Load environment variables
# load_dotenv()

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# # Add parent directory to path for importing other modules (avoid self-import)
# sys.path.append(str(Path(__file__).parent.parent))

# from openai import OpenAI
# from pinecone import Pinecone

# class UserEmbeddingProcessor:
#     """
#     Processes a user's profile from resume and GitHub markdown files.
#     It extracts skills, computes detailed experience (experience_year) exclusively from the EXPERIENCE section,
#     extracts education details (qualification) from the EDUCATION section,
#     generates a combined embedding for the profile, produces GitHub feedback with improvement suggestions,
#     saves the combined profile (text + embedding) to S3, and upserts the embedding into Pinecone.
    
#     The Pinecone metadata now includes:
#       - github_feedback: Feedback summary for the GitHub profile.
#       - github_skills: List of skills extracted from GitHub.
#       - qualification: Education summary (from the EDUCATION section).
#       - resume_s3: The resume markdown S3 URL.
#       - resume_skills: List of skills extracted from the resume.
#       - experience_year: Detailed experience info extracted solely from the EXPERIENCE section.
    
#     Other fields (source, user_id, combined_text_hash, combined_markdown_url, git_repo) are no longer stored.
#     """
    
#     def __init__(self):
#         # Initialize S3 client.
#         self.aws_bucket_name = os.getenv('AWS_BUCKET_NAME', 'skillmatchai')
#         self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
#         self.s3_client = boto3.client(
#             's3',
#             aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#             aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
#             region_name=self.aws_region
#         )
#         # Initialize OpenAI client.
#         self.openai_api_key = os.getenv('OPENAI_API_KEY')
#         if not self.openai_api_key:
#             raise ValueError("OpenAI API key not found in environment variables")
#         self.openai_client = OpenAI(api_key=self.openai_api_key)
        
#         # Initialize Pinecone client.
#         self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
#         if not self.pinecone_api_key:
#             raise ValueError("Pinecone API key not found in environment variables")
#         self.pc = Pinecone(api_key=self.pinecone_api_key)
#         self.pinecone_index_name = os.getenv('PINECONE_INDEX_NAME', 'skillmatch')
#         self.index = self.pc.Index(self.pinecone_index_name)
        
#         # Use a specific namespace for user profiles.
#         self.pinecone_user_namespace = os.getenv('PINECONE_USER_NAMESPACE', 'userprofile')
#         logger.info(f"Connected to Pinecone index: {self.pinecone_index_name}, using namespace: {self.pinecone_user_namespace}")

#     def _read_markdown_from_s3(self, s3_url: str) -> str:
#         """Read markdown content from an S3 URL."""
#         try:
#             s3_url_clean = s3_url.replace("s3://", "")
#             parts = s3_url_clean.split("/", 1)
#             bucket = parts[0]
#             key = parts[1]
#             logger.info(f"Fetching from bucket: {bucket}, key: {key}")
#             response = self.s3_client.get_object(Bucket=bucket, Key=key)
#             text = response['Body'].read().decode('utf-8')
#             logger.info(f"Successfully fetched markdown from {s3_url} (size: {len(text)} bytes)")
#             return text
#         except ClientError as e:
#             logger.error(f"Error reading from S3: {str(e)}")
#             raise
#         except Exception as e:
#             logger.error(f"Unexpected error reading from S3: {str(e)}")
#             raise

#     def _extract_section(self, text: str, section_title: str) -> str:
#         """
#         Extract a section from the text based on the given section header.
#         Looks for a line containing the section title (case-insensitive) and returns all following lines until a new header is found.
#         """
#         lines = text.splitlines()
#         capture = False
#         section_lines = []
#         for line in lines:
#             if capture:
#                 if line.strip().startswith("#"):
#                     break
#                 section_lines.append(line)
#             elif section_title.lower() in line.lower():
#                 capture = True
#         section_text = "\n".join(section_lines).strip()
#         logger.info(f"Extracted '{section_title}' section with {len(section_text)} characters")
#         return section_text

#     def extract_all_skills_from_text(self, text: str) -> List[str]:
#         """
#         Extract all technical skills, tools, frameworks, and programming languages from the text.
#         Uses an LLM prompt that considers sections like TECHNICAL SKILLS, EXPERIENCE, and PROJECTS.
#         """
#         prompt = f"""
# Extract all technical skills, tools, frameworks, and programming languages from the text below.
# Consider sections such as "TECHNICAL SKILLS", "EXPERIENCE", and "PROJECTS".
# Return ONLY a comma-separated list with no extra commentary.
# Example: Python, JavaScript, React, SQL, Docker

# Text:
# {text}
#         """
#         try:
#             response = self.openai_client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "Extract all technical skills accurately."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.0,
#                 max_tokens=250
#             )
#             skills_text = response.choices[0].message.content.strip()
#             skills_list = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
#             logger.info(f"Extracted {len(skills_list)} skills from text")
#             return skills_list
#         except Exception as e:
#             logger.error(f"Error extracting skills: {str(e)}")
#             return []
    
#     def get_combined_embedding(self, resume_text: str, github_text: Optional[str] = None) -> List[float]:
#         """
#         Generate a combined embedding by concatenating resume and GitHub markdown texts,
#         then using OpenAI's embeddings API.
#         """
#         combined_text = resume_text + " " + (github_text or "")
#         try:
#             response = self.openai_client.embeddings.create(
#                 model="text-embedding-3-large",
#                 input=combined_text
#             )
#             embedding = response.data[0].embedding
#             logger.info("Generated combined embedding for user profile")
#             return embedding
#         except Exception as e:
#             logger.error(f"Error generating combined embedding: {str(e)}")
#             raise

#     def extract_experience_details(self, resume_text: str) -> Dict[str, Union[float, str]]:
#         """
#         Extract professional experience details from the EXPERIENCE section of the resume.
#         The LLM prompt instructs to sum durations (e.g., "9 months", "1 year") only for job positions, 
#         then returns a JSON string with:
#           "total_experience_months": <number>,
#           "total_experience_years": <number>,
#           "experience_year": "<position summary with durations>" 
#         If no durations are found, returns 0 experience and "Entry Level".
#         """
#         experience_section = self._extract_section(resume_text, "EXPERIENCE")
#         if not experience_section:
#             logger.warning("No EXPERIENCE section found; defaulting to zero experience.")
#             return {"total_experience_months": 0, "total_experience_years": 0, "experience_year": "Entry Level"}
        
#         prompt = f"""
# Analyze the EXPERIENCE section below and identify references to job positions along with durations of professional experience 
# (e.g., "Software Engineer for 9 months", "Data Analyst for 1 year", etc.). Sum the durations to calculate the total months 
# of experience and generate a concise summary of positions and durations.
# Then, convert total months to full years (ignoring remainders) and classify the experience level as follows:
# - Entry Level: less than 24 months.
# - Mid Level: between 24 and 60 months.
# - Senior Level: more than 60 months.
# Return a JSON string with the following keys:
#     "total_experience_months": <number>,
#     "total_experience_years": <number>,
#     "experience_year": "<summary of positions and durations>"
# If no valid duration is found, return {{"total_experience_months": 0, "total_experience_years": 0, "experience_year": "Entry Level"}}.
# EXPERIENCE Section:
# {experience_section}
#         """
#         try:
#             response = self.openai_client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "Extract job positions and durations from the EXPERIENCE section, then sum them up."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.0,
#                 max_tokens=150
#             )
#             result_text = response.choices[0].message.content.strip()
#             try:
#                 details = json.loads(result_text)
#                 total_months = float(details.get("total_experience_months", 0))
#                 total_years = int(details.get("total_experience_years", total_months // 12))
#                 experience_year = details.get("experience_year", "Entry Level")
#             except Exception:
#                 total_months, total_years, experience_year = 0, 0, "Entry Level"
#             logger.info(f"Extracted experience: {total_months} months ({total_years} years), summary: {experience_year}")
#             return {"total_experience_months": total_months, "total_experience_years": total_years, "experience_year": experience_year}
#         except Exception as e:
#             logger.error(f"Error extracting experience details: {str(e)}")
#             return {"total_experience_months": 0, "total_experience_years": 0, "experience_year": "Entry Level"}

#     def extract_education_details(self, resume_text: str) -> str:
#         """
#         Extract a summary of educational qualifications from the EDUCATION section of the resume.
#         Include degree details, institution names, and completion or expected dates if available.
#         Returns the summary as plain text.
#         """
#         education_section = self._extract_section(resume_text, "EDUCATION")
#         if not education_section:
#             logger.warning("No EDUCATION section found.")
#             return ""
#         prompt = f"""
# Extract a concise summary of the educational qualifications from the EDUCATION section below.
# Include details such as the degree being pursued or earned, the institution(s), and any relevant dates.
# Return the summary as plain text.

# EDUCATION Section:
# {education_section}
#         """
#         try:
#             response = self.openai_client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "Extract education qualification details from the EDUCATION section."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.0,
#                 max_tokens=150
#             )
#             education_details = response.choices[0].message.content.strip()
#             logger.info("Extracted education details from resume")
#             return education_details
#         except Exception as e:
#             logger.error(f"Error extracting education details: {str(e)}")
#             return ""
    
#     def generate_github_feedback(self, github_text: str) -> str:
#         """
#         Generate a concise, constructive feedback summary for the GitHub profile,
#         including suggestions for improvement.
#         """
#         prompt = f"""
# Provide a concise and constructive feedback summary for the GitHub profile described in the text below.
# Your feedback should include:
#   - Strengths observed,
#   - Areas for improvement,
#   - Suggestions for enhancing the profile (e.g., adding more project details, improving documentation, or writing technical blogs).
# Return only a one- or two-sentence summary.

# Text:
# {github_text}
#         """
#         try:
#             response = self.openai_client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "Provide detailed and constructive feedback for a GitHub profile."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.2,
#                 max_tokens=150
#             )
#             feedback = response.choices[0].message.content.strip()
#             logger.info("Generated GitHub feedback with improvement suggestions")
#             return feedback
#         except Exception as e:
#             logger.error(f"Error generating GitHub feedback: {str(e)}")
#             return ""
    
#     def save_combined_profile_to_s3(self, user_id: str, combined_text: str, embedding: List[float]) -> str:
#         """
#         Save the combined markdown text and its embedding to S3 as a JSON file.
#         The file is stored under: user_profiles/{user_id}/{timestamp}_combined.json
#         Returns the S3 URL of the saved file.
#         """
#         try:
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             key = f"user_profiles/{user_id}/{timestamp}_combined.json"
#             data = {
#                 "combined_text": combined_text,
#                 "embedding": embedding,
#                 "timestamp": datetime.now().isoformat()
#             }
#             json_data = json.dumps(data, ensure_ascii=False)
#             self.s3_client.put_object(
#                 Bucket=self.aws_bucket_name,
#                 Key=key,
#                 Body=json_data.encode('utf-8'),
#                 ContentType='application/json'
#             )
#             s3_url = f"s3://{self.aws_bucket_name}/{key}"
#             logger.info(f"Saved combined profile to {s3_url}")
#             return s3_url
#         except Exception as e:
#             logger.error(f"Error saving combined profile to S3: {str(e)}")
#             raise
    
#     def upsert_profile_to_pinecone(self, user_id: str, combined_text: str, embedding: List[float],
#                                      extra_metadata: Dict[str, Any]) -> None:
#         """
#         Upsert the user's combined embedding to Pinecone under the userprofile namespace.
#         The vector ID is generated as "{user_id}_{md5_hash}".
#         Metadata includes:
#           - github_feedback, github_skills, qualification, resume_s3, resume_skills, experience_year
#         (Other fields like source, user_id, combined_text_hash, combined_markdown_url, and git_repo are omitted.)
#         For non-primitive values, conversion to JSON string is performed.
#         """
#         try:
#             text_hash = hashlib.md5(combined_text.encode('utf-8')).hexdigest()
#             vector_id = f"{user_id}_{text_hash}"
#             metadata = {
#                 "github_feedback": extra_metadata.get("github_feedback", ""),
#                 "github_skills": extra_metadata.get("github_skills", []),
#                 "qualification": extra_metadata.get("qualification", ""),
#                 "resume_s3": extra_metadata.get("resume_s3", ""),
#                 "resume_skills": extra_metadata.get("resume_skills", []),
#                 # Store experience details (now under the key "experience_year") as a JSON string.
#                 "experience_year": json.dumps(extra_metadata.get("experience_year", {}))
#             }
#             self.index.upsert(
#                 vectors=[(vector_id, embedding, metadata)],
#                 namespace=self.pinecone_user_namespace
#             )
#             logger.info(f"Upserted vector for user {user_id} with ID {vector_id} into Pinecone namespace '{self.pinecone_user_namespace}'")
#         except Exception as e:
#             logger.error(f"Error upserting profile to Pinecone: {str(e)}")
#             raise
    
#     def process_user_data(self, resume_url: str, github_url: Optional[str] = None,
#                           git_repo: str = "", qualification: Optional[List[str]] = None) -> Dict[str, Any]:
#         """
#         Process user data from resume and optional GitHub markdown URLs.
#         It:
#           - Reads resume and GitHub markdown from S3.
#           - Extracts skills from both sources and deduplicates them.
#           - Generates a combined embedding.
#           - Extracts detailed experience ONLY from the EXPERIENCE section (as "experience_year").
#           - Extracts education details from the EDUCATION section.
#           - Generates GitHub feedback.
#           - Saves the combined profile to S3.
#           - Upserts the embedding with metadata (now including "experience_year" and qualification) into Pinecone.
#         Returns a dictionary containing:
#           - combined_embedding: The profile embedding.
#           - all_skills: Deduplicated list of skills.
#           - experience_year: Experience details extracted from the EXPERIENCE section.
#           - qualification: Education summary.
#           - github_feedback: GitHub feedback.
#           - sources: Extraction info from each source.
#           - combined_profile_url: S3 URL where the combined profile is stored.
#         """
#         try:
#             resume_text = self._read_markdown_from_s3(resume_url)
#             github_text = self._read_markdown_from_s3(github_url) if github_url else ""
            
#             # Extract skills.
#             resume_skills = self.extract_all_skills_from_text(resume_text)
#             github_skills = self.extract_all_skills_from_text(github_text) if github_text else []
#             all_skills = list({skill for skill in resume_skills + github_skills})
            
#             # Generate the combined embedding.
#             combined_embedding = self.get_combined_embedding(resume_text, github_text)
            
#             # Prepare combined text.
#             combined_text = resume_text + "\n" + github_text
            
#             # Save the combined profile to S3.
#             user_id = "test_user_123"  # Adjust as needed.
#             combined_profile_url = self.save_combined_profile_to_s3(user_id, combined_text, combined_embedding)
            
#             # Prepare extra metadata.
#             extra_metadata = {
#                 "github_feedback": self.generate_github_feedback(github_text) if github_text else "",
#                 "github_skills": github_skills,
#                 # For qualification, extract details from the EDUCATION section.
#                 "qualification": self.extract_education_details(resume_text),
#                 "resume_s3": resume_url,
#                 "resume_skills": resume_skills,
#                 # Extract experience details from the EXPERIENCE section, stored under key "experience_year".
#                 "experience_year": self.extract_experience_details(resume_text)
#             }
            
#             # Upsert the user profile embedding into Pinecone.
#             self.upsert_profile_to_pinecone(user_id, combined_text, combined_embedding, extra_metadata)
            
#             user_data = {
#                 "combined_embedding": combined_embedding,
#                 "all_skills": all_skills,
#                 "experience_year": extra_metadata["experience_year"],
#                 "qualification": extra_metadata["qualification"],
#                 "github_feedback": extra_metadata["github_feedback"],
#                 "sources": [
#                     {"type": "resume", "extracted_skills": resume_skills},
#                     {"type": "github", "extracted_skills": github_skills}
#                 ],
#                 "combined_profile_url": combined_profile_url
#             }
#             logger.info(f"User data processed with {len(all_skills)} unique skills, experience: {extra_metadata['experience_year']}, and qualification: {extra_metadata['qualification']}")
#             return user_data
#         except Exception as e:
#             logger.error(f"Error processing user data: {str(e)}")
#             raise

# if __name__ == "__main__":
#     # Example usage when running this module directly.
#     resume_url = "s3://skillmatchai/resume/markdown/20250411_200621_AUM-JS-python-Doc.md"
#     github_url = "s3://skillmatchai/github/markdown/20250411_200617_Aumpatelarjun_github_profile.md"
#     git_repo = "https://github.com/Aumpatelarjun"
#     qualification = []  # Will be filled from the EDUCATION section.
    
#     processor = UserEmbeddingProcessor()
#     user_profile = processor.process_user_data(resume_url, github_url, git_repo, qualification)
#     print(json.dumps(user_profile, indent=2))



















































import os
import sys
import json
import logging
import string
import hashlib
import re
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional, Union

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path for importing other modules
sys.path.append(str(Path(__file__).parent.parent))

from openai import OpenAI
from pinecone import Pinecone

class UserEmbeddingProcessor:
    """
    Processes a user's profile from resume and GitHub markdown files.
    It extracts skills, computes detailed professional experience (experience_year) solely from the EXPERIENCE section,
    extracts education details (qualification) from the EDUCATION section,
    generates a combined embedding for the profile, produces GitHub feedback with suggestions,
    saves the combined profile (text + embedding) to S3, and upserts the embedding into Pinecone.

    The metadata stored in Pinecone includes:
      - github_feedback
      - github_skills
      - qualification
      - resume_s3
      - resume_skills
      - experience_year (a JSON string with total experience info and position summaries)
    """
    
    def __init__(self):
        # Initialize S3 client.
        self.aws_bucket_name = os.getenv('AWS_BUCKET_NAME', 'skillmatchai')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=self.aws_region
        )
        # Initialize OpenAI client.
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        
        # Initialize Pinecone client.
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
        if not self.pinecone_api_key:
            raise ValueError("Pinecone API key not found in environment variables")
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        self.pinecone_index_name = os.getenv('PINECONE_INDEX_NAME', 'skillmatch')
        self.index = self.pc.Index(self.pinecone_index_name)
        
        # Use a specific namespace for user profiles.
        self.pinecone_user_namespace = os.getenv('PINECONE_USER_NAMESPACE', 'userprofile')
        logger.info(f"Connected to Pinecone index: {self.pinecone_index_name}, using namespace: {self.pinecone_user_namespace}")

    def _read_markdown_from_s3(self, s3_url: str) -> str:
        """Read markdown content from an S3 URL."""
        try:
            s3_url_clean = s3_url.replace("s3://", "")
            parts = s3_url_clean.split("/", 1)
            bucket = parts[0]
            key = parts[1]
            logger.info(f"Fetching from bucket: {bucket}, key: {key}")
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            text = response['Body'].read().decode('utf-8')
            logger.info(f"Successfully fetched markdown from {s3_url} (size: {len(text)} bytes)")
            return text
        except ClientError as e:
            logger.error(f"Error reading from S3: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error reading from S3: {str(e)}")
            raise

    def _extract_section(self, text: str, section_title: str) -> str:
        """
        Extract a section from the text based on the given section header.
        Assumes section headers start with '#' and extracts until the next header.
        """
        lines = text.splitlines()
        capture = False
        section_lines = []
        for line in lines:
            if capture:
                if line.strip().startswith("#"):
                    break
                section_lines.append(line)
            elif section_title.lower() in line.lower():
                capture = True
        section_text = "\n".join(section_lines).strip()
        logger.info(f"Extracted '{section_title}' section with {len(section_text)} characters")
        return section_text

    def extract_all_skills_from_text(self, text: str) -> List[str]:
        """
        Extract all technical skills, tools, frameworks, and programming languages from the text.
        Uses an LLM prompt that considers sections such as TECHNICAL SKILLS, EXPERIENCE, and PROJECTS.
        """
        prompt = f"""
Extract all technical skills, tools, frameworks, and programming languages from the text below.
Consider sections such as "TECHNICAL SKILLS", "EXPERIENCE", and "PROJECTS".
Return ONLY a comma-separated list with no extra commentary.
Example: Python, JavaScript, React, SQL, Docker

Text:
{text}
        """
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract all technical skills accurately."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=250
            )
            skills_text = response.choices[0].message.content.strip()
            skills_list = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
            logger.info(f"Extracted {len(skills_list)} skills from text")
            return skills_list
        except Exception as e:
            logger.error(f"Error extracting skills: {str(e)}")
            return []
    
    # def get_combined_embedding(self, resume_text: str, github_text: Optional[str] = None) -> List[float]:
    #     """
    #     Generate a combined embedding by concatenating resume and GitHub markdown texts,
    #     then using OpenAI's embeddings API.
    #     """
    #     combined_text = resume_text + " " + (github_text or "")
    #     try:
    #         response = self.openai_client.embeddings.create(
    #             model="text-embedding-3-large",
    #             input=combined_text
    #         )
    #         embedding = response.data[0].embedding
    #         logger.info("Generated combined embedding for user profile")
    #         return embedding
    #     except Exception as e:
    #         logger.error(f"Error generating combined embedding: {str(e)}")
    #         raise


    def get_combined_embedding(self, resume_text: str, github_text: Optional[str] = None) -> List[float]:
        """Generate a combined embedding for the user's profile."""
        combined_text = resume_text + "\n\n" + (github_text or "")
        combined_text = self.truncate_text_to_token_limit(combined_text)  # ← 👈 Add this line
        logger.info(f"🔧 Truncated combined text to {len(combined_text)} characters before embedding")

        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-large",
                input=combined_text
            )
            embedding = response.data[0].embedding
            logger.info("✅ Successfully generated combined embedding")
            return embedding
        except Exception as e:
            logger.error(f"❌ Error generating combined embedding: {str(e)}")
            raise

    def extract_experience_details(self, resume_text: str) -> Dict[str, Union[float, str]]:
        """
        Extract professional experience details exclusively from the EXPERIENCE section of the resume.
        The prompt instructs the LLM to process each job position, extract the job title and duration in months,
        sum the durations, and produce a summary string that lists each position with its duration, 
        as well as the total months and years of experience.
        
        For example, if the EXPERIENCE section contains:
          "Software Engineering Teacher Assistant | Northeastern University | Boston, MA | April 2024 - Present (assume 12 months)
           Software Developer | Crest Data System | Ahmedabad, India | Jan 2022 - May 2023 (assume 12 months)"
        The expected JSON output would be:
          {
            "total_experience_months": 24,
            "total_experience_years": 2,
            "experience_year": "Software Engineering Teacher Assistant: 12 months; Software Developer: 12 months; Total: 24 months (2 years) - Entry Level"
          }
        
        If no valid duration is found, it returns 0 experience and "Entry Level".
        """
        experience_section = self._extract_section(resume_text, "EXPERIENCE")
        if not experience_section:
            logger.warning("No EXPERIENCE section found; defaulting to zero experience.")
            return {"total_experience_months": 0, "total_experience_years": 0, "experience_year": "Entry Level"}
        
        prompt = f"""
You are given the following EXPERIENCE section from a resume. For each job position mentioned, extract:
  - The job title (e.g., "Software Engineering Teacher Assistant").
  - The duration of that position in months (interpret phrases like "9 months", "1 year", "2 years 3 months" numerically).
Calculate the sum of the durations to get the total experience in months.
Also, produce a summary string that lists each position and its duration, and then states the total experience in months and years.
Classify the overall experience level as follows:
  - Entry Level if total experience is <= 24 months.
  - Mid Level if total experience is between 25 and 60 months.
  - Senior Level if total experience is > 60 months.
Return a strict JSON string with exactly these keys:
{{
  "total_experience_months": <number>,
  "total_experience_years": <number>,
  "experience_year": "<summary string>"
}}
If no duration can be determined, return:
{{"total_experience_months": 0, "total_experience_years": 0, "experience_year": "Entry Level"}}
EXPERIENCE Section:
{experience_section}
        """
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract detailed experience from the EXPERIENCE section, including job positions and their durations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=250
            )
            result_text = response.choices[0].message.content.strip()
            # Check for a proper closing brace to ensure complete JSON.
            if not result_text.endswith("}"):
                logger.error(f"Incomplete JSON response for experience extraction: {result_text}")
                return {"total_experience_months": 0, "total_experience_years": 0, "experience_year": "Entry Level"}
            try:
                details = json.loads(result_text)
                total_months = float(details.get("total_experience_months", 0))
                total_years = int(details.get("total_experience_years", total_months // 12))
                experience_year = details.get("experience_year", "Entry Level")
            except Exception as ex:
                logger.error(f"Error parsing experience details: {str(ex)} - Raw response: {result_text}")
                total_months, total_years, experience_year = 0, 0, "Entry Level"
            logger.info(f"Extracted experience: {total_months} months ({total_years} years), summary: {experience_year}")
            return {"total_experience_months": total_months, "total_experience_years": total_years, "experience_year": experience_year}
        except Exception as e:
            logger.error(f"Error extracting experience details: {str(e)}")
            return {"total_experience_months": 0, "total_experience_years": 0, "experience_year": "Entry Level"}

    def extract_education_details(self, resume_text: str) -> str:
        """
        Extract a concise summary of educational qualifications from the EDUCATION section of the resume.
        Include degree information, institution names, and relevant dates.
        Returns the summary as plain text.
        """
        education_section = self._extract_section(resume_text, "EDUCATION")
        if not education_section:
            logger.warning("No EDUCATION section found.")
            return ""
        prompt = f"""
Extract a concise summary of the educational qualifications from the EDUCATION section below.
Include details such as the degree(s) pursued or earned, institution name(s), and relevant dates.
Return the summary as plain text.

EDUCATION Section:
{education_section}
        """
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract education qualification details from the EDUCATION section."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=150
            )
            education_details = response.choices[0].message.content.strip()
            logger.info("Extracted education details from resume")
            return education_details
        except Exception as e:
            logger.error(f"Error extracting education details: {str(e)}")
            return ""
    
    def generate_github_feedback(self, github_text: str) -> str:
        """
        Generate a concise and constructive feedback summary for the GitHub profile,
        including suggestions for improvement.
        """
        prompt = f"""
Provide a concise, detailed and constructive feedback summary for the GitHub profile described below.
Include:
  - Strengths observed.
  - Areas that need improvement.
  - Suggestions for enhancement (e.g., adding project descriptions, engaging more with the community, updating activity).
Return only a one- or two-sentence summary.

Text:
{github_text}
        """
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Provide detailed and constructive feedback for a GitHub profile."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=150
            )
            feedback = response.choices[0].message.content.strip()
            logger.info("Generated GitHub feedback with improvement suggestions")
            return feedback
        except Exception as e:
            logger.error(f"Error generating GitHub feedback: {str(e)}")
            return ""
    
    def save_combined_profile_to_s3(self, user_id: str, combined_text: str, embedding: List[float]) -> str:
        """
        Save the combined markdown text and its embedding to S3 as a JSON file.
        The file is stored under: user_profiles/{user_id}/{timestamp}_combined.json.
        Returns the S3 URL of the saved file.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            key = f"user_profiles/{user_id}/{timestamp}_combined.json"
            data = {
                "combined_text": combined_text,
                "embedding": embedding,
                "timestamp": datetime.now().isoformat()
            }
            json_data = json.dumps(data, ensure_ascii=False)
            self.s3_client.put_object(
                Bucket=self.aws_bucket_name,
                Key=key,
                Body=json_data.encode('utf-8'),
                ContentType='application/json'
            )
            s3_url = f"s3://{self.aws_bucket_name}/{key}"
            logger.info(f"Saved combined profile to {s3_url}")
            return s3_url
        except Exception as e:
            logger.error(f"Error saving combined profile to S3: {str(e)}")
            raise

    @staticmethod 
    def truncate_text_to_token_limit(text: str, max_tokens: int = 8192, buffer: int = 100) -> str:
        try:
            max_tokens = int(max_tokens)
            buffer = int(buffer)
            approx_char_limit = (max_tokens - buffer) * 4
            return text[:approx_char_limit]
        except Exception as e:
            logger.error(f"Error in truncation: {e}")
            return text[:50000]  # fallback



    def upsert_profile_to_pinecone(self, user_id: str, combined_text: str, embedding: List[float],
                                     extra_metadata: Dict[str, Any]) -> None:
        """
        Upsert the user's combined embedding to Pinecone under the userprofile namespace.
        The vector ID is generated as "{user_id}_{md5_hash}".
        Metadata includes:
          - github_feedback, github_skills, qualification, resume_s3, resume_skills, experience_year.
        Non-primitive values (such as experience_year) are converted to a JSON string.
        """
        try:
            text_hash = hashlib.md5(combined_text.encode('utf-8')).hexdigest()
            vector_id = f"{user_id}_{text_hash}"
            metadata = {
                "github_feedback": extra_metadata.get("github_feedback", ""),
                "github_skills": extra_metadata.get("github_skills", []),
                "qualification": extra_metadata.get("qualification", ""),
                "resume_s3": extra_metadata.get("resume_s3", ""),
                "resume_skills": extra_metadata.get("resume_skills", []),
                "experience_year": json.dumps(extra_metadata.get("experience_year", {}))
            }
            self.index.upsert(
                vectors=[(vector_id, embedding, metadata)],
                namespace=self.pinecone_user_namespace
            )
            logger.info(f"Upserted vector for user {user_id} with ID {vector_id} into Pinecone namespace '{self.pinecone_user_namespace}'")
        except Exception as e:
            logger.error(f"Error upserting profile to Pinecone: {str(e)}")
            raise
    
    def process_user_data(self, resume_url: str, github_url: Optional[str] = None,
                          git_repo: str = "", qualification: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Process user data from resume and optional GitHub markdown URLs.
        Steps:
          - Read resume and GitHub markdown from S3.
          - Extract skills from both sources and deduplicate them.
          - Generate a combined embedding.
          - Extract detailed experience solely from the EXPERIENCE section as "experience_year".
          - Extract education details from the EDUCATION section.
          - Generate GitHub feedback.
          - Save the combined profile to S3.
          - Upsert the embedding with metadata into Pinecone (only the specified keys are stored).
        Returns a dictionary containing:
          - combined_embedding: The profile embedding.
          - all_skills: Deduplicated list of skills.
          - experience_year: Detailed experience information.
          - qualification: Education summary.
          - github_feedback: GitHub feedback.
          - sources: Extraction details from each source.
          - combined_profile_url: S3 URL of the combined profile.
        """
        try:
            resume_text = self._read_markdown_from_s3(resume_url)
            github_text = self._read_markdown_from_s3(github_url) if github_url else ""
            
            # Extract skills from both sources.
            resume_skills = self.extract_all_skills_from_text(resume_text)
            github_skills = self.extract_all_skills_from_text(github_text) if github_text else []
            all_skills = list({skill for skill in resume_skills + github_skills})
            
            # Generate combined embedding.
            combined_embedding = self.get_combined_embedding(resume_text, github_text)
            
            # Combine the texts.
            combined_text = resume_text + "\n\n" + (github_text or "")
            combined_text = self.truncate_text_to_token_limit(combined_text)
            
            # Save combined profile to S3.
            user_id = "test_user_123"  # Modify as needed.
            combined_profile_url = self.save_combined_profile_to_s3(user_id, combined_text, combined_embedding)
            
            # Prepare extra metadata.
            extra_metadata = {
                "github_feedback": self.generate_github_feedback(github_text) if github_text else "",
                "github_skills": github_skills,
                "qualification": self.extract_education_details(resume_text),
                "resume_s3": resume_url,
                "resume_skills": resume_skills,
                "experience_year": self.extract_experience_details(resume_text)
            }
            
            # Upsert profile embedding to Pinecone.
            self.upsert_profile_to_pinecone(user_id, combined_text, combined_embedding, extra_metadata)
            
            user_data = {
                "combined_embedding": combined_embedding,
                "all_skills": all_skills,
                "experience_year": extra_metadata["experience_year"],
                "qualification": extra_metadata["qualification"],
                "github_feedback": extra_metadata["github_feedback"],
                "sources": [
                    {"type": "resume", "extracted_skills": resume_skills},
                    {"type": "github", "extracted_skills": github_skills}
                ],
                "combined_profile_url": combined_profile_url
            }
            logger.info(f"User data processed with {len(all_skills)} unique skills, experience: {extra_metadata['experience_year']}, and qualification: {extra_metadata['qualification']}")
            return user_data
        except Exception as e:
            logger.error(f"Error processing user data: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage when running this module directly.
    resume_url = "s3://skillmatchai/resume/markdown/20250411_200621_AUM-JS-python-Doc.md"
    github_url = "s3://skillmatchai/github/markdown/20250411_200617_Aumpatelarjun_github_profile.md"
    git_repo = "https://github.com/Aumpatelarjun"
    qualification = []  # Will be extracted from the EDUCATION section.
    
    processor = UserEmbeddingProcessor()
    user_profile = processor.process_user_data(resume_url, github_url, git_repo, qualification)
    print(json.dumps(user_profile, indent=2))
