# SkillMatchAI
**TEAM 1 – DAMG7245**

**SkillMatchAI** is an AI-powered job recommendation system that uses user resumes and GitHub profiles to intelligently match candidates to suitable job opportunities. It leverages OpenAI embeddings, Pinecone vector search, and custom NLP logic to:
- Extract skills, qualifications, and experience from resumes and GitHub profiles
- Embed and match profiles with jobs scraped from JobRight.ai
- Generate cover letters tailored to job descriptions
- Provide actionable profile improvement suggestions
## 🔗 Links

- **Frontend**: https://damg7250-team1-skillmatch-ai-frontendapp-arx616.streamlit.app/

- **Backend**: https://skillmatch-xqv7xxttja-ue.a.run.app

- **Airflow**: http://34.139.104.57:8081/home

- **Demo Video**: https://northeastern-my.sharepoint.com/:v:/r/personal/kasliwal_s_northeastern_edu/Documents/Recordings/Meeting%20in%20Ek%20aakhri%20baaar-20250418_152741-Meeting%20Recording.mp4?csf=1&web=1&e=1XjD49&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D

- **Google Codelab**: https://codelabs-preview.appspot.com/?file_id=10h_ONepkMa254lWd3V8FwyAvkFKhmze9uw9t0MogVDU#6

- **Google Docs**: https://docs.google.com/document/d/10h_ONepkMa254lWd3V8FwyAvkFKhmze9uw9t0MogVDU/edit?tab=t.0#heading=h.q8w1haghexfz

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
[![PyPDF2](https://img.shields.io/badge/PyPDF2-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://pypi.org/project/PyPDF2/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://platform.openai.com/)
[![Pinecone](https://img.shields.io/badge/Pinecone-0A2239?style=for-the-badge&logoColor=white)](https://www.pinecone.io/)
[![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)](https://www.selenium.dev/)
[![Tavily](https://img.shields.io/badge/Tavily-5A67D8?style=for-the-badge&logoColor=white)](https://www.tavily.com/)
[![LangChain](https://img.shields.io/badge/LangChain-2B6CB0?style=for-the-badge&logoColor=white)](https://www.langchain.dev/)



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
├── .env                  # Environment variables file
├── .github/              # GitHub configuration
│   └── workflows/        # GitHub Actions workflows
│       ├── gcp.yaml      # Workflow for Google Cloud Platform deployment
│       └── test.yml      # Workflow for running tests
├── .gitignore            # Git ignore file
├── airflow/              # Airflow configuration and DAGs
│   ├── .env              # Airflow environment variables
│   ├── Dockerfile        # Airflow Docker configuration
│   ├── config/           # Airflow configuration files
│   ├── dags/             # Airflow DAG definitions
│   │   └── job_scraping_dag.py  # DAG for job scraping
│   ├── docker-compose.yml  # Airflow Docker Compose configuration
│   ├── logs/             # Airflow logs
│   ├── plugins/          # Airflow plugins
│   └── requirements.txt  # Airflow Python dependencies
├── backend/              # Backend code
│   ├── __init__.py       # Python package initialization
│   ├── cover/            # Cover letter generation functionality
│   ├── deploy/           # Deployment-related code
│   ├── docker-compose.yml  # Backend Docker Compose configuration
│   ├── Dockerfile        # Backend Docker configuration
│   ├── jobs/             # Job-related functionality
│   │   ├── __init__.py   # Package initialization
│   │   ├── embeddings.py # Job embeddings processing
│   │   ├── job_matching.py  # Job matching algorithm
│   │   └── scraper.py    # Web scraper for jobs
│   ├── main.py           # Main FastAPI application
│   ├── orchestration/    # Workflow orchestration
│   ├── profile_improvement/  # Profile improvement functionality
│   ├── tests/            # Test cases
│   │   ├── README.md     # Test documentation
│   │   ├── test_api.py   # API tests
│   │   ├── test_embeddings.py  # Embeddings tests
│   │   ├── test_github_processor.py  # GitHub processing tests
│   │   ├── test_integration.py  # Integration tests
│   │   ├── test_job_embeddings.py  # Job embeddings tests
│   │   ├── test_match_visualization.py  # Match visualization tests
│   │   ├── test_namespace_job_matching.py  # Namespace job matching tests
│   │   ├── test_pinecone_job.py  # Pinecone job tests
│   │   └── test_pinecone_storage.py  # Pinecone storage tests
│   ├── user/             # User-related functionality
│   │   ├── github.py     # GitHub profile processing
│   │   ├── resume.py     # Resume processing
│   │   └── user_embedding.py  # User embedding generation
│   └── web/              # Web-related functionality
├── docker-compose.yml    # Root Docker Compose configuration
├── frontend/             # Frontend code
│   └── app.py            # Streamlit frontend application
├── logs/                 # Application logs
├── plugins/              # Application plugins
└── requirements.txt      # Root Python dependencies
```

---

## 🏗 Architecture Diagram
![image (5)](https://github.com/user-attachments/assets/0b0b046b-5f71-4df2-9556-330ecc64fb70)


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







