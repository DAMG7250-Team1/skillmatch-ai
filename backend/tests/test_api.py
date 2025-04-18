import pytest
from fastapi.testclient import TestClient
import os
import sys
import json
from unittest.mock import patch, MagicMock
import numpy as np

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI app
from main import app

# Create a test client
client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.fixture
def mock_embeddings_processor():
    with patch("backend.jobs.embeddings.JobEmbeddingsProcessor") as mock:
        processor = MagicMock()
        processor.index = MagicMock()
        mock.return_value = processor
        yield processor

@pytest.fixture
def mock_resume_processor():
    with patch("backend.user.resume.ResumeProcessor") as mock:
        processor = MagicMock()
        mock.return_value = processor
        yield processor

@pytest.fixture
def mock_github_processor():
    with patch("backend.user.github.GitHubProcessor") as mock:
        processor = MagicMock()
        mock.return_value = processor
        yield processor

@pytest.fixture
def mock_user_processor():
    with patch("backend.user.user_embedding.UserEmbeddingProcessor") as mock:
        processor = MagicMock()
        mock.return_value = processor
        yield processor

@pytest.fixture
def mock_job_matcher():
    with patch("backend.jobs.job_matching.JobMatcher") as mock:
        matcher = MagicMock()
        mock.return_value = matcher
        yield matcher

@patch("backend.jobs.embeddings.JobEmbeddingsProcessor")
@patch("backend.user.resume.ResumeProcessor")
@patch("backend.user.github.GitHubProcessor")
@patch("backend.user.user_embedding.UserEmbeddingProcessor")
@patch("backend.jobs.job_matching.JobMatcher")
def test_job_details_endpoint(mock_job_matcher, mock_user_processor, 
                              mock_github_processor, mock_resume_processor, 
                              mock_embeddings_processor):
    """Test the job details endpoint"""
    # Mock the embeddings processor query response
    mock_embeddings_processor.return_value.index.fetch.return_value = {
        "vectors": {
            "test-job-id": {
                "id": "test-job-id",
                "metadata": {
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
            }
        }
    }
    
    # Test the job details endpoint
    response = client.get("/api/job-details/test-job-id")
    assert response.status_code == 200
    assert response.json()["metadata"]["job_title"] == "Test Engineer"
    assert response.json()["metadata"]["company"] == "Test Company"

@patch("backend.jobs.embeddings.JobEmbeddingsProcessor")
@patch("backend.user.resume.ResumeProcessor")
@patch("backend.user.github.GitHubProcessor")
@patch("backend.user.user_embedding.UserEmbeddingProcessor")
@patch("backend.jobs.job_matching.JobMatcher")
def test_match_jobs_endpoint(mock_job_matcher, mock_user_processor, 
                             mock_github_processor, mock_resume_processor, 
                             mock_embeddings_processor):
    """Test the match jobs endpoint"""
    # Mock the job matcher response
    mock_job_matcher.return_value.match_profile_with_jobs.return_value = {
        "status": "success",
        "total_matches": 1,
        "matches": [
            {
                "job_id": "test-job-id",
                "job_title": "Test Engineer",
                "company": "Test Company",
                "similarity_score": 0.85,
                "skills": ["Python", "Testing", "CI/CD"]
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