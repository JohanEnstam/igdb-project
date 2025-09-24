# Deployment Guide - IGDB Game Recommendation System

**Datum:** 2025-09-23
**Status:** ✅ Backend Working, ✅ Frontend Working, ✅ Pipeline Working, ✅ CI/CD Complete
**Senast uppdaterad:** 2025-09-23

## 🎯 **Översikt**

Detta dokument beskriver den kompletta deployment-strategin för IGDB Game Recommendation System, inklusive CI/CD pipelines, Docker containerization, och GCP deployment.

> **📋 Detaljerad Implementation Plan**: Se [DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md) för en komplett 4-stegs plan med success-kriterier, Terraform-konfiguration och rollback-strategier.

## 🏗️ **Systemarkitektur**

### **Backend Services**
- **Data Ingestion**: IGDB API data collection
- **Data Processing**: Data cleaning and transformation
- **ML Training**: Model training pipeline
- **API Service**: FastAPI recommendation service

### **Frontend Service**
- **Next.js Application**: React-based user interface
- **Deployment Target**: Cloud Run ✅ **WORKING**
- **URL**: https://igdb-frontend-d6xpjrmqsa-ew.a.run.app

## 🐳 **Docker Containerization**

### **Backend Services** ✅ **WORKING**
```bash
# Build all backend services
docker build -f data_pipeline/ingestion/Dockerfile -t igdb-ingestion:latest .
docker build -f data_pipeline/processing/Dockerfile -t igdb-processing:latest .
docker build -f data_pipeline/training/Dockerfile -t igdb-training:latest .
docker build -f web_app/Dockerfile -t igdb-api:latest .
```

### **Frontend Service** ✅ **WORKING**
```bash
# Frontend Docker (Cloud Run ready)
docker build -f web_app/frontend/Dockerfile -t igdb-frontend:latest .
```

### **Container Registry**
- **Registry**: `europe-west1-docker.pkg.dev/igdb-recommendation-system/igdb-repo/`
- **Images**: Frontend and backend images
- **Tags**: Latest, commit SHA, branch names
- **Status**: ✅ **WORKING**

## 🚀 **GCP Deployment**

### **Infrastructure as Code** ✅ **WORKING**
- **Tool**: Terraform v1.5.7
- **Backend**: GCS bucket (`igdb-recommendation-system-tf-state`)
- **Provider**: Google Cloud Provider v5.45.2
- **Region**: europe-west1
- **Status**: Initialized and tested

#### **Terraform Resources**
- **Artifact Registry**: `igdb-repo` (Docker repository)
- **Cloud Run Frontend**: `igdb-frontend` (public access)
- **Cloud Run Backend**: `igdb-api-staging` (existing)
- **Cloud Run Jobs**: `igdb-ingestion`, `igdb-processing`, `igdb-training`
- **Cloud Scheduler**: `igdb-ingestion-scheduler` (daily data ingestion)
- **Storage Buckets**:
  - `igdb-recommendation-system-data` (processed data)
  - `igdb-recommendation-system-models` (ML models)
  - `igdb-recommendation-system-test` (test bucket)
- **Secret Manager**: IAM bindings for Cloud Run Jobs

### **Backend Deployment** ✅ **WORKING**
- **Service**: Google Cloud Run
- **Region**: europe-west1
- **URL**: https://igdb-api-staging-d6xpjrmqsa-ew.a.run.app
- **Status**: Active and functional
- **Authentication**: Google OAuth2 integration ✅ **IMPLEMENTED**
  - Session-baserad autentisering
  - Skyddade admin endpoints (`/admin/status`)
  - OAuth endpoints: `/login`, `/auth/callback`, `/logout`

### **Frontend Deployment** ✅ **WORKING**
- **Service**: Google Cloud Run
- **Region**: europe-west1
- **URL**: https://igdb-frontend-d6xpjrmqsa-ew.a.run.app
- **Status**: Active and functional
- **Docker Image**: `europe-west1-docker.pkg.dev/igdb-recommendation-system/igdb-repo/igdb-frontend:latest`

### **Pipeline Jobs Deployment** ✅ **WORKING**
- **Service**: Google Cloud Run Jobs
- **Region**: europe-west1
- **Jobs**:
  - `igdb-ingestion` - Data collection from IGDB API
  - `igdb-processing` - Data cleaning and transformation
  - `igdb-training` - ML model training
- **Status**: Active and functional
- **Docker Images**:
  - `europe-west1-docker.pkg.dev/igdb-recommendation-system/igdb-repo/igdb-ingestion:latest`
  - `europe-west1-docker.pkg.dev/igdb-recommendation-system/igdb-repo/igdb-processing:latest`
  - `europe-west1-docker.pkg.dev/igdb-recommendation-system/igdb-repo/igdb-training:latest`

### **Cloud Scheduler** ✅ **WORKING**
- **Service**: Google Cloud Scheduler
- **Job**: `igdb-ingestion-scheduler`
- **Schedule**: Daily at 02:00 Europe/Stockholm (`0 2 * * *`)
- **Target**: Triggers `igdb-ingestion` Cloud Run Job
- **Status**: Active and functional

### **Storage Buckets** ✅ **WORKING**
- **Data Bucket**: `igdb-recommendation-system-data`
- **Models Bucket**: `igdb-recommendation-system-models`
- **Region**: europe-west1
- **Lifecycle Rules**: Auto-delete after 30/90 days
- **Status**: Active and functional

## 🔄 **CI/CD Pipeline**

### **Backend CI/CD** ✅ **WORKING**
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on:
  push:
    branches: [main]
    paths:
      - 'data_pipeline/**'
      - 'web_app/api/**'
      - 'shared/**'
```

**Jobs:**
- **Test**: Unit tests, linting, coverage ✅
- **Build**: Docker image building and pushing ✅
- **Security**: Vulnerability scanning ✅
- **Deploy**: Cloud Run deployment ✅

### **Frontend CI/CD** ❌ **BROKEN**
```yaml
# .github/workflows/deploy-frontend-appengine.yml
name: Deploy Frontend to App Engine
```

**Status**: App Engine deployment fails
**Solution**: Switch to Cloud Run deployment

## 🚨 **Known Issues**

### **App Engine Frontend Deployment**
- **Status**: ❌ **NON-FUNCTIONAL**
- **Error**: `Cannot find module '/workspace/server.js'`
- **Root Cause**: Next.js standalone output structure incompatible with App Engine expectations
- **Impact**: Frontend cannot be deployed via GitHub Actions
- **Workaround**: Manual deployment works locally
- **Solution**: Switch to Cloud Run deployment

### **Docker Build Context Issues (Resolved)**
- **Status**: ✅ **RESOLVED**
- **Issue**: Docker build context problems in CI/CD
- **Solution**: Proper .dockerignore configuration
- **Prevention**: Test CI/CD commands locally first

## 🔧 **Deployment Strategies**

### **Option 1: Cloud Run (Recommended)**
```bash
# Deploy backend to Cloud Run
gcloud run deploy igdb-api --source . --region europe-west1

# Deploy frontend to Cloud Run
gcloud run deploy igdb-frontend --source web_app/frontend --region europe-west1
```

**Benefits:**
- ✅ Proven Docker setup
- ✅ Better control and reliability
- ✅ Consistent with backend deployment
- ✅ Automatic scaling

### **Option 2: Vercel/Netlify (Alternative)**
```bash
# Deploy to Vercel
vercel --prod

# Deploy to Netlify
netlify deploy --prod
```

**Benefits:**
- ✅ Native Next.js hosting
- ✅ Zero configuration
- ✅ Automatic deployments
- ✅ Global CDN

### **Option 3: App Engine (Non-functional)**
```bash
# App Engine deployment (broken)
gcloud app deploy app.yaml
```

**Status**: ❌ **NON-FUNCTIONAL**
**Reason**: Next.js standalone output incompatibility

## 📊 **Environment Management**

### **Staging Environment**
- **Backend**: `igdb-api-staging-d6xpjrmqsa-ew.a.run.app`
- **Frontend**: `igdb-frontend-d6xpjrmqsa-ew.a.run.app` ✅ **WORKING**
- **Trigger**: Automatic on main branch push
- **Resources**: Lower resource limits

### **Production Environment**
- **Backend**: Ready for production deployment
- **Frontend**: ✅ **WORKING** - Cloud Run deployment via GitHub Actions
- **Trigger**: Automatic on main branch push (frontend), Manual (backend)
- **Resources**: Higher resource limits

## 🔄 **CI/CD och Monitoring**

**Status:** ✅ Complete
**Last Updated:** 2025-09-23
**Next Review:** 2025-09-30
**Description:** Komplett CI/CD pipeline med automatisk frontend-deployment, monitoring och alerting implementerat.
**Referenser:** [CICD_PIPELINE.md](CICD_PIPELINE.md), [LESSONS_LEARNED.md](LESSONS_LEARNED.md)

### **GitHub Actions Workflows**
- **Frontend Deployment** (`deploy-frontend.yml`): ✅ **WORKING**
  - Automatisk deployment till Cloud Run på push till `main`
  - Terraform-integration för infrastructure management
  - Docker build och push till Artifact Registry
  - Pipeline job-verifiering efter deployment
- **Backend CI/CD** (`ci.yml`, `deploy.yml`): ✅ **WORKING**
  - Automatisk testing, building och deployment
  - Security scanning med Bandit och Safety
  - Multi-environment support (staging/production)

### **Monitoring och Alerting**
- **Error Alerts**: ✅ **ACTIVE**
  - Frontend Error Alert (5xx responses)
  - API Error Alert (5xx responses)
  - Pipeline Job Failure Alert
- **Latency Alert**: ✅ **PREPARED** (aktiveras när service får trafik)
- **Notification Channels**: Tomma (kan utökas med email/Slack)
- **Terraform Management**: Alla alerts hanterade som Infrastructure as Code

### **Security Scanning**
- **CI/CD Integration**: Bandit och Safety-scanning i alla workflows
- **Artifact Upload**: Säkerhetsrapporter sparas som GitHub artifacts
- **Frontend Scanning**: Säkerhetsscanning för Node.js-dependencies

### **Pipeline Verification**
- **Job Execution**: Automatisk test av `igdb-ingestion` job efter deployment
- **Log Access**: Korrekt gcloud CLI syntax för Cloud Run Jobs logs
- **Status Monitoring**: Verifiering av job completion och execution status

## 🔐 **Security & Secrets**

### **Required Secrets**
- `GCP_SA_KEY`: Service account key for GCP access
- `IGDB_CLIENT_ID`: IGDB API client ID
- `IGDB_CLIENT_SECRET`: IGDB API client secret
- `GOOGLE_CLIENT_ID`: Google OAuth2 client ID (backend auth) ✅ **IMPLEMENTED**
- `GOOGLE_CLIENT_SECRET`: Google OAuth2 client secret (backend auth) ✅ **IMPLEMENTED**
- `SESSION_SECRET_KEY`: Secret key for FastAPI SessionMiddleware ✅ **IMPLEMENTED**

### **OAuth Configuration**
- **Google OAuth Console**: Konfigurerad med både production och development URIs
  - Production: `https://igdb-api-staging-d6xpjrmqsa-ew.a.run.app/auth/callback`
  - Development: `http://localhost:8080/auth/callback`
- **Authorized JavaScript Origins**: Både production och localhost
- **Scopes**: `openid email profile`
- **Session Security**: Säker secret key för session-hantering

### **Security Scanning**
- **Container Scanning**: Trivy vulnerability scanner
- **Code Scanning**: Bandit security linter
- **Dependency Scanning**: Safety vulnerability check

## 📈 **Performance Optimization**

### **Build Optimization**
- **Multi-stage builds**: Reduce image size
- **Layer caching**: Optimize build times
- **Parallel builds**: Build multiple services simultaneously

### **Deployment Optimization**
- **Blue-green deployment**: Zero-downtime deployments
- **Rolling updates**: Gradual service updates
- **Health checks**: Automatic rollback on failures

## 🎯 **Next Steps**

### **Completed Actions** ✅
1. **Step 1**: Terraform Setup and Infrastructure ✅ **COMPLETE**
2. **Step 2**: Frontend Migration to Cloud Run ✅ **COMPLETE**
3. **Step 3**: Backend Improvements and Full Pipeline ✅ **COMPLETE**
4. **Step 4**: CI/CD Integration and Monitoring ✅ **COMPLETE**

### **Optional Improvements**
1. **Monitoring Enhancement**:
   - Aktivera latency alert när frontend får trafik
   - Lägg till email/Slack notification channels
   - Skapa Cloud Monitoring dashboard
2. **Cost Optimization**:
   - Implementera budget alerts
   - Regular cleanup av gamla Docker images
3. **Advanced CI/CD**:
   - Blue-green deployments för zero-downtime
   - Automatic rollbacks på deployment failures
4. **Testing Enhancement**:
   - Comprehensive deployment testing
   - Integration tests för pipeline jobs

## 📚 **References**

- **[DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md)** - Detaljerad 4-stegs implementation plan med Terraform och Cloud Run
- [Lessons Learned](LESSONS_LEARNED.md) - Centralized knowledge base
- [ADR-010: Docker Deployment Lessons](decisions/010-docker-deployment-lessons.md)
- [ADR-011: App Engine Frontend Deployment](decisions/011-app-engine-frontend-deployment.md)
- [GCP Current State](GCP_CURRENT_STATE.md)
- [Frontend Architecture](FRONTEND_ARCHITECTURE.md)

## 🧹 **GCP Resource Cleanup**

**Status:** ✅ Complete
**Last Updated:** 2025-09-23
**Next Review:** 2025-09-30
**Description:** Tog bort överblivna resurser från experimentering. Endast aktiva Cloud Run services, jobs, och buckets kvar.
**Referenser:** [GCP_CURRENT_STATE.md](GCP_CURRENT_STATE.md)

### Cleanup Summary
- **Borttagna Cloud Storage Buckets:**
  - `igdb-recommendation-system-test` (tom test bucket)
  - `igdb-recommendation-system.appspot.com` (tom App Engine bucket)
  - `igdb-recommendation-system_cloudbuild` (gammal Cloud Build artifact)
- **Inaktiverade APIs:**
  - `compute.googleapis.com` (oavsiktligt aktiverad, inga instanser)
- **Terraform State:**
  - Uppdaterat för att reflektera rensad miljö

### Aktiva Resurser (efter cleanup)
- **Cloud Run Services:** `igdb-api-staging`, `igdb-frontend`
- **Cloud Run Jobs:** `igdb-ingestion`, `igdb-processing`, `igdb-training`
- **Cloud Scheduler:** `igdb-ingestion-scheduler`
- **GCS Buckets:** `data`, `models`, `tf-state`
- **Artifact Registry:** `igdb-repo` med aktiva images

## 🔗 **Useful Commands**

### **Local Development**
```bash
# Run backend locally
python -m web_app.api.main

# Run frontend locally
cd web_app/frontend && npm run dev

# Test Docker builds
docker build -t igdb-api:latest .
docker run --rm -p 8080:8080 igdb-api:latest
```

### **Deployment**
```bash
# Deploy backend
gcloud run deploy igdb-api --source . --region europe-west1

# Deploy frontend (when Cloud Run is implemented)
gcloud run deploy igdb-frontend --source web_app/frontend --region europe-west1

# Check deployment status
gcloud run services list --region=europe-west1
```

### **Debugging**
```bash
# Check workflow runs
gh run list

# View workflow logs
gh run view <run-id>

# Check GCP services
gcloud run services list --region=europe-west1

# View service logs
gcloud run services logs <service-name> --region=europe-west1
```

---

**Senast uppdaterad:** 2025-01-23
**Uppdaterad av:** AI Assistant
**Nästa review:** 2025-02-23
