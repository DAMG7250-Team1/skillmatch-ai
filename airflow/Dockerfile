FROM apache/airflow:2.7.1-python3.9

USER root

# Install Chrome and dependencies for Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    chromium \
    chromium-driver \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    xvfb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Install additional dependencies needed for our job pipeline
RUN pip install --no-cache-dir \
    selenium \
    webdriver-manager \
    pinecone-client \
    openai \
    boto3 \
    python-dotenv \
    psycopg2-binary \
    requests \
    pandas

# Create directories for our app
WORKDIR /opt/airflow

# Set environment variables for Chrome
ENV PYTHONPATH=/opt/airflow
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV CHROME_BIN=/usr/bin/chromium 