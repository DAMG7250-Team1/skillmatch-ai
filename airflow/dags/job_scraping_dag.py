"""
DAG for scraping jobs from JobRight.ai
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# Airflow imports
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago


# Add backend directory to path for imports
sys.path.append('/opt/airflow/backend')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the scraper
try:
    from jobs.scraper import scrape_jobs
    from jobs.embeddings import JobEmbeddingsProcessor
    logger.info("Successfully imported job modules")
except ImportError as e:
    logger.error(f"Error importing job modules: {str(e)}")
    raise

# Define DAG arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create the DAG
dag = DAG(
    'job_scraping',
    default_args=default_args,
    description='Scrape jobs from JobRight.ai',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    catchup=False,
    tags=['scraping', 'jobs'],
)

# Task function for scraping
def run_job_scraper(**kwargs):
    """Run the job scraper"""
    logger.info("Starting job scraper task")
    try:
        success = scrape_jobs()
        if success:
            logger.info("Job scraping completed successfully")
            return "Success"
        else:
            logger.error("Job scraping failed")
            raise Exception("Job scraping failed with False return")
    except Exception as e:
        logger.error(f"Exception in job scraper: {str(e)}")
        raise

# Task function for embeddings
def process_embeddings_task(**kwargs):
    """Task to process job files and create embeddings"""
    try:
        logger.info("Starting embeddings processing task")
        processor = JobEmbeddingsProcessor()
        all_job_files = processor.list_s3_job_files()
        
        if not all_job_files:
            logger.warning("No job files found to process")
            return []
        
        # Get list of already processed files from S3 or create if it doesn't exist
        processed_files = processor.get_processed_files()
        logger.info(f"Found {len(processed_files)} previously processed files")
        
        # Filter to get only new files that haven't been processed before
        new_files = [file_key for file_key in all_job_files if file_key not in processed_files]
        logger.info(f"Found {len(new_files)} new files to process")
        
        if not new_files:
            logger.info("No new files to process")
            return []
            
        results = []
        for file_key in new_files:
            try:
                logger.info(f"Processing file: {file_key}")
                result = processor.process_job_file(file_key)
                results.append(result)
                processed_files.append(file_key)
                logger.info(f"Successfully processed {file_key}")
            except Exception as e:
                logger.error(f"Failed to process {file_key}: {str(e)}")
                continue
        
        # Update the list of processed files in S3
        processor.save_processed_files(processed_files)
        logger.info(f"Completed processing {len(results)} new files")
        return results
    except Exception as e:
        logger.error(f"Error in embeddings processing task: {str(e)}")
        raise

# Define the scraping task
scrape_task = PythonOperator(
    task_id='scrape_jobs',
    python_callable=run_job_scraper,
    dag=dag,
)

# Define the embeddings task
embeddings_task = PythonOperator(
    task_id='create_embeddings',
    python_callable=process_embeddings_task,
    dag=dag,
)

# Set task dependencies - process embeddings after scraping
scrape_task >> embeddings_task 