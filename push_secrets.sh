#!/bin/bash
set -e

# ---------------------------------------------------------------------------
# push_secrets.sh — Upload local secrets to GCP Secret Manager
#
# Reads GCP config (project ID, region) and file paths from .env.
# No secrets are hardcoded — everything is read from local files at runtime.
# Safe to commit to a public repository.
# ---------------------------------------------------------------------------

# Load GCP config from .env
if [ -f .env ]; then
  export $(grep -v '^#' .env | sed 's/ #.*//' | grep -v '^\s*$' | xargs)
fi

if [ -z "$GCP_PROJECT_ID" ]; then
  echo "ERROR: GCP_PROJECT_ID not set. Add it to your .env file."
  exit 1
fi

# File paths — defaults to conventional locations, .env values override
ENV_FILE=".env"
CREDS_FILE="${GOOGLE_CALENDAR_CRED_FILE_PATH:-google_secret/credentials2.json}"
TOKEN_FILE="${GOOGLE_CALENDAR_TOKEN_FILE_PATH:-google_secret/token.json}"

# Secret names in Secret Manager (must match what the app code expects)
ENV_SECRET="agentic_env"
CREDS_SECRET="google-calendar-creds"
TOKEN_SECRET="google-calendar-token"

# ---------------------------------------------------------------------------

upsert_secret() {
  local secret_name="$1"
  local file_path="$2"

  if ! [ -f "$file_path" ]; then
    echo "  SKIP  $secret_name — file not found: $file_path"
    return
  fi

  if ! gcloud secrets describe "$secret_name" --project="$GCP_PROJECT_ID" &>/dev/null; then
    echo "  CREATE  $secret_name"
    gcloud secrets create "$secret_name" \
      --project="$GCP_PROJECT_ID" \
      --replication-policy="automatic" \
      --quiet
  fi

  echo "  UPLOAD  $secret_name ← $file_path"
  gcloud secrets versions add "$secret_name" \
    --data-file="$file_path" \
    --project="$GCP_PROJECT_ID" \
    --quiet
}

# ---------------------------------------------------------------------------

echo "=== Pushing secrets to GCP Secret Manager ==="
echo "Project: $GCP_PROJECT_ID"
echo ""

upsert_secret "$ENV_SECRET"    "$ENV_FILE"
upsert_secret "$CREDS_SECRET"  "$CREDS_FILE"
upsert_secret "$TOKEN_SECRET"  "$TOKEN_FILE"

# ---------------------------------------------------------------------------
# Grant the Cloud Run service account access to all secrets
# ---------------------------------------------------------------------------

PROJECT_NUMBER=$(gcloud projects describe "$GCP_PROJECT_ID" --format="value(projectNumber)")
SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo ""
echo "=== Granting Secret Manager access to Cloud Run service account ==="
echo "Service account: $SA"

for secret in "$ENV_SECRET" "$CREDS_SECRET" "$TOKEN_SECRET"; do
  gcloud secrets add-iam-policy-binding "$secret" \
    --project="$GCP_PROJECT_ID" \
    --member="serviceAccount:${SA}" \
    --role="roles/secretmanager.secretAccessor" \
    --quiet &>/dev/null
  echo "  GRANTED  $secret"
done

echo ""
echo "=== Done! ==="
echo "Secrets are ready. Run ./deploy.sh to deploy with these secrets."
