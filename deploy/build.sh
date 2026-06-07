#!/bin/bash
set -e

# Load environment variables
if [ -f .env ]; then
  export $(grep -v '^#' .env | sed 's/ #.*//' | grep -v '^\s*$' | xargs)
fi

# Validate required vars
if [ -z "$GCP_PROJECT_ID" ] || [ -z "$GCP_REGION" ] || [ -z "$GCP_AR_REPO" ] || [ -z "$GCP_IMAGE_NAME" ]; then
  echo "ERROR: Missing required GCP variables in .env"
  echo "Required: GCP_PROJECT_ID, GCP_REGION, GCP_AR_REPO, GCP_IMAGE_NAME"
  exit 1
fi

IMAGE="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GCP_AR_REPO}/${GCP_IMAGE_NAME}:latest"

echo "=== Building image via Cloud Build ==="
echo "Image: $IMAGE"
echo ""

gcloud builds submit . \
  --tag "$IMAGE" \
  --project "$GCP_PROJECT_ID" \
  --region "$GCP_REGION" \
  --quiet

echo ""
echo "=== Build complete! ==="
echo "Image pushed to: $IMAGE"
echo ""
echo "Next: run ./deploy.sh to deploy this image to Cloud Run"
