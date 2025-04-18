import pytest
import os
import sys
import json
from unittest.mock import patch, MagicMock, mock_open

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock dependencies before importing
with patch('boto3.client'), \
     patch('pinecone.Pinecone'), \
     patch('openai.embeddings.create'):
    # Import the GitHub processor
    from backend.user.github import GitHubProcessor

class TestGitHubProcessor:
    """
    Test the GitHubProcessor class functionality
    """
    
    @pytest.fixture
    def github_processor(self):
        """Create a GitHub processor instance"""
        with patch('boto3.client'):
            processor = GitHubProcessor()
            yield processor
    
    @patch('requests.get')
    def test_fetch_github_profile(self, mock_requests_get, github_processor):
        """Test fetching a GitHub profile"""
        # Mock response for GitHub API calls
        mock_profile_response = MagicMock()
        mock_profile_response.status_code = 200
        mock_profile_response.json.return_value = {
            "login": "testuser",
            "name": "Test User",
            "company": "Test Company",
            "blog": "https://testuser.com",
            "location": "Test Location",
            "email": "test@example.com",
            "bio": "Test bio",
            "public_repos": 10,
            "followers": 50,
            "following": 20,
            "created_at": "2020-01-01T00:00:00Z"
        }
        
        mock_repos_response = MagicMock()
        mock_repos_response.status_code = 200
        mock_repos_response.json.return_value = [
            {
                "name": "test-repo-1",
                "html_url": "https://github.com/testuser/test-repo-1",
                "description": "Test repository 1",
                "language": "Python",
                "stargazers_count": 5,
                "forks_count": 2,
                "fork": False,
                "created_at": "2020-01-01T00:00:00Z",
                "updated_at": "2020-02-01T00:00:00Z"
            },
            {
                "name": "test-repo-2",
                "html_url": "https://github.com/testuser/test-repo-2",
                "description": "Test repository 2",
                "language": "JavaScript",
                "stargazers_count": 10,
                "forks_count": 3,
                "fork": False,
                "created_at": "2020-03-01T00:00:00Z",
                "updated_at": "2020-04-01T00:00:00Z"
            }
        ]
        
        # Set side effects for mock_requests_get
        mock_requests_get.side_effect = [mock_profile_response, mock_repos_response]
        
        # Call the method
        profile_data = github_processor._fetch_github_profile("https://github.com/testuser")
        
        # Assertions
        assert profile_data["login"] == "testuser"
        assert profile_data["name"] == "Test User"
        assert len(profile_data["repositories"]) == 2
        assert profile_data["repositories"][0]["name"] == "test-repo-1"
        assert profile_data["repositories"][1]["language"] == "JavaScript"
        
    @patch('requests.get')
    @patch('boto3.client')
    def test_process_github_profile(self, mock_boto3_client, mock_requests_get, github_processor):
        """Test processing a GitHub profile"""
        # Mock S3 client
        mock_s3 = MagicMock()
        mock_boto3_client.return_value = mock_s3
        
        # Mock response for GitHub API calls
        mock_profile_response = MagicMock()
        mock_profile_response.status_code = 200
        mock_profile_response.json.return_value = {
            "login": "testuser",
            "name": "Test User",
            "bio": "Test bio",
            "public_repos": 10
        }
        
        mock_repos_response = MagicMock()
        mock_repos_response.status_code = 200
        mock_repos_response.json.return_value = [
            {
                "name": "test-repo-1",
                "language": "Python",
                "description": "Test repository 1"
            }
        ]
        
        # Set side effects for mock_requests_get
        mock_requests_get.side_effect = [mock_profile_response, mock_repos_response]
        
        # Patch the _fetch_github_profile method to use our mocks
        with patch.object(github_processor, '_fetch_github_profile', return_value={
            "login": "testuser",
            "name": "Test User",
            "bio": "Test bio",
            "public_repos": 10,
            "repositories": [
                {
                    "name": "test-repo-1",
                    "language": "Python",
                    "description": "Test repository 1"
                }
            ]
        }):
            # Mock the S3 upload
            mock_s3.put_object.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
            
            # Call the method to test
            result = github_processor.process_github_profile("https://github.com/testuser")
            
            # Assertions
            assert result["status"] == "success"
            assert "markdown_url" in result
            assert "s3://" in result["markdown_url"]
            assert "github_user" in result
            assert result["github_user"] == "testuser"

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 