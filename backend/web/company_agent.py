# # # import os
# # # import sys
# # # import logging
# # # from datetime import datetime
# # # from pathlib import Path
# # # import boto3
# # # from botocore.exceptions import ClientError
# # # import json
# # # import time
# # # import requests
# # # from pinecone import Pinecone
# # # from openai import OpenAI

# # # # Add the parent directory to the Python path
# # # sys.path.append(str(Path(__file__).parent.parent))

# # # # Configure logging
# # # logging.basicConfig(
# # #     level=logging.INFO,
# # #     format='%(asctime)s - %(levelname)s - %(message)s',
# # #     handlers=[
# # #         logging.StreamHandler()
# # #     ]
# # # )
# # # logger = logging.getLogger(__name__)

# # # # Initialize S3 client (reusing from your existing code)
# # # s3_client = boto3.client(
# # #     's3',
# # #     aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
# # #     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
# # #     region_name=os.getenv('AWS_REGION', 'us-east-1')
# # # )

# # # S3_BUCKET = 'skillmatchai'
# # # S3_BASE_PATH = 'jobs/raw_files/'

# # # # Initialize Pinecone client
# # # PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
# # # pc = Pinecone(api_key=PINECONE_API_KEY)
# # # PINECONE_INDEX_NAME = 'skillmatch'  # Using the same index name as in your existing code

# # # # Initialize OpenAI client for embeddings
# # # openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# # # # Initialize Tavily client
# # # TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
# # # TAVILY_API_BASE_URL = 'https://api.tavily.com/v1'

# # # def save_to_s3(data, filename):
# # #     """
# # #     Save data to S3 bucket (reused from your existing code)
# # #     """
# # #     try:
# # #         # Convert data to JSON string
# # #         json_data = json.dumps(data, ensure_ascii=False)
        
# # #         # Upload to S3
# # #         s3_key = f"{S3_BASE_PATH}{filename}"
# # #         s3_client.put_object(
# # #             Bucket=S3_BUCKET,
# # #             Key=s3_key,
# # #             Body=json_data,
# # #             ContentType='application/json'
# # #         )
        
# # #         logger.info(f"Successfully saved data to s3://{S3_BUCKET}/{s3_key}")
# # #         return f"s3://{S3_BUCKET}/{s3_key}"
# # #     except ClientError as e:
# # #         logger.error(f"Error saving to S3: {str(e)}")
# # #         raise
# # #     except Exception as e:
# # #         logger.error(f"Unexpected error saving to S3: {str(e)}")
# # #         raise

# # # def tavily_search(query, search_depth="advanced", max_results=5, include_domains=None, exclude_domains=None):
# # #     """
# # #     Perform a search using Tavily API
# # #     """
# # #     try:
# # #         headers = {
# # #             "Content-Type": "application/json",
# # #             "X-API-Key": TAVILY_API_KEY
# # #         }
        
# # #         payload = {
# # #             "query": query,
# # #             "search_depth": search_depth,
# # #             "max_results": max_results
# # #         }
        
# # #         if include_domains:
# # #             payload["include_domains"] = include_domains
# # #         if exclude_domains:
# # #             payload["exclude_domains"] = exclude_domains
            
# # #         response = requests.post(
# # #             f"{TAVILY_API_BASE_URL}/search",
# # #             headers=headers,
# # #             json=payload
# # #         )
        
# # #         if response.status_code == 200:
# # #             return response.json()
# # #         else:
# # #             logger.error(f"Tavily API error: {response.status_code} - {response.text}")
# # #             return None
            
# # #     except Exception as e:
# # #         logger.error(f"Error in Tavily search: {str(e)}")
# # #         return None

# # # def research_company(company_name):
# # #     """
# # #     Research company information using Tavily API
# # #     """
# # #     logger.info(f"Researching company: {company_name}")
    
# # #     # Create search queries for different aspects of the company
# # #     queries = [
# # #         f"{company_name} company overview background history",
# # #         f"{company_name} careers jobs website portal",
# # #         f"{company_name} working culture employee reviews",
# # #         f"{company_name} technology stack projects",
# # #         f"{company_name} achievements awards recognition"
# # #     ]
    
# # #     company_info = {
# # #         "name": company_name,
# # #         "overview": "",
# # #         "career_site": "",
# # #         "culture": "",
# # #         "technology": "",
# # #         "achievements": "",
# # #         "search_time": datetime.now().isoformat()
# # #     }
    
# # #     # Execute searches for each aspect
# # #     for i, query in enumerate(queries):
# # #         try:
# # #             # Use Tavily's search API
# # #             response = tavily_search(
# # #                 query=query,
# # #                 search_depth="advanced",
# # #                 max_results=3
# # #             )
            
# # #             # Extract the content from the response
# # #             if response and 'results' in response:
# # #                 content = " ".join([result.get('content', '') for result in response['results']])
                
# # #                 # Store the content in the appropriate field
# # #                 if i == 0:
# # #                     company_info["overview"] = content
# # #                 elif i == 1:
# # #                     company_info["career_site"] = content
# # #                     # Try to extract career site URL
# # #                     for result in response['results']:
# # #                         if 'careers' in result.get('url', '').lower() or 'jobs' in result.get('url', '').lower():
# # #                             company_info["career_site_url"] = result.get('url', '')
# # #                             break
# # #                 elif i == 2:
# # #                     company_info["culture"] = content
# # #                 elif i == 3:
# # #                     company_info["technology"] = content
# # #                 elif i == 4:
# # #                     company_info["achievements"] = content
            
# # #             # Add a small delay to avoid rate limiting
# # #             time.sleep(1)
            
# # #         except Exception as e:
# # #             logger.error(f"Error researching {query}: {str(e)}")
    
# # #     logger.info(f"Completed research for {company_name}")
# # #     return company_info

# # # def generate_embedding(text):
# # #     """
# # #     Generate an embedding for text using OpenAI's API
# # #     """
# # #     try:
# # #         response = openai_client.embeddings.create(
# # #             input=text,
# # #             model="text-embedding-ada-002"
# # #         )
        
# # #         # Extract embedding from response
# # #         embedding = response.data[0].embedding
# # #         return embedding
    
# # #     except Exception as e:
# # #         logger.error(f"Error generating embedding: {str(e)}")
# # #         # Return a random embedding as fallback
# # #         import random
# # #         return [random.uniform(-1, 1) for _ in range(1536)]

# # # def find_similar_jobs(job_title, company_name):
# # #     """
# # #     Find similar jobs using Tavily API
# # #     """
# # #     logger.info(f"Finding similar jobs to: {job_title} at {company_name}")
    
# # #     # Create a search query for similar jobs
# # #     query = f"job openings similar to {job_title} at {company_name} with links"
    
# # #     similar_jobs = []
    
# # #     try:
# # #         # Use Tavily's search API
# # #         response = tavily_search(
# # #             query=query,
# # #             search_depth="advanced",
# # #             max_results=5
# # #         )
        
# # #         # Extract job information from the response
# # #         if response and 'results' in response:
# # #             for result in response['results']:
# # #                 # Extract job details from the result
# # #                 title = ""
# # #                 company = ""
# # #                 url = result.get('url', '')
# # #                 content = result.get('content', '')
                
# # #                 # Try to parse job title and company from content
# # #                 lines = content.split('\n')
# # #                 for line in lines:
# # #                     if 'job title' in line.lower() or 'position' in line.lower():
# # #                         title = line.split(':')[-1].strip()
# # #                     if 'company' in line.lower() or 'organization' in line.lower():
# # #                         company = line.split(':')[-1].strip()
                
# # #                 # If we couldn't extract title or company, use the page title
# # #                 if not title:
# # #                     title = result.get('title', '').split('-')[0].strip()
# # #                 if not company:
# # #                     # Try to extract company from title
# # #                     title_parts = result.get('title', '').split('-')
# # #                     if len(title_parts) > 1:
# # #                         company = title_parts[1].strip()
                
# # #                 # Create a job object
# # #                 job = {
# # #                     "title": title,
# # #                     "company": company,
# # #                     "url": url,
# # #                     "description": content[:500],  # Truncate description
# # #                     "source": "tavily",
# # #                     "found_date": datetime.now().isoformat()
# # #                 }
                
# # #                 # Add a unique hash for deduplication
# # #                 job_hash = hash(f"{title}|{company}|{url}")
# # #                 job["hash_code"] = str(job_hash)
                
# # #                 similar_jobs.append(job)
        
# # #     except Exception as e:
# # #         logger.error(f"Error finding similar jobs: {str(e)}")
    
# # #     logger.info(f"Found {len(similar_jobs)} potential similar jobs")
# # #     return similar_jobs[:3]  # Return top 3 jobs

# # # def check_job_exists_in_pinecone(job_hash):
# # #     """
# # #     Check if a job already exists in Pinecone by its hash code
# # #     """
# # #     try:
# # #         # Connect to the Pinecone index
# # #         index = pc.Index(PINECONE_INDEX_NAME)
        
# # #         # Query for jobs with the same hash code
# # #         results = index.query(
# # #             vector=[0.1] * 1536,  # Dummy vector for metadata filtering
# # #             filter={"hash_code": {"$eq": job_hash}},
# # #             top_k=1,
# # #             include_metadata=True
# # #         )
        
# # #         # If we got any matches, the job exists
# # #         return len(results['matches']) > 0
    
# # #     except Exception as e:
# # #         logger.error(f"Error checking if job exists in Pinecone: {str(e)}")
# # #         return False

# # # def store_job_in_pinecone(job, embedding):
# # #     """
# # #     Store a job in Pinecone with its embedding
# # #     """
# # #     try:
# # #         # Connect to the Pinecone index
# # #         index = pc.Index(PINECONE_INDEX_NAME)
        
# # #         # Create a unique ID for the job
# # #         job_id = f"job_{int(time.time())}_{hash(job['title'])}"
        
# # #         # Prepare metadata
# # #         metadata = {
# # #             "title": job["title"],
# # #             "company": job["company"],
# # #             "url": job["url"],
# # #             "description": job["description"],
# # #             "source": job["source"],
# # #             "found_date": job["found_date"],
# # #             "hash_code": job["hash_code"]
# # #         }
        
# # #         # Upsert the job into Pinecone
# # #         index.upsert(
# # #             vectors=[
# # #                 {
# # #                     "id": job_id,
# # #                     "values": embedding,
# # #                     "metadata": metadata
# # #                 }
# # #             ]
# # #         )
        
# # #         logger.info(f"Stored job in Pinecone: {job['title']} at {job['company']}")
# # #         return True
    
# # #     except Exception as e:
# # #         logger.error(f"Error storing job in Pinecone: {str(e)}")
# # #         return False

# # # def research_and_recommend_jobs(company_name, job_title):
# # #     """
# # #     Research company information and recommend similar jobs
# # #     """
# # #     logger.info(f"Starting research and job recommendations for {job_title} at {company_name}")
    
# # #     # Step 1: Research company information
# # #     company_info = research_company(company_name)
    
# # #     # Step 2: Find similar jobs
# # #     similar_jobs_raw = find_similar_jobs(job_title, company_name)
    
# # #     # Step 3: Filter out existing jobs and store new ones
# # #     similar_jobs_filtered = []
# # #     for job in similar_jobs_raw:
# # #         # Check if job already exists
# # #         if not check_job_exists_in_pinecone(job["hash_code"]):
# # #             # Generate embedding for the job
# # #             job_text = f"{job['title']} {job['company']} {job['description']}"
# # #             embedding = generate_embedding(job_text)
            
# # #             # Store job in Pinecone
# # #             store_job_in_pinecone(job, embedding)
            
# # #             # Add job to filtered list
# # #             similar_jobs_filtered.append(job)
            
# # #             # If we have 3 jobs, we're done
# # #             if len(similar_jobs_filtered) >= 3:
# # #                 break
    
# # #     # Step 4: If we don't have enough jobs, find more
# # #     while len(similar_jobs_filtered) < 3:
# # #         # Modify the search query slightly to get different results
# # #         additional_jobs = find_similar_jobs(
# # #             job_title + " alternative", 
# # #             company_name + " competitor"
# # #         )
        
# # #         for job in additional_jobs:
# # #             if not check_job_exists_in_pinecone(job["hash_code"]):
# # #                 job_text = f"{job['title']} {job['company']} {job['description']}"
# # #                 embedding = generate_embedding(job_text)
# # #                 store_job_in_pinecone(job, embedding)
# # #                 similar_jobs_filtered.append(job)
                
# # #                 if len(similar_jobs_filtered) >= 3:
# # #                     break
        
# # #         # Prevent infinite loop if we can't find enough jobs
# # #         if len(similar_jobs_filtered) < 3 and len(additional_jobs) == 0:
# # #             break
    
# # #     # Step 5: Prepare the final result
# # #     result = {
# # #         "company_info": company_info,
# # #         "similar_jobs": similar_jobs_filtered,
# # #         "timestamp": datetime.now().isoformat()
# # #     }
    
# # #     # Step 6: Save the result to S3
# # #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# # #     filename = f"company_research_{company_name.replace(' ', '_')}_{timestamp}.json"
# # #     save_to_s3(result, filename)
    
# # #     logger.info(f"Completed research and job recommendations for {job_title} at {company_name}")
# # #     return result

# # # if __name__ == "__main__":
# # #     # Example usage
# # #     if len(sys.argv) > 2:
# # #         company_name = sys.argv[1]
# # #         job_title = sys.argv[2]
# # #     else:
# # #         company_name = "Google"
# # #         job_title = "Software Engineer"
    
# # #     result = research_and_recommend_jobs(company_name, job_title)
    
# # #     # Display the results
# # #     print("\n=== COMPANY INFORMATION ===")
# # #     print(f"Company: {result['company_info']['name']}")
# # #     print(f"Overview: {result['company_info']['overview'][:300]}...")
    
# # #     if 'career_site_url' in result['company_info']:
# # #         print(f"Career Site: {result['company_info']['career_site_url']}")
# # #     else:
# # #         print(f"Career Site: Not found")
        
# # #     print(f"Culture: {result['company_info']['culture'][:300]}...")
# # #     print(f"Technology: {result['company_info']['technology'][:300]}...")
# # #     print(f"Achievements: {result['company_info']['achievements'][:300]}...")
    
# # #     print("\n=== SIMILAR JOB RECOMMENDATIONS ===")
# # #     for i, job in enumerate(result['similar_jobs'], 1):
# # #         print(f"\nJob {i}:")
# # #         print(f"Title: {job['title']}")
# # #         print(f"Company: {job['company']}")
# # #         print(f"URL: {job['url']}")
# # #         print(f"Description: {job['description'][:150]}...")


# # from dotenv import load_dotenv
# # import os
# # import sys
# # import logging
# # from datetime import datetime
# # from pathlib import Path
# # import boto3
# # from botocore.exceptions import ClientError
# # import json
# # import time
# # import hashlib
# # import requests
# # from pinecone import Pinecone
# # from openai import OpenAI
# # from tavily import TavilyClient

# # # Load environment variables from .env file
# # load_dotenv()




# # # Get Tavily API key
# # TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
# # if not TAVILY_API_KEY:
# #     raise ValueError("TAVILY_API_KEY not found in environment variables")
# # # Add the parent directory to the Python path
# # sys.path.append(str(Path(__file__).parent.parent))

# # # Configure logging
# # logging.basicConfig(
# #     level=logging.INFO,
# #     format='%(asctime)s - %(levelname)s - %(message)s',
# #     handlers=[
# #         logging.StreamHandler()
# #     ]
# # )
# # logger = logging.getLogger(__name__)

# # # Initialize S3 client (reusing from your existing code)
# # s3_client = boto3.client(
# #     's3',
# #     aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
# #     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
# #     region_name=os.getenv('AWS_REGION', 'us-east-1')
# # )

# # S3_BUCKET = 'skillmatchai'
# # S3_BASE_PATH = 'jobs/raw_files/'

# # # Initialize Pinecone client
# # PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
# # pc = Pinecone(api_key=PINECONE_API_KEY)
# # PINECONE_INDEX_NAME = 'skillmatch'  # Using the same index name as in your existing code

# # # Initialize OpenAI client for embeddings
# # openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# # # # Initialize Tavily client
# # # TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
# # TAVILY_API_BASE_URL = 'https://api.tavily.com/v1'

# # def save_to_s3(data, filename):
# #     """
# #     Save data to S3 bucket (reused from your existing code)
# #     """
# #     try:
# #         # Convert data to JSON string
# #         json_data = json.dumps(data, ensure_ascii=False)
        
# #         # Upload to S3
# #         s3_key = f"{S3_BASE_PATH}{filename}"
# #         s3_client.put_object(
# #             Bucket=S3_BUCKET,
# #             Key=s3_key,
# #             Body=json_data,
# #             ContentType='application/json'
# #         )
        
# #         logger.info(f"Successfully saved data to s3://{S3_BUCKET}/{s3_key}")
# #         return f"s3://{S3_BUCKET}/{s3_key}"
# #     except ClientError as e:
# #         logger.error(f"Error saving to S3: {str(e)}")
# #         raise
# #     except Exception as e:
# #         logger.error(f"Unexpected error saving to S3: {str(e)}")
# #         raise

# # def tavily_search(query, search_depth="advanced", max_results=5, include_domains=None, exclude_domains=None):
# #     """
# #     Perform a search using Tavily API
# #     """
# #     try:
# #         headers = {
# #             "Content-Type": "application/json",
# #             "X-API-Key": TAVILY_API_KEY
# #         }
        
# #         payload = {
# #             "query": query,
# #             "search_depth": search_depth,
# #             "max_results": max_results
# #         }
        
# #         if include_domains:
# #             payload["include_domains"] = include_domains
# #         if exclude_domains:
# #             payload["exclude_domains"] = exclude_domains
            
# #         response = requests.post(
# #             f"{TAVILY_API_BASE_URL}/search",
# #             headers=headers,
# #             json=payload
# #         )
        
# #         if response.status_code == 200:
# #             return response.json()
# #         else:
# #             logger.error(f"Tavily API error: {response.status_code} - {response.text}")
# #             return None
            
# #     except Exception as e:
# #         logger.error(f"Error in Tavily search: {str(e)}")
# #         return None

# # def research_company(company_name):
# #     """
# #     Research company information using Tavily API
# #     """
# #     logger.info(f"Researching company: {company_name}")
    
# #     # Create search queries for different aspects of the company
# #     queries = [
# #         f"{company_name} company overview background history",
# #         f"{company_name} careers jobs website portal",
# #         f"{company_name} working culture employee reviews",
# #         f"{company_name} technology stack projects",
# #         f"{company_name} achievements awards recognition"
# #     ]
    
# #     company_info = {
# #         "name": company_name,
# #         "overview": "",
# #         "career_site": "",
# #         "culture": "",
# #         "technology": "",
# #         "achievements": "",
# #         "search_time": datetime.now().isoformat()
# #     }
    
# #     # Execute searches for each aspect
# #     for i, query in enumerate(queries):
# #         try:
# #             # Use Tavily's search API
# #             response = tavily_search(
# #                 query=query,
# #                 search_depth="advanced",
# #                 max_results=3
# #             )
            
# #             # Extract the content from the response
# #             if response and 'results' in response:
# #                 content = " ".join([result.get('content', '') for result in response['results']])
                
# #                 # Store the content in the appropriate field
# #                 if i == 0:
# #                     company_info["overview"] = content
# #                 elif i == 1:
# #                     company_info["career_site"] = content
# #                     # Try to extract career site URL
# #                     for result in response['results']:
# #                         if 'careers' in result.get('url', '').lower() or 'jobs' in result.get('url', '').lower():
# #                             company_info["career_site_url"] = result.get('url', '')
# #                             break
# #                 elif i == 2:
# #                     company_info["culture"] = content
# #                 elif i == 3:
# #                     company_info["technology"] = content
# #                 elif i == 4:
# #                     company_info["achievements"] = content
            
# #             # Add a small delay to avoid rate limiting
# #             time.sleep(1)
            
# #         except Exception as e:
# #             logger.error(f"Error researching {query}: {str(e)}")
    
# #     logger.info(f"Completed research for {company_name}")
# #     return company_info

# # def generate_embedding(text):
# #     """
# #     Generate an embedding for text using OpenAI's API
# #     """
# #     try:
# #         response = openai_client.embeddings.create(
# #             input=text,
# #             model="text-embedding-ada-002"
# #         )
        
# #         # Extract embedding from response
# #         embedding = response.data[0].embedding
# #         return embedding
    
# #     except Exception as e:
# #         logger.error(f"Error generating embedding: {str(e)}")
# #         # Return a random embedding as fallback
# #         import random
# #         return [random.uniform(-1, 1) for _ in range(1536)]

# # def find_jobs_with_tavily(job_title, company_name=None, location=None):
# #     """
# #     Find jobs using Tavily API
# #     """
# #     logger.info(f"Finding jobs: {job_title} at {company_name if company_name else 'any company'}")
    
# #     # Create a search query for jobs
# #     query = f"{job_title} job openings"
# #     if company_name:
# #         query += f" at {company_name}"
# #     if location:
# #         query += f" in {location}"
    
# #     jobs_found = []
    
# #     try:
# #         # Use Tavily's search API
# #         response = tavily_search(
# #             query=query,
# #             search_depth="advanced",
# #             max_results=10
# #         )
        
# #         # Extract job information from the response
# #         if response and 'results' in response:
# #             for result in response['results']:
# #                 # Extract job details from the result
# #                 title = ""
# #                 company = company_name if company_name else ""
# #                 job_location = location if location else ""
# #                 url = result.get('url', '')
# #                 content = result.get('content', '')
                
# #                 # Try to parse job details from content
# #                 lines = content.split('\n')
# #                 for line in lines:
# #                     if not title and ('job title' in line.lower() or 'position' in line.lower() or 'role:' in line.lower()):
# #                         title = line.split(':')[-1].strip()
# #                     if not company and ('company' in line.lower() or 'organization' in line.lower()):
# #                         company = line.split(':')[-1].strip()
# #                     if not job_location and ('location' in line.lower() or 'city' in line.lower()):
# #                         job_location = line.split(':')[-1].strip()
                
# #                 # If we couldn't extract title, use the page title
# #                 if not title:
# #                     title = result.get('title', '').split('-')[0].strip()
# #                     # Try to extract company from title if not already set
# #                     if not company:
# #                         title_parts = result.get('title', '').split('-')
# #                         if len(title_parts) > 1:
# #                             company = title_parts[1].strip()
                
# #                 # Extract responsibilities and qualifications
# #                 responsibilities = ""
# #                 qualifications = ""
# #                 skills = []
                
# #                 # Look for responsibilities section
# #                 resp_start = content.lower().find('responsibilities')
# #                 qual_start = content.lower().find('qualifications')
# #                 req_start = content.lower().find('requirements')
# #                 skills_start = content.lower().find('skills')
                
# #                 if resp_start != -1:
# #                     end_idx = min(x for x in [qual_start, req_start, skills_start, len(content)] if x > resp_start)
# #                     responsibilities = content[resp_start:end_idx].strip()
                
# #                 # Look for qualifications section
# #                 if qual_start != -1:
# #                     end_idx = min(x for x in [resp_start, req_start, skills_start, len(content)] if x > qual_start and x != qual_start)
# #                     qualifications = content[qual_start:end_idx].strip()
# #                 elif req_start != -1:
# #                     end_idx = min(x for x in [resp_start, qual_start, skills_start, len(content)] if x > req_start and x != req_start)
# #                     qualifications = content[req_start:end_idx].strip()
                
# #                 # Extract skills
# #                 if skills_start != -1:
# #                     skills_text = content[skills_start:].strip()
# #                     skills_lines = skills_text.split('\n')
# #                     for i in range(1, min(10, len(skills_lines))):
# #                         skill = skills_lines[i].strip()
# #                         if skill and len(skill) < 50:  # Reasonable skill length
# #                             skills.append(skill)
                
# #                 # If no skills found, try to extract from qualifications
# #                 if not skills and qualifications:
# #                     qual_lines = qualifications.split('\n')
# #                     for line in qual_lines:
# #                         if 'experience with' in line.lower() or 'knowledge of' in line.lower() or 'proficiency in' in line.lower():
# #                             potential_skill = line.split('with')[-1].split('of')[-1].split('in')[-1].strip()
# #                             if potential_skill and len(potential_skill) < 50:
# #                                 skills.append(potential_skill)
                
# #                 # Determine job type, work mode, and seniority
# #                 job_type = "Full-time"  # Default
# #                 work_mode = "Hybrid"    # Default
# #                 seniority = "Mid Level" # Default
                
# #                 if 'part-time' in content.lower() or 'part time' in content.lower():
# #                     job_type = "Part-time"
# #                 if 'contract' in content.lower() or 'contractor' in content.lower():
# #                     job_type = "Contract"
# #                 if 'internship' in content.lower():
# #                     job_type = "Internship"
                
# #                 if 'remote' in content.lower():
# #                     work_mode = "Remote"
# #                 if 'on-site' in content.lower() or 'onsite' in content.lower() or 'in office' in content.lower():
# #                     work_mode = "On-site"
                
# #                 if 'senior' in content.lower() or 'sr.' in content.lower():
# #                     seniority = "Senior Level"
# #                 if 'junior' in content.lower() or 'jr.' in content.lower():
# #                     seniority = "Entry Level"
# #                 if 'principal' in content.lower() or 'lead' in content.lower() or 'director' in content.lower():
# #                     seniority = "Principal"
                
# #                 # Create a job object
# #                 job = {
# #                     "job_title": title,
# #                     "company": company,
# #                     "location": job_location,
# #                     "job_type": job_type,
# #                     "work_mode": work_mode,
# #                     "seniority": seniority,
# #                     "salary": "",  # Typically not available from search results
# #                     "experience": "",  # Typically not available from search results
# #                     "responsibilities": responsibilities,
# #                     "qualifications": qualifications,
# #                     "skills": skills,
# #                     "source": "tavily",
# #                     "timestamp": int(time.time())
# #                 }
                
# #                 # Generate a unique ID for the job
# #                 job_id = f"job_{title.lower().replace(' ', '_')}_{int(time.time())}"
                
# #                 jobs_found.append((job_id, job))
        
# #     except Exception as e:
# #         logger.error(f"Error finding jobs: {str(e)}")
    
# #     logger.info(f"Found {len(jobs_found)} potential jobs")
# #     return jobs_found

# # def check_job_exists_in_pinecone(job_title, company):
# #     """
# #     Check if a job already exists in Pinecone by its title and company
# #     """
# #     try:
# #         # Connect to the Pinecone index
# #         index = pc.Index(PINECONE_INDEX_NAME)
        
# #         # Create a normalized version of job title and company for comparison
# #         normalized_title = job_title.lower().strip()
# #         normalized_company = company.lower().strip()
        
# #         # Query for jobs with similar title and company
# #         results = index.query(
# #             vector=[0.1] * 1536,  # Dummy vector for metadata filtering
# #             filter={
# #                 "$and": [
# #                     {"job_title": {"$eq": normalized_title}},
# #                     {"company": {"$eq": normalized_company}}
# #                 ]
# #             },
# #             top_k=1,
# #             include_metadata=True
# #         )
        
# #         # If we got any matches, the job exists
# #         return len(results['matches']) > 0
    
# #     except Exception as e:
# #         logger.error(f"Error checking if job exists in Pinecone: {str(e)}")
# #         return False

# # def store_job_in_pinecone(job_id, job_data, embedding):
# #     """
# #     Store a job in Pinecone with its embedding
# #     """
# #     try:
# #         # Connect to the Pinecone index
# #         index = pc.Index(PINECONE_INDEX_NAME)
        
# #         # Prepare metadata - ensure it matches the expected structure
# #         metadata = {
# #             "company": job_data["company"],
# #             "experience": job_data["experience"],
# #             "job_title": job_data["job_title"],
# #             "job_type": job_data["job_type"],
# #             "location": job_data["location"],
# #             "qualifications": job_data["qualifications"],
# #             "responsibilities": job_data["responsibilities"],
# #             "salary": job_data["salary"],
# #             "seniority": job_data["seniority"],
# #             "skills": job_data["skills"],
# #             "source": job_data["source"],
# #             "timestamp": job_data["timestamp"],
# #             "work_mode": job_data["work_mode"]
# #         }
        
# #         # Upsert the job into Pinecone
# #         index.upsert(
# #             vectors=[
# #                 {
# #                     "id": job_id,
# #                     "values": embedding,
# #                     "metadata": metadata
# #                 }
# #             ]
# #         )
        
# #         logger.info(f"Stored job in Pinecone: {job_data['job_title']} at {job_data['company']}")
# #         return True
    
# #     except Exception as e:
# #         logger.error(f"Error storing job in Pinecone: {str(e)}")
# #         return False

# # def find_and_store_jobs(job_title, company_name=None, location=None):
# #     """
# #     Find jobs using Tavily API and store them in Pinecone
# #     """
# #     logger.info(f"Starting job search for {job_title}")
    
# #     # Step 1: Find jobs using Tavily
# #     jobs_found = find_jobs_with_tavily(job_title, company_name, location)
    
# #     # Step 2: Filter out existing jobs and store new ones
# #     jobs_stored = []
# #     for job_id, job_data in jobs_found:
# #         # Check if job already exists
# #         if not check_job_exists_in_pinecone(job_data["job_title"], job_data["company"]):
# #             # Generate embedding for the job
# #             job_text = f"{job_data['job_title']} {job_data['company']} {job_data['responsibilities']} {job_data['qualifications']}"
# #             embedding = generate_embedding(job_text)
            
# #             # Store job in Pinecone
# #             if store_job_in_pinecone(job_id, job_data, embedding):
# #                 jobs_stored.append(job_data)
    
# #     # Step 3: Save the results to S3
# #     if jobs_stored:
# #         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# #         filename = f"tavily_jobs_{job_title.replace(' ', '_')}_{timestamp}.json"
# #         save_to_s3(jobs_stored, filename)
    
# #     logger.info(f"Stored {len(jobs_stored)} new jobs in Pinecone")
# #     return jobs_stored

# # def research_company_and_find_jobs(company_name, job_title=None):
# #     """
# #     Research company information and find related jobs
# #     """
# #     logger.info(f"Starting research for {company_name}")
    
# #     # Step 1: Research company information
# #     company_info = research_company(company_name)
    
# #     # Step 2: Find jobs at this company
# #     jobs = []
# #     if job_title:
# #         jobs = find_and_store_jobs(job_title, company_name)
# #     else:
# #         # If no specific job title, find various roles at the company
# #         common_roles = ["Software Engineer", "Data Scientist", "Product Manager", "Marketing Manager", "Sales Representative"]
# #         for role in common_roles:
# #             role_jobs = find_and_store_jobs(role, company_name)
# #             jobs.extend(role_jobs)
# #             if len(jobs) >= 3:
# #                 break
    
# #     # Step 3: Prepare the final result
# #     result = {
# #         "company_info": company_info,
# #         "jobs": jobs[:3],  # Return top 3 jobs
# #         "timestamp": datetime.now().isoformat()
# #     }
    
# #     # Step 4: Save the result to S3
# #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# #     filename = f"company_research_{company_name.replace(' ', '_')}_{timestamp}.json"
# #     save_to_s3(result, filename)
    
# #     logger.info(f"Completed research and job search for {company_name}")
# #     return result

# # if __name__ == "__main__":
# #     # Example usage
# #     if len(sys.argv) > 1:
# #         company_name = sys.argv[1]
# #         job_title = sys.argv[2] if len(sys.argv) > 2 else None
        
# #         result = research_company_and_find_jobs(company_name, job_title)
        
# #         # Display the results
# #         print("\n=== COMPANY INFORMATION ===")
# #         print(f"Company: {result['company_info']['name']}")
# #         print(f"Overview: {result['company_info']['overview'][:300]}...")
        
# #         if 'career_site_url' in result['company_info']:
# #             print(f"Career Site: {result['company_info']['career_site_url']}")
# #         else:
# #             print(f"Career Site: Not found")
            
# #         print(f"Culture: {result['company_info']['culture'][:300]}...")
# #         print(f"Technology: {result['company_info']['technology'][:300]}...")
# #         print(f"Achievements: {result['company_info']['achievements'][:300]}...")
        
# #         print("\n=== RELATED JOBS ===")
# #         for i, job in enumerate(result['jobs'], 1):
# #             print(f"\nJob {i}:")
# #             print(f"Title: {job['job_title']}")
# #             print(f"Company: {job['company']}")
# #             print(f"Location: {job['location']}")
# #             print(f"Job Type: {job['job_type']}")
# #             print(f"Work Mode: {job['work_mode']}")
# #             print(f"Seniority: {job['seniority']}")
# #             print(f"Skills: {', '.join(job['skills'][:5])}")
# #     else:
# #         print("Usage: python tavily_job_search.py <company_name> [job_title]")











# import os
# import sys
# import logging
# from datetime import datetime
# from pathlib import Path
# import json
# import time
# import hashlib
# import requests
# from dotenv import load_dotenv
# from tavily import TavilyClient
# from pinecone import Pinecone
# from openai import OpenAI

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger(__name__)

# # Load environment variables from .env file
# load_dotenv()

# # Initialize API clients
# try:
#     # Retrieve API keys from environment variables
#     tavily_api_key = os.getenv('TAVILY_API_KEY')
#     openai_api_key = os.getenv('OPENAI_API_KEY')
#     pinecone_api_key = os.getenv('PINECONE_API_KEY')
    
#     # Log API key status (safely)
#     logger.info(f"Tavily API key present: {bool(tavily_api_key)}")
#     logger.info(f"OpenAI API key present: {bool(openai_api_key)}")
#     logger.info(f"Pinecone API key present: {bool(pinecone_api_key)}")
    
#     # Provide more informative error message if API keys are missing
#     missing_keys = []
#     if not tavily_api_key:
#         missing_keys.append("TAVILY_API_KEY")
#     if not openai_api_key:
#         missing_keys.append("OPENAI_API_KEY")
#     if not pinecone_api_key:
#         missing_keys.append("PINECONE_API_KEY")
#     if missing_keys:
#         error_msg = f"Missing environment variables: {', '.join(missing_keys)}. Please check your .env file or set these environment variables."
#         logger.error(error_msg)
#         raise ValueError(error_msg)
    
#     # Initialize Tavily client
#     logger.info("Initializing Tavily client...")
#     tavily_client = TavilyClient(api_key=tavily_api_key)
#     logger.info("Tavily client initialized successfully")
    
#     # Initialize OpenAI client
#     logger.info("Initializing OpenAI client...")
#     openai_client = OpenAI(api_key=openai_api_key)
#     logger.info("OpenAI client initialized successfully")
    
#     # Initialize Pinecone client
#     logger.info("Initializing Pinecone client...")
#     pc = Pinecone(api_key=pinecone_api_key)
#     PINECONE_INDEX_NAME = 'skillmatch'
#     logger.info(f"Pinecone client initialized with index: {PINECONE_INDEX_NAME}")
    
# except Exception as e:
#     logger.error(f"Error initializing clients: {str(e)}")
#     raise

# # Initialize S3 client
# try:
#     import boto3
#     from botocore.exceptions import ClientError
    
#     s3_client = boto3.client(
#         's3',
#         aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#         aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
#         region_name=os.getenv('AWS_REGION', 'us-east-1')
#     )
    
#     S3_BUCKET = 'skillmatchai'
#     S3_BASE_PATH = 'jobs/raw_files/'
#     logger.info(f"S3 client initialized with bucket: {S3_BUCKET}")
    
# except Exception as e:
#     logger.error(f"Error initializing S3 client: {str(e)}")
#     s3_client = None

# def save_to_s3(data, filename):
#     """
#     Save data to S3 bucket
#     """
#     if not s3_client:
#         logger.warning("S3 client not initialized, skipping S3 save")
#         return None
        
#     try:
#         # Convert data to JSON string
#         json_data = json.dumps(data, ensure_ascii=False)
        
#         # Upload to S3
#         s3_key = f"{S3_BASE_PATH}{filename}"
#         s3_client.put_object(
#             Bucket=S3_BUCKET,
#             Key=s3_key,
#             Body=json_data,
#             ContentType='application/json'
#         )
        
#         logger.info(f"Successfully saved data to s3://{S3_BUCKET}/{s3_key}")
#         return f"s3://{S3_BUCKET}/{s3_key}"
#     except Exception as e:
#         logger.error(f"Error saving to S3: {str(e)}")
#         return None

# def generate_embedding(text):
#     """
#     Generate an embedding for text using OpenAI's API
#     """
#     try:
#         response = openai_client.embeddings.create(
#             input=text,
#             model="text-embedding-ada-002"
#         )
        
#         # Extract embedding from response
#         embedding = response.data[0].embedding
#         return embedding
    
#     except Exception as e:
#         logger.error(f"Error generating embedding: {str(e)}")
#         # Return a random embedding as fallback
#         import random
#         return [random.uniform(-1, 1) for _ in range(1536)]

# def research_company(company_name):
#     """
#     Research company information using Tavily API
#     """
#     logger.info(f"Researching company: {company_name}")
    
#     # Create search queries for different aspects of the company
#     queries = [
#         f"{company_name} company overview background history",
#         f"{company_name} careers jobs website portal",
#         f"{company_name} working culture employee reviews",
#         f"{company_name} technology stack projects",
#         f"{company_name} achievements awards recognition"
#     ]
    
#     company_info = {
#         "name": company_name,
#         "overview": "",
#         "career_site": "",
#         "culture": "",
#         "technology": "",
#         "achievements": "",
#         "search_time": datetime.now().isoformat()
#     }
    
#     # Execute searches for each aspect
#     for i, query in enumerate(queries):
#         try:
#             # Use Tavily's search API
#             search_results = tavily_client.search(
#                 query=query,
#                 search_depth="advanced",
#                 max_results=3
#             )
            
#             # Extract the content from the response
#             if search_results and 'results' in search_results:
#                 content = " ".join([result.get('content', '') for result in search_results['results']])
                
#                 # Store the content in the appropriate field
#                 if i == 0:
#                     company_info["overview"] = content
#                 elif i == 1:
#                     company_info["career_site"] = content
#                     # Try to extract career site URL
#                     for result in search_results['results']:
#                         if 'careers' in result.get('url', '').lower() or 'jobs' in result.get('url', '').lower():
#                             company_info["career_site_url"] = result.get('url', '')
#                             break
#                 elif i == 2:
#                     company_info["culture"] = content
#                 elif i == 3:
#                     company_info["technology"] = content
#                 elif i == 4:
#                     company_info["achievements"] = content
            
#             # Add a small delay to avoid rate limiting
#             time.sleep(1)
            
#         except Exception as e:
#             logger.error(f"Error researching {query}: {str(e)}")
    
#     logger.info(f"Completed research for {company_name}")
#     return company_info

# def find_jobs_with_tavily(job_title, company_name=None, location=None):
#     """
#     Find jobs using Tavily API
#     """
#     logger.info(f"Finding jobs: {job_title} at {company_name if company_name else 'any company'}")
    
#     # Create a search query for jobs
#     query = f"{job_title} job openings"
#     if company_name:
#         query += f" at {company_name}"
#     if location:
#         query += f" in {location}"
    
#     jobs_found = []
    
#     try:
#         # Use Tavily's search API
#         search_results = tavily_client.search(
#             query=query,
#             search_depth="advanced",
#             max_results=10
#         )
        
#         # Extract job information from the response
#         if search_results and 'results' in search_results:
#             for result in search_results['results']:
#                 # Extract job details from the result
#                 title = ""
#                 company = company_name if company_name else ""
#                 job_location = location if location else ""
#                 url = result.get('url', '')
#                 content = result.get('content', '')
                
#                 # Try to parse job details from content
#                 lines = content.split('\n')
#                 for line in lines:
#                     if not title and ('job title' in line.lower() or 'position' in line.lower() or 'role:' in line.lower()):
#                         title = line.split(':')[-1].strip()
#                     if not company and ('company' in line.lower() or 'organization' in line.lower()):
#                         company = line.split(':')[-1].strip()
#                     if not job_location and ('location' in line.lower() or 'city' in line.lower()):
#                         job_location = line.split(':')[-1].strip()
                
#                 # If we couldn't extract title, use the page title
#                 if not title:
#                     title = result.get('title', '').split('-')[0].strip()
#                     # Try to extract company from title if not already set
#                     if not company:
#                         title_parts = result.get('title', '').split('-')
#                         if len(title_parts) > 1:
#                             company = title_parts[1].strip()
                
#                 # Extract responsibilities and qualifications
#                 responsibilities = ""
#                 qualifications = ""
#                 skills = []
                
#                 # Look for responsibilities section
#                 resp_start = content.lower().find('responsibilities')
#                 qual_start = content.lower().find('qualifications')
#                 req_start = content.lower().find('requirements')
#                 skills_start = content.lower().find('skills')
                
#                 if resp_start != -1:
#                     end_idx = min(x for x in [qual_start, req_start, skills_start, len(content)] if x > resp_start)
#                     responsibilities = content[resp_start:end_idx].strip()
                
#                 # Look for qualifications section
#                 if qual_start != -1:
#                     end_idx = min(x for x in [resp_start, req_start, skills_start, len(content)] if x > qual_start and x != qual_start)
#                     qualifications = content[qual_start:end_idx].strip()
#                 elif req_start != -1:
#                     end_idx = min(x for x in [resp_start, qual_start, skills_start, len(content)] if x > req_start and x != req_start)
#                     qualifications = content[req_start:end_idx].strip()
                
#                 # Extract skills
#                 if skills_start != -1:
#                     skills_text = content[skills_start:].strip()
#                     skills_lines = skills_text.split('\n')
#                     for i in range(1, min(10, len(skills_lines))):
#                         skill = skills_lines[i].strip()
#                         if skill and len(skill) < 50:  # Reasonable skill length
#                             skills.append(skill)
                
#                 # If no skills found, try to extract from qualifications
#                 if not skills and qualifications:
#                     qual_lines = qualifications.split('\n')
#                     for line in qual_lines:
#                         if 'experience with' in line.lower() or 'knowledge of' in line.lower() or 'proficiency in' in line.lower():
#                             potential_skill = line.split('with')[-1].split('of')[-1].split('in')[-1].strip()
#                             if potential_skill and len(potential_skill) < 50:
#                                 skills.append(potential_skill)
                
#                 # Determine job type, work mode, and seniority
#                 job_type = "Full-time"  # Default
#                 work_mode = "Hybrid"    # Default
#                 seniority = "Mid Level" # Default
                
#                 if 'part-time' in content.lower() or 'part time' in content.lower():
#                     job_type = "Part-time"
#                 if 'contract' in content.lower() or 'contractor' in content.lower():
#                     job_type = "Contract"
#                 if 'internship' in content.lower():
#                     job_type = "Internship"
                
#                 if 'remote' in content.lower():
#                     work_mode = "Remote"
#                 if 'on-site' in content.lower() or 'onsite' in content.lower() or 'in office' in content.lower():
#                     work_mode = "On-site"
                
#                 if 'senior' in content.lower() or 'sr.' in content.lower():
#                     seniority = "Senior Level"
#                 if 'junior' in content.lower() or 'jr.' in content.lower():
#                     seniority = "Entry Level"
#                 if 'principal' in content.lower() or 'lead' in content.lower() or 'director' in content.lower():
#                     seniority = "Principal"
                
#                 # Create a job object that matches the expected structure
#                 job = {
#                     "job_title": title,
#                     "company": company,
#                     "location": job_location,
#                     "job_type": job_type,
#                     "work_mode": work_mode,
#                     "seniority": seniority,
#                     "salary": "",  # Typically not available from search results
#                     "experience": "",  # Typically not available from search results
#                     "responsibilities": responsibilities,
#                     "qualifications": qualifications,
#                     "skills": skills,
#                     "source": "tavily",
#                     "timestamp": int(time.time())
#                 }
                
#                 # Generate a unique ID for the job
#                 job_id = f"job_{title.lower().replace(' ', '_')}_{int(time.time())}"
                
#                 jobs_found.append((job_id, job))
        
#     except Exception as e:
#         logger.error(f"Error finding jobs: {str(e)}")
    
#     logger.info(f"Found {len(jobs_found)} potential jobs")
#     return jobs_found

# def check_job_exists_in_pinecone(job_title, company):
#     """
#     Check if a job already exists in Pinecone by its title and company
#     """
#     try:
#         # Connect to the Pinecone index
#         index = pc.Index(PINECONE_INDEX_NAME)
        
#         # Create a normalized version of job title and company for comparison
#         normalized_title = job_title.lower().strip()
#         normalized_company = company.lower().strip()
        
#         # Query for jobs with similar title and company
#         results = index.query(
#             vector=[0.1] * 1536,  # Dummy vector for metadata filtering
#             filter={
#                 "$and": [
#                     {"job_title": {"$eq": normalized_title}},
#                     {"company": {"$eq": normalized_company}}
#                 ]
#             },
#             top_k=1,
#             include_metadata=True
#         )
        
#         # If we got any matches, the job exists
#         return len(results['matches']) > 0
    
#     except Exception as e:
#         logger.error(f"Error checking if job exists in Pinecone: {str(e)}")
#         return False

# def store_job_in_pinecone(job_id, job_data, embedding):
#     """
#     Store a job in Pinecone with its embedding
#     """
#     try:
#         # Connect to the Pinecone index
#         index = pc.Index(PINECONE_INDEX_NAME)
        
#         # Prepare metadata - ensure it matches the expected structure
#         metadata = {
#             "company": job_data["company"],
#             "experience": job_data["experience"],
#             "job_title": job_data["job_title"],
#             "job_type": job_data["job_type"],
#             "location": job_data["location"],
#             "qualifications": job_data["qualifications"],
#             "responsibilities": job_data["responsibilities"],
#             "salary": job_data["salary"],
#             "seniority": job_data["seniority"],
#             "skills": job_data["skills"],
#             "source": job_data["source"],
#             "timestamp": job_data["timestamp"],
#             "work_mode": job_data["work_mode"]
#         }
        
#         # Upsert the job into Pinecone
#         index.upsert(
#             vectors=[
#                 {
#                     "id": job_id,
#                     "values": embedding,
#                     "metadata": metadata
#                 }
#             ]
#         )
        
#         logger.info(f"Stored job in Pinecone: {job_data['job_title']} at {job_data['company']}")
#         return True
    
#     except Exception as e:
#         logger.error(f"Error storing job in Pinecone: {str(e)}")
#         return False

# def find_and_store_jobs(job_title, company_name=None, location=None):
#     """
#     Find jobs using Tavily API and store them in Pinecone
#     """
#     logger.info(f"Starting job search for {job_title}")
    
#     # Step 1: Find jobs using Tavily
#     jobs_found = find_jobs_with_tavily(job_title, company_name, location)
    
#     # Step 2: Filter out existing jobs and store new ones
#     jobs_stored = []
#     for job_id, job_data in jobs_found:
#         # Check if job already exists
#         if not check_job_exists_in_pinecone(job_data["job_title"], job_data["company"]):
#             # Generate embedding for the job
#             job_text = f"{job_data['job_title']} {job_data['company']} {job_data['responsibilities']} {job_data['qualifications']}"
#             embedding = generate_embedding(job_text)
            
#             # Store job in Pinecone
#             if store_job_in_pinecone(job_id, job_data, embedding):
#                 jobs_stored.append(job_data)
    
#     # Step 3: Save the results to S3
#     if jobs_stored:
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"tavily_jobs_{job_title.replace(' ', '_')}_{timestamp}.json"
#         save_to_s3(jobs_stored, filename)
    
#     logger.info(f"Stored {len(jobs_stored)} new jobs in Pinecone")
#     return jobs_stored

# def research_company_and_find_jobs(company_name, job_title=None):
#     """
#     Research company information and find related jobs
#     """
#     logger.info(f"Starting research for {company_name}")
    
#     # Step 1: Research company information
#     company_info = research_company(company_name)
    
#     # Step 2: Find jobs at this company
#     jobs = []
#     if job_title:
#         jobs = find_and_store_jobs(job_title, company_name)
#     else:
#         # If no specific job title, find various roles at the company
#         common_roles = ["Software Engineer", "Data Scientist", "Product Manager", "Marketing Manager", "Sales Representative"]
#         for role in common_roles:
#             role_jobs = find_and_store_jobs(role, company_name)
#             jobs.extend(role_jobs)
#             if len(jobs) >= 3:
#                 break
    
#     # Step 3: Prepare the final result
#     result = {
#         "company_info": company_info,
#         "jobs": jobs[:3],  # Return top 3 jobs
#         "timestamp": datetime.now().isoformat()
#     }
    
#     # Step 4: Save the result to S3
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename = f"company_research_{company_name.replace(' ', '_')}_{timestamp}.json"
#     save_to_s3(result, filename)
    
#     logger.info(f"Completed research and job search for {company_name}")
#     return result

# if __name__ == "__main__":
#     # Example usage
#     if len(sys.argv) > 1:
#         company_name = sys.argv[1]
#         job_title = sys.argv[2] if len(sys.argv) > 2 else None
        
#         result = research_company_and_find_jobs(company_name, job_title)
        
#         # Display the results
#         print("\n=== COMPANY INFORMATION ===")
#         print(f"Company: {result['company_info']['name']}")
#         print(f"Overview: {result['company_info']['overview'][:300]}...")
        
#         if 'career_site_url' in result['company_info']:
#             print(f"Career Site: {result['company_info']['career_site_url']}")
#         else:
#             print(f"Career Site: Not found")
            
#         print(f"Culture: {result['company_info']['culture'][:300]}...")
#         print(f"Technology: {result['company_info']['technology'][:300]}...")
#         print(f"Achievements: {result['company_info']['achievements'][:300]}...")
        
#         print("\n=== RELATED JOBS ===")
#         for i, job in enumerate(result['jobs'], 1):
#             print(f"\nJob {i}:")
#             print(f"Title: {job['job_title']}")
#             print(f"Company: {job['company']}")
#             print(f"Location: {job['location']}")
#             print(f"Job Type: {job['job_type']}")
#             print(f"Work Mode: {job['work_mode']}")
#             print(f"Seniority: {job['seniority']}")
#             print(f"Skills: {', '.join(job['skills'][:5]) if job['skills'] else 'None specified'}")
#     else:
#         print("Usage: python company_agent.py <company_name> [job_title]")



# import os
# import sys
# import logging
# from datetime import datetime
# from pathlib import Path
# import json
# import time
# import hashlib
# import requests
# from dotenv import load_dotenv
# from serpapi import GoogleSearch
# from openai import OpenAI
# from pinecone import Pinecone

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger(__name__)

# # Load environment variables from .env file
# load_dotenv()

# # Initialize API clients
# try:
#     # Retrieve API keys from environment variables
#     serpapi_api_key = os.getenv('SERPAPI_API_KEY')
#     openai_api_key = os.getenv('OPENAI_API_KEY')
#     pinecone_api_key = os.getenv('PINECONE_API_KEY')
    
#     # Log API key status (safely)
#     logger.info(f"SerpAPI key present: {bool(serpapi_api_key)}")
#     logger.info(f"OpenAI API key present: {bool(openai_api_key)}")
#     logger.info(f"Pinecone API key present: {bool(pinecone_api_key)}")
    
#     # Provide more informative error message if API keys are missing
#     missing_keys = []
#     if not serpapi_api_key:
#         missing_keys.append("SERPAPI_API_KEY")
#     if not openai_api_key:
#         missing_keys.append("OPENAI_API_KEY")
#     if not pinecone_api_key:
#         missing_keys.append("PINECONE_API_KEY")
#     if missing_keys:
#         error_msg = f"Missing environment variables: {', '.join(missing_keys)}. Please check your .env file or set these environment variables."
#         logger.error(error_msg)
#         raise ValueError(error_msg)
    
#     # Initialize OpenAI client
#     logger.info("Initializing OpenAI client...")
#     openai_client = OpenAI(api_key=openai_api_key)
#     logger.info("OpenAI client initialized successfully")
    
#     # Initialize Pinecone client
#     logger.info("Initializing Pinecone client...")
#     pc = Pinecone(api_key=pinecone_api_key)
#     PINECONE_INDEX_NAME = 'skillmatch'
#     logger.info(f"Pinecone client initialized with index: {PINECONE_INDEX_NAME}")
    
# except Exception as e:
#     logger.error(f"Error initializing clients: {str(e)}")
#     raise

# # Initialize S3 client
# try:
#     import boto3
#     from botocore.exceptions import ClientError
    
#     s3_client = boto3.client(
#         's3',
#         aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#         aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
#         region_name=os.getenv('AWS_REGION', 'us-east-1')
#     )
    
#     S3_BUCKET = 'skillmatchai'
#     S3_BASE_PATH = 'jobs/raw_files/'
#     logger.info(f"S3 client initialized with bucket: {S3_BUCKET}")
    
# except Exception as e:
#     logger.error(f"Error initializing S3 client: {str(e)}")
#     s3_client = None

# def save_to_s3(data, filename):
#     """
#     Save data to S3 bucket
#     """
#     if not s3_client:
#         logger.warning("S3 client not initialized, skipping S3 save")
#         return None
        
#     try:
#         # Convert data to JSON string
#         json_data = json.dumps(data, ensure_ascii=False)
        
#         # Upload to S3
#         s3_key = f"{S3_BASE_PATH}{filename}"
#         s3_client.put_object(
#             Bucket=S3_BUCKET,
#             Key=s3_key,
#             Body=json_data,
#             ContentType='application/json'
#         )
        
#         logger.info(f"Successfully saved data to s3://{S3_BUCKET}/{s3_key}")
#         return f"s3://{S3_BUCKET}/{s3_key}"
#     except Exception as e:
#         logger.error(f"Error saving to S3: {str(e)}")
#         return None

# def generate_embedding(text):
#     """
#     Generate an embedding for text using OpenAI's API
#     """
#     try:
#         response = openai_client.embeddings.create(
#             input=text,
#             model="text-embedding-ada-002"
#         )
        
#         # Extract embedding from response
#         embedding = response.data[0].embedding
#         return embedding
    
#     except Exception as e:
#         logger.error(f"Error generating embedding: {str(e)}")
#         # Return a random embedding as fallback
#         import random
#         return [random.uniform(-1, 1) for _ in range(1536)]

# class CompanyResearchAgent:
#     def __init__(self):
#         self.api_key = serpapi_api_key
        
#     def research_company(self, company_name):
#         """
#         Research company information using SerpAPI
#         """
#         logger.info(f"Researching company: {company_name}")
        
#         company_info = {
#             "name": company_name,
#             "overview": "",
#             "career_site": "",
#             "culture": "",
#             "technology": "",
#             "achievements": "",
#             "search_time": datetime.now().isoformat()
#         }
        
#         # Create search queries for different aspects of the company
#         search_aspects = [
#             {"aspect": "overview", "query": f"{company_name} company overview background history"},
#             {"aspect": "career_site", "query": f"{company_name} careers jobs website portal"},
#             {"aspect": "culture", "query": f"{company_name} working culture employee reviews"},
#             {"aspect": "technology", "query": f"{company_name} technology stack projects"},
#             {"aspect": "achievements", "query": f"{company_name} achievements awards recognition"}
#         ]
        
#         for aspect_info in search_aspects:
#             aspect = aspect_info["aspect"]
#             query = aspect_info["query"]
            
#             try:
#                 # Use SerpAPI to search
#                 search_params = {
#                     "api_key": self.api_key,
#                     "engine": "google",
#                     "q": query,
#                     "num": 3,
#                     "gl": "us"  # Search in US
#                 }
                
#                 search = GoogleSearch(search_params)
#                 results = search.get_dict()
                
#                 # Extract content from organic results
#                 content = ""
#                 if "organic_results" in results:
#                     for result in results["organic_results"][:3]:
#                         if "snippet" in result:
#                             content += result["snippet"] + " "
                        
#                         # For career site, try to find the URL
#                         if aspect == "career_site" and "link" in result:
#                             link = result["link"]
#                             if 'careers' in link.lower() or 'jobs' in link.lower():
#                                 company_info["career_site_url"] = link
                
#                 company_info[aspect] = content.strip()
                
#                 # Add a small delay to avoid rate limiting
#                 time.sleep(1)
                
#             except Exception as e:
#                 logger.error(f"Error researching {aspect} for {company_name}: {str(e)}")
        
#         logger.info(f"Completed research for {company_name}")
#         return company_info

#     def find_jobs(self, job_title, company_name=None, location=None):
#         """
#         Find jobs using SerpAPI
#         """
#         logger.info(f"Finding jobs: {job_title} at {company_name if company_name else 'any company'}")
        
#         # Create a search query for jobs
#         query = f"{job_title} job openings"
#         if company_name:
#             query += f" at {company_name}"
#         if location:
#             query += f" in {location}"
        
#         jobs_found = []
        
#         try:
#             # Use SerpAPI to search for jobs
#             search_params = {
#                 "api_key": self.api_key,
#                 "engine": "google_jobs",
#                 "q": query,
#                 "hl": "en",
#                 "gl": "us"
#             }
            
#             search = GoogleSearch(search_params)
#             results = search.get_dict()
            
#             # Extract job information from the response
#             if "jobs_results" in results:
#                 for job in results["jobs_results"]:
#                     # Extract job details
#                     title = job.get("title", "")
#                     company = job.get("company_name", company_name if company_name else "")
#                     job_location = job.get("location", location if location else "")
                    
#                     # Get job description if available
#                     description = ""
#                     responsibilities = ""
#                     qualifications = ""
                    
#                     if "description" in job:
#                         description = job["description"]
                        
#                         # Try to extract responsibilities and qualifications
#                         resp_start = description.lower().find('responsibilities')
#                         qual_start = description.lower().find('qualifications')
#                         req_start = description.lower().find('requirements')
                        
#                         if resp_start != -1:
#                             end_idx = min(x for x in [qual_start, req_start, len(description)] 
#                                          if x > resp_start and x != -1)
#                             responsibilities = description[resp_start:end_idx].strip()
                        
#                         if qual_start != -1:
#                             end_idx = min(x for x in [resp_start, req_start, len(description)] 
#                                          if x > qual_start and x != -1 and x != qual_start)
#                             qualifications = description[qual_start:end_idx].strip()
#                         elif req_start != -1:
#                             end_idx = min(x for x in [resp_start, qual_start, len(description)] 
#                                          if x > req_start and x != -1 and x != req_start)
#                             qualifications = description[req_start:end_idx].strip()
                    
#                     # Extract skills from qualifications
#                     skills = []
#                     if qualifications:
#                         skill_keywords = ["experience with", "knowledge of", "proficiency in", 
#                                          "familiarity with", "skilled in", "expertise in"]
                        
#                         for line in qualifications.split('\n'):
#                             for keyword in skill_keywords:
#                                 if keyword in line.lower():
#                                     potential_skill = line.split(keyword)[-1].strip()
#                                     if potential_skill and len(potential_skill) < 50:
#                                         skills.append(potential_skill)
                    
#                     # Determine job type, work mode, and seniority
#                     job_type = "Full-time"  # Default
#                     if "detected_extensions" in job and "schedule_type" in job["detected_extensions"]:
#                         job_type = job["detected_extensions"]["schedule_type"]
                    
#                     work_mode = "Hybrid"  # Default
#                     if "detected_extensions" in job and "work_from_home" in job["detected_extensions"]:
#                         if job["detected_extensions"]["work_from_home"]:
#                             work_mode = "Remote"
#                         else:
#                             work_mode = "On-site"
                    
#                     seniority = "Mid Level"  # Default
#                     if "seniority" in job:
#                         seniority = job["seniority"]
#                     elif title.lower().startswith("senior") or "sr." in title.lower():
#                         seniority = "Senior Level"
#                     elif title.lower().startswith("junior") or "jr." in title.lower():
#                         seniority = "Entry Level"
                    
#                     # Create a job object that matches the expected structure
#                     job_data = {
#                         "job_title": title,
#                         "company": company,
#                         "location": job_location,
#                         "job_type": job_type,
#                         "work_mode": work_mode,
#                         "seniority": seniority,
#                         "salary": job.get("salary", ""),
#                         "experience": "",  # Not directly available from SerpAPI
#                         "responsibilities": responsibilities,
#                         "qualifications": qualifications,
#                         "skills": skills,
#                         "source": "serpapi",
#                         "timestamp": int(time.time())
#                     }
                    
#                     # Generate a unique ID for the job
#                     job_id = f"job_{title.lower().replace(' ', '_')}_{int(time.time())}"
                    
#                     jobs_found.append((job_id, job_data))
            
#         except Exception as e:
#             logger.error(f"Error finding jobs: {str(e)}")
        
#         logger.info(f"Found {len(jobs_found)} potential jobs")
#         return jobs_found

# def check_job_exists_in_pinecone(job_title, company):
#     """
#     Check if a job already exists in Pinecone by its title and company
#     """
#     try:
#         # Connect to the Pinecone index
#         index = pc.Index(PINECONE_INDEX_NAME)
        
#         # Create a normalized version of job title and company for comparison
#         normalized_title = job_title.lower().strip()
#         normalized_company = company.lower().strip()
        
#         # Query for jobs with similar title and company
#         results = index.query(
#             vector=[0.1] * 1536,  # Dummy vector for metadata filtering
#             filter={
#                 "$and": [
#                     {"job_title": {"$eq": normalized_title}},
#                     {"company": {"$eq": normalized_company}}
#                 ]
#             },
#             top_k=1,
#             include_metadata=True
#         )
        
#         # If we got any matches, the job exists
#         return len(results['matches']) > 0
    
#     except Exception as e:
#         logger.error(f"Error checking if job exists in Pinecone: {str(e)}")
#         return False

# def store_job_in_pinecone(job_id, job_data, embedding):
#     """
#     Store a job in Pinecone with its embedding
#     """
#     try:
#         # Connect to the Pinecone index
#         index = pc.Index(PINECONE_INDEX_NAME)
        
#         # Prepare metadata - ensure it matches the expected structure
#         metadata = {
#             "company": job_data["company"],
#             "experience": job_data["experience"],
#             "job_title": job_data["job_title"],
#             "job_type": job_data["job_type"],
#             "location": job_data["location"],
#             "qualifications": job_data["qualifications"],
#             "responsibilities": job_data["responsibilities"],
#             "salary": job_data["salary"],
#             "seniority": job_data["seniority"],
#             "skills": job_data["skills"],
#             "source": job_data["source"],
#             "timestamp": job_data["timestamp"],
#             "work_mode": job_data["work_mode"]
#         }
        
#         # Upsert the job into Pinecone
#         index.upsert(
#             vectors=[
#                 {
#                     "id": job_id,
#                     "values": embedding,
#                     "metadata": metadata
#                 }
#             ]
#         )
        
#         logger.info(f"Stored job in Pinecone: {job_data['job_title']} at {job_data['company']}")
#         return True
    
#     except Exception as e:
#         logger.error(f"Error storing job in Pinecone: {str(e)}")
#         return False

# def find_and_store_jobs(agent, job_title, company_name=None, location=None):
#     """
#     Find jobs using SerpAPI and store them in Pinecone
#     """
#     logger.info(f"Starting job search for {job_title}")
    
#     # Step 1: Find jobs using SerpAPI
#     jobs_found = agent.find_jobs(job_title, company_name, location)
    
#     # Step 2: Filter out existing jobs and store new ones
#     jobs_stored = []
#     for job_id, job_data in jobs_found:
#         # Check if job already exists
#         if not check_job_exists_in_pinecone(job_data["job_title"], job_data["company"]):
#             # Generate embedding for the job
#             job_text = f"{job_data['job_title']} {job_data['company']} {job_data['responsibilities']} {job_data['qualifications']}"
#             embedding = generate_embedding(job_text)
            
#             # Store job in Pinecone
#             if store_job_in_pinecone(job_id, job_data, embedding):
#                 jobs_stored.append(job_data)
    
#     # Step 3: Save the results to S3
#     if jobs_stored:
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"serpapi_jobs_{job_title.replace(' ', '_')}_{timestamp}.json"
#         save_to_s3(jobs_stored, filename)
    
#     logger.info(f"Stored {len(jobs_stored)} new jobs in Pinecone")
#     return jobs_stored

# def research_company_and_find_jobs(company_name, job_title=None):
#     """
#     Research company information and find related jobs
#     """
#     logger.info(f"Starting research for {company_name}")
    
#     # Initialize the agent
#     agent = CompanyResearchAgent()
    
#     # Step 1: Research company information
#     company_info = agent.research_company(company_name)
    
#     # Step 2: Find jobs at this company
#     jobs = []
#     if job_title:
#         jobs = find_and_store_jobs(agent, job_title, company_name)
#     else:
#         # If no specific job title, find various roles at the company
#         common_roles = ["Software Engineer", "Data Scientist", "Product Manager", "Marketing Manager", "Sales Representative"]
#         for role in common_roles:
#             role_jobs = find_and_store_jobs(agent, role, company_name)
#             jobs.extend(role_jobs)
#             if len(jobs) >= 3:
#                 break
    
#     # Step 3: Prepare the final result
#     result = {
#         "company_info": company_info,
#         "jobs": jobs[:3],  # Return top 3 jobs
#         "timestamp": datetime.now().isoformat()
#     }
    
#     # Step 4: Save the result to S3
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename = f"company_research_{company_name.replace(' ', '_')}_{timestamp}.json"
#     save_to_s3(result, filename)
    
#     logger.info(f"Completed research and job search for {company_name}")
#     return result

# if __name__ == "__main__":
#     # Example usage
#     if len(sys.argv) > 1:
#         company_name = sys.argv[1]
#         job_title = sys.argv[2] if len(sys.argv) > 2 else None
        
#         result = research_company_and_find_jobs(company_name, job_title)
        
#         # Display the results
#         print("\n=== COMPANY INFORMATION ===")
#         print(f"Company: {result['company_info']['name']}")
#         print(f"Overview: {result['company_info']['overview'][:300]}...")
        
#         if 'career_site_url' in result['company_info']:
#             print(f"Career Site: {result['company_info']['career_site_url']}")
#         else:
#             print(f"Career Site: Not found")
            
#         print(f"Culture: {result['company_info']['culture'][:300]}...")
#         print(f"Technology: {result['company_info']['technology'][:300]}...")
#         print(f"Achievements: {result['company_info']['achievements'][:300]}...")
        
#         print("\n=== RELATED JOBS ===")
#         for i, job in enumerate(result['jobs'], 1):
#             print(f"\nJob {i}:")
#             print(f"Title: {job['job_title']}")
#             print(f"Company: {job['company']}")
#             print(f"Location: {job['location']}")
#             print(f"Job Type: {job['job_type']}")
#             print(f"Work Mode: {job['work_mode']}")
#             print(f"Seniority: {job['seniority']}")
#             print(f"Skills: {', '.join(job['skills'][:5]) if job['skills'] else 'None specified'}")
#     else:
#         print("Usage: python company_agent.py <company_name> [job_title]")
















# import os
# import sys
# import logging
# from datetime import datetime
# from pathlib import Path
# import json
# import time
# import hashlib
# import requests
# from dotenv import load_dotenv
# from tavily import TavilyClient
# from pinecone import Pinecone
# from openai import OpenAI

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger(__name__)

# # Load environment variables from .env file
# load_dotenv()

# # Initialize API clients
# try:
#     # Retrieve API keys from environment variables
#     tavily_api_key = os.getenv('TAVILY_API_KEY')
#     openai_api_key = os.getenv('OPENAI_API_KEY')
#     pinecone_api_key = os.getenv('PINECONE_API_KEY')
    
#     # Log API key status (safely)
#     logger.info(f"Tavily API key present: {bool(tavily_api_key)}")
#     logger.info(f"OpenAI API key present: {bool(openai_api_key)}")
#     logger.info(f"Pinecone API key present: {bool(pinecone_api_key)}")
    
#     # Provide more informative error message if API keys are missing
#     missing_keys = []
#     if not tavily_api_key:
#         missing_keys.append("TAVILY_API_KEY")
#     if not openai_api_key:
#         missing_keys.append("OPENAI_API_KEY")
#     if not pinecone_api_key:
#         missing_keys.append("PINECONE_API_KEY")
#     if missing_keys:
#         error_msg = f"Missing environment variables: {', '.join(missing_keys)}. Please check your .env file or set these environment variables."
#         logger.error(error_msg)
#         raise ValueError(error_msg)
    
#     # Initialize Tavily client
#     logger.info("Initializing Tavily client...")
#     tavily_client = TavilyClient(api_key=tavily_api_key)
#     logger.info("Tavily client initialized successfully")
    
#     # Initialize OpenAI client
#     logger.info("Initializing OpenAI client...")
#     openai_client = OpenAI(api_key=openai_api_key)
#     logger.info("OpenAI client initialized successfully")
    
#     # Initialize Pinecone client
#     logger.info("Initializing Pinecone client...")
#     pc = Pinecone(api_key=pinecone_api_key)
#     PINECONE_INDEX_NAME = 'skillmatch-index'  # Updated to correct index name
#     PINECONE_HOST = 'https://skillmatch-index-u4bo3mo.svc.aped-4627-b74a.pinecone.io'  # Added host
#     logger.info(f"Pinecone client initialized with index: {PINECONE_INDEX_NAME}")
    
# except Exception as e:
#     logger.error(f"Error initializing clients: {str(e)}")
#     raise

# # Initialize S3 client
# try:
#     import boto3
#     from botocore.exceptions import ClientError
    
#     s3_client = boto3.client(
#         's3',
#         aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#         aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
#         region_name=os.getenv('AWS_REGION', 'us-east-1')
#     )
    
#     S3_BUCKET = 'skillmatchai'
#     S3_BASE_PATH = 'jobs/raw_files/'
#     logger.info(f"S3 client initialized with bucket: {S3_BUCKET}")
    
# except Exception as e:
#     logger.error(f"Error initializing S3 client: {str(e)}")
#     s3_client = None

# def save_to_s3(data, filename):
#     """
#     Save data to S3 bucket
#     """
#     if not s3_client:
#         logger.warning("S3 client not initialized, skipping S3 save")
#         return None
        
#     try:
#         # Convert data to JSON string
#         json_data = json.dumps(data, ensure_ascii=False)
        
#         # Upload to S3
#         s3_key = f"{S3_BASE_PATH}{filename}"
#         s3_client.put_object(
#             Bucket=S3_BUCKET,
#             Key=s3_key,
#             Body=json_data,
#             ContentType='application/json'
#         )
        
#         logger.info(f"Successfully saved data to s3://{S3_BUCKET}/{s3_key}")
#         return f"s3://{S3_BUCKET}/{s3_key}"
#     except Exception as e:
#         logger.error(f"Error saving to S3: {str(e)}")
#         return None

# def generate_embedding(text):
#     """
#     Generate an embedding for text using OpenAI's API with text-embedding-3-large
#     """
#     try:
#         response = openai_client.embeddings.create(
#             input=text,
#             model="text-embedding-3-large"  # Updated to match your Pinecone configuration
#         )
        
#         # Extract embedding from response
#         embedding = response.data[0].embedding
        
#         # Verify embedding dimension
#         if len(embedding) != 3072:  # Updated to match your Pinecone dimension
#             logger.warning(f"Embedding dimension mismatch: expected 3072, got {len(embedding)}")
            
#         return embedding
    
#     except Exception as e:
#         logger.error(f"Error generating embedding: {str(e)}")
#         # Return a random embedding as fallback
#         import random
#         return [random.uniform(-1, 1) for _ in range(3072)]  # Updated to match your Pinecone dimension

# def research_company(company_name):
#     """
#     Research company information using Tavily API
#     """
#     logger.info(f"Researching company: {company_name}")
    
#     # Create search queries for different aspects of the company
#     queries = [
#         f"{company_name} company overview background history",
#         f"{company_name} careers jobs website portal",
#         f"{company_name} working culture employee reviews",
#         f"{company_name} technology stack projects",
#         f"{company_name} achievements awards recognition"
#     ]
    
#     company_info = {
#         "name": company_name,
#         "overview": "",
#         "career_site": "",
#         "culture": "",
#         "technology": "",
#         "achievements": "",
#         "search_time": datetime.now().isoformat()
#     }
    
#     # Execute searches for each aspect
#     for i, query in enumerate(queries):
#         try:
#             # Use Tavily's search API
#             search_results = tavily_client.search(
#                 query=query,
#                 search_depth="advanced",
#                 max_results=3
#             )
            
#             # Extract the content from the response
#             if search_results and 'results' in search_results:
#                 content = " ".join([result.get('content', '') for result in search_results['results']])
                
#                 # Store the content in the appropriate field
#                 if i == 0:
#                     company_info["overview"] = content
#                 elif i == 1:
#                     company_info["career_site"] = content
#                     # Try to extract career site URL
#                     for result in search_results['results']:
#                         if 'careers' in result.get('url', '').lower() or 'jobs' in result.get('url', '').lower():
#                             company_info["career_site_url"] = result.get('url', '')
#                             break
#                 elif i == 2:
#                     company_info["culture"] = content
#                 elif i == 3:
#                     company_info["technology"] = content
#                 elif i == 4:
#                     company_info["achievements"] = content
            
#             # Add a small delay to avoid rate limiting
#             time.sleep(1)
            
#         except Exception as e:
#             logger.error(f"Error researching {query}: {str(e)}")
    
#     logger.info(f"Completed research for {company_name}")
#     return company_info

# def find_jobs_with_tavily(job_title, company_name=None, location=None):
#     """
#     Find jobs using Tavily API
#     """
#     logger.info(f"Finding jobs: {job_title} at {company_name if company_name else 'any company'}")
    
#     # Create a search query for jobs
#     query = f"{job_title} job openings"
#     if company_name:
#         query += f" at {company_name}"
#     if location:
#         query += f" in {location}"
    
#     jobs_found = []
    
#     try:
#         # Use Tavily's search API
#         search_results = tavily_client.search(
#             query=query,
#             search_depth="advanced",
#             max_results=10
#         )
        
#         # Extract job information from the response
#         if search_results and 'results' in search_results:
#             for result in search_results['results']:
#                 # Extract job details from the result
#                 title = ""
#                 company = company_name if company_name else ""
#                 job_location = location if location else ""
#                 url = result.get('url', '')
#                 content = result.get('content', '')
                
#                 # Try to parse job details from content
#                 lines = content.split('\n')
#                 for line in lines:
#                     if not title and ('job title' in line.lower() or 'position' in line.lower() or 'role:' in line.lower()):
#                         title = line.split(':')[-1].strip()
#                     if not company and ('company' in line.lower() or 'organization' in line.lower()):
#                         company = line.split(':')[-1].strip()
#                     if not job_location and ('location' in line.lower() or 'city' in line.lower()):
#                         job_location = line.split(':')[-1].strip()
                
#                 # If we couldn't extract title, use the page title
#                 if not title:
#                     title = result.get('title', '').split('-')[0].strip()
#                     # Try to extract company from title if not already set
#                     if not company:
#                         title_parts = result.get('title', '').split('-')
#                         if len(title_parts) > 1:
#                             company = title_parts[1].strip()
                
#                 # Extract responsibilities and qualifications
#                 responsibilities = ""
#                 qualifications = ""
#                 skills = []
                
#                 # Look for responsibilities section
#                 resp_start = content.lower().find('responsibilities')
#                 qual_start = content.lower().find('qualifications')
#                 req_start = content.lower().find('requirements')
#                 skills_start = content.lower().find('skills')
                
#                 if resp_start != -1:
#                     end_idx = min(x for x in [qual_start, req_start, skills_start, len(content)] if x > resp_start)
#                     responsibilities = content[resp_start:end_idx].strip()
                
#                 # Look for qualifications section
#                 if qual_start != -1:
#                     end_idx = min(x for x in [resp_start, req_start, skills_start, len(content)] if x > qual_start and x != qual_start)
#                     qualifications = content[qual_start:end_idx].strip()
#                 elif req_start != -1:
#                     end_idx = min(x for x in [resp_start, qual_start, skills_start, len(content)] if x > req_start and x != req_start)
#                     qualifications = content[req_start:end_idx].strip()
                
#                 # Extract skills
#                 if skills_start != -1:
#                     skills_text = content[skills_start:].strip()
#                     skills_lines = skills_text.split('\n')
#                     for i in range(1, min(10, len(skills_lines))):
#                         skill = skills_lines[i].strip()
#                         if skill and len(skill) < 50:  # Reasonable skill length
#                             skills.append(skill)
                
#                 # If no skills found, try to extract from qualifications
#                 if not skills and qualifications:
#                     qual_lines = qualifications.split('\n')
#                     for line in qual_lines:
#                         if 'experience with' in line.lower() or 'knowledge of' in line.lower() or 'proficiency in' in line.lower():
#                             potential_skill = line.split('with')[-1].split('of')[-1].split('in')[-1].strip()
#                             if potential_skill and len(potential_skill) < 50:
#                                 skills.append(potential_skill)
                
#                 # Determine job type, work mode, and seniority
#                 job_type = "Full-time"  # Default
#                 work_mode = "Hybrid"    # Default
#                 seniority = "Mid Level" # Default
                
#                 if 'part-time' in content.lower() or 'part time' in content.lower():
#                     job_type = "Part-time"
#                 if 'contract' in content.lower() or 'contractor' in content.lower():
#                     job_type = "Contract"
#                 if 'internship' in content.lower():
#                     job_type = "Internship"
                
#                 if 'remote' in content.lower():
#                     work_mode = "Remote"
#                 if 'on-site' in content.lower() or 'onsite' in content.lower() or 'in office' in content.lower():
#                     work_mode = "On-site"
                
#                 if 'senior' in content.lower() or 'sr.' in content.lower():
#                     seniority = "Senior Level"
#                 if 'junior' in content.lower() or 'jr.' in content.lower():
#                     seniority = "Entry Level"
#                 if 'principal' in content.lower() or 'lead' in content.lower() or 'director' in content.lower():
#                     seniority = "Principal"
                
#                 # Create a job object that matches the expected structure
#                 job = {
#                     "job_title": title,
#                     "company": company,
#                     "location": job_location,
#                     "job_type": job_type,
#                     "work_mode": work_mode,
#                     "seniority": seniority,
#                     "salary": "",  # Typically not available from search results
#                     "experience": "",  # Typically not available from search results
#                     "responsibilities": responsibilities,
#                     "qualifications": qualifications,
#                     "skills": skills,
#                     "source": "tavily",
#                     "timestamp": int(time.time())
#                 }
                
#                 # Generate a unique ID for the job
#                 job_id = f"job_{title.lower().replace(' ', '_')}_{int(time.time())}"
                
#                 jobs_found.append((job_id, job))
        
#     except Exception as e:
#         logger.error(f"Error finding jobs: {str(e)}")
    
#     logger.info(f"Found {len(jobs_found)} potential jobs")
#     return jobs_found

# def check_job_exists_in_pinecone(job_title, company):
#     """
#     Check if a job already exists in Pinecone by its title and company
#     """
#     try:
#         # Connect to the Pinecone index with the correct host
#         index = pc.Index(PINECONE_INDEX_NAME, host=PINECONE_HOST)
        
#         # Create a normalized version of job title and company for comparison
#         normalized_title = job_title.lower().strip()
#         normalized_company = company.lower().strip()
        
#         # Query for jobs with similar title and company
#         results = index.query(
#             vector=[0.1] * 3072,  # Updated to match your Pinecone dimension
#             filter={
#                 "$and": [
#                     {"job_title": {"$eq": normalized_title}},
#                     {"company": {"$eq": normalized_company}}
#                 ]
#             },
#             top_k=1,
#             include_metadata=True,
#             namespace=None  # Use default namespace as specified
#         )
        
#         # If we got any matches, the job exists
#         return len(results['matches']) > 0
    
#     except Exception as e:
#         logger.error(f"Error checking if job exists in Pinecone: {str(e)}")
#         return False

# def store_job_in_pinecone(job_id, job_data, embedding):
#     """
#     Store a job in Pinecone with its embedding
#     """
#     try:
#         # Connect to the Pinecone index with the correct host
#         index = pc.Index(PINECONE_INDEX_NAME, host=PINECONE_HOST)
        
#         # Prepare metadata - ensure it matches the expected structure
#         metadata = {
#             "company": job_data["company"],
#             "experience": job_data["experience"],
#             "job_title": job_data["job_title"],
#             "job_type": job_data["job_type"],
#             "location": job_data["location"],
#             "qualifications": job_data["qualifications"],
#             "responsibilities": job_data["responsibilities"],
#             "salary": job_data["salary"],
#             "seniority": job_data["seniority"],
#             "skills": job_data["skills"],
#             "source": job_data["source"],
#             "timestamp": job_data["timestamp"],
#             "work_mode": job_data["work_mode"]
#         }
        
#         # Upsert the job into Pinecone
#         index.upsert(
#             vectors=[
#                 {
#                     "id": job_id,
#                     "values": embedding,
#                     "metadata": metadata
#                 }
#             ],
#             namespace=None  # Use default namespace as specified
#         )
        
#         logger.info(f"Stored job in Pinecone: {job_data['job_title']} at {job_data['company']}")
#         return True
    
#     except Exception as e:
#         logger.error(f"Error storing job in Pinecone: {str(e)}")
#         return False

# def find_and_store_jobs(job_title, company_name=None, location=None):
#     """
#     Find jobs using Tavily API and store them in Pinecone
#     """
#     logger.info(f"Starting job search for {job_title}")
    
#     # Step 1: Find jobs using Tavily
#     jobs_found = find_jobs_with_tavily(job_title, company_name, location)
    
#     # Step 2: Filter out existing jobs and store new ones
#     jobs_stored = []
#     for job_id, job_data in jobs_found:
#         # Check if job already exists
#         if not check_job_exists_in_pinecone(job_data["job_title"], job_data["company"]):
#             # Generate embedding for the job
#             job_text = f"{job_data['job_title']} {job_data['company']} {job_data['responsibilities']} {job_data['qualifications']}"
#             embedding = generate_embedding(job_text)
            
#             # Store job in Pinecone
#             if store_job_in_pinecone(job_id, job_data, embedding):
#                 jobs_stored.append(job_data)
    
#     # Step 3: Save the results to S3
#     if jobs_stored:
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"tavily_jobs_{job_title.replace(' ', '_')}_{timestamp}.json"
#         save_to_s3(jobs_stored, filename)
    
#     logger.info(f"Stored {len(jobs_stored)} new jobs in Pinecone")
#     return jobs_stored

# def research_company_and_find_jobs(company_name, job_title=None):
#     """
#     Research company information and find related jobs
#     """
#     logger.info(f"Starting research for {company_name}")
    
#     # Step 1: Research company information
#     company_info = research_company(company_name)
    
#     # Step 2: Find jobs at this company
#     jobs = []
#     if job_title:
#         jobs = find_and_store_jobs(job_title, company_name)
#     else:
#         # If no specific job title, find various roles at the company
#         common_roles = ["Software Engineer", "Data Scientist", "Product Manager", "Marketing Manager", "Sales Representative"]
#         for role in common_roles:
#             role_jobs = find_and_store_jobs(role, company_name)
#             jobs.extend(role_jobs)
#             if len(jobs) >= 3:
#                 break
    
#     # Step 3: Prepare the final result
#     result = {
#         "company_info": company_info,
#         "jobs": jobs[:3],  # Return top 3 jobs
#         "timestamp": datetime.now().isoformat()
#     }
    
#     # Step 4: Save the result to S3
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename = f"company_research_{company_name.replace(' ', '_')}_{timestamp}.json"
#     save_to_s3(result, filename)
    
#     logger.info(f"Completed research and job search for {company_name}")
#     return result

# if __name__ == "__main__":
#     # Example usage
#     if len(sys.argv) > 1:
#         company_name = sys.argv[1]
#         job_title = sys.argv[2] if len(sys.argv) > 2 else None
        
#         result = research_company_and_find_jobs(company_name, job_title)
        
#         # Display the results
#         print("\n=== COMPANY INFORMATION ===")
#         print(f"Company: {result['company_info']['name']}")
#         print(f"Overview: {result['company_info']['overview'][:300]}...")
        
#         if 'career_site_url' in result['company_info']:
#             print(f"Career Site: {result['company_info']['career_site_url']}")
#         else:
#             print(f"Career Site: Not found")
            
#         print(f"Culture: {result['company_info']['culture'][:300]}...")
#         print(f"Technology: {result['company_info']['technology'][:300]}...")
#         print(f"Achievements: {result['company_info']['achievements'][:300]}...")
        
#         print("\n=== RELATED JOBS ===")
#         for i, job in enumerate(result['jobs'], 1):
#             print(f"\nJob {i}:")
#             print(f"Title: {job['job_title']}")
#             print(f"Company: {job['company']}")
#             print(f"Location: {job['location']}")
#             print(f"Job Type: {job['job_type']}")
#             print(f"Work Mode: {job['work_mode']}")
#             print(f"Seniority: {job['seniority']}")
#             print(f"Skills: {', '.join(job['skills'][:5]) if job['skills'] else 'None specified'}")
#     else:
#         print("Usage: python company_agent.py <company_name> [job_title]")











import os
import time
import json
import logging
from datetime import datetime
from urllib.parse import urlparse
import boto3
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
from tavily import TavilyClient
from botocore.exceptions import ClientError

class CompanyJobAgent:
    def __init__(self):
        load_dotenv()

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

        self.tavily_api_key = os.getenv('TAVILY_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')

        if not all([self.tavily_api_key, self.openai_api_key, self.pinecone_api_key]):
            raise ValueError("Missing one or more required API keys.")

        self.tavily_client = TavilyClient(api_key=self.tavily_api_key)
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        self.pc = Pinecone(api_key=self.pinecone_api_key)

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.aws_region
        )
        self.S3_BUCKET = 'skillmatchai'
        self.S3_BASE_PATH = 'jobs/raw_files/'

        self.PINECONE_INDEX_NAME = 'skillmatch-index'
        self.PINECONE_HOST = 'https://skillmatch-index-u4bo3mo.svc.aped-4627-b74a.pinecone.io'

    def save_to_s3(self, data, filename):
        try:
            key = f"{self.S3_BASE_PATH}{filename}"
            self.s3_client.put_object(
                Bucket=self.S3_BUCKET,
                Key=key,
                Body=json.dumps(data, ensure_ascii=False),
                ContentType='application/json'
            )
            return f"s3://{self.S3_BUCKET}/{key}"
        except ClientError as e:
            self.logger.error(f"S3 save error: {e}")
            return None

    def generate_embedding(self, text):
        try:
            response = self.openai_client.embeddings.create(input=text, model="text-embedding-3-large")
            return response.data[0].embedding
        except Exception as e:
            self.logger.error(f"Embedding error: {e}")
            import random
            return [random.uniform(-1, 1) for _ in range(3072)]

    def research_company(self, company_name):
        queries = [
            f"{company_name} company overview background history",
            f"{company_name} careers jobs website portal",
            f"{company_name} working culture employee reviews",
            f"{company_name} technology stack projects",
            f"{company_name} achievements awards recognition"
        ]


        info = {"name": company_name, "overview": "", "career_site": "", "culture": "", "technology": "", "achievements": "", "search_time": datetime.now().isoformat()}

        for i, q in enumerate(queries):
            try:
                res = self.tavily_client.search(query=q, search_depth="advanced", max_results=3)
                content = " ".join([r.get('content', '') for r in res.get('results', [])])

                if i == 0: info["overview"] = content
                elif i == 1:
                    info["career_site"] = content
                    for r in res.get('results', []):
                        if 'careers' in r.get('url', '').lower() or 'jobs' in r.get('url', '').lower():
                            info["career_site_url"] = r.get('url')
                            break
                elif i == 2: info["culture"] = content
                elif i == 3: info["technology"] = content
                elif i == 4: info["achievements"] = content

                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Error researching '{q}': {e}")
        return info

    def find_and_store_jobs(self, job_title, company_name=None, location=None):
        jobs = self._search_jobs(job_title, company_name, location)
        stored_jobs = []

        for job_id, job in jobs:
            if not self._job_exists(job['job_title'], job['company']):
                text = f"{job['job_title']} {job['company']} {job['responsibilities']} {job['qualifications']}"
                embedding = self.generate_embedding(text)
                if self._store_job(job_id, job, embedding):
                    stored_jobs.append(job)

        if stored_jobs:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tavily_jobs_{job_title.replace(' ', '_')}_{ts}.json"
            self.save_to_s3(stored_jobs, filename)

        return stored_jobs

    def _search_jobs(self, title, company=None, location=None):
        query = f"{title} job openings"
        if company: query += f" at {company}"
        if location: query += f" in {location}"

        jobs = []
        try:
            results = self.tavily_client.search(query=query, search_depth="advanced", max_results=10)
            for res in results.get('results', []):
                content = res.get('content', '')
                title = res.get('title', '').split('-')[0].strip()
                company_name = company or (res.get('title', '').split('-')[1].strip() if '-' in res.get('title', '') else '')
                responsibilities = self._extract_section(content, "responsibilities")
                qualifications = self._extract_section(content, "qualifications")
                skills = self._extract_skills(content)
                job = {
                    "job_title": title,
                    "company": company_name,
                    "location": location or "",
                    "job_type": "Full-time",
                    "work_mode": "Hybrid",
                    "seniority": "Mid Level",
                    "salary": "",
                    "experience": "",
                    "responsibilities": responsibilities or "Not specified",
                    "qualifications": qualifications or "Not specified",
                     "skills": skills or [],
                    "source": "tavily",
                    "timestamp": int(time.time())
                }
                job_id = f"job_{title.lower().replace(' ', '_')}_{int(time.time())}"
                jobs.append((job_id, job))
        except Exception as e:
            self.logger.error(f"Job search error: {e}")
        return jobs

    def _job_exists(self, title, company):
        try:
            index = self.pc.Index(self.PINECONE_INDEX_NAME, host=self.PINECONE_HOST)
            results = index.query(
                vector=[0.1] * 3072,
                filter={"$and": [
                    {"job_title": {"$eq": title.lower()}},
                    {"company": {"$eq": company.lower()}}
                ]},
                top_k=1,
                include_metadata=True
            )
            return len(results.get('matches', [])) > 0
        except Exception as e:
            self.logger.error(f"Pinecone check error: {e}")
            return False

    def _store_job(self, job_id, job, embedding):
        try:
            index = self.pc.Index(self.PINECONE_INDEX_NAME, host=self.PINECONE_HOST)
            index.upsert(vectors=[{
                "id": job_id,
                "values": embedding,
                "metadata": job
            }])
            return True
        except Exception as e:
            self.logger.error(f"Pinecone store error: {e}")
            return False
        
    def _extract_section(self, text, keyword):
        start = text.lower().find(keyword)
        if start == -1:
            return ""
        next_section = text.lower().find('\n\n', start)
        return text[start:next_section].strip() if next_section != -1 else text[start:].strip()

    def _extract_skills(self, text):
        import re
        prompt = f"""
            Extract technical skills, programming languages, and tools from this job description text.
            Return as a comma-separated list with no explanations.

            Text:
            {text}
            """
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract skills from job description."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=100
            )
            skills_raw = response.choices[0].message.content
            return [s.strip() for s in re.split(r'[,\n]', skills_raw) if s.strip()]
        except Exception as e:
            self.logger.warning(f"Failed to extract skills: {e}")
            return []





    def research_company_and_find_jobs(self, company_name, job_title=None):
        info = self.research_company(company_name)
        jobs = self.find_and_store_jobs(job_title, company_name) if job_title else []
        return {
            "company_info": info,
            "jobs": jobs[:3],
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    import sys
    agent = CompanyJobAgent()
    if len(sys.argv) > 1:
        company = sys.argv[1]
        job = sys.argv[2] if len(sys.argv) > 2 else None
        results = agent.research_company_and_find_jobs(company, job)

        print("\n=== COMPANY INFORMATION ===")
        print(f"Company: {results['company_info']['name']}")
        print(f"Overview: {results['company_info']['overview'][:300]}...")
        if 'career_site_url' in results['company_info']:
            print(f"Career Site: {results['company_info']['career_site_url']}")
        else:
            print("Career Site: Not found")
        print(f"Culture: {results['company_info']['culture'][:300]}...")
        print(f"Technology: {results['company_info']['technology'][:300]}...")
        print(f"Achievements: {results['company_info']['achievements'][:300]}...")

        print("\n=== RELATED JOBS ===")
        for i, job in enumerate(results['jobs'], 1):
            print(f"\nJob {i}:")
            print(f"Title: {job['job_title']}")
            print(f"Company: {job['company']}")
            print(f"Location: {job['location']}")
            print(f"Job Type: {job['job_type']}")
            print(f"Work Mode: {job['work_mode']}")
            print(f"Seniority: {job['seniority']}")
            print(f"Skills: {', '.join(job['skills'][:5]) if job['skills'] else 'None specified'}")
    else:
        print("Usage: python company_agent.py <company_name> [job_title]")
