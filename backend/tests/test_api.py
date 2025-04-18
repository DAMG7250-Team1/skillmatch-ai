import pytest
from fastapi.testclient import TestClient
import os
import sys
import json
from unittest.mock import patch, MagicMock
import numpy as np

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock Pinecone before importing app
with patch('pinecone.Pinecone') as mock_pinecone:
    # Set up the mock index
    mock_index = MagicMock()
    mock_pinecone.return_value.Index.return_value = mock_index
    
    # Now import the app with mocked Pinecone
    from main import app

# Create a test client
client = TestClient(app)

# Apply patches for all processor classes
@pytest.fixture(autouse=True)
def mock_dependencies():
    """Mock all external dependencies for tests"""
    with patch('backend.jobs.embeddings.JobEmbeddingsProcessor') as mock_embeddings, \
         patch('backend.user.resume.ResumeProcessor') as mock_resume, \
         patch('backend.user.github.GitHubProcessor') as mock_github, \
         patch('backend.user.user_embedding.UserEmbeddingProcessor') as mock_user, \
         patch('backend.jobs.job_matching.JobMatcher') as mock_matcher, \
         patch('pinecone.Pinecone') as mock_pinecone, \
         patch('boto3.client') as mock_boto3, \
         patch('openai.embeddings.create') as mock_openai:
        
        # Set up mock returns
        mock_pinecone_instance = MagicMock()
        mock_index = MagicMock()
        mock_pinecone.return_value = mock_pinecone_instance
        mock_pinecone_instance.Index.return_value = mock_index
        
        yield {
            'embeddings': mock_embeddings,
            'resume': mock_resume,
            'github': mock_github,
            'user': mock_user,
            'matcher': mock_matcher,
            'pinecone': mock_pinecone,
            'boto3': mock_boto3,
            'openai': mock_openai
        }

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_job_details_endpoint():
    """Test the job details endpoint"""
    # Mock the app's embeddings processor
    with patch.object(app.embeddings_processor.index, 'fetch') as mock_fetch:
        mock_fetch.return_value = {
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

def test_match_jobs_endpoint():
    """Test the match jobs endpoint"""
    # Mock the app's job matcher
    with patch.object(app.job_matcher, 'match_profile_with_jobs') as mock_match:
        mock_match.return_value = {
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