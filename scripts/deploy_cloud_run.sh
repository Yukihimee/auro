#!/usr/bin/env bash

set -euo pipefail

# Usage:
# scripts/deploy_cloud_run.sh <PROJECT_ID> <REGION> [SERVICE_NAME]
#
# Example:
# scripts/deploy_cloud_run.sh my-project us-central1 auro-api

PROJECT_ID="${1:-gen2-491819}"
REGION="${2:-us-central1}"
SERVICE_NAME="${3:-auro-api}"
REPOSITORY="auro-containers"
IMAGE_NAME="auro-api"
IMAGE_TAG="${IMAGE_TAG:-$(date +%Y%m%d-%H%M%S)}"
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "Enabling required services..."
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  --project "${PROJECT_ID}"

echo "Ensuring Artifact Registry repository exists..."
if ! gcloud artifacts repositories describe "${REPOSITORY}" --location "${REGION}" --project "${PROJECT_ID}" >/dev/null 2>&1; then
  gcloud artifacts repositories create "${REPOSITORY}" \
    --repository-format docker \
    --location "${REGION}" \
    --description "Container images for auro" \
    --project "${PROJECT_ID}"
fi

echo "Submitting container build..."
gcloud builds submit \
  --project "${PROJECT_ID}" \
  --tag "${IMAGE_URI}" \
  .

echo "Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --platform managed \
  --image "${IMAGE_URI}" \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars "APP_NAME=auro,APP_ENV=prod,LOG_LEVEL=INFO,API_V1_PREFIX=/api/v1,DB_PORT=5432,DB_SSL_MODE=disable,OLLAMA_BASE_URL=http://localhost:11434,OLLAMA_MODEL=qwen2.5:7b,CLOUD_LLM_BASE_URL=https://generativelanguage.googleapis.com,WEB_BUILDER_PRIMARY_PROVIDER=ollama,WEB_BUILDER_FALLBACK_PROVIDER=cloud,WEB_BUILDER_FORCE_CLOUD_FOR_DESIGN=false,STITCH_MCP_URL=https://your-stitch-mcp-endpoint.example.com,CALENDAR_MCP_URL=https://your-calendar-mcp.example.com,REQUEST_TIMEOUT_SECONDS=30" \
  --set-secrets "DB_HOST=auro-db-host:latest,DB_NAME=auro-db-name:latest,DB_USER=auro-db-user:latest,DB_PASSWORD=auro-db-password:latest,CLOUD_LLM_API_KEY=auro-cloud-llm-api-key:latest,CLOUD_LLM_MODEL=auro-cloud-llm-model:latest,STITCH_MCP_API_KEY=auro-stitch-mcp-api-key:latest,CALENDAR_MCP_API_KEY=auro-calendar-mcp-api-key:latest"

echo "Deployed ${SERVICE_NAME} using image ${IMAGE_URI}"
echo "Remember to run migrations from a trusted environment:"
echo "  alembic upgrade head"
