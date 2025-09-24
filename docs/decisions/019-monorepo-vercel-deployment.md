# ADR-019: Monorepo Structure with Vercel Frontend Deployment

## Status

Accepted

## Context

The project initially faced deployment challenges when trying to deploy a monorepo (Python + Next.js) to Vercel. The main issues were:

1. **Git Configuration**: `.gitignore` was blocking frontend configuration files
2. **Vercel Configuration**: `vercel.json` was in wrong location and had conflicting properties
3. **File Size Limits**: Large files (node_modules, .terraform, models) were causing deployment failures
4. **Build Context**: Vercel was trying to deploy entire repository instead of just frontend

## Decision

Maintain monorepo structure while fixing deployment configuration:

### **Repository Structure**
```
igdb-project/                    # Monorepo Root
├── data_pipeline/              # Data Pipeline (Factory)
├── web_app/                    # Web Application (Store)
│   ├── api/                   # FastAPI backend
│   └── frontend/              # Next.js frontend (Vercel)
├── shared/                     # Shared utilities
├── infrastructure/            # Terraform/Pulumi for GCP
├── docs/                      # Documentation
├── models/                    # ML model files
├── data/                      # Local data storage
├── vercel.json               # Vercel configuration (in frontend/)
├── .vercelignore             # Vercel file exclusions
└── .gitignore                # Git file exclusions
```

### **Deployment Strategy**
- **Frontend**: Vercel (Next.js) - `web_app/frontend/`
- **Backend**: Google Cloud Run (FastAPI) - `web_app/api/`
- **Data Pipeline**: Google Cloud Run Jobs - `data_pipeline/`
- **Infrastructure**: Terraform - `infrastructure/`

### **Configuration Changes**

#### **Git Configuration**
- Updated `.gitignore` to allow frontend config files
- Added exceptions for `web_app/frontend/package.json`, `tsconfig.json`, etc.
- Maintained exclusions for large files (node_modules, .terraform, venv)

#### **Vercel Configuration**
- Moved `vercel.json` to `web_app/frontend/`
- Simplified configuration to avoid `builds`/`functions` conflicts
- Added `.vercelignore` to exclude large files from deployment

#### **Pre-commit Hooks**
- Updated to allow ML model files (`.pkl`)
- Maintained security checks while allowing necessary files

## Rationale

### **Benefits of Monorepo**
- **Unified Development**: All components in single repository
- **Shared Dependencies**: Common utilities and configurations
- **Atomic Changes**: Related changes across components
- **Simplified CI/CD**: Single pipeline for entire system
- **Context Preservation**: Full system view in IDE

### **Why Not Separate Repositories**
- **Loss of Context**: Developers lose full system view
- **Complexity**: Multiple repositories to manage
- **Deployment Coordination**: Harder to coordinate deployments
- **Shared Code**: Difficult to share utilities between components

### **Deployment Strategy**
- **Vercel for Frontend**: Optimized for Next.js, excellent CDN
- **Cloud Run for Backend**: Scalable, serverless Python runtime
- **Cloud Run Jobs for Pipeline**: Batch processing capabilities
- **Terraform for Infrastructure**: Infrastructure as Code

## Consequences

### **Positive**
- ✅ **Unified Development**: All components in single repository
- ✅ **Successful Deployment**: Frontend deploys to Vercel successfully
- ✅ **Context Preservation**: Full system view maintained
- ✅ **Simplified Management**: Single repository to manage
- ✅ **Atomic Changes**: Related changes can be committed together

### **Negative**
- ❌ **Deployment Complexity**: Requires careful configuration
- ❌ **File Size Management**: Need to exclude large files
- ❌ **Build Context**: Must specify correct root directories

### **Risks**
- **File Size Limits**: Large files could cause deployment failures
- **Configuration Drift**: Multiple configuration files to maintain
- **Build Failures**: Monorepo builds can be more complex

## Implementation

### **Completed**
1. ✅ Fixed `.gitignore` to allow frontend config files
2. ✅ Moved `vercel.json` to `web_app/frontend/`
3. ✅ Added `.vercelignore` to exclude large files
4. ✅ Updated pre-commit hooks to allow ML model files
5. ✅ Successfully deployed frontend to Vercel
6. ✅ Configured OAuth with production URLs

### **Configuration Files**
- **vercel.json**: Located in `web_app/frontend/`
- **.vercelignore**: Excludes large files from deployment
- **.gitignore**: Allows frontend configs, excludes large files
- **.pre-commit-config.yaml**: Allows ML model files

## Monitoring

### **Success Metrics**
- ✅ Frontend deploys successfully to Vercel
- ✅ OAuth authentication works with production URLs
- ✅ Admin panel loads and functions correctly
- ✅ Build process completes without errors
- ✅ Large files properly excluded from deployment

### **Deployment URLs**
- **Frontend**: https://igdb-frontend.vercel.app
- **Admin Panel**: https://igdb-frontend.vercel.app/admin
- **Backend API**: https://igdb-api-d6xpjrmqsa-ew.a.run.app

## Future Considerations

### **Potential Improvements**
- **Git LFS**: Consider Git LFS for large model files
- **Build Optimization**: Optimize build process for faster deployments
- **Monitoring**: Add deployment monitoring and alerts
- **Testing**: Add end-to-end tests for deployment process

### **Alternative Approaches**
- **Microservices**: Could separate into multiple repositories
- **Monorepo Tools**: Could use tools like Lerna or Nx
- **Containerization**: Could use Docker for all deployments

## Conclusion

The monorepo structure with fixed deployment configuration provides the best balance of development efficiency and deployment success. The solution maintains the benefits of unified development while solving the deployment challenges through proper configuration management.
