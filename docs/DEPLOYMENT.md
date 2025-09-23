# Deployment Guide - IGDB Game Recommendation System

**Datum:** 2025-01-23  
**Status:** ✅ Backend Working, ⚠️ Frontend Needs Update  
**Senast uppdaterad:** 2025-01-23

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
- **Deployment Target**: Cloud Run (App Engine non-functional)

## 🐳 **Docker Containerization**

### **Backend Services** ✅ **WORKING**
```bash
# Build all backend services
docker build -f data_pipeline/ingestion/Dockerfile -t igdb-ingestion:latest .
docker build -f data_pipeline/processing/Dockerfile -t igdb-processing:latest .
docker build -f data_pipeline/training/Dockerfile -t igdb-training:latest .
docker build -f web_app/Dockerfile -t igdb-api:latest .
```

### **Frontend Service** ⚠️ **NEEDS UPDATE**
```bash
# Frontend Docker (ready for Cloud Run)
docker build -f web_app/frontend/Dockerfile -t igdb-frontend:latest .
```

### **Container Registry**
- **Registry**: `gcr.io/igdb-recommendation-system/`
- **Images**: Automatically built and pushed on main branch
- **Tags**: Latest, commit SHA, branch names

## 🚀 **GCP Deployment**

### **Infrastructure as Code** ✅ **WORKING**
- **Tool**: Terraform v1.5.7
- **Backend**: GCS bucket (`igdb-recommendation-system-tf-state`)
- **Provider**: Google Cloud Provider v5.45.2
- **Region**: europe-west1
- **Status**: Initialized and tested

### **Backend Deployment** ✅ **WORKING**
- **Service**: Google Cloud Run
- **Region**: europe-west1
- **URL**: https://igdb-api-staging-d6xpjrmqsa-ew.a.run.app
- **Status**: Active and functional

### **Frontend Deployment** ❌ **NON-FUNCTIONAL**
- **Current Target**: App Engine (broken)
- **Error**: `Cannot find module '/workspace/server.js'`
- **Recommended Target**: Cloud Run
- **Status**: Needs implementation

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
- **Frontend**: Not deployed (App Engine broken)
- **Trigger**: Automatic on main branch push
- **Resources**: Lower resource limits

### **Production Environment**
- **Backend**: Ready for production deployment
- **Frontend**: Needs Cloud Run implementation
- **Trigger**: Manual workflow dispatch
- **Resources**: Higher resource limits

## 🔐 **Security & Secrets**

### **Required Secrets**
- `GCP_SA_KEY`: Service account key for GCP access
- `IGDB_CLIENT_ID`: IGDB API client ID
- `IGDB_CLIENT_SECRET`: IGDB API client secret

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

### **Immediate Actions**
1. **Execute Step 2**: Migrate Frontend to Cloud Run (4-6 hours)
2. **Execute Step 3**: Backend Improvements and Full Pipeline (6-8 hours)
3. **Execute Step 4**: CI/CD Integration and Monitoring (4-6 hours)
4. **Follow DEPLOYMENT_PLAN.md**: Detailed implementation guide available

### **Long-term Improvements**
1. **Monitoring**: Implement proper monitoring and alerting
2. **Automation**: Automatic rollbacks on deployment failures
3. **Testing**: Comprehensive deployment testing
4. **Cost Optimization**: Regular cleanup of unnecessary resources

## 📚 **References**

- **[DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md)** - Detaljerad 4-stegs implementation plan med Terraform och Cloud Run
- [Lessons Learned](LESSONS_LEARNED.md) - Centralized knowledge base
- [ADR-010: Docker Deployment Lessons](decisions/010-docker-deployment-lessons.md)
- [ADR-011: App Engine Frontend Deployment](decisions/011-app-engine-frontend-deployment.md)
- [GCP Current State](GCP_CURRENT_STATE.md)
- [Frontend Architecture](FRONTEND_ARCHITECTURE.md)

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
