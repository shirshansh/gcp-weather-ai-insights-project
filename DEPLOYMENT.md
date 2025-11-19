# Deployment Guide — GCP Weather AI Insights Project

This guide provides **step‑by‑step instructions** to deploy the entire system from scratch. It includes infrastructure setup, serverless deployments, backend API deployment, and frontend deployment to GKE.

---

# Steps

[1. Prerequisites](#1-prerequisites)

[2. Clone Repository](#2-clone-repository)

[3. Deploy Infrastructure using Terraform](#3️-deploy-infrastructure-using-terraform)

[4. Deploy Backend API (Cloud Run - Source Deploy) ](#4-deploy-backend-api-cloud-run---source-deploy)

[5. Deploy Frontend (React UI) to GKE](#5️-deploy-frontend-react-ui-to-gke)

[6. Manual Verification Steps](#6️-manual-verification-steps)

---

# 1. Prerequisites

- Make sure **Google Cloud Project** is created with **billing enabled**

- Before deploying, ensure the following tools are installed:

  - **gcloud CLI**
  - **Terraform (v1.0+)**
  - **kubectl**
  - **Docker**

- Enable required GCP APIs:

  ```bash
  gcloud services enable \
    cloudscheduler.googleapis.com \
    cloudfunctions.googleapis.com \
    secretmanager.googleapis.com \
    storage.googleapis.com \
    eventarc.googleapis.com \
    aiplatform.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    compute.googleapis.com \
    container.googleapis.com
  ```

---

# 2. Clone repository

```bash
git clone https://github.com/shirshansh/gcp-weather-ai-insights-project.git

cd gcp-weather-ai-insights-project/infra
```

---

# 3️. Deploy Infrastructure using Terraform

This creates:

- Service accounts with least privilege
- GCS bucket
- Cloud Function (processor)
- Cloud Scheduler
- Secret Manager secret
- Cloud Function (collector)
- Eventarc trigger
- Artifact Registry repo
- GKE cluster
- Supporting IAM

## **Check**

pwd is **infra/**

**If not**, then **GO TO infra/**

## Step 1: Configure variables

- Create `terraform.tfvars`:

  ```hcl
  openweathermap_api_key = <openweather map api key>
  ```

- Edit `variables.tf` as required

## Step 2: Terraform init & apply

```bash
terraform init
terraform plan
terraform apply
```

This:

- Deploys ingestion and processing pipeline
- Creates Google Kubernetes Engine cluster

---

# 4. Deploy Backend API (Cloud Run - Source Deploy)

This API serves the latest processed weather insights.

## Step 1: Go to backend/api/

## Step 2: Deploy using Cloud Run (source-based build):

```bash
gcloud run deploy weather-backend-api \
  --source . \
  --region=<region> \
  --allow-unauthenticated \
  --service-account=<process-service-account>
  --set-env-var="PROJECT_ID=<project id>,GCS_BUCKET_NAME=<gcs bucket name>"
```

The service automatically listens on port **8080**.

## Retrieve Cloud Run URL:

```bash
gcloud run services describe weather-backend-api --region asia-south1 --format='value(status.url)'
```

---

# 5️. Deploy Frontend (React UI) to GKE

The frontend consumes the Cloud Run backend API.

## Step 1: Update Frontend API URL

React app must call the **Cloud Run Backend API URL**

Otherwise, your deployed UI cannot fetch data.

- ### Step 1: Go to frontend/src/apis

- ### Step 2: Open api.js

  **Replace** the line 4 `https://weather-backend-api-737404936819.asia-south1.run.app/weather` with the `<Cloud Run URL>/weather`

## Step 2: Build Docker image

### Go to frontend/

```bash
docker build -t <region>-docker.pkg.dev/<project>/frontend/weather-frontend:v1 .
```

## Step 3: Push image

```bash
docker push <region>-docker.pkg.dev/<project>/frontend/weather-frontend:v1
```

## Step 4: Authenticate with GKE

```bash
gcloud container clusters get-credentials <cluster-name> --region=<region>
```

## Step 5: Apply Kubernetes manifests

```
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Retrieve LoadBalancer IP:

```bash
kubectl get svc weather-frontend-service
```

Open in browser:

```
http://<EXTERNAL-IP>
```

---

# 6️. Manual Verification Steps

These steps validate the pipeline end‑to‑end.

### ✓ Cloud Function 1 — Collector

- Trigger manually: `gcloud scheduler jobs run weather-data-ingestion-job`
- Check bucket: A new file appears under `/raw_weather_data/`

### ✓ Cloud Function 2 — Processor

- After raw file upload → Eventarc triggers Cloud Function 2
- Confirm `/processed_weather_data/` has a new enriched JSON

### ✓ Backend API (Cloud Run)

```bash
curl https://<cloud-run-url>/weather
```

You should receive processed data with `mood` and `summary`.

### ✓ Frontend (GKE)

- Visit the LoadBalancer IP
- Verify table loads insights
- Ensure data refreshes every 30 minutes

---

# Deployment Completed

Your end‑to‑end serverless + AI‑powered + containerized weather insights system is now live!
