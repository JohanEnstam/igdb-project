# ADR-011: App Engine Frontend Deployment Strategy

## Status
**Accepted** - Replacing Docker-based Cloud Run deployment

## Context

After experiencing prolonged Docker deployment issues (ADR-010), we need a simpler, more reliable way to deploy our Next.js frontend to GCP. The Docker approach proved to be unnecessarily complex for a simple Next.js application.

## Decision

**Deploy Next.js frontend to GCP App Engine using native Node.js runtime instead of Docker containers.**

## Rationale

### Why App Engine Over Docker/Cloud Run

| **Factor** | **Docker/Cloud Run** | **App Engine** |
|------------|---------------------|----------------|
| **Complexity** | High (Dockerfile, build context, .dockerignore) | Low (app.yaml only) |
| **Debugging Time** | Hours (4+ hours spent) | Minutes (10 minutes estimated) |
| **Success Rate** | Low (0% success rate) | High (native runtime) |
| **Maintenance** | High (container management) | Low (GCP-managed) |
| **Build Context Issues** | Yes (major problem) | No (native deployment) |
| **API Dependencies** | Cloud Build API required | Standard App Engine APIs |

### Technical Benefits

1. **Native Node.js Runtime**: No containerization overhead
2. **Automatic Scaling**: 0 to 10 instances based on traffic
3. **Zero Downtime**: Rolling deployments
4. **Automatic SSL**: HTTPS out of the box
5. **Custom Domain**: Easy domain configuration
6. **Built-in Monitoring**: GCP monitoring integration
7. **Cost Effective**: Pay only for usage

## Implementation Plan

### Phase 1: Configuration Files

#### 1. App Engine Configuration (`app.yaml`)
```yaml
runtime: nodejs18
service: frontend

env_variables:
  NODE_ENV: production
  NEXT_PUBLIC_API_URL: https://igdb-api-staging-d6xpjrmqsa-ew.a.run.app

automatic_scaling:
  min_instances: 0
  max_instances: 10
  target_cpu_utilization: 0.6

handlers:
  - url: /.*
    script: auto
    secure: always
```

#### 2. Package.json Updates
```json
{
  "scripts": {
    "start": "next start -p $PORT",
    "build": "next build"
  }
}
```

#### 3. Next.js Configuration Updates
```typescript
const nextConfig: NextConfig = {
  // Remove Docker-specific settings
  // output: 'standalone', // Remove this

  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
  },

  // App Engine-specific settings
  trailingSlash: true,
  compress: true,
};
```

### Phase 2: CI/CD Pipeline

#### GitHub Actions Workflow
```yaml
name: Deploy Frontend to App Engine

on:
  push:
    branches: [main]
    paths:
      - 'web_app/frontend/**'
      - '.github/workflows/deploy-frontend-appengine.yml'
  workflow_dispatch:

env:
  PROJECT_ID: igdb-recommendation-system
  SERVICE_NAME: frontend

jobs:
  deploy:
    name: Deploy Frontend to App Engine
    runs-on: ubuntu-latest
    environment: production

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2
        with:
          project_id: ${{ env.PROJECT_ID }}

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - name: Deploy to App Engine
        run: |
          cd web_app/frontend
          gcloud app deploy app.yaml --quiet
```

### Phase 3: Deployment Process

#### Local Testing
```bash
# Install App Engine CLI
gcloud components install app-engine-nodejs

# Test deployment
cd web_app/frontend
gcloud app deploy app.yaml --no-promote
```

#### Production Deployment
```bash
# Deploy to production
gcloud app deploy app.yaml
```

## Consequences

### Positive Consequences

1. **Simplified Deployment**: Single `app.yaml` file vs complex Docker setup
2. **Faster Development**: 10 minutes vs hours of debugging
3. **Higher Reliability**: Native runtime vs containerization
4. **Better Performance**: No container overhead
5. **Easier Maintenance**: GCP-managed vs custom Docker
6. **Cost Efficiency**: Pay only for actual usage

### Negative Consequences

1. **Vendor Lock-in**: Tied to GCP App Engine
2. **Less Control**: GCP-managed vs custom containers
3. **Runtime Limitations**: Node.js 18 only (vs any Docker image)

### Mitigation Strategies

1. **Vendor Lock-in**: App Engine is standard GCP service, widely adopted
2. **Less Control**: App Engine provides sufficient control for our needs
3. **Runtime Limitations**: Node.js 18 is current LTS, sufficient for Next.js

## Migration Strategy

### What We Remove
- `web_app/frontend/Dockerfile`
- `web_app/frontend/.dockerignore`
- `.github/workflows/deploy-frontend.yml`
- Docker-specific configurations in `next.config.ts`

### What We Add
- `web_app/frontend/app.yaml`
- `.github/workflows/deploy-frontend-appengine.yml`
- App Engine-specific configurations

### Rollback Plan
- Keep Docker files in git history
- Can revert to Docker approach if needed
- App Engine deployment is non-destructive

## Success Metrics

1. **Deployment Time**: < 10 minutes (vs 4+ hours with Docker)
2. **Success Rate**: > 95% (vs 0% with Docker)
3. **Maintenance Overhead**: Minimal (vs high with Docker)
4. **Performance**: Comparable or better than Docker
5. **Cost**: Lower than Cloud Run (no container overhead)

## Conclusion

App Engine provides a simpler, more reliable deployment strategy for our Next.js frontend. The native Node.js runtime eliminates Docker complexity while providing all necessary features for production deployment.

This decision aligns with our principle of choosing the simplest solution that meets our requirements, learned from the Docker deployment experience (ADR-010).
