#!/bin/bash

# Set default values
GCP_PROJECT_ID=${GCP_PROJECT_ID:-"skillmatch-ai"}
IMAGE_NAME=${IMAGE_NAME:-"skillmatch-backend"}
REGION=${REGION:-"us-central1"}
SERVICE_NAME=${SERVICE_NAME:-"skillmatch-api"}

# Navigate to the backend directory
cd "$(dirname "$0")/../.."

# Build the Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME -f backend/Dockerfile .

# Tag the Docker image for GCP
echo "Tagging Docker image for GCP..."
docker tag $IMAGE_NAME gcr.io/$GCP_PROJECT_ID/$IMAGE_NAME:latest

# Push the Docker image to GCP Container Registry
echo "Authenticating with GCP..."
gcloud auth configure-docker

echo "Pushing Docker image to GCP Container Registry..."
docker push gcr.io/$GCP_PROJECT_ID/$IMAGE_NAME:latest

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$GCP_PROJECT_ID/$IMAGE_NAME:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID},AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY},AWS_REGION=${AWS_REGION},PINECONE_API_KEY=${PINECONE_API_KEY},OPENAI_API_KEY=${OPENAI_API_KEY}"

# Get the deployed service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo -e "\n\nDeployment complete!"
echo "Service URL: $SERVICE_URL"
echo "Test health endpoint: curl -s $SERVICE_URL/api/health" 