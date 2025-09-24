# IGDB Deployment Plan - Terraform & Cloud Run Migration

**Status**: ✅ Ready for Implementation
**Last Updated**: 2025-01-23
**Next Review**: 2025-02-23
**Created By**: AI Assistant (Cursor + Grok collaboration)
**Based On**: Existing documentation analysis and lessons learned

## Overview

This document outlines a comprehensive 4-step deployment plan to migrate the IGDB recommendation system from App Engine to Cloud Run using Terraform for Infrastructure as Code. The plan addresses known issues (App Engine "server.js not found", Docker build context problems) and builds upon existing successful components (Cloud Run backend, Docker setup, CI/CD pipeline).

## Context & Background

### Current State (from GCP_CURRENT_STATE.md)
- **Working**: Cloud Run backend (`igdb-api-staging`), Cloud Storage buckets, CI/CD for backend
- **Issues**: Frontend blocked on App Engine, old Docker images consuming 8GB storage
- **Infrastructure**: europe-west1 region, service accounts configured

### Key Problems to Solve
1. **App Engine Frontend Issue**: "server.js not found" error preventing frontend deployment
2. **Docker Build Context**: Resolved via .dockerignore (from LESSONS_LEARNED.md)
3. **Cost Optimization**: Cleanup of old Docker images in Artifact Registry
4. **Infrastructure Management**: Move from manual GCP Console to Terraform IaC

### Success Criteria Framework
Each step includes:
- **Verifiable Success Criteria**: Specific, measurable outcomes
- **Documentation Standards**: Status sections, dates, references (from README.md)
- **Time Limits**: Max 1 hour debugging per issue (from LESSONS_LEARNED.md)
- **Rollback Strategy**: Clear steps if issues arise

---

## Step 1: Setup Terraform Environment

**Duration**: 2-4 hours
**Priority**: Critical (foundation for all other steps)

### Objectives
- Configure Terraform with GCS backend for state management
- Clean up old Docker images from Artifact Registry
- Establish Infrastructure as Code foundation

### Success Criteria
1. **Terraform Initialized**
   - `terraform init` runs without errors
   - GCP provider (~> 5.0) loaded correctly
   - Remote state configured in GCS bucket (`igdb-recommendation-system-tf-state`)
   - Verification: `terraform state list` shows empty state initially

2. **GCP Authentication Working**
   - Service account (`github-actions@igdb-recommendation-system.iam.gserviceaccount.com`) has correct roles
   - Required roles: "Cloud Run Admin", "Storage Admin", "Artifact Registry Writer"
   - Verification: `gcloud auth list` and test deployment of simple bucket

3. **Artifact Registry Cleanup**
   - Old Docker images (>30 days) deleted from:
     - `europe-west1-docker.pkg.dev/igdb-recommendation-system/igdb-repo`
     - `europe-west1-docker.pkg.dev/igdb-recommendation-system/igdb-repo`
   - Verification: Total size <2GB (compared to current 8GB)

4. **Test Resource Deployed**
   - Test bucket (`igdb-recommendation-system-test`) created via `terraform apply`
   - Verification: GCP Console > Cloud Storage shows bucket

5. **Documentation Updated**
   - Terraform section added to DEPLOYMENT.md
   - README.md updated with Terraform reference
   - Verification: Git commit with updates

### Implementation Steps
1. **Install and Initialize Terraform**
   ```bash
   # Install Terraform (if not already installed)
   brew install terraform

   # Create terraform directory structure
   mkdir -p infrastructure/terraform
   cd infrastructure/terraform
   ```

2. **Create main.tf Configuration**
   ```hcl
   terraform {
     required_providers {
       google = {
         source  = "hashicorp/google"
         version = "~> 5.0"
       }
     }
     backend "gcs" {
       bucket  = "igdb-recommendation-system-tf-state"
       prefix  = "terraform/state"
     }
   }

   provider "google" {
     project = "igdb-recommendation-system"
     region  = "europe-west1"
   }
   ```

3. **Initialize and Test**
   ```bash
   terraform init
   terraform plan
   ```

### Documentation Updates
- **DEPLOYMENT.md**: Add Terraform section with status ✅ Working
- **LESSONS_LEARNED.md**: Log any issues encountered
- **ADR**: Create ADR-012 if backend choice differs from plan

### Rollback Strategy
- If state corruption: `terraform force-unlock <lock-id>`
- If provider issues: Downgrade to stable version
- If GCS bucket issues: Use local state temporarily

---

## Step 2: Migrate Frontend to Cloud Run

**Duration**: 4-6 hours
**Priority**: High (unblocks frontend deployment)

### Objectives
- Fix "server.js not found" error by moving from App Engine to Cloud Run
- Implement multi-stage Docker build for production optimization
- Establish frontend-backend integration

### Success Criteria
1. **Docker Build Working**
   - Multi-stage Dockerfile in `web_app/frontend/` builds without errors
   - Container starts and responds on port 8080
   - Verification: `curl http://localhost:8080` returns frontend HTML

2. **Cloud Run Deployment**
   - Terraform deploys `igdb-frontend` to Cloud Run in europe-west1
   - Service is public (`allUsers` has `roles/run.invoker`)
   - Verification: URL shows Next.js UI in browser

3. **Backend Integration**
   - Frontend fetches data from `https://igdb-api-staging-d6xpjrmqsa-ew.a.run.app`
   - Environment variable `BACKEND_URL` configured correctly
   - Verification: Test `/games/{id}/recommendations` via UI

4. **No App Engine Errors**
   - No "server.js not found" errors in Cloud Run logs
   - Verification: `gcloud run services logs igdb-frontend` shows no entrypoint errors

5. **Documentation Updated**
   - DEPLOYMENT.md and FRONTEND_ARCHITECTURE.md updated
   - Verification: Git commit with changes

### Implementation Steps
1. **Update Dockerfile (Multi-stage Build)**
   ```dockerfile
   # Build stage
   FROM node:20 AS builder
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci
   COPY . .
   RUN npm run build

   # Run stage
   FROM node:20-slim
   WORKDIR /app
   RUN addgroup --system appgroup && adduser --system --group appuser
   USER appuser
   COPY --from=builder /app/.next/standalone ./
   COPY --from=builder /app/.next/static ./.next/static
   ENV PORT=8080
   EXPOSE 8080
   CMD ["node", "server.js"]
   ```

2. **Terraform Configuration**
   ```hcl
   resource "google_cloud_run_v2_service" "frontend" {
     name     = "igdb-frontend"
     location = "europe-west1"
     ingress  = "INGRESS_TRAFFIC_ALL"

     template {
       scaling {
         min_instance_count = 0
         max_instance_count = 10
       }
       containers {
         image = "europe-west1-docker.pkg.dev/igdb-recommendation-system/igdb-repo/igdb-frontend:latest"
         ports {
           container_port = 8080
         }
         env {
           name  = "BACKEND_URL"
           value = "https://igdb-api-staging-d6xpjrmqsa-ew.a.run.app"
         }
         resources {
           limits = {
             cpu    = "1"
             memory = "512Mi"
           }
         }
       }
     }
   }

   resource "google_cloud_run_v2_service_iam_member" "public_access" {
     service  = google_cloud_run_v2_service.frontend.name
     location = google_cloud_run_v2_service.frontend.location
     role     = "roles/run.invoker"
     member   = "allUsers"
   }
   ```

### Documentation Updates
- **DEPLOYMENT.md**: Add Frontend Deployment (Cloud Run) section
- **FRONTEND_ARCHITECTURE.md**: Update deployment section
- **LESSONS_LEARNED.md**: Log any cold start or build issues

### Rollback Strategy
- If cold starts: Set `min_instance_count = 1` (increases cost)
- If build issues: Revert to previous Dockerfile
- If integration issues: Check environment variables

---

## Step 3: Backend Improvements and Full Pipeline

**Duration**: 6-8 hours
**Priority**: Medium (enhances existing working backend)

### Objectives
- Containerize pipeline steps (ingestion/processing/training) as Cloud Run Jobs
- Implement scheduled data ingestion via Cloud Scheduler
- Complete ML pipeline automation

### Success Criteria
1. **Pipeline Containers Working**
   - Docker images for ingestion, processing, training build and run locally
   - Verification: `docker run igdb-training:latest` saves model to GCS

2. **Cloud Run Jobs Deployed**
   - Terraform deploys jobs for `igdb-ingestion`, `igdb-processing`, `igdb-training`
   - Verification: `gcloud run jobs execute igdb-training --region europe-west1` runs without errors

3. **Scheduler Working**
   - Cloud Scheduler triggers `igdb-ingestion` daily at 02:00 (Europe/Stockholm)
   - Verification: Cloud Scheduler logs show successful HTTP POST

4. **Data and Models in GCS**
   - Ingestion saves to `gs://igdb-recommendation-system-data`
   - Training saves to `gs://igdb-recommendation-system-models`
   - Verification: Check files in GCS via Console

5. **Documentation Updated**
   - DEPLOYMENT.md and ARCHITECTURE.md updated with jobs/scheduler
   - Verification: Git commit

### Implementation Steps
1. **Update Pipeline Dockerfiles**
   - Use existing Dockerfiles from DOCKER_SETUP.md
   - Add environment variables for GCS bucket names
   - Ensure non-root users and minimal images

2. **Terraform for Jobs and Scheduler**
   ```hcl
   resource "google_cloud_run_v2_job" "training_job" {
     name     = "igdb-training"
     location = "europe-west1"

     template {
       template {
         containers {
           image = "europe-west1-docker.pkg.dev/igdb-recommendation-system/igdb-repo/igdb-training:latest"
           env {
             name  = "MODEL_BUCKET"
             value = "igdb-recommendation-system-models"
           }
         }
       }
     }
   }

   resource "google_cloud_scheduler_job" "ingestion_scheduler" {
     name        = "igdb-ingestion-scheduler"
     description = "Daily IGDB data ingestion"
     schedule    = "0 2 * * *"
     time_zone   = "Europe/Stockholm"
     region      = "europe-west1"

     http_target {
       http_method = "POST"
       uri         = "https://${google_cloud_run_v2_job.ingestion_job.name}-d6xpjrmqsa-ew.a.run.app/execute"
       oidc_token {
         service_account_email = "github-actions@igdb-recommendation-system.iam.gserviceaccount.com"
       }
     }
   }
   ```

### Documentation Updates
- **DEPLOYMENT.md**: Add Pipeline Deployment (Cloud Run Jobs) section
- **ARCHITECTURE.md**: Update pipeline jobs section
- **LESSONS_LEARNED.md**: Log any scheduler or job execution issues

### Rollback Strategy
- If job failures: Check container logs and environment variables
- If scheduler issues: Verify service account permissions
- If data issues: Check GCS bucket permissions

---

## Step 4: CI/CD Integration and Monitoring

**Duration**: 4-6 hours
**Priority**: Medium (enhances existing CI/CD)

### Objectives
- Update GitHub Actions for frontend deployment
- Integrate Terraform into CI/CD pipeline
- Implement monitoring and alerting

### Success Criteria
1. **GitHub Actions Updated**
   - Frontend workflow (`deploy-frontend.yml`) deploys to Cloud Run
   - Terraform steps (init, plan, apply) run on push to main
   - Verification: `gh run list` shows successful run

2. **Monitoring Active**
   - Alert policy for high latency (>1000ms) deployed via Terraform
   - Verification: Cloud Monitoring Console shows policy

3. **Security Intact**
   - Bandit/safety scanning runs in CI/CD without vulnerabilities
   - Verification: Workflow logs show clean security scan

4. **Documentation Updated**
   - DEPLOYMENT.md and CICD_PIPELINE.md updated
   - Verification: Git commit

### Implementation Steps
1. **Update GitHub Actions Workflow**
   ```yaml
   # .github/workflows/deploy-frontend.yml
   name: Deploy Frontend
   on:
     push:
       branches: [main]
       paths: ['web_app/frontend/**']

   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - name: Setup Terraform
           uses: hashicorp/setup-terraform@v2
         - name: Terraform Init
           run: terraform init
         - name: Terraform Plan
           run: terraform plan
         - name: Terraform Apply
           run: terraform apply -auto-approve
   ```

2. **Terraform Monitoring Configuration**
   ```hcl
   resource "google_monitoring_alert_policy" "run_alert" {
     display_name = "Cloud Run Alert"
     combiner     = "OR"
     conditions {
       display_name = "High Latency"
       condition_threshold {
         filter     = "metric.type=\"run.googleapis.com/request/latencies\" AND resource.type=\"cloud_run_revision\""
         duration   = "60s"
         comparison = "COMPARISON_GT"
         threshold_value = 1000
       }
     }
   }
   ```

### Documentation Updates
- **DEPLOYMENT.md**: Add CI/CD and Monitoring section
- **CICD_PIPELINE.md**: Update with Terraform integration
- **LESSONS_LEARNED.md**: Log any workflow or monitoring issues

### Rollback Strategy
- If workflow failures: Check service account keys and permissions
- If monitoring issues: Verify metric names and thresholds
- If security issues: Review scanning configuration

---

## Hybrid Alternative Analysis

### Overview
Based on sys-admin background and cost considerations, a hybrid approach using private servers for compute-intensive tasks (ML training) while keeping data storage and API in GCP could provide 20-40% cost savings.

### Pros
- **Cost Savings**: ~20-40% reduction in compute costs (OpenMetal 2025 pricing)
- **Local Control**: Full control over ML training environment
- **Data Privacy**: Sensitive ML models stay on-premises
- **Performance**: Potentially faster training with dedicated hardware

### Cons
- **Complexity**: Increased infrastructure management
- **Latency**: 50-200ms for data sync between local and GCP
- **Maintenance**: Additional Docker and server maintenance
- **CI/CD**: More complex deployment pipeline

### Implementation Strategy
1. **Phase 1**: Implement pure GCP solution (this plan)
2. **Phase 2**: Evaluate cost and performance after 3 months
3. **Phase 3**: Consider hybrid for ML training if volume grows significantly

### Technical Approach (if implemented)
- Use Cloud VPN to connect private servers to GCP
- Run ingestion locally, sync to GCS buckets
- Keep API and frontend on Cloud Run
- Use Terraform to manage VPN and networking

---

## Risk Assessment and Mitigation

### High-Risk Items
1. **Terraform State Corruption**
   - Risk: State file corruption could break infrastructure
   - Mitigation: Regular state backups, use GCS backend with versioning

2. **Service Account Permissions**
   - Risk: Insufficient permissions causing deployment failures
   - Mitigation: Test permissions early, use principle of least privilege

3. **Docker Build Context Issues**
   - Risk: Large build contexts causing timeouts
   - Mitigation: Use .dockerignore, multi-stage builds

### Medium-Risk Items
1. **Cold Start Performance**
   - Risk: Slow response times for low-traffic services
   - Mitigation: Set appropriate min_instance_count

2. **Cost Overruns**
   - Risk: Unexpected costs from Cloud Run scaling
   - Mitigation: Set resource limits, monitor usage

### Low-Risk Items
1. **Data Loss**
   - Risk: Loss of existing data during migration
   - Mitigation: Backup existing data, test with staging environment

---

## Success Metrics

### Technical Metrics
- **Deployment Success Rate**: >95% successful deployments
- **Response Time**: <500ms average response time
- **Uptime**: >99.9% service availability
- **Build Time**: <10 minutes for full pipeline

### Business Metrics
- **Cost Reduction**: 20-40% reduction in infrastructure costs
- **Development Velocity**: Faster feature deployment
- **Operational Efficiency**: Reduced manual deployment tasks

### Monitoring Metrics
- **Error Rate**: <1% error rate across all services
- **Resource Utilization**: <80% CPU/memory utilization
- **Security**: Zero high-severity vulnerabilities

---

## Next Steps

1. **Review and Approve Plan**: Team review of this deployment plan
2. **Prepare Environment**: Ensure all prerequisites are met
3. **Execute Step 1**: Begin with Terraform setup
4. **Monitor Progress**: Track success criteria for each step
5. **Document Lessons**: Update LESSONS_LEARNED.md throughout process

## References

- [DEPLOYMENT.md](DEPLOYMENT.md) - Current deployment documentation
- [FRONTEND_ARCHITECTURE.md](FRONTEND_ARCHITECTURE.md) - Frontend architecture details
- [LESSONS_LEARNED.md](LESSONS_LEARNED.md) - Previous deployment lessons
- [GCP_CURRENT_STATE.md](GCP_CURRENT_STATE.md) - Current GCP infrastructure
- [DOCKER_SETUP.md](DOCKER_SETUP.md) - Docker configuration details
- [ARCHITECTURE.md](ARCHITECTURE.md) - Overall system architecture
- [CICD_PIPELINE.md](CICD_PIPELINE.md) - CI/CD pipeline documentation

---

**Document Status**: ✅ Ready for Implementation
**Last Updated**: 2025-01-23
**Next Review**: 2025-02-23
**Reviewer**: Development Team
