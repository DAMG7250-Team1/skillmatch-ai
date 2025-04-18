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
    from user.github import GitHubProcessor

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
    def test_get_user_profile(self, mock_requests_get, github_processor):
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
            "created_at": "2020-01-01T00:00:00Z",
            "updated_at": "2020-01-01T00:00:00Z"
        }
        
        # Set mock response
        mock_requests_get.return_value = mock_profile_response
        
        # Call the method
        profile_data = github_processor.get_user_profile("testuser")
        
        # Assertions
        assert profile_data["login"] == "testuser"
        assert profile_data["name"] == "Test User"
        assert profile_data["bio"] == "Test bio"
        assert profile_data["public_repos"] == 10
        
    @patch('requests.get')
    def test_get_user_repositories(self, mock_requests_get, github_processor):
        """Test fetching a user's repositories"""
        # Mock repositories response
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
                "updated_at": "2020-02-01T00:00:00Z",
                "topics": ["python", "testing"]
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
                "updated_at": "2020-04-01T00:00:00Z",
                "topics": ["javascript", "web"]
            }
        ]
        
        # For the second page, return empty list to end the pagination
        mock_empty_response = MagicMock()
        mock_empty_response.status_code = 200
        mock_empty_response.json.return_value = []
        
        # Set side effects for mock_requests_get
        mock_requests_get.side_effect = [mock_repos_response, mock_empty_response]
        
        # Call the method
        repos = github_processor.get_user_repositories("testuser")
        
        # Assertions
        assert len(repos) == 2
        assert repos[0]["name"] == "test-repo-1"
        assert repos[1]["language"] == "JavaScript"

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 