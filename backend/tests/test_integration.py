import pytest
import os
import sys
import json
import io
from unittest.mock import patch, MagicMock
import numpy as np
from fastapi.testclient import TestClient

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock all dependencies before importing
with patch('backend.jobs.embeddings.JobEmbeddingsProcessor'), \
     patch('backend.user.resume.ResumeProcessor'), \
     patch('backend.user.github.GitHubProcessor'), \
     patch('backend.user.user_embedding.UserEmbeddingProcessor'), \
     patch('backend.jobs.job_matching.JobMatcher'), \
     patch('backend.web.company_agent.CompanyJobAgent'), \
     patch('backend.cover.cover_letter.CoverProfileAgent'), \
     patch('pinecone.Pinecone'), \
     patch('boto3.client'), \
     patch('openai.embeddings.create'):
    
    # Import the FastAPI app with mocks in place
    from main import app

# Create a test client
client = TestClient(app)

class TestIntegration:
    """Integration tests that test the full flow from uploading a resume to job matching"""

    def test_resume_upload_and_job_matching(self):
        """Test the full flow from uploading a resume to job matching"""
        
        # Mock the necessary components for the test
        with patch('main.resume_processor.process_resume') as mock_resume_process, \
             patch('main.github_processor.process_github_profile') as mock_github_process, \
             patch('main.user_processor.process_user_data') as mock_user_process, \
             patch('main.embeddings_processor.index.query') as mock_query, \
             patch('main.job_matcher.match_profile_with_jobs') as mock_match, \
             patch('main.embeddings_processor.index.fetch') as mock_fetch:
            
            # Mock resume processor
            mock_resume_process.return_value = {
                'extracted_text': 'Mock resume text content',
                's3_url': 's3://mock-bucket/resumes/mock-resume.pdf',
                'filename': 'mock-resume.pdf',
                'markdown_url': 's3://mock-bucket/markdown/mock-resume.md'
            }
            
            # Mock GitHub processor
            mock_github_process.return_value = {
                'status': 'success',
                'username': 'testuser',
                'profile_url': 'https://github.com/testuser',
                'repository_count': 10,
                'readme_count': 5,
                'markdown_url': 's3://mock-bucket/markdown/testuser-github.md'
            }
            
            # Mock user processor
            mock_user_process.return_value = {
                'combined_embedding': [0.1] * 1536,  # Mock embedding vector
                'all_skills': ['Python', 'AWS', 'Docker', 'Kubernetes', 'CI/CD'],
                'experience_year': '5+',
                'qualification': 'Master\'s'
            }
            
            # Mock Pinecone query
            mock_query.return_value = {
                'matches': [
                    {
                        'id': 'job-1',
                        'score': 0.85,
                        'metadata': {
                            'job_title': 'Senior Software Engineer',
                            'company': 'Tech Company',
                            'job_type': 'Full-time',
                            'work_mode': 'Remote',
                            'location': 'Anywhere',
                            'seniority': 'Senior',
                            'experience': '5+ years',
                            'responsibilities': 'Coding, Architecture, Mentoring',
                            'qualifications': 'Python, AWS, CI/CD',
                            'skills': 'Python, AWS, CI/CD, Docker, Kubernetes'
                        }
                    }
                ]
            }
            
            # Mock job matcher
            mock_match.return_value = {
                'status': 'success',
                'total_matches': 2,
                'matches': [
                    {
                        'job_id': 'job-1',
                        'job_title': 'Senior Software Engineer',
                        'company': 'Tech Company',
                        'similarity_score': 0.85,
                        'matching_skills': ['Python', 'AWS', 'CI/CD', 'Docker', 'Kubernetes']
                    },
                    {
                        'job_id': 'job-2',
                        'job_title': 'DevOps Engineer',
                        'company': 'Cloud Solutions',
                        'similarity_score': 0.75,
                        'matching_skills': ['AWS', 'Docker', 'Kubernetes', 'Jenkins', 'Terraform']
                    }
                ]
            }
            
            # Mock fetch for job details
            mock_fetch.return_value = MagicMock()
            mock_fetch.return_value.vectors = {
                'job-1': MagicMock(
                    metadata={
                        'job_title': 'Senior Software Engineer',
                        'company': 'Tech Company'
                    }
                )
            }
            
            # Create a mock PDF file
            mock_pdf = io.BytesIO(b'%PDF-1.5\nMock PDF content')
            mock_pdf.name = 'mock-resume.pdf'
            
            # Test uploading a resume and processing GitHub profile
            response = client.post(
                '/api/upload-resume',
                files={'file': ('mock-resume.pdf', mock_pdf, 'application/pdf')},
                params={'github_url': 'https://github.com/testuser'}
            )
            
            # Check the response
            assert response.status_code == 200
            assert response.json()['status'] == 'success'
            assert response.json()['data']['github_url'] == 'https://github.com/testuser'
            assert response.json()['data']['resume_url'] == 's3://mock-bucket/resumes/mock-resume.pdf'
            assert len(response.json()['data']['job_matches']) == 2
            
            # Test getting job details
            response = client.get('/api/job-details/job-1')
            assert response.status_code == 200
            job_details = response.json()['metadata']
            assert job_details['job_title'] == 'Senior Software Engineer'
            assert job_details['company'] == 'Tech Company'
            
            # Test matching jobs with a profile
            profile = {
                'combined_embedding': [0.1] * 1536,
                'all_skills': ['Python', 'AWS', 'Docker'],
                'experience_year': '5+',
                'qualification': 'Master\'s'
            }
            
            response = client.post(
                '/api/match-jobs',
                json={'profile': profile}
            )
            
            assert response.status_code == 200
            assert response.json()['status'] == 'success'
            assert response.json()['total_matches'] == 2
            assert response.json()['matches'][0]['job_title'] == 'Senior Software Engineer'
            
    def test_github_profile_endpoint(self):
        """Test the GitHub profile processing endpoint"""
        
        with patch('main.github_processor.process_github_profile') as mock_github_process, \
             patch('main.embeddings_processor.process_github_markdown') as mock_embeddings_process:
            
            # Mock GitHub processor response
            mock_github_process.return_value = {
                'username': 'testuser',
                'profile_url': 'https://github.com/testuser',
                'repository_count': 10,
                'readme_count': 5,
                'markdown_url': 's3://mock-bucket/markdown/testuser-github.md'
            }
            
            # Mock embeddings processor response
            mock_embeddings_process.return_value = {
                'status': 'success',
                'total_skills': 5,
                'vectors_created': 1
            }
            
            # Test the GitHub profile endpoint
            response = client.post(
                '/api/process-github',
                json={'url': 'https://github.com/testuser'}
            )
            
            # Check the response
            assert response.status_code == 200
            assert response.json()['status'] == 'success'
            assert response.json()['data']['username'] == 'testuser'
            assert response.json()['data']['embeddings_info']['total_skills'] == 5

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 