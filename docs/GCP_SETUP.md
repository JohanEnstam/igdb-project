# GCP Setup Guide - CI/CD Pipeline

## 🎯 **Overview**

This guide explains how to set up Google Cloud Platform for the IGDB Game Recommendation System CI/CD pipeline.

## 🔧 **Prerequisites**

- GCP project: `igdb-recommendation-system`
- gcloud CLI installed and authenticated
- Docker installed
- GitHub repository with Actions enabled

## 🚀 **Step 1: Enable Required APIs**

```bash
# Enable necessary APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

## 🔐 **Step 2: Create Service Account**

```bash
# Create service account for CI/CD
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Service Account" \
  --description="Service account for GitHub Actions CI/CD pipeline"

# Grant necessary permissions
gcloud projects add-iam-policy-binding igdb-recommendation-system \
  --member="serviceAccount:github-actions@igdb-recommendation-system.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding igdb-recommendation-system \
  --member="serviceAccount:github-actions@igdb-recommendation-system.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding igdb-recommendation-system \
  --member="serviceAccount:github-actions@igdb-recommendation-system.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding igdb-recommendation-system \
  --member="serviceAccount:github-actions@igdb-recommendation-system.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.builder"
```

## 🔑 **Step 3: Create Service Account Key**

```bash
# Create and download service account key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions@igdb-recommendation-system.iam.gserviceaccount.com

# Display the key (copy this to GitHub Secrets)
cat github-actions-key.json
```

## 🔒 **Step 4: Configure GitHub Secrets**

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:

### **Required Secrets**
- `GCP_SA_KEY`: The entire contents of `github-actions-key.json`
- `IGDB_CLIENT_ID`: Your IGDB API client ID
- `IGDB_CLIENT_SECRET`: Your IGDB API client secret  <!-- pragma: allowlist secret -->

### **Optional Secrets**
- `CODECOV_TOKEN`: Code coverage reporting token
- `SLACK_WEBHOOK`: Slack notifications webhook URL

## 🐳 **Step 5: Configure Container Registry**

```bash
# Configure Docker for GCR
gcloud auth configure-docker

# Test Docker push (optional)
docker pull hello-world
docker tag hello-world gcr.io/igdb-recommendation-system/hello-world
docker push gcr.io/igdb-recommendation-system/hello-world
```

## 🧪 **Step 6: Test CI/CD Pipeline**

### **Test Local Deployment**
```bash
# Test deployment script locally
./scripts/deploy.sh staging

# Check deployed services
gcloud run services list --region=europe-west1
```

### **Test GitHub Actions**
1. Push changes to `main` branch
2. Check Actions tab in GitHub
3. Verify all workflows run successfully

## 📊 **Step 7: Monitor Deployment**

### **View Logs**
```bash
# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# View specific service logs
gcloud run services logs igdb-ingestion-staging --region=europe-west1
```

### **Check Service Status**
```bash
# List all services
gcloud run services list --region=europe-west1

# Get service details
gcloud run services describe igdb-ingestion-staging --region=europe-west1
```

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Authentication Errors**
   ```bash
   # Re-authenticate
   gcloud auth login
   gcloud auth application-default login
   ```

2. **Permission Denied**
   ```bash
   # Check service account permissions
   gcloud projects get-iam-policy igdb-recommendation-system
   ```

3. **Docker Push Failures**
   ```bash
   # Reconfigure Docker
   gcloud auth configure-docker
   ```

4. **Secret Access Issues**
   ```bash
   # Test secret access
   gcloud secrets versions access latest --secret="IGDB_CLIENT_ID"  # pragma: allowlist secret
   ```

### **Debug Commands**

```bash
# Check current project
gcloud config get-value project

# Check authentication
gcloud auth list

# Check service account
gcloud iam service-accounts list

# Check secrets
gcloud secrets list
```

## 🚀 **Production Deployment**

### **Manual Production Deployment**
```bash
# Deploy to production
./scripts/deploy.sh production

# Verify deployment
gcloud run services list --region=europe-west1
```

### **Automated Production Deployment**
1. Create a release tag: `git tag v1.0.0`
2. Push tag: `git push origin v1.0.0`
3. GitHub Actions will automatically deploy to production

## 📈 **Monitoring and Alerting**

### **Set up Monitoring**
```bash
# Enable monitoring
gcloud services enable monitoring.googleapis.com

# Create alerting policies (optional)
gcloud alpha monitoring policies create --policy-from-file=alert-policy.yaml
```

### **Set up Logging**
```bash
# View logs in real-time
gcloud logging tail "resource.type=cloud_run_revision"
```

## 🔄 **CI/CD Pipeline Overview**

### **Workflows**
1. **CI Pipeline** (`.github/workflows/ci.yml`)
   - Runs on every push and PR
   - Tests, builds, and scans images
   - Pushes to Container Registry

2. **CD Pipeline** (`.github/workflows/deploy.yml`)
   - Runs on main branch pushes
   - Deploys to staging automatically
   - Supports manual production deployment

3. **Test Pipeline** (`.github/workflows/test.yml`)
   - Comprehensive testing suite
   - Performance and security tests
   - Runs daily and on changes

### **Environments**
- **Staging**: Automatic deployment from main branch
- **Production**: Manual deployment via workflow dispatch

## 📚 **References**

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- [gcloud CLI Reference](https://cloud.google.com/sdk/gcloud/reference)
