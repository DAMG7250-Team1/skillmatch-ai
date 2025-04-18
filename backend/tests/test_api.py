import pytest
import os
import sys
import json
from unittest.mock import patch, MagicMock
import numpy as np

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock dependencies before importing
with patch('backend.jobs.embeddings.JobEmbeddingsProcessor'), \
     patch('backend.user.resume.ResumeProcessor'), \
     patch('backend.user.github.GitHubProcessor'), \
     patch('backend.user.user_embedding.UserEmbeddingProcessor'), \
     patch('backend.jobs.job_matching.JobMatcher'), \
     patch('backend.web.company_agent.CompanyJobAgent'), \
     patch('backend.cover.cover_letter.CoverProfileAgent'), \
     patch('pinecone.Pinecone'), \
     patch('boto3.client'):
    
    # Now import the FastAPI app with mocks in place
    from fastapi.testclient import TestClient
    from main import app

# Create a test client
client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_job_details_endpoint():
    """Test the job details endpoint"""
    # Create a mock for the embeddings_processor.index.fetch method
    with patch('main.embeddings_processor.index.fetch') as mock_fetch:
        mock_fetch.return_value = MagicMock()
        mock_fetch.return_value.vectors = {
            "test-job-id": MagicMock(
                metadata={
                    "job_title": "Test Engineer",
                    "company": "Test Company",
                    "job_type": "Full-time",
                    "work_mode": "Remote",
                    "location": "Test Location",
                    "seniority": "Mid-level",
                    "experience": "3-5 years",
                    "responsibilities": "Testing, Coding",
                    "qualifications": "Python, Testing",
                    "skills": "Python, Testing, CI/CD"
                }
            )
        }
        
        # Test the job details endpoint
        response = client.get("/api/job-details/test-job-id")
        assert response.status_code == 200
        assert response.json()["metadata"]["job_title"] == "Test Engineer"
        assert response.json()["metadata"]["company"] == "Test Company"

def test_match_jobs_endpoint():
    """Test the match jobs endpoint"""
    # Create a mock for the job_matcher.match_profile_with_jobs method
    with patch('main.job_matcher.match_profile_with_jobs') as mock_match:
        mock_match.return_value = {
            "status": "success",
            "total_matches": 1,
            "matches": [
                {
                    "job_id": "test-job-id",
                    "job_title": "Test Engineer",
                    "company": "Test Company",
                    "similarity_score": 0.85,
                    "matching_skills": ["Python", "Testing", "CI/CD"]
                }
            ]
        }
        
        # Create a test profile
        test_profile = {
            "combined_embedding": [0.1] * 1536,  # Mock embedding vector
            "all_skills": ["Python", "Testing"],
            "experience_year": "3-5",
            "qualification": "Bachelor's"
        }
        
        # Test the match jobs endpoint
        response = client.post("/api/match-jobs", json={"profile": test_profile})
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["total_matches"] == 1
        assert response.json()["matches"][0]["job_title"] == "Test Engineer"

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 