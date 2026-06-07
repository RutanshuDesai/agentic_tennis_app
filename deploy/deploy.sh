#!/bin/bash
set -e

# Load environment variables
if [ -f .env ]; then
  export $(grep -v '^#' .env | sed 's/ #.*//' | grep -v '^\s*$' | xargs)
fi

# Validate required vars
if [ -z "$GCP_PROJECT_ID" ] || [ -z "$GCP_REGION" ] || [ -z "$GCP_SERVICE_NAME" ] || [ -z "$GCP_AR_REPO" ] || [ -z "$GCP_IMAGE_NAME" ]; then
  echo "ERROR: Missing required GCP variables in .env"
  echo "Required: GCP_PROJECT_ID, GCP_REGION, GCP_SERVICE_NAME, GCP_AR_REPO, GCP_IMAGE_NAME"
  exit 1
fi

IMAGE="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GCP_AR_REPO}/${GCP_IMAGE_NAME}:latest"

echo "=== Deploying $GCP_SERVICE_NAME to Cloud Run ==="
echo "Image: $IMAGE"
echo ""

gcloud run deploy "$GCP_SERVICE_NAME" \
  --image "$IMAGE" \
  --project "$GCP_PROJECT_ID" \
  --region "$GCP_REGION" \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 1 \
  --port 8080 \
  --timeout 300 \
  --set-secrets="/secrets/.env=agentic_env:latest" \
  --set-env-vars="RUNTIME_ENV=cloud,GCP_PROJECT_ID=$GCP_PROJECT_ID" \
  --quiet

echo ""
echo "=== Deployment complete! ==="
gcloud run services describe "$GCP_SERVICE_NAME" \
  --project "$GCP_PROJECT_ID" \
  --region "$GCP_REGION" \
  --format="value(status.url)"
