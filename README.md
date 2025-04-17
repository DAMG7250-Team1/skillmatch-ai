# SkillMatchAI

SkillMatchAI is an advanced job matching platform that uses AI and vector embeddings to connect job seekers with the most relevant job opportunities. The system automatically scrapes job listings, extracts skills, and creates semantic embeddings to provide intelligent job matching.

## Architecture

The platform consists of several key components:

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

## Deployment Options

### Local Development
```bash
# Clone the repository
git clone https://github.com/your-org/skillmatch-ai.git
cd skillmatch-ai

# Create necessary directories
mkdir -p ./logs ./plugins

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials

# Start the services
docker-compose up -d
```

### Production Deployment
The project includes a CI/CD pipeline that automatically deploys to production:

1. Push changes to the main branch
2. GitHub Actions will build, test and deploy to EC2
3. Access the Airflow UI at http://your-ec2-ip:8081

## Environment Variables

The following environment variables are required:
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `AWS_REGION` - AWS region (default: us-east-1)
- `PINECONE_API_KEY` - Pinecone API key
- `OPENAI_API_KEY` - OpenAI API key
- `GOOGLE_EMAIL` - Email for JobRight.ai
- `GOOGLE_PASSWORD` - Password for JobRight.ai

## Airflow DAGs

The project contains the following DAGs:
- `job_scraping` - Scrapes job listings and processes embeddings (runs every 4 hours)

## Access Links

- Frontend: 
- Airflow UI: http://34.139.104.57:8081/home
- Project Video:
- Codelabs: 
- Documentation: 

## Team

TEAM 1 - DAMG7245 Final Project

## License

[MIT License](LICENSE)
