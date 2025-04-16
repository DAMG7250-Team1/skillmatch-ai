# import sys
# import re
# import json
# from sentence_transformers import SentenceTransformer, util
# import pinecone
# import os
# import logging

# logger = logging.getLogger(__name__)
# from pinecone import Pinecone, ServerlessSpec
# # Load a pre-trained sentence transformer model once for local specialization matching.
# _local_embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


# def normalize_skill(skill: str) -> str:
#     """
#     Normalize a skill string by converting to lowercase, stripping whitespace,
#     and removing unwanted punctuation (except periods).
#     """
#     skill = skill.lower().strip()
#     return re.sub(r'[^\w\s\.]', '', skill)


# def extract_degree_and_specialization(qual_text: str) -> tuple[str, str]:
#     """
#     Extract the highest degree and candidate specialization from a qualification string.
#     Returns a tuple: (degree_level, specialization)
#     """
#     qual_text = qual_text.lower()
#     degree_level = None
#     if "phd" in qual_text or "doctor" in qual_text:
#         degree_level = "phd"
#     elif "master" in qual_text:
#         degree_level = "masters"
#     elif "bachelor" in qual_text:
#         degree_level = "bachelors"
    
#     specialization = ""
#     if degree_level:
#         pattern = r"(phd|master(?:s)?|bachelor(?:s)?)\s+in\s+([a-z\s]+)[,\.]"
#         match = re.search(pattern, qual_text)
#         if match:
#             specialization = match.group(2).strip()
#         else:
#             pattern = r"(phd|master(?:s)?|bachelor(?:s)?)\s+in\s+([a-z\s]+)"
#             match = re.search(pattern, qual_text)
#             if match:
#                 specialization = " ".join(match.group(2).split()[:3]).strip()
#     return degree_level, specialization


# def dynamic_specialization_match(user_spec: str, job_spec: str, threshold: float = 0.75) -> bool:
#     """
#     Dynamically compares two specialization strings using local embeddings.
#     Computes cosine similarity between their embeddings.
#     Returns True if similarity is above the threshold, else False.
#     """
#     user_spec = user_spec.lower().strip()
#     job_spec = job_spec.lower().strip()
#     user_vec = _local_embedding_model.encode(user_spec, convert_to_tensor=True)
#     job_vec = _local_embedding_model.encode(job_spec, convert_to_tensor=True)
#     similarity = util.pytorch_cos_sim(user_vec, job_vec).item()
#     return similarity >= threshold


# class JobMatcher:
#     def __init__(self):
#         # These attributes should be injected externally (e.g., via dependency injection).
#         # self.index = None            # For example, a Pinecone index instance.
#         # self.user_processor = None   # Optional: for processing user data.
#         # self.job_processor = None    # Optional: for computing embeddings from job text.
#         # Thresholds for categorizing the matching score.
#         self.similarity_thresholds = {"high": 65, "medium": 35, "low": 10}

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


#     def get_similarity_category(self, score: float) -> str:
#         """
#         Determine the matching category based on the final computed score.
#         """
#         if score >= self.similarity_thresholds["high"]:
#             return "high"
#         elif score >= self.similarity_thresholds["medium"]:
#             return "average"
#         elif score >= self.similarity_thresholds["low"]:
#             return "low"
#         else:
#             return "very_low"
    
#     def get_user_profile_embedding(self, profile: dict) -> list:
#         """
#         Retrieve the user's embedding from the profile dictionary.
#         """
#         return profile.get("combined_embedding", [])
    
#     def query_jobs(self, embedding: list, top_k: int = 5) -> list:
#         """
#         Query the job index using the provided embedding.
#         Tries multiple namespaces to find job data.
#         """
#         # Try several namespaces where jobs might be stored
#         namespaces_to_try = ["default", "jobs", "", None]
#         matches = []
        
#         for namespace in namespaces_to_try:
#             try:
#                 response = self.index.query(
#                     vector=embedding,
#                     top_k=top_k,
#                     include_metadata=True,
#                     namespace=namespace
#                 )
                
#                 namespace_matches = response.get("matches", [])
                
#                 if namespace_matches:
#                     matches = namespace_matches
#                     break
#             except Exception:
#                 # Continue to the next namespace
#                 continue
        
#         return matches
    
#     def compute_weighted_score(self, profile: dict, job_metadata: dict) -> float:
#         """
#         Compute a weighted matching score between a user profile and a job posting.
#         Breakdown:
#             - Skills Matching (40%): Jaccard similarity between normalized skills.
#           - Qualification Matching (30% total):
#                  * Degree Matching (15%) and Specialization Matching (15% if related, otherwise 5%).
#             - Experience Matching (30%): Based on years difference.
#         """
#         # Skills Matching (40%)
#         profile_skills = set([normalize_skill(s) for s in profile.get("all_skills", [])])
#         job_skills = set([normalize_skill(s) for s in job_metadata.get("extracted_skills", [])])
#         if profile_skills or job_skills:
#             skills_similarity = (len(profile_skills.intersection(job_skills)) / 
#                                  len(profile_skills.union(job_skills))) * 100
#         else:
#             skills_similarity = 0
#         skills_weighted = skills_similarity * 0.40

#         # Qualification Matching (30% total)
#         user_qual_text = profile.get("qualification", "")
#         job_qual_text = job_metadata.get("qualifications", "")
#         user_degree, user_spec = extract_degree_and_specialization(user_qual_text)
#         job_degree, job_spec = extract_degree_and_specialization(job_qual_text)
#         degree_rank = {'bachelors': 1, 'masters': 2, 'phd': 3}
        
#         # Degree matching (15%):
#         if user_degree and job_degree and degree_rank.get(user_degree, 0) >= degree_rank.get(job_degree, 0):
#             degree_component = 100
#         else:
#             degree_component = 0
#         degree_weighted = degree_component * 0.15

#         # Specialization matching:
#         if user_spec and job_spec:
#             if dynamic_specialization_match(user_spec, job_spec):
#                 specialization_component = 100
#                 spec_weight = 0.15
#             else:
#                 specialization_component = 0
#                 spec_weight = 0.05
#         else:
#             specialization_component = 0
#             spec_weight = 0.05
#         specialization_weighted = specialization_component * spec_weight

#         qualification_weighted = degree_weighted + specialization_weighted

#         # Experience Matching (30%)
#         experience_score = 0
#         user_years = 0
#         if "experience_year" in profile:
#             try:
#                 exp_data = json.loads(profile["experience_year"])
#                 user_years = float(exp_data.get("total_experience_years", 0))
#             except Exception:
#                 user_years = 0
#         exp_match = re.search(r'(\d+)', job_metadata.get("experience", ""))
#         if exp_match:
#             job_exp = float(exp_match.group(1))
#         else:
#             job_exp = 0
#         if job_exp > 0:
#             diff_percentage = abs(user_years - job_exp) / job_exp * 100
#             experience_score = max(100 - diff_percentage, 0)
#         experience_weighted = experience_score * 0.30

#         # --- Final Weighted Score ---
#         final_score = skills_weighted + qualification_weighted + experience_weighted
#         return final_score
    
#     def match_profile_with_jobs(self, profile: dict, top_k: int = 5) -> dict:
#         """
#         Match a user profile with jobs:
#           1. Retrieve user's embedding.
#           2. Query jobs from the "default" namespace.
#           3. Compute weighted matching scores.
#           4. Sort and return results.
#         """
#         embedding = self.get_user_profile_embedding(profile)
#         matches = self.query_jobs(embedding, top_k=top_k)
#         results = {"status": "success", "total_matches": len(matches), "matches": []}
#         processed_matches = []
#         for match in matches:
#             job_meta = match.metadata
#             weighted_score = self.compute_weighted_score(profile, job_meta)
#             category = self.get_similarity_category(weighted_score)
#             profile_skills = set([normalize_skill(s) for s in profile.get("all_skills", [])])
#             job_skills = set([normalize_skill(s) for s in job_meta.get("extracted_skills", [])])
#             matching_skills = list(profile_skills.intersection(job_skills))
#             processed_matches.append({
#                 "job_id": match.id,
#                 "job_title": job_meta.get("job_title", ""),
#                 "company": job_meta.get("company", ""),
#                 "similarity_score": weighted_score,
#                 "similarity_category": category,
#                 "matching_skills": matching_skills
#             })
#         processed_matches = sorted(processed_matches, key=lambda x: x["similarity_score"], reverse=True)
#         results["matches"] = processed_matches[:top_k]
#         results["total_matches"] = len(processed_matches)
#         return results

#     def match_skills_with_jobs(self, skills: list, top_k: int = 10) -> dict:
#         """
#         Match jobs based solely on a given list of skills.
#         Concatenates skills into a text string, computes an embedding using job_processor, then queries the index.
#         """
#         skills_text = ", ".join(skills)
#         print(skills_text)
#         embedding = self.job_processor.get_embedding(skills_text)
#         matches = self.query_jobs(embedding, top_k=top_k)
#         results = {"status": "success", "total_matches": len(matches), "matches": []}
#         for match in matches:
#             job_meta = match.metadata
#             result = {
#                 "job_id": match.id,
#                 "job_title": job_meta.get("job_title", ""),
#                 "similarity_score": match.score,
#                 "matching_skills": job_meta.get("extracted_skills", [])
#             }
#             results["matches"].append(result)
#         return results

#     def get_user_profile_from_pinecone(self, user_id: str) -> dict:
#         """
#         Retrieve a user profile from Pinecone from the "userprofile" namespace.
#         Uses a dummy zero vector with a filter on "user_id".
#         After retrieval, merges resume_skills and github_skills into 'all_skills'.
#         """
#         dummy_vector = [0.0] * 3072
#         try:
#             # 1. First try with user_id field
#             result = self.index.query(
#                 vector=dummy_vector,
#                 filter={"user_id": user_id},
#                 top_k=1,
#                 include_metadata=True,
#                 namespace="userprofile"
#             )
            
#             matches = result.get("matches", [])
            
#             # 2. If no match, try with ID field
#             if not matches:
#                 result = self.index.query(
#                     vector=dummy_vector,
#                     filter={"ID": user_id},
#                     top_k=1,
#                     include_metadata=True,
#                     namespace="userprofile"
#                 )
#                 matches = result.get("matches", [])
            
#             # 3. If still no match, try direct fetch by ID
#             if not matches:
#                 try:
#                     vector_response = self.index.fetch(
#                         ids=[user_id],
#                         namespace="userprofile"
#                     )
                    
#                     if user_id in vector_response.vectors:
#                         vector = vector_response.vectors[user_id]
#                         profile = vector.metadata if hasattr(vector, 'metadata') else {}
#                         profile["combined_embedding"] = vector.values
                        
#                         # Combine skills
#                         resume_skills = profile.get("resume_skills", [])
#                         github_skills = profile.get("github_skills", [])
#                         profile["all_skills"] = list(set(resume_skills + github_skills))
                        
#                         return profile
#                 except Exception:
#                     # Continue to next approach
#                     pass
                
#             # 4. If still no match, try listing all vectors and checking IDs
#             if not matches:
#                 check_result = self.index.query(
#                     vector=dummy_vector,
#                     top_k=5,
#                     include_metadata=True,
#                     namespace="userprofile"
#                 )
                
#                 if check_result.get("matches"):
#                     # Check if any match has the ID we're looking for
#                     for match in check_result.get("matches", []):
#                         if match.id == user_id:
#                             profile = match.metadata
                            
#                             # Try to get the embedding
#                             try:
#                                 vector_response = self.index.fetch(
#                                     ids=[match.id],
#                                     namespace="userprofile"
#                                 )
                                
#                                 if match.id in vector_response.vectors:
#                                     profile["combined_embedding"] = vector_response.vectors[match.id].values
#                                 else:
#                                     profile["combined_embedding"] = [0.1] * 3072
#                             except Exception:
#                                 profile["combined_embedding"] = [0.1] * 3072
                            
#                             # Combine skills
#                             resume_skills = profile.get("resume_skills", [])
#                             github_skills = profile.get("github_skills", [])
#                             profile["all_skills"] = list(set(resume_skills + github_skills))
                            
#                             return profile
                    
#                     # If we're here, no profile with matching ID was found
#                     available_ids = [match.id for match in check_result.get("matches", [])[:3]]
#                     raise Exception(f"No user profile found for user_id: {user_id}. Available profiles: {available_ids}")
#                 else:
#                     raise Exception(f"No user profiles found in namespace 'userprofile'")
            
#             # 5. Process profile if found through query
#             if matches:
#                 profile = matches[0].metadata
#                 vector_id = matches[0].id
                
#                 # Try to get the embedding via fetch
#                 try:
#                     vector_response = self.index.fetch(
#                         ids=[vector_id],
#                         namespace="userprofile"
#                     )
                    
#                     if vector_id in vector_response.vectors:
#                         profile["combined_embedding"] = vector_response.vectors[vector_id].values
#                     else:
#                         profile["combined_embedding"] = [0.1] * 3072
#                 except Exception:
#                     profile["combined_embedding"] = [0.1] * 3072
                
#                 # Combine skills
#                 resume_skills = profile.get("resume_skills", [])
#                 github_skills = profile.get("github_skills", [])
#                 profile["all_skills"] = list(set(resume_skills + github_skills))
                
#                 return profile
            
#             raise Exception(f"No user profile found for user_id: {user_id}")
#         except Exception as e:
#             raise Exception(f"Error retrieving user profile: {str(e)}")

# def main():
#     # import os
#     # from pinecone import Pinecone, ServerlessSpec
#     # pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))
#     # index = pinecone.Index(os.getenv("PINECONE_INDEX_NAME"))
    
#     # Create a matcher and assign the live index.
#     matcher = JobMatcher()
#     # matcher.index 

#     # Example user profile (or retrieve via get_user_profile_from_pinecone)
#     user_profile_data = {
#         "ID": "test_user_123_d147f88fba006c714e27f17e96ea04bf",
#         "combined_embedding": [0.25] * 3072,
#         "qualification": "- Master of Computer Software Engineering from Northeastern University, Boston, USA (Expected Dec 2025)\n- Bachelor of Computer Science from Maharaja Sayajirao University, Vadodara, India (July 2018 - May 2022)",
#         "experience_year": '{"total_experience_months": 39.0, "total_experience_years": 3, "experience_year": "Software Engineering Teacher Assistant: 7 months, Software Developer at Crest Data System: 16 months, Software Developer at Overclocked Brains: 16 months. Total Experience: 3 years"}',
#         "github_skills": ["JavaScript", "TypeScript", "TSQL", "C++", "HTML", "CSS", "Node.js", "Yarn", "React", "SQL"],
#         "resume_skills": ["JavaScript", "Java", "Python", "C++", "Typescript", "HTML", "CSS", "React.js", "Node.js"]
#     }

#     results = matcher.match_profile_with_jobs(user_profile_data, top_k=5)
#     print(json.dumps(results, indent=2))

# if __name__ == "__main__":
#     main()








import sys
import re
import json
from sentence_transformers import SentenceTransformer, util
import pinecone
import os
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jobs.embeddings import JobEmbeddingsProcessor

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG to see all logs

from pinecone import Pinecone, ServerlessSpec
# Load a pre-trained sentence transformer model once for local specialization matching.
_local_embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def normalize_skill(skill: str) -> str:
    """
    Normalize a skill string by converting to lowercase, stripping whitespace,
    and removing unwanted punctuation (except periods).
    """
    skill = skill.lower().strip()
    return re.sub(r'[^\w\s\.]', '', skill)

def extract_degree_and_specialization(qual_text: str) -> tuple[str, str]:
    """
    Extract the highest degree and candidate specialization from a qualification string.
    Returns a tuple: (degree_level, specialization)
    """
    qual_text = qual_text.lower()
    degree_level = None
    if "phd" in qual_text or "doctor" in qual_text:
        degree_level = "phd"
    elif "master" in qual_text:
        degree_level = "masters"
    elif "bachelor" in qual_text:
        degree_level = "bachelors"
    
    specialization = ""
    if degree_level:
        pattern = r"(phd|master(?:s)?|bachelor(?:s)?)\s+in\s+([a-z\s]+)[,\.]"
        match = re.search(pattern, qual_text)
        if match:
            specialization = match.group(2).strip()
        else:
            pattern = r"(phd|master(?:s)?|bachelor(?:s)?)\s+in\s+([a-z\s]+)"
            match = re.search(pattern, qual_text)
            if match:
                specialization = " ".join(match.group(2).split()[:3]).strip()
    return degree_level, specialization

def dynamic_specialization_match(user_spec: str, job_spec: str, threshold: float = 0.75) -> bool:
    """
    Dynamically compares two specialization strings using local embeddings.
    Computes cosine similarity between their embeddings.
    Returns True if similarity is above the threshold, else False.
    """
    user_spec = user_spec.lower().strip()
    job_spec = job_spec.lower().strip()
    user_vec = _local_embedding_model.encode(user_spec, convert_to_tensor=True)
    job_vec = _local_embedding_model.encode(job_spec, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(user_vec, job_vec).item()
    return similarity >= threshold

class JobMatcher:
    def __init__(self):
        # Thresholds for categorizing the matching score.
        self.similarity_thresholds = {"high": 65, "medium": 35, "low": 10}

        # Initialize Pinecone client.
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
        if not self.pinecone_api_key:
            raise ValueError("Pinecone API key not found in environment variables")
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        self.pinecone_index_name = os.getenv('PINECONE_INDEX_NAME', 'skillmatch')
        self.index = self.pc.Index(self.pinecone_index_name)
        
        # Use a specific namespace for user profiles.
        self.pinecone_user_namespace = 'userprofile'
        logger.info(f"Connected to Pinecone index: {self.pinecone_index_name}, using namespace: {self.pinecone_user_namespace}")

        # It is expected that an external job embedding processor instance is set as:
        # self.job_processor = <JobEmbeddingsProcessor instance>
        self.job_processor = JobEmbeddingsProcessor()

    def get_similarity_category(self, score: float) -> str:
        if score >= self.similarity_thresholds["high"]:
            return "high"
        elif score >= self.similarity_thresholds["medium"]:
            return "average"
        elif score >= self.similarity_thresholds["low"]:
            return "low"
        else:
            return "very_low"
    
    def get_user_profile_embedding(self, profile: dict) -> list:
        return profile.get("combined_embedding", [])
    
    def query_jobs(self, embedding: list, top_k: int = 5) -> list:
        matches = []
        try:
            logger.info("🔍 Querying Pinecone in namespace=None")
            response = self.index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True,
                namespace=None
            )
            matches = response.get("matches", [])
            logger.info(f" Retrieved {len(matches)} job matches")
            for m in matches[:3]:
                logger.info(f"🔎 Job ID: {m.id} — Title: {m.metadata.get('job_title')} | Score: {m.score:.2f}")
        except Exception as e:
            logger.error(f" Error during Pinecone query: {e}")
        return matches

    
    def compute_weighted_score(self, profile: dict, job_metadata: dict) -> float:
        # Skills Matching (40%)
        profile_skills = set(normalize_skill(s) for s in profile.get("all_skills", []))
        job_skills = set(normalize_skill(s) for s in job_metadata.get("extracted_skills", []))
        if profile_skills or job_skills:
            skills_similarity = (len(profile_skills.intersection(job_skills)) / 
                                 len(profile_skills.union(job_skills))) * 100
        else:
            skills_similarity = 0
        skills_weighted = skills_similarity * 0.40

        logger.debug(f"Profile skills: {profile_skills}")
        logger.debug(f"Job skills: {job_skills}")
        logger.debug(f"Skills similarity: {skills_similarity:.2f} -> weighted: {skills_weighted:.2f}")

        # Qualification Matching (30% total)
        user_qual_text = profile.get("qualification", "")
        job_qual_text = job_metadata.get("qualifications", "")
        user_degree, user_spec = extract_degree_and_specialization(user_qual_text)
        job_degree, job_spec = extract_degree_and_specialization(job_qual_text)
        degree_rank = {'bachelors': 1, 'masters': 2, 'phd': 3}
        if user_degree and job_degree and degree_rank.get(user_degree, 0) >= degree_rank.get(job_degree, 0):
            degree_component = 100
        else:
            degree_component = 0
        degree_weighted = degree_component * 0.15

        if user_spec and job_spec:
            if dynamic_specialization_match(user_spec, job_spec):
                specialization_component = 100
                spec_weight = 0.15
            else:
                specialization_component = 0
                spec_weight = 0.05
        else:
            specialization_component = 0
            spec_weight = 0.05
        specialization_weighted = specialization_component * spec_weight

        qualification_weighted = degree_weighted + specialization_weighted

        logger.debug(f"Degree component: {degree_component} -> weighted: {degree_weighted:.2f}")
        logger.debug(f"Specialization component: {specialization_component} -> weighted: {specialization_weighted:.2f}")
        logger.debug(f"Qualification weighted total: {qualification_weighted:.2f}")

        # Experience Matching (30%)
        experience_score = 0
        user_years = 0
        if "experience_year" in profile:
            try:
                exp_data = json.loads(profile["experience_year"])
                user_years = float(exp_data.get("total_experience_years", 0))
            except Exception:
                user_years = 0
        exp_match = re.search(r'(\d+)', job_metadata.get("experience", ""))
        if exp_match:
            job_exp = float(exp_match.group(1))
        else:
            job_exp = 0
        if job_exp > 0:
            diff_percentage = abs(user_years - job_exp) / job_exp * 100
            experience_score = max(100 - diff_percentage, 0)
        experience_weighted = experience_score * 0.30

        logger.debug(f"User years: {user_years}, Job years: {job_exp}, Experience score: {experience_score:.2f} -> weighted: {experience_weighted:.2f}")

        final_score = skills_weighted + qualification_weighted + experience_weighted
        logger.debug(f"Final weighted score: {final_score:.2f}")
        return final_score
    
    def match_profile_with_jobs(self, profile: dict, top_k: int = 5) -> dict:
        embedding = self.get_user_profile_embedding(profile)
        matches = self.query_jobs(embedding, top_k=top_k)
        results = {"status": "success", "total_matches": len(matches), "matches": []}
        processed_matches = []
        for match in matches:
            job_meta = match.metadata
            weighted_score = self.compute_weighted_score(profile, job_meta)
            category = self.get_similarity_category(weighted_score)
            profile_skills = set(normalize_skill(s) for s in profile.get("all_skills", []))
            job_skills = set(normalize_skill(s) for s in job_meta.get("extracted_skills", []))



            matching_skills = list(profile_skills.intersection(job_skills))

            if not matching_skills and weighted_score >= 60:
                logger.info(f"⚠️ No matching skills found — fallback triggered for: {job_meta.get('job_title', '')}")
                matching_skills = list(job_skills)[:3]
            
            processed_matches.append({
                "job_id": match.id,
                "job_title": job_meta.get("job_title", ""),
                "company": job_meta.get("company", ""),
                "similarity_score": weighted_score,
                "similarity_category": category,
                "matching_skills": matching_skills
            })
        processed_matches = sorted(processed_matches, key=lambda x: x["similarity_score"], reverse=True)
        results["matches"] = processed_matches[:top_k]
        results["total_matches"] = len(processed_matches)



        logger.info(f"🎯 Processed {len(processed_matches)} job matches out of {len(matches)} raw matches")

        # Print top 2 for debugging
        for i, job in enumerate(processed_matches[:2]):
            logger.info(f"--- MATCH {i+1} ---")
            logger.info(f"📝 Job Title: {job['job_title']}")
            logger.info(f"🏢 Company: {job.get('company')}")
            logger.info(f"🔥 Score: {job['similarity_score']:.2f} ({job['similarity_category']})")
            logger.info(f"🛠 Matching Skills: {job['matching_skills']}")
        return results

    def match_skills_with_jobs(self, skills: list, top_k: int = 10) -> dict:
        """
        Match jobs based solely on a given list of skills.
        Concatenate the skills into a text string, compute an embedding using job_processor,
        then query the index.
        """
        skills_text = ", ".join(skills)
        logger.debug(f"Matching skills text: {skills_text}")
        # Ensure job_processor is not None
        if self.job_processor is None:
            raise ValueError("job_processor is not set. Please assign a valid embeddings processor.")
        embedding = self.job_processor.get_embedding(skills_text)
        matches = self.query_jobs(embedding, top_k=top_k)
        results = {"status": "success", "total_matches": len(matches), "matches": []}
        for match in matches:
            job_meta = match.metadata
            results["matches"].append({
                "job_id": match.id,
                "job_title": job_meta.get("job_title", ""),
                "similarity_score": match.score,
                "matching_skills": job_meta.get("extracted_skills", [])
            })
        return results

    def get_user_profile_from_pinecone(self, user_id: str) -> dict:
        dummy_vector = [0.0] * 3072
        try:
            result = self.index.query(
                vector=dummy_vector,
                filter={"user_id": user_id},
                top_k=1,
                include_metadata=True,
                namespace="userprofile"
            )
            matches = result.get("matches", [])
            if not matches:
                result = self.index.query(
                    vector=dummy_vector,
                    filter={"ID": user_id},
                    top_k=1,
                    include_metadata=True,
                    namespace="userprofile"
                )
                matches = result.get("matches", [])
            if not matches:
                try:
                    vector_response = self.index.fetch(ids=[user_id], namespace="userprofile")
                    if user_id in vector_response.vectors:
                        vector = vector_response.vectors[user_id]
                        profile = vector.metadata if hasattr(vector, 'metadata') else {}
                        profile["combined_embedding"] = vector.values
                        resume_skills = profile.get("resume_skills", [])
                        github_skills = profile.get("github_skills", [])
                        profile["all_skills"] = list(set(resume_skills + github_skills))
                        return profile
                except Exception:
                    pass
            if not matches:
                check_result = self.index.query(
                    vector=dummy_vector,
                    top_k=5,
                    include_metadata=True,
                    namespace="userprofile"
                )
                if check_result.get("matches"):
                    for match in check_result.get("matches", []):
                        if match.id == user_id:
                            profile = match.metadata
                            try:
                                vector_response = self.index.fetch(ids=[match.id], namespace="userprofile")
                                if match.id in vector_response.vectors:
                                    profile["combined_embedding"] = vector_response.vectors[match.id].values
                                else:
                                    profile["combined_embedding"] = [0.1] * 3072
                            except Exception:
                                profile["combined_embedding"] = [0.1] * 3072
                            resume_skills = profile.get("resume_skills", [])
                            github_skills = profile.get("github_skills", [])
                            profile["all_skills"] = list(set(resume_skills + github_skills))
                            return profile
                    available_ids = [match.id for match in check_result.get("matches", [])[:3]]
                    raise Exception(f"No user profile found for user_id: {user_id}. Available profiles: {available_ids}")
                else:
                    raise Exception("No user profiles found in namespace 'userprofile'")
            if matches:
                profile = matches[0].metadata
                vector_id = matches[0].id
                try:
                    vector_response = self.index.fetch(ids=[vector_id], namespace="userprofile")
                    if vector_id in vector_response.vectors:
                        profile["combined_embedding"] = vector_response.vectors[vector_id].values
                    else:
                        profile["combined_embedding"] = [0.1] * 3072
                except Exception:
                    profile["combined_embedding"] = [0.1] * 3072
                resume_skills = profile.get("resume_skills", [])
                github_skills = profile.get("github_skills", [])
                profile["all_skills"] = list(set(resume_skills + github_skills))
                return profile
            raise Exception(f"No user profile found for user_id: {user_id}")
        except Exception as e:
            raise Exception(f"Error retrieving user profile: {str(e)}")

def main():
    # import os
    # from pinecone import Pinecone, ServerlessSpec
    # pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))
    # index = pinecone.Index(os.getenv("PINECONE_INDEX_NAME"))
    
    matcher = JobMatcher()
    # matcher.index = index

    user_profile_data = {
        "ID": "test_user_123_d147f88fba006c714e27f17e96ea04bf",
        "combined_embedding": [0.25] * 3072,
        "qualification": "- Master of Computer Software Engineering from Northeastern University, Boston, USA (Expected Dec 2025)\n- Bachelor of Computer Science from Maharaja Sayajirao University, Vadodara, India (July 2018 - May 2022)",
        "experience_year": '{"total_experience_months": 39.0, "total_experience_years": 3, "experience_year": "Software Engineering Teacher Assistant: 7 months, Software Developer at Crest Data System: 16 months, Software Developer at Overclocked Brains: 16 months. Total Experience: 3 years"}',
        "github_skills": ["JavaScript", "TypeScript", "TSQL", "C++", "HTML", "CSS", "Node.js", "Yarn", "React", "SQL"],
        "resume_skills": ["JavaScript", "Java", "Python", "C++", "Typescript", "HTML", "CSS", "React.js", "Node.js"]
    }

    results = matcher.match_profile_with_jobs(user_profile_data, top_k=5)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
