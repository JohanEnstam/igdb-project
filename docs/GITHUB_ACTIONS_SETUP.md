# GitHub Actions Setup Guide

## 🎯 **Overview**

This guide explains how to set up GitHub Actions for the IGDB Game Recommendation System CI/CD pipeline.

## 🔧 **Prerequisites**

- GitHub repository with Actions enabled
- GCP project configured (see `GCP_SETUP.md`)
- Service account key created
- Secrets configured in GitHub

## 🔐 **Step 1: Configure GitHub Secrets**

Go to your repository → Settings → Secrets and variables → Actions

### **Required Secrets**

#### **GCP_SA_KEY**
- **Description**: Service account key for GCP access
- **Value**: Entire contents of `github-actions-key.json`
- **Format**: JSON string

#### **IGDB_CLIENT_ID**
- **Description**: IGDB API client ID
- **Value**: Your IGDB API client ID
- **Format**: String

#### **IGDB_CLIENT_SECRET**
- **Description**: IGDB API client secret
- **Value**: Your IGDB API client secret
- **Format**: String

### **Optional Secrets**

#### **CODECOV_TOKEN**
- **Description**: Code coverage reporting token
- **Value**: Token from codecov.io
- **Format**: String

#### **SLACK_WEBHOOK**
- **Description**: Slack notifications webhook URL
- **Value**: Slack webhook URL
- **Format**: URL

## 🚀 **Step 2: Enable GitHub Actions**

### **Check Actions are Enabled**
1. Go to repository Settings
2. Navigate to Actions → General
3. Ensure "Allow all actions and reusable workflows" is selected

### **Verify Workflow Files**
Ensure these files exist in `.github/workflows/`:
- `ci.yml` - Continuous Integration
- `deploy.yml` - Continuous Deployment
- `test.yml` - Comprehensive Testing

## 🧪 **Step 3: Test the Pipeline**

### **Test CI Pipeline**
1. Make a small change to any file
2. Commit and push to `main` branch
3. Go to Actions tab in GitHub
4. Verify CI pipeline runs successfully

### **Test CD Pipeline**
1. Push to `main` branch
2. Check Actions tab for deployment
3. Verify services are deployed to GCP

### **Test Manual Deployment**
1. Go to Actions tab
2. Select "CD Pipeline" workflow
3. Click "Run workflow"
4. Select environment (staging/production)
5. Click "Run workflow"

## 🔍 **Step 4: Monitor Workflows**

### **View Workflow Runs**
- Go to Actions tab in GitHub
- Click on any workflow run
- View detailed logs and status

### **Check Deployment Status**
```bash
# Check deployed services
gcloud run services list --region=europe-west1

# View service logs
gcloud run services logs igdb-ingestion-staging --region=europe-west1
```

## 🐛 **Troubleshooting**

### **Common Issues**

#### **Authentication Errors**
```
Error: gcloud auth failed
```
**Solution**: Verify `GCP_SA_KEY` secret is correctly set

#### **Permission Denied**
```
Error: Permission denied on GCP
```
**Solution**: Check service account permissions in GCP

#### **Docker Push Failures**
```
Error: Failed to push to GCR
```
**Solution**: Verify Container Registry is enabled

#### **Secret Access Issues**
```
Error: Secret not found
```
**Solution**: Check secret names match exactly

### **Debug Steps**

1. **Check Workflow Logs**
   - Go to Actions tab
   - Click on failed workflow
   - Review error messages

2. **Verify Secrets**
   - Go to Settings → Secrets
   - Ensure all required secrets are set

3. **Test GCP Access**
   ```bash
   # Test service account
   gcloud auth activate-service-account --key-file=github-actions-key.json
   gcloud projects list
   ```

4. **Check GCP Services**
   ```bash
   # Verify APIs are enabled
   gcloud services list --enabled
   ```

## 📊 **Workflow Status**

### **CI Pipeline Status**
- ✅ **Test**: Unit tests, linting, coverage
- ✅ **Build**: Docker image building
- ✅ **Security**: Vulnerability scanning

### **CD Pipeline Status**
- ✅ **Deploy Staging**: Automatic deployment
- ✅ **Deploy Production**: Manual deployment
- ✅ **Integration Tests**: End-to-end testing

### **Test Pipeline Status**
- ✅ **Unit Tests**: Comprehensive testing
- ✅ **Integration Tests**: Mock service testing
- ✅ **Docker Tests**: Container testing
- ✅ **Performance Tests**: Benchmark testing
- ✅ **Security Tests**: Security scanning

## 🔄 **Workflow Triggers**

### **CI Pipeline**
- **Push**: Any push to `main` or `develop`
- **Pull Request**: Any PR to `main` or `develop`

### **CD Pipeline**
- **Push**: Push to `main` branch
- **Manual**: Workflow dispatch with environment selection

### **Test Pipeline**
- **Push**: Any push to `main` or `develop`
- **Pull Request**: Any PR to `main` or `develop`
- **Schedule**: Daily at 2 AM UTC

## 🎯 **Best Practices**

### **Branch Strategy**
- **main**: Production-ready code
- **develop**: Integration branch
- **feature/***: Feature development
- **hotfix/***: Critical fixes

### **Commit Messages**
- Use conventional commits format
- Include scope and description
- Reference issues when applicable

### **Pull Requests**
- Include description of changes
- Reference related issues
- Ensure all checks pass
- Request review from team members

## 📈 **Performance Optimization**

### **Build Optimization**
- Use Docker layer caching
- Parallel build strategies
- Optimize Dockerfile layers

### **Test Optimization**
- Run tests in parallel
- Cache dependencies
- Use test matrices

### **Deployment Optimization**
- Use blue-green deployments
- Implement health checks
- Monitor deployment metrics

## 🔒 **Security Considerations**

### **Secrets Management**
- Never commit secrets to code
- Use GitHub Secrets for sensitive data
- Rotate secrets regularly

### **Access Control**
- Use least privilege principle
- Regular access reviews
- Monitor access logs

### **Security Scanning**
- Regular vulnerability scans
- Dependency updates
- Security policy enforcement

## 📚 **References**

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Google Cloud Actions](https://github.com/google-github-actions)
- [Docker Actions](https://github.com/docker/github-actions)
