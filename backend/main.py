



from fastapi import FastAPI, UploadFile, HTTPException, Path  # Import FastAPI's Path
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid
import logging
import numpy as np

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import standard library Path as FSPath if needed to avoid conflict
from pathlib import Path as FSPath

# Pydantic models
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

# Add the parent directory to the Python path
import sys
sys.path.append(str(FSPath(__file__).parent.parent))

# Import our processors from our modules
from backend.jobs.embeddings import JobEmbeddingsProcessor
from backend.user.resume import ResumeProcessor
from backend.user.github import GitHubProcessor
from backend.user.user_embedding import UserEmbeddingProcessor
from backend.jobs.job_matching import JobMatcher
from backend.web.company_agent import CompanyJobAgent
# Import our combined cover letter and feedback generation function (from cover_letter.py, for example)
from backend.cover.cover_letter import CoverProfileAgent

# Create the FastAPI app
app = FastAPI(title="Resume Processing API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set this to allowed origins only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors
resume_processor = ResumeProcessor()
github_processor = GitHubProcessor()
embeddings_processor = JobEmbeddingsProcessor()
user_processor = UserEmbeddingProcessor()
job_matcher = JobMatcher()
job_matcher.index = embeddings_processor.index
job_matcher.job_processor = embeddings_processor  # Required for job embedding queries
generate_cover_letter_and_improvements = CoverProfileAgent()

# Define Pydantic models for endpoint responses
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

class GenerateResponse(BaseModel):
    status: str
    cover_letter: str
    improvement_suggestions: str

class CoverLetterRequest(BaseModel):
    profile_text: str
    job_description: str

class CoverLetterResponse(BaseModel):
    cover_letter: str
class WebAgentResponse(BaseModel):
    status: str
    company_info: dict
    similar_jobs: list

# ----------------------------------------------------------------
# Endpoint: Upload Resume & Process Profile
# ----------------------------------------------------------------
@app.post("/api/upload-resume", response_model=ResumeResponse)
async def upload_resume(file: UploadFile, github_url: str):
    """
    Upload a resume PDF and GitHub URL.
    1. Process resume: extract text, convert to markdown, and upload to S3.
    2. Process GitHub profile: convert GitHub profile to markdown and upload to S3.
    3. Combine both to generate a combined embedding saved in Pinecone under "userprofile".
    4. Query job embeddings to get top job matches.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        user_id = str(uuid.uuid4())
        file_content = await file.read()
        
        # Process the resume
        resume_result = resume_processor.process_resume(
            file_content=file_content,
            original_filename=file.filename
        )
        required_fields = ['extracted_text', 's3_url', 'filename', 'markdown_url']
        if not all(key in resume_result for key in required_fields):
            raise HTTPException(status_code=500, detail="Missing required fields in resume processing result")
        
        # Process GitHub profile if provided
        github_result = None
        if github_url:
            try:
                github_result = github_processor.process_github_profile(github_url)
            except Exception as e:
                logging.warning(f"Failed to process GitHub profile: {str(e)}")
                github_result = {"status": "failed", "error": str(e)}
        
        # Combine user data using our embedding processor
        user_profile = user_processor.process_user_data(
            resume_url=resume_result["markdown_url"],
            github_url=github_result["markdown_url"] if github_result and "markdown_url" in github_result else None
        )
        
        user_embedding = user_profile.get("combined_embedding")
        all_skills = user_profile.get("all_skills", [])
        logging.info(f"[Embedding] Norm: {np.linalg.norm(user_embedding):.4f}, Dimensions: {len(user_embedding)}")
        
        # Query job embeddings (default namespace is used)
        job_query_result = embeddings_processor.index.query(
            vector=user_embedding,
            top_k=50,
            include_metadata=True,
            namespace=None
        )
        
        # Process job matches based on skill overlap and adjust score
        matcher = job_matcher
        matcher.index         = embeddings_processor.index
        matcher.job_processor = embeddings_processor   # ← very important!

        profile_payload = {
            "combined_embedding": user_embedding,
            "all_skills":          all_skills,
            "experience_year":     user_profile["experience_year"],      
            "qualification":       user_profile["qualification"]
        }
        match_result    = matcher.match_profile_with_jobs(profile_payload, top_k=10)
        top_10_matches  = match_result.get("matches", [])

        
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
        logging.error(f"Error in /api/upload-resume: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------------
# Endpoint: Process GitHub Profile
# ----------------------------------------------------------------
@app.post("/api/process-github", response_model=GitHubResponse)
async def process_github(profile: GitHubProfile):
    """
    Process GitHub profile to extract information and generate markdown embedding.
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
            logging.warning(f"Failed to process GitHub embeddings: {str(e)}")
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
        logging.error(f"Error in /api/process-github: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------------
# Endpoint: Get Job Details
# ----------------------------------------------------------------




@app.get("/api/job-details/{job_id}")
async def get_job_details(job_id: str = Path(...)):
    try:
        result = embeddings_processor.index.fetch(
            ids=[job_id],
            namespace=None  # default namespace
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
        logging.error(f"Error fetching job details for {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------------
# Endpoint: Match Jobs based on Full User Profile
# ----------------------------------------------------------------
@app.post("/api/match-jobs", response_model=JobMatchResponse)
async def match_jobs(request: JobMatchRequest):
    try:
        profile = request.profile
        if not profile:
            raise HTTPException(status_code=400, detail="Missing profile data")
        logging.info("Performing advanced job matching using full profile")
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
        logging.error(f"Error in /api/match-jobs: {str(e)}")
        return JobMatchResponse(
            status="error",
            total_skills=0,
            total_matches=0,
            matches=[],
            error=str(e)
        )

# ----------------------------------------------------------------
# Endpoint: Generate Feedback & Cover Letter
# ----------------------------------------------------------------



@app.post("/api/generate-feedback-cover-letter", response_model=GenerateResponse)
async def generate_feedback_cover_letter(data: dict):

    # Log the received data
    logger.info("Received data for cover letter and feedback generation")
    logger.debug(f"Received data: {data}")



    profile_text = data.get("profile_text", "")
    job_description = data.get("job_description", "")
    
    if not profile_text or not job_description:
        raise HTTPException(status_code=400, detail="Missing profile_text or job_description")
    
    try:
        cover_letter = generate_cover_letter_and_improvements.generate_cover_letter(profile_text, job_description)
        improvement_suggestions = generate_cover_letter_and_improvements.generate_improvement_suggestions(profile_text, job_description)
        

        logger.info("Cover letter generation completed")
        logger.debug(f"Cover letter: {cover_letter}")
        logger.info("Improvement suggestions generation completed")
        logger.debug(f"Improvement suggestions: {improvement_suggestions}")

        
        return GenerateResponse(
            status="success",
            cover_letter=cover_letter,
            improvement_suggestions=improvement_suggestions
        )
    except Exception as e:
        logging.error(f"Error generating feedback and cover letter: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))











# ----------------------------------------------------------------
# Endpoint: Generate more similar jobs & comapny background
# ----------------------------------------------------------------
from fastapi import Body
@app.post("/api/webagent", response_model=WebAgentResponse)
async def webagent_suggestions(company: str = Body(...), job_query: str = Body(...)):
    try:
        logging.info(f"[WebAgent] Company = {company}, Job Query = {job_query}")
        
        agent = CompanyJobAgent()
        
        company_info = agent.research_company(company)
        logging.info(f"[WebAgent] Retrieved company info with keys: {list(company_info.keys())}")
        
        similar_jobs = [job for _, job in agent._search_jobs(job_query)[:3]]

        return {
            "status": "success",
            "company_info": company_info,
            "similar_jobs": similar_jobs
        }

    except Exception as e:
        import traceback
        logging.error("❌ Error inside /api/webagent")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))















# ----------------------------------------------------------------
# Health Check Endpoint
# ----------------------------------------------------------------
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# ----------------------------------------------------------------
# Run the Server
# ----------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
