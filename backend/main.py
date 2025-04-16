# from fastapi import FastAPI, UploadFile, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from user.resume import ResumeProcessor
# import sys
# from user.github import GitHubProcessor

# from pydantic import BaseModel
# from typing import Optional, Dict, Any, List
# import uvicorn
# import uuid
# import logging
# from pathlib import Path
# import numpy as np

# logger = logging.getLogger(__name__)

# # Add the parent directory to the Python path
# sys.path.append(str(Path(__file__).parent.parent))

# from jobs.embeddings import JobEmbeddingsProcessor
# from user.user_embedding import UserEmbeddingProcessor
# app = FastAPI(title="Resume Processing API")

# # Configure CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # In production, replace with specific origins
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize processors
# resume_processor = ResumeProcessor()
# github_processor = GitHubProcessor()
# embeddings_processor = JobEmbeddingsProcessor()
# user_processor = UserEmbeddingProcessor()

# class GitHubProfile(BaseModel):
#     url: str

# class GitHubResponse(BaseModel):
#     status: str
#     message: str
#     data: Dict[str, Any]

# class ResumeResponse(BaseModel):
#     status: str
#     message: str
#     data: Dict[str, Any]

# class JobData(BaseModel):
#     job_title: str
#     company: str
#     location: str
#     job_type: str
#     work_mode: str
#     seniority: str
#     salary: str
#     experience: str
#     responsibilities: str
#     qualifications: str
#     skills: str

# class JobMatchRequest(BaseModel):
#     resume_skills: List[str]
#     github_skills: List[str]

# class JobMatchResponse(BaseModel):
#     status: str
#     total_skills: int
#     total_matches: int
#     matches: List[Dict[str, Any]]
#     error: Optional[str] = None

# @app.post("/api/upload-resume", response_model=ResumeResponse)
# async def upload_resume(file: UploadFile, github_url: str):
#     """
#     Upload and process a resume file, then find matching jobs
#     """
#     if not file.filename.lower().endswith('.pdf'):
#         raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
#     try:
#         # Generate a unique user ID if not provided
#         user_id = str(uuid.uuid4())
        
#         # Read file content
#         file_content = await file.read()
        
#         # Process resume
#         result = resume_processor.process_resume(
#             file_content=file_content,
#             original_filename=file.filename
#         )
        
#         # Ensure all required fields are present
#         required_fields = ['extracted_text', 's3_url', 'filename', 'markdown_url']
#         if not all(key in result for key in required_fields):
#             raise HTTPException(
#                 status_code=500,
#                 detail="Missing required fields in resume processing result"
#             )
        
#         # Process GitHub profile if URL is provided
#         github_result = None
#         if github_url:
#             try:
#                 github_result = github_processor.process_github_profile(github_url)
#             except Exception as e:
#                 print(f"Warning: Failed to process GitHub profile: {str(e)}")
#                 github_result = {
#                     "status": "failed",
#                     "error": str(e)
#                 }
        
#         # Use proper combined embedding from UserEmbeddingProcessor
#         user_profile = user_processor.process_user_data(
#             resume_url=result["markdown_url"],
#             github_url=github_result["markdown_url"] if github_result else None
#         )
        
#         # Get the combined embedding and skills
#         user_embedding = user_profile.get("combined_embedding", [])
#         all_skills = user_profile.get("all_skills", [])
        
#         # Log vector sanity check
#         logger.info(f"[Embedding] Norm: {np.linalg.norm(user_embedding):.4f}, Dimensions: {len(user_embedding)}")
        
#         # Query Pinecone with user embedding
#         job_vectors = embeddings_processor.index.query(
#             vector=user_embedding,
#             filter={"source": "job"},
#             top_k=50,  # Get more matches to filter
#             include_metadata=True
#         )
        
#         # Process matches with skill overlap
#         job_matches = []
#         seen_jobs = set()  # Track seen jobs to avoid duplicates
        
#         for match in job_vectors.matches:
#             # Create unique job identifier
#             job_key = f"{match.metadata.get('job_title', '')}_{match.metadata.get('company', '')}"
#             if job_key in seen_jobs:
#                 continue
#             seen_jobs.add(job_key)
            
#             # Get job skills
#             job_skills = set(match.metadata.get("extracted_skills", []))
            
#             # Calculate skill overlap
#             matching_skills = set(all_skills).intersection(job_skills)
#             overlap_pct = (len(matching_skills) / min(len(job_skills), len(all_skills)) * 100) if job_skills and all_skills else 0
            
#             # Skip if no skill overlap
#             if not matching_skills:
#                 continue
            
#             # Adjust score based on skill overlap
#             base_score = match.score
#             skill_bonus = (overlap_pct / 100) * 0.4  # Add up to 40% bonus for skill overlap
#             adjusted_score = min(base_score + skill_bonus, 1.0)
            
#             job_matches.append({
#                 "job_id": match.id,
#                 "job_title": match.metadata["job_title"],
#                 "company": match.metadata["company"],
#                 "location": match.metadata["location"],
#                 "job_type": match.metadata["job_type"],
#                 "work_mode": match.metadata["work_mode"],
#                 "seniority": match.metadata["seniority"],
#                 "experience": match.metadata["experience"],
#                 "similarity_score": adjusted_score,
#                 "skills": list(matching_skills),
#                 "skill_overlap_percent": overlap_pct
#             })
        
#         # Sort by adjusted score and skill overlap
#         job_matches.sort(key=lambda x: (x["similarity_score"], x["skill_overlap_percent"]), reverse=True)
        
#         # Return only top 10 matches
#         job_matches = job_matches[:10]
        
#         return {
#             "status": "success",
#             "message": "Resume processed successfully",
#             "data": {
#                 "user_id": user_id,
#                 "github_url": github_url,
#                 "resume_url": result["s3_url"],
#                 "filename": result["filename"],
#                 "markdown_url": result["markdown_url"],
#                 "extracted_text_preview": result["extracted_text"][:500] + "..." if result["extracted_text"] else "",
#                 "embeddings_info": {
#                     "status": "success",
#                     "total_skills": len(all_skills),
#                     "skills": all_skills,
#                     "embedding_norm": float(np.linalg.norm(user_embedding)),
#                     "embedding_dimensions": len(user_embedding)
#                 },
#                 "github_info": github_result,
#                 "job_matches": job_matches
#             }
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/process-github", response_model=GitHubResponse)
# async def process_github(profile: GitHubProfile):
#     """
#     Process GitHub profile and extract information
#     """
#     try:
#         # Generate a unique user ID if not provided
#         user_id = str(uuid.uuid4())
        
#         # Process GitHub profile
#         result = github_processor.process_github_profile(profile.url)
        
#         # Process GitHub embeddings
#         try:
#             embeddings_result = embeddings_processor.process_github_markdown(
#                 markdown_url=result["markdown_url"],
#                 user_id=user_id
#             )
#             result["embeddings_info"] = embeddings_result
#         except Exception as e:
#             # Log the error but don't fail the request
#             print(f"Warning: Failed to process GitHub embeddings: {str(e)}")
#             result["embeddings_info"] = {
#                 "status": "failed",
#                 "total_skills": 0,
#                 "vectors_created": 0,
#                 "error": str(e)
#             }
        
#         return {
#             "status": "success",
#             "message": "GitHub profile processed successfully",
#             "data": {
#                 "user_id": user_id,
#                 "username": result["username"],
#                 "profile_url": result["profile_url"],
#                 "repository_count": str(result["repository_count"]),
#                 "readme_count": str(result["readme_count"]),
#                 "markdown_url": result["markdown_url"],
#                 "embeddings_info": result.get("embeddings_info", {})
#             }
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/match-jobs", response_model=JobMatchResponse)
# async def match_jobs(request: JobMatchRequest):
#     try:
#         # Combine and deduplicate skills
#         all_skills = list(set(request.resume_skills + request.github_skills))
        
#         # Create a text query from skills
#         skills_text = ", ".join(all_skills)
#         query_text = f"Find jobs requiring these skills: {skills_text}"
        
#         # Find matching jobs
#         result = embeddings_processor.find_matching_jobs(query_text=query_text)
        
#         if result["status"] == "error":
#             return JobMatchResponse(
#                 status="error",
#                 total_skills=len(all_skills),
#                 total_matches=0,
#                 matches=[],
#                 error=result.get("error", "Unknown error occurred")
#             )
        
#         # Transform matches to match frontend expectations
#         transformed_matches = []
#         for match in result["matches"]:
#             metadata = match.get("metadata", {})
#             transformed_matches.append({
#                 "job_title": metadata.get("job_title", "Unknown Title"),
#                 "company": metadata.get("company", "Unknown Company"),
#                 "location": metadata.get("location", "Unknown Location"),
#                 "job_type": metadata.get("job_type", "Unknown Type"),
#                 "work_mode": metadata.get("work_mode", "Unknown Mode"),
#                 "seniority": metadata.get("seniority", "Unknown Level"),
#                 "salary": metadata.get("salary", "Not Specified"),
#                 "experience": metadata.get("experience", "Not Specified"),
#                 "responsibilities": metadata.get("responsibilities", "Not Specified"),
#                 "qualifications": metadata.get("qualifications", "Not Specified"),
#                 "skills": metadata.get("skills", "Not Specified"),
#                 "similarity_score": match.get("similarity", 0.0),
#                 "match_category": match.get("category", "unknown")
#             })
        
#         return JobMatchResponse(
#             status="success",
#             total_skills=len(all_skills),
#             total_matches=result["total_matches"],
#             matches=transformed_matches
#         )
        
#     except Exception as e:
#         logger.error(f"Error matching jobs: {str(e)}")
#         return JobMatchResponse(
#             status="error",
#             total_skills=0,
#             total_matches=0,
#             matches=[],
#             error=str(e)
#         )

# @app.post("/api/batch-match-jobs", response_model=JobMatchResponse)
# async def batch_match_jobs(jobs: List[JobData]):
#     """
#     Process multiple job descriptions and find matching user profiles
#     """
#     try:
#         results = []
#         for job in jobs:
#             job_dict = job.dict()
#             matches = embeddings_processor.get_job_matches(job_dict)
#             results.append({
#                 "job_info": matches["job_info"],
#                 "matches": matches["matches"]
#             })
        
#         return {
#             "status": "success",
#             "message": f"Processed {len(results)} jobs successfully",
#             "data": {
#                 "results": results
#             }
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/health")
# async def health_check():
#     """Health check endpoint"""
#     return {"status": "healthy"}

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)




from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# Add the parent directory to the Python path
import sys





from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import uuid
import logging
from pathlib import Path
import numpy as np

# Updated logger
logger = logging.getLogger(__name__)
sys.path.append(str(Path(__file__).parent.parent))


from jobs.embeddings import JobEmbeddingsProcessor
from jobs.job_matching import JobMatcher, normalize_skill

from user.resume import ResumeProcessor
from user.github import GitHubProcessor
from user.user_embedding import UserEmbeddingProcessor

app = FastAPI(title="Resume Processing API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors
resume_processor = ResumeProcessor()
github_processor = GitHubProcessor()
embeddings_processor = JobEmbeddingsProcessor()
user_processor = UserEmbeddingProcessor()
# ✅ Job matcher setup
job_matcher = JobMatcher()
job_matcher.index = embeddings_processor.index
job_matcher.job_processor = embeddings_processor  # ✅ critical to avoid no matches


# Pydantic models for input/output
class GitHubProfile(BaseModel):
    url: str

class GitHubResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]

class ResumeResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]

class JobMatchRequest(BaseModel):
    profile: Dict[str, Any]

class JobMatchResponse(BaseModel):
    status: str
    total_skills: int
    total_matches: int
    matches: List[Dict[str, Any]]
    error: Optional[str] = None

@app.post("/api/upload-resume", response_model=ResumeResponse)
async def upload_resume(file: UploadFile, github_url: str):
    """
    Upload a resume PDF and GitHub URL.
      1. Processes resume: converts PDF to markdown and uploads to S3.
      2. Processes GitHub profile: converts profile data to markdown and uploads to S3.
      3. Combines these markdown files, extracts skills & experience, 
         and generates a combined embedding that is upserted into Pinecone 
         under the "userprofile" namespace.
      4. Then queries the job embeddings (from the default namespace)
         using the combined embedding to find the top 10 job matches.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Generate unique user ID
        user_id = str(uuid.uuid4())
        
        # Read resume file content
        file_content = await file.read()
        
        # Process resume (convert PDF to markdown and upload to S3)
        resume_result = resume_processor.process_resume(
            file_content=file_content,
            original_filename=file.filename
        )
        
        # Check for required fields in resume processing result
        required_fields = ['extracted_text', 's3_url', 'filename', 'markdown_url']
        if not all(key in resume_result for key in required_fields):
            raise HTTPException(
                status_code=500,
                detail="Missing required fields in resume processing result"
            )
        
        # Process GitHub profile if a URL is provided
        github_result = None
        if github_url:
            try:
                github_result = github_processor.process_github_profile(github_url)
            except Exception as e:
                logger.warning(f"Failed to process GitHub profile: {str(e)}")
                github_result = {"status": "failed", "error": str(e)}
        
        # Now combine the user data using the embedding processor;
        # this reads the resume markdown (and GitHub markdown if available) from S3,
        # extracts skills, computes a combined embedding and upserts into Pinecone in "userprofile" namespace.
        user_profile = user_processor.process_user_data(
            resume_url=resume_result["markdown_url"],
            github_url=github_result["markdown_url"] if github_result and "markdown_url" in github_result else None
        )
        
        # Retrieve the combined embedding and skills from the user profile
        user_embedding = user_profile.get("combined_embedding", [])
        all_skills = user_profile.get("all_skills", [])
        logger.info(f"[Embedding] Norm: {np.linalg.norm(user_embedding):.4f}, Dimensions: {len(user_embedding)}")
        
        # Query job embeddings from Pinecone using the user embedding.
        # Here we specify namespace="default" to query job postings.
        job_query_result = embeddings_processor.index.query(
            vector=user_embedding,
            top_k=50,      # Get more candidates to filter later
            include_metadata=True,
            namespace=None  # Explicitly use default namespace for job postings
        )
        
        # Process job matches. Calculate skill overlap and adjust similarity score.
        job_matches = []
        seen_jobs = set()
        for match in job_query_result.matches:
            # Create a unique key to avoid duplicate job matches
            job_key = f"{match.metadata.get('job_title', '')}_{match.metadata.get('company', '')}"
            if job_key in seen_jobs:
                continue
            seen_jobs.add(job_key)
            
            job_skills = set(match.metadata.get("extracted_skills", []))
            matching_skills = set(all_skills).intersection(job_skills)
            if job_skills and all_skills:
                overlap_pct = (len(matching_skills) / min(len(job_skills), len(all_skills))) * 100
            else:
                overlap_pct = 0
            
            # Skip if there is no overlap in skills
            if not matching_skills:
                continue
            
            base_score = match.score
            # Bonus: add up to 40% bonus for skill overlap
            skill_bonus = (overlap_pct / 100) * 0.4
            adjusted_score = min(base_score + skill_bonus, 1.0)
            
            job_matches.append({
                "job_id": match.id,
                "job_title": match.metadata.get("job_title", ""),
                "company": match.metadata.get("company", ""),
                "location": match.metadata.get("location", ""),
                "job_type": match.metadata.get("job_type", ""),
                "work_mode": match.metadata.get("work_mode", ""),
                "seniority": match.metadata.get("seniority", ""),
                "experience": match.metadata.get("experience", ""),
                "similarity_score": adjusted_score,
                "skills": list(matching_skills),
                "skill_overlap_percent": overlap_pct
            })
        
        # Sort the matches by adjusted score and overlap percentage, then return the top 10
        job_matches.sort(key=lambda x: (x["similarity_score"], x["skill_overlap_percent"]), reverse=True)
        top_10_matches = job_matches[:10]
        
        return {
            "status": "success",
            "message": "Resume processed successfully",
            "data": {
                "user_id": user_id,
                "github_url": github_url,
                "resume_url": resume_result["s3_url"],
                "filename": resume_result["filename"],
                "markdown_url": resume_result["markdown_url"],
                "extracted_text_preview": resume_result["extracted_text"][:500] + "..." if resume_result["extracted_text"] else "",
                "embeddings_info": {
                    "status": "success",
                    "total_skills": len(all_skills),
                    "skills": all_skills,
                    "embedding": user_embedding,
                    "embedding_norm": float(np.linalg.norm(user_embedding)),
                    "embedding_dimensions": len(user_embedding)
                },
                "github_info": github_result,
                "job_matches": top_10_matches
            }
        }
    except Exception as e:
        logger.error(f"Error in /api/upload-resume: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/process-github", response_model=GitHubResponse)
async def process_github(profile: GitHubProfile):
    """
    Process GitHub profile and extract necessary information.
    Also, process GitHub markdown to create an embedding.
    """
    try:
        user_id = str(uuid.uuid4())
        result = github_processor.process_github_profile(profile.url)
        try:
            embeddings_result = embeddings_processor.process_github_markdown(
                markdown_url=result["markdown_url"],
                user_id=user_id
            )
            result["embeddings_info"] = embeddings_result
        except Exception as e:
            logger.warning(f"Failed to process GitHub embeddings: {str(e)}")
            result["embeddings_info"] = {
                "status": "failed",
                "total_skills": 0,
                "vectors_created": 0,
                "error": str(e)
            }
        
        return {
            "status": "success",
            "message": "GitHub profile processed successfully",
            "data": {
                "user_id": user_id,
                "username": result["username"],
                "profile_url": result["profile_url"],
                "repository_count": str(result["repository_count"]),
                "readme_count": str(result["readme_count"]),
                "markdown_url": result["markdown_url"],
                "embeddings_info": result.get("embeddings_info", {})
            }
        }
    except Exception as e:
        logger.error(f"Error in /api/process-github: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import Path

@app.get("/api/job-details/{job_id}")
async def get_job_details(job_id: str = Path(...)):
    try:
        # Fetch job vector from Pinecone using job ID (assuming jobs are in "default" namespace)
        result = embeddings_processor.index.fetch(
            ids=[job_id],
            namespace=None  # or use os.getenv('PINECONE_NAMESPACE', 'default')
        )

        vector = result.vectors.get(job_id)
        if not vector:
            raise HTTPException(status_code=404, detail="Job not found")

        metadata = vector.metadata or {}
        return {
            "status": "success",
            "job_id": job_id,
            "metadata": metadata
        }

    except Exception as e:
        logger.error(f"Error fetching job details for {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



# @app.post("/api/match-jobs", response_model=JobMatchResponse)
# async def match_jobs(request: JobMatchRequest):
#     try:
#         if job_matcher.job_processor is None:
#             raise Exception("JobMatcher.job_processor is not set.")

#         all_skills = list(set(normalize_skill(s) for s in request.resume_skills + request.github_skills))
#         logger.info(f"Matching with {len(all_skills)} normalized skills")

#         match_result = job_matcher.match_skills_with_jobs(all_skills, top_k=10)
#         logger.info(f"Found {match_result.get('total_matches', 0)} job matches")

#         # ✅ Use match fields directly (not match['metadata'])
#         transformed_matches = []
#         for match in match_result.get("matches", []):
#             transformed_matches.append({
#                 "job_id": match.get("job_id"),
#                 "job_title": match.get("job_title"),
#                 "company": match.get("company"),
#                 "location": match.get("location"),
#                 "job_type": match.get("job_type"),
#                 "work_mode": match.get("work_mode"),
#                 "seniority": match.get("seniority"),
#                 "salary": match.get("salary"),
#                 "experience": match.get("experience"),
#                 "responsibilities": match.get("responsibilities"),
#                 "qualifications": match.get("qualifications"),
#                 "skills": match.get("matching_skills", []),  # only intersection, not full skills
#                 "similarity_score": match.get("similarity_score", 0.0),
#                 "match_category": match.get("similarity_category", "unknown")
#             })

#         return JobMatchResponse(
#             status=match_result.get("status", "error"),
#             total_skills=len(all_skills),
#             total_matches=match_result.get("total_matches", 0),
#             matches=transformed_matches
#         )

#     except Exception as e:
#         logger.error(f"Error in /api/match-jobs: {str(e)}")
#         return JobMatchResponse(
#             status="error",
#             total_skills=0,
#             total_matches=0,
#             matches=[],
#             error=str(e)
#         )





@app.post("/api/match-jobs", response_model=JobMatchResponse)
async def match_jobs(request: JobMatchRequest):
    try:
        profile = request.profile
        if not profile:
            raise HTTPException(status_code=400, detail="Missing profile data")

        logger.info("Performing advanced job matching using full profile")
        match_result = job_matcher.match_profile_with_jobs(profile, top_k=10)

        transformed_matches = []
        for match in match_result.get("matches", []):
            transformed_matches.append({
                "job_id": match.get("job_id"),
                "job_title": match.get("job_title"),
                "company": match.get("company", "N/A"),
                "location": match.get("location", "Unknown"),
                "job_type": match.get("job_type", "Unknown"),
                "work_mode": match.get("work_mode", "Unknown"),
                "seniority": match.get("seniority", "Unknown"),
                "salary": match.get("salary", "Not Specified"),
                "experience": match.get("experience", "Not Specified"),
                "responsibilities": match.get("responsibilities", "Not Specified"),
                "qualifications": match.get("qualifications", "Not Specified"),
                "skills": match.get("matching_skills", []),
                "similarity_score": match.get("similarity_score", 0.0),
                "match_category": match.get("similarity_category", "unknown")
            })

        return JobMatchResponse(
            status=match_result.get("status", "error"),
            total_skills=len(profile.get("all_skills", [])),
            total_matches=match_result.get("total_matches", 0),
            matches=transformed_matches
        )

    except Exception as e:
        logger.error(f"Error in /api/match-jobs: {str(e)}")
        return JobMatchResponse(
            status="error",
            total_skills=0,
            total_matches=0,
            matches=[],
            error=str(e)
        )







@app.get("/api/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
