# Deploy `auro` on GCP (Cloud Run)

This guide deploys `auro` to Cloud Run using:
- Artifact Registry for images
- Secret Manager for runtime secrets
- Cloud Build for container builds

## 1) Set project and region

```bash
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"
export SERVICE_NAME="auro-api"
gcloud config set project "${GCP_PROJECT_ID}"
```

## 2) Enable required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com
```

## 3) Create secrets (no secrets in repo)

Use either **Option A** (split DB vars) or **Option B** (single DSN).
For hybrid model routing, also create cloud model provider secrets.

### Option A: split DB secrets

```bash
printf '%s' "10.30.0.5" | gcloud secrets create auro-db-host --data-file=- || true
printf '%s' "postgres" | gcloud secrets create auro-db-name --data-file=- || true
printf '%s' "postgres" | gcloud secrets create auro-db-user --data-file=- || true
printf '%s' "replace-with-real-password" | gcloud secrets create auro-db-password --data-file=- || true
printf '%s' "replace-with-cloud-provider-api-key" | gcloud secrets create auro-cloud-llm-api-key --data-file=- || true
printf '%s' "gpt-4.1-mini" | gcloud secrets create auro-cloud-llm-model --data-file=- || true
```

If secret already exists, add a new version:

```bash
printf '%s' "new-value" | gcloud secrets versions add auro-db-password --data-file=-
```

### Option B: single DSN secret

```bash
printf '%s' "postgresql+psycopg://user:password@host:5432/dbname?sslmode=disable" \
  | gcloud secrets create auro-database-url --data-file=- || true
```

## 4) Grant Cloud Run runtime access to secrets

```bash
PROJECT_NUMBER="$(gcloud projects describe "${GCP_PROJECT_ID}" --format='value(projectNumber)')"
RUNTIME_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding "${GCP_PROJECT_ID}" \
  --member="serviceAccount:${RUNTIME_SA}" \
  --role="roles/secretmanager.secretAccessor"
```

If you deploy Cloud Run with a custom service account, grant this role to that account instead.

## 5) Deploy with script

```bash
./scripts/deploy_cloud_run.sh "${GCP_PROJECT_ID}" "${GCP_REGION}" "${SERVICE_NAME}"
```

The script builds the image and deploys with:
- non-secret config via `--set-env-vars`
- DB + cloud model secrets via `--set-secrets`

## 6) Optional: deploy using `DATABASE_URL` secret instead

If you prefer `DATABASE_URL` over split vars, deploy directly:

```bash
IMAGE_URI="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/auro-containers/auro-api:manual-$(date +%Y%m%d-%H%M%S)"

gcloud builds submit --tag "${IMAGE_URI}" .

gcloud run deploy "${SERVICE_NAME}" \
  --region "${GCP_REGION}" \
  --platform managed \
  --image "${IMAGE_URI}" \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars "APP_NAME=auro,APP_ENV=prod,LOG_LEVEL=INFO,API_V1_PREFIX=/api/v1,OLLAMA_BASE_URL=http://localhost:11434,OLLAMA_MODEL=qwen2.5:7b,CLOUD_LLM_BASE_URL=https://api.openai.com,WEB_BUILDER_PRIMARY_PROVIDER=ollama,WEB_BUILDER_FALLBACK_PROVIDER=cloud,WEB_BUILDER_FORCE_CLOUD_FOR_DESIGN=false,REQUEST_TIMEOUT_SECONDS=30" \
  --set-secrets "DATABASE_URL=auro-database-url:latest,CLOUD_LLM_API_KEY=auro-cloud-llm-api-key:latest,CLOUD_LLM_MODEL=auro-cloud-llm-model:latest"
```

## 7) Run database migrations

Run migrations from a trusted environment with network access to your DB:

```bash
alembic upgrade head
```

## 8) Verify deployment and probes

```bash
SERVICE_URL="$(gcloud run services describe "${SERVICE_NAME}" --region "${GCP_REGION}" --format='value(status.url)')"
echo "${SERVICE_URL}"

curl -sS "${SERVICE_URL}/api/v1/health"
curl -sS "${SERVICE_URL}/api/v1/health/live"
curl -sS "${SERVICE_URL}/api/v1/health/ready"
```

Expected:
- `/health` -> basic app status
- `/health/live` -> process liveness (no DB dependency)
- `/health/ready` -> readiness check with DB connectivity (503 when DB unavailable)
