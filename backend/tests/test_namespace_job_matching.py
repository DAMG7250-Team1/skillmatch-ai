import os
import sys
import unittest
import json
from unittest.mock import MagicMock, patch

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from jobs.job_matching import JobMatcher
from pinecone import Pinecone

class TestNamespaceJobMatching(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Retrieve Pinecone configuration from environment variables
        cls.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        cls.pinecone_env = os.getenv("PINECONE_ENVIRONMENT")
        cls.pinecone_index = os.getenv("PINECONE_INDEX_NAME")
        cls.jobs_namespace = os.getenv("PINECONE_NAMESPACE", "default")  # Jobs namespace (default)
        cls.user_namespace = os.getenv("PINECONE_USER_NAMESPACE", "userprofile")  # User profile namespace

        if not cls.pinecone_api_key or not cls.pinecone_env or not cls.pinecone_index:
            raise Exception("Please set PINECONE_API_KEY, PINECONE_ENVIRONMENT, and PINECONE_INDEX_NAME environment variables.")

        # Initialize Pinecone
        cls.pc = Pinecone(api_key=cls.pinecone_api_key)
        cls.index = cls.pc.Index(cls.pinecone_index)

        # Create and configure the JobMatcher to use the Pinecone index
        cls.matcher = JobMatcher()
        cls.matcher.index = cls.index
        
    def test_match_user_profile_with_jobs(self):
        """Test matching a user profile with jobs stored in the default namespace"""
        
        # Create a sample user profile based on actual structure
        user_profile_data = {
            "id": "test_user_123_d147f88fba006c714e27f17e96ea04bf",
            # Using a dummy embedding for testing
            "combined_embedding": [0.1] * 3072,
            "experience_year": "{\"total_experience_months\": 39.0, \"total_experience_years\": 3, \"experience_year\": \"Software Engineering Teacher Assistant: 7 months, Software Developer at Crest Data System: 16 months, Software Developer at Overclocked Brains: 16 months. Total Experience: 3 years\"}",
            "github_feedback": "The GitHub profile of Aumpatelarjun shows a good variety of projects in different languages and domains. The repositories have detailed README files, which is a strength. However, the profile lacks engagement with the community, as evidenced by the low follower count and lack of activity. To enhance the profile, consider adding project descriptions, engaging more with the community through discussions or contributions, and updating repository activity to showcase ongoing work.",
            "github_skills": ["JavaScript", "TypeScript", "TSQL", "C++", "HTML", "CSS", "Node.js", "Yarn", "React", "SQL"],
            "qualification": "- Master of Computer Software Engineering from Northeastern University, Boston, USA (Expected Dec 2025)\n- Bachelor of Computer Science from Maharaja Sayajirao University, Vadodara, India (July 2018 - May 2022)",
            "resume_s3": "s3://skillmatchai/resume/markdown/20250411_200621_AUM-JS-python-Doc.md",
            "resume_skills": ["JavaScript", "Java", "Python", "C++", "Typescript", "HTML", "CSS", "React.js", "Node.js"]
        }
        
        # Add all_skills by combining resume_skills and github_skills
        user_profile_data["all_skills"] = list(set(user_profile_data["resume_skills"] + user_profile_data["github_skills"]))
        
        # Override query_jobs method to use the default namespace only
        def namespace_query_jobs(embedding, top_k=5):
            response = self.index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True,
                namespace=self.jobs_namespace  # Specifically query the default namespace for jobs
            )
            return response.matches
        
        # Patch the query_jobs method temporarily for this test
        with patch.object(self.matcher, 'query_jobs', side_effect=namespace_query_jobs):
            # Call match_profile_with_jobs to get job matches
            top_k = 5
            results = self.matcher.match_profile_with_jobs(user_profile_data, top_k=top_k)
            
            # Print results for debugging
            print("\n=== Job Matching Results (Default Namespace) ===")
            print(f"Status: {results.get('status')}")
            print(f"Total Matches: {results.get('total_matches')}")
            print("Matches:")
            for job in results.get("matches", []):
                print(f"  Job ID: {job.get('job_id')}")
                print(f"  Job Title: {job.get('job_title')}")
                print(f"  Company: {job.get('company', 'N/A')}")
                print(f"  Similarity Score: {job.get('similarity_score'):.2f} ({job.get('similarity_category')})")
                print(f"  Matching Skills: {', '.join(job.get('matching_skills', []))}\n")
            
            # Basic assertions
            self.assertEqual(results.get("status"), "success")
            self.assertIsInstance(results.get("total_matches"), int)
            self.assertLessEqual(len(results.get("matches", [])), top_k)
            
            # Check that each match has expected keys if there are matches
            if results.get("matches"):
                first_match = results["matches"][0]
                expected_keys = ["job_id", "job_title", "similarity_score", "similarity_category", "matching_skills"]
                for key in expected_keys:
                    self.assertIn(key, first_match)

    def test_skills_matching_with_jobs(self):
        """Test matching skills with jobs from the default namespace"""
        
        # Sample skills from a user profile
        skills = ["JavaScript", "TypeScript", "Python", "React", "Node.js"]
        
        # Mock the job processor for getting embeddings
        self.matcher.job_processor = MagicMock()
        self.matcher.job_processor.get_embedding.return_value = [0.1] * 3072
        
        # Override query_jobs method to use the default namespace only
        def namespace_query_jobs(embedding, top_k=5):
            response = self.index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True,
                namespace=self.jobs_namespace  # Specifically query the default namespace for jobs
            )
            return response.matches
        
        # Patch the query_jobs method temporarily for this test
        with patch.object(self.matcher, 'query_jobs', side_effect=namespace_query_jobs):
            # Call match_skills_with_jobs to get job matches based on skills
            results = self.matcher.match_skills_with_jobs(skills, top_k=5)
            
            # Print results for debugging
            print("\n=== Skills Matching Results (Default Namespace) ===")
            print(f"Status: {results.get('status')}")
            print(f"Total Matches: {results.get('total_matches')}")
            print("Matches:")
            for job in results.get("matches", []):
                print(f"  Job ID: {job.get('job_id')}")
                print(f"  Job Title: {job.get('job_title')}")
                print(f"  Similarity Score: {job.get('similarity_score'):.2f}")
            
            # Assertions
            self.assertEqual(results.get("status"), "success")
            self.assertIsInstance(results.get("total_matches"), int)
            
            # Check that each match has expected keys if there are matches
            if results.get("matches"):
                first_match = results["matches"][0]
                expected_keys = ["job_id", "job_title", "similarity_score"]
                for key in expected_keys:
                    self.assertIn(key, first_match)

if __name__ == '__main__':
    unittest.main() 