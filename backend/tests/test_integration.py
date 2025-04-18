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

# Mock dependencies before importing
with patch('backend.jobs.embeddings.JobEmbeddingsProcessor') as mock_embeddings, \
     patch('backend.user.resume.ResumeProcessor') as mock_resume, \
     patch('backend.user.github.GitHubProcessor') as mock_github, \
     patch('backend.user.user_embedding.UserEmbeddingProcessor') as mock_user, \
     patch('backend.jobs.job_matching.JobMatcher') as mock_matcher, \
     patch('pinecone.Pinecone') as mock_pinecone, \
     patch('boto3.client') as mock_boto3, \
     patch('openai.embeddings.create') as mock_openai:

    # Set up mock instances
    mock_pinecone_instance = MagicMock()
    mock_index = MagicMock()
    mock_pinecone.return_value = mock_pinecone_instance
    mock_pinecone_instance.Index.return_value = mock_index
    
    # Import the FastAPI app
    from main import app

# Create a test client
client = TestClient(app)

class TestIntegration:
    """Integration tests that test the full flow from uploading a resume to job matching"""

    @pytest.fixture
    def mock_s3_client(self):
        """Mock the S3 client"""
        with patch('boto3.client') as mock:
            s3_client = MagicMock()
            mock.return_value = s3_client
            
            # Mock the get_object response
            s3_client.get_object.return_value = {
                'Body': io.BytesIO(b'Mock resume text content')
            }
            
            # Mock the put_object response
            s3_client.put_object.return_value = {
                'ResponseMetadata': {'HTTPStatusCode': 200}
            }
            
            yield s3_client

    @pytest.fixture
    def mock_pinecone_index(self):
        """Mock the Pinecone index"""
        with patch('pinecone.Pinecone') as mock:
            pinecone_instance = MagicMock()
            mock.return_value = pinecone_instance
            
            index = MagicMock()
            pinecone_instance.Index.return_value = index
            
            # Mock the query response
            index.query.return_value = {
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
                    },
                    {
                        'id': 'job-2',
                        'score': 0.75,
                        'metadata': {
                            'job_title': 'DevOps Engineer',
                            'company': 'Cloud Solutions',
                            'job_type': 'Full-time',
                            'work_mode': 'Hybrid',
                            'location': 'New York',
                            'seniority': 'Mid-level',
                            'experience': '3-5 years',
                            'responsibilities': 'Infrastructure, CI/CD, Monitoring',
                            'qualifications': 'AWS, Docker, Kubernetes',
                            'skills': 'AWS, Docker, Kubernetes, Jenkins, Terraform'
                        }
                    }
                ]
            }
            
            # Mock the fetch response
            index.fetch.return_value = {
                'vectors': {
                    'job-1': {
                        'id': 'job-1',
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
                }
            }
            
            yield index

    def test_resume_upload_and_job_matching(self):
        """Test the full flow from uploading a resume to job matching"""
        # Mock the necessary components directly on the app instance
        with patch.object(app, 'resume_processor') as mock_resume, \
             patch.object(app, 'github_processor') as mock_github, \
             patch.object(app, 'user_processor') as mock_user, \
             patch.object(app, 'job_matcher') as mock_matcher, \
             patch.object(app, 'embeddings_processor') as mock_embed, \
             patch('boto3.client') as mock_boto3:
             
            # Mock the resume processor
            mock_resume.process_resume.return_value = {
                'extracted_text': 'Mock resume text content',
                's3_url': 's3://mock-bucket/resumes/mock-resume.pdf',
                'filename': 'mock-resume.pdf',
                'markdown_url': 's3://mock-bucket/markdown/mock-resume.md'
            }
            
            # Mock the GitHub processor
            mock_github.process_github_profile.return_value = {
                'status': 'success',
                'github_user': 'testuser',
                'markdown_url': 's3://mock-bucket/markdown/testuser-github.md'
            }
            
            # Mock the user processor
            mock_user.process_user_data.return_value = {
                'combined_embedding': [0.1] * 1536,  # Mock embedding vector
                'all_skills': ['Python', 'AWS', 'Docker', 'Kubernetes', 'CI/CD'],
                'experience_year': '5+',
                'qualification': 'Master\'s'
            }
            
            # Mock the job matcher
            mock_matcher.match_profile_with_jobs.return_value = {
                'status': 'success',
                'total_matches': 2,
                'matches': [
                    {
                        'job_id': 'job-1',
                        'job_title': 'Senior Software Engineer',
                        'company': 'Tech Company',
                        'similarity_score': 0.85,
                        'skills': ['Python', 'AWS', 'CI/CD', 'Docker', 'Kubernetes']
                    },
                    {
                        'job_id': 'job-2',
                        'job_title': 'DevOps Engineer',
                        'company': 'Cloud Solutions',
                        'similarity_score': 0.75,
                        'skills': ['AWS', 'Docker', 'Kubernetes', 'Jenkins', 'Terraform']
                    }
                ]
            }
            
            # Mock the embeddings processor index
            mock_index = MagicMock()
            mock_embed.index = mock_index
            mock_index.fetch.return_value = {
                'vectors': {
                    'job-1': {
                        'id': 'job-1',
                        'metadata': {
                            'job_title': 'Senior Software Engineer',
                            'company': 'Tech Company',
                        }
                    }
                }
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
            assert response.json()['data']['job_matches'][0]['job_title'] == 'Senior Software Engineer'
            assert response.json()['data']['job_matches'][0]['similarity_score'] == 0.85
            
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

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 