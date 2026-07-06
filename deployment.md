# CityPulse — Google Cloud Deployment Guide

> **Prototype deployment** — single-region, minimal cost, hackathon/demo ready.
> Covers direct `gcloud` CLI deployment and Antigravity/MCP server workflows.

---

## 1. Prerequisites

### Tools Required

| Tool | Version | Purpose |
|------|---------|---------|
| `gcloud` CLI | latest | GCP resource management |
| Docker | 24+ | Container builds |
| Node.js | 22+ | Frontend build |
| Python | 3.12+ | Backend |

### GCP Account Setup

```bash
gcloud auth login
gcloud config set project citypulse-dev
gcloud auth application-default login
```

### Enable Required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  bigquery.googleapis.com \
  secretmanager.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com
```

---

## 2. GCP Resources Overview

```
Project: citypulse-dev
├── Artifact Registry    → Container images (backend + frontend)
├── Secret Manager       → Gemini API key, service credentials
├── Cloud Run            → Backend (FastAPI) + Frontend (Nginx/React)
├── BigQuery             → Civic data warehouse (civic_raw dataset)
├── Cloud Logging        → Structured logs
└── Cloud Monitoring     → Health checks, uptime alerts
```

**Prototype note:** For the demo, BigQuery can be swapped for the local SQLite fallback already built into the repository layer. This avoids provisioning costs during development.

---

## 3. Project Structure Before Deploy

```
AtlasAI/
├── backend/
│   ├── app/                   # FastAPI application
│   │   ├── agents/            # Data, Reasoning, Policy agents
│   │   ├── api/               # REST endpoints (v1)
│   │   ├── core/              # Logging, exceptions
│   │   ├── models/
│   │   ├── repositories/      # Data access layer
│   │   └── services/          # Gemini, scoring, recommendations
│   ├── tests/                 # Unit + integration tests
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/                   # React + TypeScript
│   │   ├── components/        # map, scoring, reasoning, etc.
│   │   ├── pages/             # Ask, Dashboard, Landing, etc.
│   │   ├── services/          # API client
│   │   └── stores/            # Zustand state
│   └── nginx.conf
├── docker/
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── data/
│   ├── datasets/              # Synthetic CSV + GeoJSON (15 zones)
│   └── generate_data.py
├── .gitignore
├── docker-compose.yml         # Local dev only
└── deployment.md              # This file
```

---

## 4. Step-by-Step Deployment

### 4.1 Create GCP Project & Billing

```bash
gcloud projects create citypulse-dev --name="CityPulse Development"
gcloud config set project citypulse-dev
# Link billing account in GCP Console: https://console.cloud.google.com/billing
```

### 4.2 Set Up Artifact Registry

Artifact Registry stores Docker images for Cloud Run.

```bash
gcloud artifacts repositories create citypulse-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="CityPulse container images"

gcloud auth configure-docker us-central1-docker.pkg.dev
```

### 4.3 Store Secrets (Gemini API Key)

CityPulse uses Gemini for NL query parsing. Store the API key securely.

```bash
echo -n "your-gemini-api-key" | gcloud secrets create citypulse-gemini-key \
  --data-file=- \
  --replication-policy=automatic

# Grant Cloud Run service account access
gcloud secrets add-iam-policy-binding citypulse-gemini-key \
  --member="serviceAccount:citypulse-dev-sa@citypulse-dev.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

If you don't have a Gemini API key yet, the backend's Data Agent falls back to keyword-based pattern matching, so the app works without it during prototyping.

### 4.4 Set Up BigQuery (Optional — Prototype Uses SQLite)

If deploying with real BigQuery data:

```bash
# Create dataset
bq mk --dataset citypulse-dev:civic_raw

# Load synthetic data (from data/datasets/)
bq load --autodetect --source_format=CSV \
  citypulse-dev:civic_raw.complaints_311 \
  data/datasets/complaints_311.csv

bq load --autodetect --source_format=CSV \
  citypulse-dev:civic_raw.traffic_incidents \
  data/datasets/traffic_incidents.csv

# Repeat for all datasets...
```

**Prototype fallback:** The current `DataRepository` class auto-detects whether BigQuery is configured. If not, it falls back to SQLite using the embedded CSV data. Set `CITYPULSE_DATA_DIR=./data/datasets` to use SQLite during prototyping.

### 4.5 Create Service Account

```bash
gcloud iam service-accounts create citypulse-dev-sa \
  --display-name="CityPulse Dev Service Account"

# Grant roles
gcloud projects add-iam-policy-binding citypulse-dev \
  --member="serviceAccount:citypulse-dev-sa@citypulse-dev.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataViewer"

gcloud projects add-iam-policy-binding citypulse-dev \
  --member="serviceAccount:citypulse-dev-sa@citypulse-dev.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"

gcloud projects add-iam-policy-binding citypulse-dev \
  --member="serviceAccount:citypulse-dev-sa@citypulse-dev.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 4.6 Create Cloud Run Service YAML

Create `backend/service.yaml`:

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: citypulse-backend
  labels:
    cloud.googleapis.com/location: us-central1
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "3"
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      serviceAccountName: citypulse-dev-sa@citypulse-dev.iam.gserviceaccount.com
      containers:
      - image: us-central1-docker.pkg.dev/citypulse-dev/citypulse-repo/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: CITYPULSE_ENV
          value: "production"
        - name: CITYPULSE_GCP_PROJECT
          value: "citypulse-dev"
        - name: CITYPULSE_BQ_DATASET
          value: "civic_raw"
        - name: CITYPULSE_CORS_ORIGINS
          value: '["https://citypulse-frontend-xxxxx-uc.a.run.app"]'
        - name: CITYPULSE_GEMINI_MODEL
          value: "gemini-2.0-flash"
        - name: CITYPULSE_DATA_DIR
          value: "./data/datasets"
        - name: CITYPULSE_LOG_LEVEL
          value: "INFO"
        - name: CITYPULSE_GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: citypulse-gemini-key
              key: latest
        resources:
          limits:
            cpu: "2"
            memory: "1Gi"
        startupProbe:
          httpGet:
            path: /api/v1/health
          initialDelaySeconds: 5
        livenessProbe:
          httpGet:
            path: /api/v1/health
```

Create `frontend/service.yaml`:

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: citypulse-frontend
  labels:
    cloud.googleapis.com/location: us-central1
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "5"
    spec:
      containerConcurrency: 80
      timeoutSeconds: 60
      containers:
      - image: us-central1-docker.pkg.dev/citypulse-dev/citypulse-repo/frontend:latest
        ports:
        - containerPort: 80
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
        env:
        - name: VITE_API_URL
          value: "https://citypulse-backend-xxxxx-uc.a.run.app"
```

### 4.7 Build & Push Docker Images

```bash
# Build both from project root
# Backend
docker build -t us-central1-docker.pkg.dev/citypulse-dev/citypulse-repo/backend:latest \
  -f docker/Dockerfile.backend .
docker push us-central1-docker.pkg.dev/citypulse-dev/citypulse-repo/backend:latest

# Frontend
docker build -t us-central1-docker.pkg.dev/citypulse-dev/citypulse-repo/frontend:latest \
  -f docker/Dockerfile.frontend ./frontend
docker push us-central1-docker.pkg.dev/citypulse-dev/citypulse-repo/frontend:latest
```

### 4.8 Deploy to Cloud Run

```bash
# Deploy backend
gcloud run deploy citypulse-backend \
  --image=us-central1-docker.pkg.dev/citypulse-dev/citypulse-repo/backend:latest \
  --region=us-central1 \
  --min-instances=1 \
  --max-instances=3 \
  --memory=1Gi \
  --cpu=2 \
  --concurrency=80 \
  --timeout=300 \
  --service-account=citypulse-dev-sa@citypulse-dev.iam.gserviceaccount.com \
  --set-env-vars=^:^CITYPULSE_ENV=production:CITYPULSE_GCP_PROJECT=citypulse-dev:CITYPULSE_DATA_DIR=./data/datasets:CITYPULSE_LOG_LEVEL=INFO \
  --set-secrets=CITYPULSE_GEMINI_API_KEY=citypulse-gemini-key:latest \
  --allow-unauthenticated

# Get backend URL
BACKEND_URL=$(gcloud run services describe citypulse-backend \
  --region=us-central1 --format='value(status.url)')
echo "Backend: $BACKEND_URL"

# Deploy frontend
gcloud run deploy citypulse-frontend \
  --image=us-central1-docker.pkg.dev/citypulse-dev/citypulse-repo/frontend:latest \
  --region=us-central1 \
  --min-instances=1 \
  --max-instances=5 \
  --memory=512Mi \
  --cpu=1 \
  --concurrency=80 \
  --set-env-vars=VITE_API_URL=$BACKEND_URL \
  --allow-unauthenticated

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe citypulse-frontend \
  --region=us-central1 --format='value(status.url)')
echo "Frontend: $FRONTEND_URL"
```

### 4.9 Update CORS

After deployment, update the backend's CORS to allow the frontend URL:

```bash
gcloud run services update citypulse-backend \
  --region=us-central1 \
  --update-env-vars=CITYPULSE_CORS_ORIGINS="[\"$FRONTEND_URL\"]"
```

### 4.10 Verify Deployment

```bash
# Health check
curl "$BACKEND_URL/api/v1/health"

# Recommendation test
curl -X POST "$BACKEND_URL/api/v1/recommend" \
  -H "Content-Type: application/json" \
  -d '{"question":"We have ₹50L for infrastructure — where should it go?","strategy":"balanced","max_results":3}'

# Frontend
echo "Open: $FRONTEND_URL/ask"
```

---

## 5. Antigravity / MCP Server Deployment (Alternative Workflow)

If you use Antigravity with MCP (Model Context Protocol) servers, the deployment flow is:

### 5.1 Configure Antigravity Provider

In your Antigravity workspace, add the GCP provider:

```yaml
# antigravity.yaml — project root
providers:
  gcp:
    project: citypulse-dev
    region: us-central1
    credentials: ${GCP_SA_KEY}

services:
  backend:
    type: cloud-run
    source: ./backend
    dockerfile: ./docker/Dockerfile.backend
    port: 8000
    minInstances: 1
    maxInstances: 3
    memory: 1Gi
    cpu: 2
    env:
      CITYPULSE_ENV: production
      CITYPULSE_GCP_PROJECT: citypulse-dev
      CITYPULSE_LOG_LEVEL: INFO
    secrets:
      - CITYPULSE_GEMINI_API_KEY

  frontend:
    type: cloud-run
    source: ./frontend
    dockerfile: ./docker/Dockerfile.frontend
    port: 80
    minInstances: 1
    maxInstances: 5
    memory: 512Mi
    cpu: 1
    env:
      VITE_API_URL: ${backend.url}
    dependsOn:
      - backend

  bigquery:
    type: bigquery
    datasets:
      - civic_raw
    sources:
      - ./data/datasets/*.csv
```

### 5.2 Deploy via MCP

```bash
# If using Antigravity CLI
antigravity deploy --env production

# Or via MCP server endpoint
curl -X POST http://localhost:ANTIGRAVITY_PORT/mcp/deploy \
  -H "Content-Type: application/json" \
  -d '{"service": "all", "env": "production"}'
```

### 5.3 Antigravity Health Checks

Antigravity automatically sets up Cloud Monitoring alerts:

```bash
antigravity monitor --service citypulse-backend --check /api/v1/health
```

---

## 6. Demo Readiness Checklist

Before demo, verify:

- [ ] Backend deployed at `https://citypulse-backend-xxxxx-uc.a.run.app`
- [ ] Frontend deployed at `https://citypulse-frontend-xxxxx-uc.a.run.app`
- [ ] `GET /api/v1/health` returns `200 OK`
- [ ] `POST /api/v1/recommend` returns ranked zones in < 5 seconds
- [ ] `POST /api/v1/chat` returns meaningful responses
- [ ] `GET /api/v1/zones` lists all 15 zones with stats
- [ ] Frontend loads, Ask page renders, ask question → reasoning trail appears
- [ ] Zone map renders colored polygons
- [ ] Scenario simulator re-ranks zones on weight change
- [ ] Reasonable cold start time (< 3 seconds with min-instances=1)
- [ ] 3 demo scenarios pre-cached and tested

### Demo Scenarios to Pre-test

```
1. "We have ₹50L for infrastructure this quarter — where should it go?"
   → Expect: Ranked zones, visible reasoning trail, bias flags

2. "Which zones need the most safety investment?"
   → Expect: Safety-first ranking, Zone 3 highlighted for accident severity

3. Scenario Simulator: Switch to "Equity Focused"
   → Expect: Zones with high poverty rates rise in ranking
```

---

## 7. Architecture on GCP

```
                          ┌──────────────────────┐
                          │   Cloud CDN (cached   │
                          │   static assets)      │
                          └──────────┬───────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
     ┌────────▼────────┐   ┌────────▼────────┐   ┌─────────▼────────┐
     │  Cloud Run       │   │  Cloud Run       │   │  Looker Studio   │
     │  Frontend        │   │  Backend         │   │  (optional)      │
     │  (Nginx+React)   │   │  (FastAPI+ADK)   │   │                  │
     │  Port: 80        │──▶│  Port: 8000      │   │                  │
     └─────────────────┘   └────────┬─────────┘   └──────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
           ┌────────▼──────┐ ┌──────▼──────┐ ┌──────▼─────────┐
           │  BigQuery      │ │  Secret      │ │  Cloud Logging │
           │  civic_raw     │ │  Manager     │ │  + Monitoring  │
           │  (or SQLite)   │ │  (API keys)  │ │                │
           └───────────────┘ └─────────────┘ └────────────────┘
```

---

## 8. Cost Estimate (Prototype / Demo)

| Resource | Monthly Cost | Notes |
|----------|-------------|-------|
| **Cloud Run Backend** | ~$0 | Min 1 instance, scales to zero when idle |
| **Cloud Run Frontend** | ~$0 | Same |
| **Artifact Registry** | ~$0 | Under free tier (0.5 GB) |
| **BigQuery** | ~$0 | Prototype uses SQLite; BQ with < 1 TB queries |
| **Secret Manager** | ~$0 | Under free tier |
| **Cloud CDN** | ~$0 | Minimal traffic |
| **Total** | **~$0-5/mo** | Hackathon/prototype budget |

---

## 9. Quick Teardown

```bash
# Delete Cloud Run services
gcloud run services delete citypulse-backend --region=us-central1 --quiet
gcloud run services delete citypulse-frontend --region=us-central1 --quiet

# Delete Artifact Registry
gcloud artifacts repositories delete citypulse-repo --location=us-central1 --quiet

# Delete secrets
gcloud secrets delete citypulse-gemini-key --quiet

# Delete service account
gcloud iam service-accounts delete citypulse-dev-sa@citypulse-dev.iam.gserviceaccount.com --quiet

# Delete project (optional)
gcloud projects delete citypulse-dev --quiet
```

---

## 10. Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Cloud Run fails to start | Missing `CITYPULSE_GEMINI_API_KEY` secret | Verify secret exists and SA has access |
| `POST /recommend` returns 500 | BigQuery not configured | Set `CITYPULSE_DATA_DIR=./data/datasets` for SQLite fallback |
| CORS errors from frontend | CORS origins not updated | Run step 4.9 to update backend CORS |
| Cold start > 5 seconds | No min instances | Set `--min-instances=1` |
| Frontend shows blank page | `VITE_API_URL` not set | Update env var to backend URL |
| "quota exceeded" | GCP free tier limits | Check GCP Console → IAM → Quotas |

---

## 11. Post-Hackathon Production Path

When moving from prototype to production:

| Area | Prototype | Production |
|------|-----------|-----------|
| **Data** | SQLite / synthetic | BigQuery with real municipal data |
| **Auth** | None (open access) | Google IAP or OAuth2 |
| **Gemini** | Full Gemini 2.0 Flash (with SQLite fallback) | Gemini 2.0 Flash with BigQuery |
| **Region** | Single (us-central1) | Multi-region with failover |
| **CI/CD** | Manual deploy | Cloud Build pipeline |
| **Cache** | None | Redis / Memorystore |
| **Monitoring** | Basic Cloud Logging | Cloud Trace, custom dashboards, SLOs |
| **Scaling** | 1-5 instances | Auto-scaling with load testing |
