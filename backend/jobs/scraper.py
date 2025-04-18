import os
import sys
import logging
from datetime import datetime
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, WebDriverException
from selenium.webdriver.chrome.options import Options
 

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

S3_BUCKET = 'skillmatchai'
S3_BASE_PATH = 'jobs/raw_files/'

def save_to_s3(data, filename):
    """
    Save data to S3 bucket
    """
    try:
        # Convert data to JSON string
        json_data = json.dumps(data, ensure_ascii=False)
        
        # Upload to S3
        s3_key = f"{S3_BASE_PATH}{filename}"
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json_data,
            ContentType='application/json'
        )
        
        logger.info(f"Successfully saved data to s3://{S3_BUCKET}/{s3_key}")
        return f"s3://{S3_BUCKET}/{s3_key}"
        
    except ClientError as e:
        logger.error(f"Error saving to S3: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error saving to S3: {str(e)}")
        return None

def scrape_jobs():
    """
    Main function to scrape jobs and save to S3
    """
    driver = None
    try:
        logger.info("Starting job scraping...")
        
        # Initialize Chrome options
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-extensions')
        
        # Connect to Selenium service
        logger.info("Connecting to Selenium Chrome service")
        driver = webdriver.Remote(
            command_executor='http://selenium-chrome:4444/wd/hub',
            options=options
        )
        
        # Set reasonable timeouts
        driver.set_page_load_timeout(60)
        driver.set_script_timeout(60)
        wait = WebDriverWait(driver, 20)
        
        # Navigate to JobRight homepage
        logger.info("Navigating to JobRight.ai homepage")
        driver.get("https://jobright.ai")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Take screenshot for debugging
        driver.save_screenshot("/tmp/jobright_homepage.png")
        logger.info("Saved screenshot of JobRight homepage")
        
        # Click on Sign In button
        logger.info("Looking for Sign In button")
        sign_in_button = None
        selectors = [
            "//span[contains(text(), 'SIGN IN')]",
            "//button[contains(@class, 'sign-in')]",
            "//*[contains(text(), 'SIGN IN') or contains(text(), 'Sign In')]"
        ]
        
        for selector in selectors:
            try:
                sign_in_button = driver.find_element(By.XPATH, selector)
                logger.info(f"Found Sign In button using selector: {selector}")
                break
            except Exception as e:
                logger.warning(f"Selector {selector} failed: {str(e)}")
        
        if not sign_in_button:
            logger.error("Could not find Sign In button")
            driver.quit()
            return False
        
        # Click Sign In
        try:
            sign_in_button.click()
            logger.info("Clicked Sign In button using standard click")
        except:
            try:
                driver.execute_script("arguments[0].click();", sign_in_button)
                logger.info("Clicked Sign In button using JavaScript")
            except Exception as e:
                logger.error(f"Failed to click Sign In button: {str(e)}")
                driver.quit()
                return False
        
        time.sleep(3)
        
        # Check if login form appears
        try:
            email_input = wait.until(EC.presence_of_element_located((By.ID, "basic_email")))
            logger.info("Login form found - Sign In click successful")
        except Exception as e:
            logger.error(f"Login form not found: {str(e)}")
            driver.quit()
            return False
        
        # Enter credentials
        GOOGLE_EMAIL = os.getenv('GOOGLE_EMAIL')
        GOOGLE_PASSWORD = os.getenv('GOOGLE_PASSWORD')
        
        if not GOOGLE_EMAIL or not GOOGLE_PASSWORD:
            logger.error("Google credentials not found in environment variables")
            driver.quit()
            return False
        
        try:
            logger.info("Entering login credentials")
            email_input.clear()
            email_input.send_keys(GOOGLE_EMAIL)
            
            password_input = wait.until(EC.presence_of_element_located((By.ID, "basic_password")))
            password_input.clear()
            password_input.send_keys(GOOGLE_PASSWORD)
            
            # Submit login form
            submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'sign-in-button')]")))
            submit_button.click()
            logger.info("Submitted login form")
            
            # Wait for login to complete
            time.sleep(5)
            
            # Navigate to jobs page
            logger.info("Navigating to jobs page")
            driver.get("https://jobright.ai/jobs/recommend")
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Wait for job listings to load
            time.sleep(5)
            
            # Take screenshot
            driver.save_screenshot("/tmp/jobright_jobs.png")
            logger.info("Saved screenshot of jobs page")
            
            # Scroll to load more jobs
            for i in range(3):
                driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(2)
            
            # Find job elements
            job_elements = []
            selectors = ["index_front__oxzpW", "job-card", "ant-card"]
            
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CLASS_NAME, selector)
                    if elements:
                        job_elements = elements
                        logger.info(f"Found {len(elements)} jobs with selector '{selector}'")
                        break
                except Exception as e:
                    logger.warning(f"Failed to find jobs with selector '{selector}': {str(e)}")
            
            # Process jobs
            job_data = []
            job_count = len(job_elements)
            
            if job_count == 0:
                logger.error("No job elements found on page")
                driver.quit()
                return False
            
            logger.info(f"Processing {job_count} jobs")
            max_jobs = min(3, job_count)  # Process at most 3 jobs for stability
            
            for i in range(max_jobs):
                try:
                    logger.info(f"Processing job {i+1}/{max_jobs}")
                    
                    # Close any open modals
                    try:
                        modals = driver.find_elements(By.CLASS_NAME, "ant-modal-wrap")
                        for modal in modals:
                            if modal.is_displayed():
                                close_button = modal.find_element(By.CLASS_NAME, "ant-modal-close")
                                close_button.click()
                                time.sleep(2)  # Increased wait time
                    except:
                        # Try escape key
                        try:
                            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                            time.sleep(2)  # Increased wait time
                        except:
                            pass
                    
                    # Take a screenshot before clicking
                    driver.save_screenshot(f"/tmp/before_job_{i+1}.png")
                    
                    # Re-fetch job elements if needed
                    if i >= len(job_elements):
                        for selector in selectors:
                            try:
                                elements = driver.find_elements(By.CLASS_NAME, selector)
                                if elements and len(elements) > i:
                                    job_elements = elements
                                    break
                            except:
                                continue
                    
                    if i >= len(job_elements):
                        logger.error(f"Job index {i} out of range (only {len(job_elements)} available)")
                        continue
                    
                    # Click on job with more careful handling
                    job = job_elements[i]
                    try:
                        # Scroll element into view and pause
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job)
                        time.sleep(3)  # Longer pause before clicking
                        
                        try:
                            job.click()
                            logger.info(f"Clicked job {i+1} with standard click")
                        except:
                            driver.execute_script("arguments[0].click();", job)
                            logger.info(f"Clicked job {i+1} with JavaScript click")
                    except Exception as e:
                        logger.error(f"Failed to click job {i+1}: {str(e)}")
                        continue
                    
                    # Wait longer for job details modal
                    time.sleep(5)  # Increased wait time
                    
                    # Take screenshot after clicking
                    driver.save_screenshot(f"/tmp/job_{i+1}_modal.png")
                    
                    # Extract job details
                    job_info = {
                        "Job Title": "Not specified",
                        "Company": "Not specified",
                        "Location": "Not specified",
                        "Skills": []
                    }
                    
                    # Get title with better error handling
                    try:
                        title_elements = driver.find_elements(By.CLASS_NAME, "index_job-title__sStdA")
                        if title_elements:
                            job_info["Job Title"] = title_elements[0].text.strip()
                            logger.info(f"Found job title: {job_info['Job Title']}")
                    except Exception as e:
                        logger.warning(f"Could not extract job title: {str(e)}")
                    
                    # Get company with better error handling
                    try:
                        company_elements = driver.find_elements(By.CSS_SELECTOR, ".index_company-row__vOzgg strong")
                        if company_elements:
                            job_info["Company"] = company_elements[0].text.strip()
                            logger.info(f"Found company: {job_info['Company']}")
                    except Exception as e:
                        logger.warning(f"Could not extract company: {str(e)}")
                    
                    # Get location with better error handling
                    try:
                        location_elements = driver.find_elements(By.XPATH, "//img[@alt='position']/following-sibling::span")
                        if location_elements:
                            job_info["Location"] = location_elements[0].text.strip()
                            logger.info(f"Found location: {job_info['Location']}")
                    except Exception as e:
                        logger.warning(f"Could not extract location: {str(e)}")
                    
                    # Get skills with better error handling
                    try:
                        skill_elements = driver.find_elements(By.CLASS_NAME, "index_qualification-tag__5ZiFf")
                        if skill_elements:
                            job_info["Skills"] = [s.text.strip() for s in skill_elements if s.text.strip()]
                            logger.info(f"Found {len(job_info['Skills'])} skills")
                    except Exception as e:
                        logger.warning(f"Could not extract skills: {str(e)}")
                    
                    # Save the job data immediately after processing
                    if job_info["Job Title"] != "Not specified" or job_info["Company"] != "Not specified":
                        # Add job to data
                        job_data.append(job_info)
                        
                        # Save this job immediately to avoid losing data
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        single_job_filename = f"jobright_job_{i+1}_{timestamp}.json"
                        s3_url = save_to_s3([job_info], single_job_filename)
                        logger.info(f"Saved job {i+1} to S3: {s3_url}")
                    
                    # Close modal carefully
                    try:
                        close_buttons = driver.find_elements(By.CLASS_NAME, "ant-modal-close")
                        for button in close_buttons:
                            if button.is_displayed():
                                driver.execute_script("arguments[0].click();", button)
                                logger.info("Closed modal with JavaScript click")
                                break
                    except:
                        try:
                            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                            logger.info("Attempted to close modal with ESCAPE key")
                        except:
                            pass
                    
                    # Wait longer between jobs
                    time.sleep(5)  # Increased wait time between jobs
                
                except Exception as e:
                    logger.error(f"Error processing job {i+1}: {str(e)}")
                    # Take error screenshot
                    try:
                        driver.save_screenshot(f"/tmp/error_job_{i+1}.png")
                    except:
                        pass
            
            # Save collective results to S3
            if job_data:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"jobright_jobs_{timestamp}.json"
                s3_url = save_to_s3(job_data, filename)
                logger.info(f"Successfully saved all {len(job_data)} jobs to S3: {s3_url}")
                driver.quit()
                return True
            else:
                logger.error("No job data was collected")
                driver.quit()
                return False
            
        except Exception as e:
            logger.error(f"Error during login/scraping: {str(e)}")
            if driver:
                driver.quit()
            return False
    
    except Exception as e:
        logger.error(f"Error during job scraping: {str(e)}")
        if driver:
            try:
                driver.quit()
            except:
                pass
        return False

if __name__ == "__main__":
    success = scrape_jobs()
    if success:
        logger.info("Job scraping task completed successfully")
    else:
        logger.error("Job scraping task failed")
        sys.exit(1)