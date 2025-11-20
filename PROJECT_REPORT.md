# Project Report

# Table of Contents

- [1. Introduction](#1-introduction)
- [2. System Design Overview](#2-system-design-overview)
- [3. Design Decisions](#3-design-decisions)
- [4. Challenges Faced & How They Were Sovled](#4-challenges-faced--how-they-were-solved)
- [5. Lessons Learned](#5-lessons-learned)
- [6. Final Outcome](#6-final-outcome)
- [7. Conclusion](#7-conclusion)

---

# 1. Introduction

This project involved designing and deploying a fully serverless, event-driven, AI-enhanced microservice architecture on Google Cloud Platform (GCP). The goal was to build an automated weather data pipeline that collects, processes, enriches, and visualizes global weather information, using GCP’s serverless offerings, Vertex AI, and modern DevOps tooling.

Before starting this project, I had zero experience with DevOps, Kubernetes, GCP, CI/CD systems, or large-scale distributed architecture. This project became a complete end-to-end learning journey through real-world cloud engineering.

---

# 2. System Design Overview

The final architecture followed a clean, modular, event-driven pattern:

- ## Data Ingestion & Storage

  Cloud Scheduler triggers **Cloud Function #1** every 30 minutes.

  Function fetches weather data via OpenWeather API.

  Stores raw data in **Google Cloud Storage (GCS)**.

  API keys secured using **Secret Manager**.

- ## Processing & AI Enrichment

  Eventarc detects finalized objects in GCS.

  Sends event to **Cloud Function #2**.

  Function processes raw weather data and uses **Vertex AI Gemini model** to generate:

  - mood/sentiment (“gloomy”, “refreshing”, etc.)

  - descriptive summaries

  Processed results stored back in **GCS**.

- ## Backend API Layer

  **Cloud Run service** exposes the latest processed file.

  Lightweight Flask API.

  Integrated with frontend via REST endpoint.

- ## Frontend UI

  React.js application containerized with Docker.

  Deployed to **GKE Autopilot** using Kubernetes manifests.

  Exposed via **LoadBalancer Service**.

- ## Infrastructure as Code

  **Terraform** used to deploy:

  GCS

  Secret Manager

  Cloud Functions (Gen 2)

  Cloud Scheduler

  IAM Policies

  Service Accounts

  Eventarc triggers

  Artifact Registry

  GKE Cluster

- ## CI/CD Pipeline

  **GitHub Actions workflows**:

  Backend auto-deploys to Cloud Run

  Frontend auto-deploys to GKE

  CI/CD uses a dedicated service account.

---

# 3. Design Decisions

- ## 3.1 Serverless First

  I chose serverless technologies (Cloud Functions, Cloud Run, Eventarc) to:

  - Reduce operational overhead
  - Eliminate server management
  - Ensure automatic scaling
  - Pay only for actual usage

- ## 3.2 Event-Driven Architecture

  Eventarc → Cloud Function → GCS flow ensured:

  - Loose coupling
  - Clean separation of ingestion vs processing
  - Real-time reaction to new data
  - Automatic triggering with no manual scheduler for processing

- ## 3.3 GKE Autopilot for Frontend

  Even though Cloud Run was capable of hosting the frontend, GKE was chosen:

  - To learn Kubernetes fundamentals (Deployments, Services)
  - To practice container orchestration & DevOps workflows
  - To meet project requirements

- ## 3.4 Least Privilege IAM

  Every service account received least required permissions.

  This improved security & followed industry standards.

- ## 3.5 Terraform for reproducibility

  Terraform allowed:

  - Full infrastructure automation
  - Repeatable deployments
  - Version-controlled infra
  - Team collaboration readiness

---

# 4. Challenges Faced & How They Were Solved

- ## 4.1 IAM & Permission Errors

  **Challenge**:

  - Cloud Functions deployment failures
  - Eventarc inability to invoke Cloud Run
  - Cloud Scheduler unauthorized to call Cloud Function
  - Vertex AI “permission denied”
  - Build and Deploy failed during CI/CD

  **Cause**:

  - Missing IAM roles on service accounts

  **Solution**:

  - Deep understanding of GCP IAM
  - Added all the required roles

- ## 4.2 Infinite Retry Loop in Eventarc Trigger

  **Challenge**:

  - Eventarc retried on failure → spammed logs
  - Caused repeated failed calls

  **Solution**:

  - Disabled retry policy
  - Ensured function handled missing/partial data gracefully

- ## 4.3 GKE Auth Plugin Missing in GitHub Actions

  **Challenge**:

  - CI/CD failed:

    ```bash
    exec: executable gke-gcloud-auth-plugin not found
    ```

  **Cause**:

  - GitHub Actions now uses Ubuntu Noble
  - GKE plugin not installed by default

  **Solution**:

  - Installed official Google Cloud APT repo
  - Installed plugin with apt
  - Set `USE_GKE_GCLOUD_AUTH_PLUGIN=True`

- ## 4.4 Kubernetes Ingress Not Working

  **Challenge**:

  - Ingress stuck at “Missing resources”
  - NEG not being created
  - No external IP assigned

  **Cause**:

  - Wrong ingress configuration for Autopilot
  - Unnecessary complexity

  **Solution**:

  - Removed ingress
  - Exposed via Service → LoadBalancer
  - Simplified and achieved requirement reliably

- ## 4.5 High GKE Costs

  **Challenge**:

  - Daily GKE cost unexpectedly high

  **Cause**:

  - LoadBalancer cost
  - Monitoring charges
  - Possibly unused resources

  **Solution**:

  - Cleaned up cluster
  - Optimized resources
  - Verified Autopilot usage

---

# 5. Lessons Learned

- ## 5.1 IAM is crucial

  Most errors were not coding problems, but permission problems.
  I now understand:

  - How IAM works
  - Which roles are required for which services
  - How different APIs interconnect

- ## 5.2 Terraform makes infrastructure predictable

  **Without Terraform**:

  - Hard to track changes
  - Impossible to maintain permissions and triggers

  **With Terraform**:

  - Entire infra is version-controlled
  - Easy to reproduce anywhere

- ## 5.3 Kubernetes is powerful, but complex

  I learned:

  - Deployments, Services, LoadBalancers
  - Pods, replicas
  - Cluster authentication
  - Autopilot vs Standard

- ## 5.4 CI/CD pipelines are extremely sensitive

  Small mistakes in:

  - service account permissions
  - Kubernetes authentication
  - YAML syntax
  - break the entire pipeline.

  **This taught me careful debugging**.

---

## 6. Final Outcome

By the end of the project, I built a production-grade serverless architecture featuring:

- Least-privilege IAM
- Automated data ingestion
- Secure secrets handling
- Real-time processing pipeline
- AI-enhanced insights
- Fully managed backend API
- Containerized responsive UI
- Terraform-managed infrastructure
- Kubernetes deployment
- CI/CD automation
- Cost-optimized architecture

Compared to where I started, the outcome demonstrates full-stack cloud engineering capability across DevOps, CI/CD, AI, serverless, and Kubernetes.

---

# 7. Conclusion

This project was a complete end-to-end cloud journey.
From initial confusion over IAM errors to deploying a robust automated multi-service architecture, the experience built strong practical skills in:

- Google Cloud
- AI integration
- Serverless
- Microservices
- Terraform
- DevOps
- Kubernetes
- CI/CD

This report demonstrates not just the technical system, but the real-world engineering journey behind successfully building and deploying it.
