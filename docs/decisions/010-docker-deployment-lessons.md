# ADR-010: Docker Deployment Lessons Learned

## Status
**Superseded** - Replaced by App Engine deployment strategy

## Context
During the frontend deployment phase, we attempted to deploy our Next.js frontend to GCP Cloud Run using Docker. This led to a prolonged debugging process spanning multiple hours and multiple failed attempts.

## Problem Analysis

### Root Cause: Docker Build Context Issues
The primary issue was **Docker build context problems** in GitHub Actions, specifically:

1. **Conflicting .dockerignore files**:
   - Root `.dockerignore` was filtering out `package.json`
   - Frontend-specific `.dockerignore` was excluding critical files
   - When building from root context, both files were considered

2. **Build context size mismatch**:
   - Local builds: ~2.70MB context
   - GitHub Actions: ~63.28kB context
   - Indicated files were being filtered out

3. **COPY instruction mismatch**:
   - Dockerfile expected files in specific locations
   - Build context didn't match expected file structure

### Secondary Issues
- **Cloud Build API was disabled** (discovered late in process)
- **Turbopack compatibility issues** with Docker
- **lightningcss native module problems** with Alpine Linux
- **TypeScript missing in production** after `npm prune --production`

## Lessons Learned

### 1. Docker Complexity for Simple Applications
**Lesson**: Docker adds unnecessary complexity for simple Next.js applications
- **Time spent**: 4+ hours debugging
- **Success rate**: 0% (multiple failed attempts)
- **Alternative**: Native runtime deployment (App Engine) would have taken 10 minutes

### 2. Build Context is Critical
**Lesson**: Docker build context must be carefully managed
- **Problem**: `.dockerignore` files can silently exclude critical files
- **Solution**: Always verify build context size and contents
- **Prevention**: Use explicit paths in COPY instructions

### 3. Environment Differences
**Lesson**: Local Docker builds ≠ CI/CD Docker builds
- **Local**: Works perfectly
- **CI/CD**: Fails due to different build contexts
- **Solution**: Test exact CI/CD commands locally

### 4. API Dependencies
**Lesson**: Always verify required GCP APIs are enabled
- **Missing**: Cloud Build API was disabled
- **Impact**: `gcloud builds submit` commands failed
- **Prevention**: Document and verify all required APIs upfront

## Decision

### Superseded Approach: Docker + Cloud Run
- ❌ **Complexity**: High (Dockerfile, build context, .dockerignore)
- ❌ **Debugging time**: Hours
- ❌ **Success rate**: Low
- ❌ **Maintenance**: High

### New Approach: App Engine
- ✅ **Complexity**: Low (app.yaml only)
- ✅ **Debugging time**: Minutes
- ✅ **Success rate**: High
- ✅ **Maintenance**: Low

## Implementation Notes

### What We Removed
- `web_app/frontend/Dockerfile`
- `web_app/frontend/.dockerignore`
- `.github/workflows/deploy-frontend.yml`
- Docker-specific configurations in `next.config.ts`

### What We Learned
1. **Always start with the simplest solution** (App Engine vs Docker)
2. **Verify build context** before debugging
3. **Test CI/CD commands locally** first
4. **Document all required APIs** upfront
5. **Consider alternatives** when debugging takes too long

## Prevention Strategies

### For Future Deployments
1. **Start with native runtimes** (App Engine, Vercel) before containerization
2. **Document all required APIs** in setup documentation
3. **Test CI/CD workflows locally** before pushing
4. **Set time limits** on debugging (e.g., 1 hour max)
5. **Have fallback plans** ready

### For Docker Projects
1. **Use explicit paths** in COPY instructions
2. **Verify build context** with `docker build --no-cache --progress=plain`
3. **Test exact CI/CD commands** locally
4. **Document .dockerignore** rules clearly
5. **Use multi-stage builds** for production optimization

## Conclusion

While Docker is powerful for complex applications, it adds unnecessary complexity for simple Next.js frontends. The App Engine approach provides:
- **Faster deployment** (10 minutes vs hours)
- **Lower complexity** (app.yaml vs Dockerfile + .dockerignore + build context)
- **Higher success rate** (native runtime vs containerization)
- **Better maintainability** (GCP-managed vs custom Docker)

This experience reinforces the principle: **Choose the simplest solution that meets your requirements.**
