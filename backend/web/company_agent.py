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
