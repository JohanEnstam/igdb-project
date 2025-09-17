# CI/CD Pipeline Documentation

## 🎯 **Overview**

This document describes the complete CI/CD pipeline for the IGDB Game Recommendation System, including GitHub Actions workflows, automated testing, and GCP deployment.

## 🏗️ **Pipeline Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Code Push     │───▶│   GitHub        │───▶│   GCP Cloud     │
│   / PR          │    │   Actions       │    │   Run           │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Local         │    │   Automated     │    │   Production    │
│   Development   │    │   Testing       │    │   Deployment    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔄 **Workflow Overview**

### **1. CI Pipeline** (`.github/workflows/ci.yml`)
**Triggers:** Push to main/develop, Pull requests

**Jobs:**
- **Test**: Unit tests, linting, coverage
- **Build**: Docker image building and pushing
- **Security**: Vulnerability scanning

**Steps:**
1. Checkout code
2. Set up Python environment
3. Install dependencies
4. Run linting (flake8, black, mypy)
5. Run unit tests with coverage
6. Build Docker images for all services
7. Push images to GCR
8. Run security scans

### **2. CD Pipeline** (`.github/workflows/deploy.yml`)
**Triggers:** Push to main, Manual workflow dispatch

**Jobs:**
- **Deploy Staging**: Automatic deployment to staging
- **Deploy Production**: Manual deployment to production

**Steps:**
1. Checkout code
2. Set up GCP CLI
3. Deploy services to Cloud Run
4. Run integration tests
5. Notify deployment status

### **3. Test Pipeline** (`.github/workflows/test.yml`)
**Triggers:** Push, PR, Daily schedule

**Jobs:**
- **Unit Tests**: Comprehensive unit testing
- **Integration Tests**: End-to-end testing
- **Docker Tests**: Container testing
- **Performance Tests**: Benchmark testing
- **Security Tests**: Security scanning

## 🐳 **Docker Integration**

### **Multi-Service Build**
```yaml
strategy:
  matrix:
    service: [ingestion, processing, training]
```

### **Image Tagging Strategy**
- `latest`: Latest build from main branch
- `staging`: Staging environment builds
- `production`: Production environment builds
- `pr-123`: Pull request builds
- `branch-feature`: Feature branch builds

### **Container Registry**
- **Registry**: `gcr.io/igdb-recommendation-system`
- **Images**: `igdb-ingestion`, `igdb-processing`, `igdb-training`

## 🧪 **Testing Strategy**

### **Unit Tests**
- **Framework**: pytest
- **Coverage**: Minimum 80% coverage required
- **Parallel**: Tests run in parallel for speed
- **Reporting**: Coverage reports uploaded to Codecov

### **Integration Tests**
- **Mock Services**: Mock IGDB API for testing
- **Database**: SQLite in-memory for testing
- **End-to-End**: Full pipeline testing

### **Docker Tests**
- **Image Build**: Verify images build successfully
- **Container Start**: Test container startup
- **Health Checks**: Verify health endpoints
- **Command Tests**: Test CLI arguments

### **Performance Tests**
- **Benchmarking**: pytest-benchmark for performance
- **Load Testing**: Simulated load testing
- **Resource Usage**: Memory and CPU monitoring

### **Security Tests**
- **Vulnerability Scanning**: Trivy for container scanning
- **Code Analysis**: Bandit for Python security
- **Dependency Check**: Safety for known vulnerabilities

## 🚀 **Deployment Strategy**

### **Environments**

#### **Staging Environment**
- **Trigger**: Automatic on main branch push
- **Resources**: Lower resource limits
- **URLs**: `*-staging.run.app`
- **Purpose**: Testing and validation

#### **Production Environment**
- **Trigger**: Manual workflow dispatch
- **Resources**: Higher resource limits
- **URLs**: `*.run.app`
- **Purpose**: Live user-facing services

### **Service Configuration**

#### **Data Ingestion Service**
```yaml
memory: 1Gi (staging) / 2Gi (production)
cpu: 1 (staging) / 2 (production)
max-instances: 10 (staging) / 20 (production)
secrets: IGDB_CLIENT_ID, IGDB_CLIENT_SECRET
```

#### **Data Processing Service**
```yaml
memory: 2Gi (staging) / 4Gi (production)
cpu: 2 (staging) / 4 (production)
max-instances: 5 (staging) / 10 (production)
```

#### **ML Training Service**
```yaml
memory: 4Gi (staging) / 8Gi (production)
cpu: 4 (staging) / 8 (production)
max-instances: 3 (staging) / 5 (production)
```

## 🔐 **Security & Secrets**

### **Secrets Management**
- **GitHub Secrets**: Stored in repository settings
- **GCP Secret Manager**: Production secrets
- **Service Account**: Minimal permissions

### **Required Secrets**
- `GCP_SA_KEY`: Service account key for GCP access
- `IGDB_CLIENT_ID`: IGDB API client ID
- `IGDB_CLIENT_SECRET`: IGDB API client secret
- `CODECOV_TOKEN`: Code coverage reporting

### **Security Scanning**
- **Container Scanning**: Trivy vulnerability scanner
- **Code Scanning**: Bandit security linter
- **Dependency Scanning**: Safety vulnerability check
- **SARIF Reports**: Uploaded to GitHub Security tab

## 📊 **Monitoring & Observability**

### **Deployment Monitoring**
- **Status Checks**: Automatic health checks
- **Log Aggregation**: Cloud Logging integration
- **Metrics**: Cloud Monitoring integration
- **Alerts**: Automated alerting on failures

### **Performance Monitoring**
- **Response Times**: Service response time tracking
- **Resource Usage**: CPU and memory monitoring
- **Error Rates**: Error rate tracking
- **Throughput**: Request throughput monitoring

## 🔧 **Local Development**

### **Manual Deployment**
```bash
# Deploy to staging
./scripts/deploy.sh staging

# Deploy to production
./scripts/deploy.sh production

# Check deployment status
gcloud run services list --region=europe-west1
```

### **Testing Locally**
```bash
# Run all tests
make test

# Run specific tests
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/

# Run linting
make lint
```

## 🐛 **Troubleshooting**

### **Common Issues**

#### **Build Failures**
- Check Dockerfile syntax
- Verify base image availability
- Check resource limits

#### **Deployment Failures**
- Verify GCP permissions
- Check service account configuration
- Verify secrets are accessible

#### **Test Failures**
- Check test environment setup
- Verify mock services are running
- Check test data availability

### **Debug Commands**
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

## 📈 **Performance Optimization**

### **Build Optimization**
- **Multi-stage builds**: Reduce image size
- **Layer caching**: Optimize build times
- **Parallel builds**: Build multiple services simultaneously

### **Deployment Optimization**
- **Blue-green deployment**: Zero-downtime deployments
- **Rolling updates**: Gradual service updates
- **Health checks**: Automatic rollback on failures

### **Testing Optimization**
- **Parallel testing**: Run tests in parallel
- **Test caching**: Cache test dependencies
- **Selective testing**: Run only relevant tests

## 🔄 **Pipeline Maintenance**

### **Regular Tasks**
- **Dependency Updates**: Keep dependencies current
- **Security Updates**: Regular security scanning
- **Performance Monitoring**: Monitor pipeline performance
- **Documentation Updates**: Keep documentation current

### **Monitoring Metrics**
- **Build Time**: Track build duration
- **Test Coverage**: Monitor test coverage
- **Deployment Success Rate**: Track deployment success
- **Service Uptime**: Monitor service availability

## 📚 **References**

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Docker Documentation](https://docs.docker.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [Trivy Security Scanner](https://trivy.dev/)
