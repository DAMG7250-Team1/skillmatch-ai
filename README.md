# SkillMatchAI
**TEAM 1 – DAMG7245**

**SkillMatchAI** is an AI-powered job recommendation system that uses user resumes and GitHub profiles to intelligently match candidates to suitable job opportunities. It leverages OpenAI embeddings, Pinecone vector search, and custom NLP logic to:
- Extract skills, qualifications, and experience from resumes and GitHub profiles
- Embed and match profiles with jobs scraped from JobRight.ai
- Generate cover letters tailored to job descriptions
- Provide actionable profile improvement suggestions
## 🔗 Links

- **Frontend**: 

- **Backend**: 

- **Airflow**: http://34.139.104.57:8081/home

- **Demo Video**: 

- **Google Codelab**: 

## 📘 Project Description 

### 1. Job Scraping System
- Automated scraping of job listings from JobRight.ai
- Scheduled Airflow DAG running every 4 hours
- Selenium-based web scraper with Chrome WebDriver

### 2. Vector Embedding Engine
- OpenAI embeddings for job descriptions (text-embedding-3-large)
- Skill extraction using GPT-3.5
- Pinecone vector database for efficient similarity search

### 3. Matching Algorithm
- Vector similarity search for relevance ranking
- Skill overlap detection and scoring
- Deduplication and result filtering

### 4. Infrastructure
- Docker containerization for all services
- AWS S3 for storage of job data and embeddings
- CI/CD pipeline with GitHub Actions
- Airflow for workflow orchestration
---

## 💻 Technologies and Tools

[![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white)](https://fastapi.tiangolo.com/)
[![Apache Airflow](https://img.shields.io/badge/Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white)](https://airflow.apache.org/)
[![Amazon S3](https://img.shields.io/badge/AWS_S3-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)](https://aws.amazon.com/s3/)
[![Docker](https://img.shields.io/badge/Docker-%232496ED?style=for-the-badge&logo=Docker&color=blue&logoColor=white)](https://www.docker.com)
[![Google Cloud](https://img.shields.io/badge/Google_Cloud-%234285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/)
[![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-8A4182?style=for-the-badge&logo=python&logoColor=white)](https://www.crummy.com/software/BeautifulSoup/)
[![PyPDF2](https://img.shields.io/badge/PyPDF2-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://pypi.org/project/PyPDF2/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://platform.openai.com/)
[![Pinecone](https://img.shields.io/badge/Pinecone-0A2239?style=for-the-badge&logoColor=white)](https://www.pinecone.io/)

---

## ⚙️ Setup Instructions (Step-by-Step Guide)
1. **Clone the Repository:**
```bash
git clone https://github.com/your-org/skillmatch-ai.git
cd skillmatch-ai
```

2. **Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

3. **Frontend Setup (Streamlit):**
```bash
cd frontend
streamlit run app.py
```

4. **Set Environment Variables (.env):**
```env
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
GITHUB_ACCESS_TOKEN=your_github_token
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_BUCKET_NAME=skillmatchai
TAVILY_API_KEY=your_tavily_key
```

5. **Run Airflow (optional for daily jobs update):**
Configure Airflow DAGs to trigger `scraper.py` and `embeddings.py` for daily job scraping and embedding generation.

---

## 📂 Directory Structure
```
skillmatch-ai/
├── backend/
│   ├── main.py             # FastAPI app entry point
│   ├── orchestrator.py     # LangGraph orchestrator
│   ├── resume.py           # Resume processing and markdown conversion
│   ├── github.py           # GitHub repo parsing and markdown
│   ├── user_embedding.py   # Embedding & Pinecone upsert for user profile
│   ├── cover_letter.py     # Cover letter & profile improvement agent
│   ├── job_matching.py     # Job matching logic with score weights
│   ├── embeddings.py       # Job embedding pipeline
│   ├── scraper.py          # Job scraper from JobRight.ai
│   ├── company_agent.py    # Tavily agent for company info
├── frontend/
│   ├── app.py              # Streamlit app
├── requirements.txt
├── Dockerfile
```

---

## 🏗 Architecture Diagram
*(To be added)*

---

## 👥 Team Members

- Member 1: Dhrumil Patel
  
- Member 2: Husain
  
- Member 3: Sahil Kasliwal

---

## 📜 Disclosures
```
WE ATTEST THAT WE HAVEN’T USED ANY OTHER STUDENTS’ WORK IN OUR ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK.

Dhrumil Patel: 33.3%  

Husain: 33.3% 

Sahil Kasliwal: 33.3%
```

---







