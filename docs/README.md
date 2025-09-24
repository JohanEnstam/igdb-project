# 📚 IGDB Project Documentation

## 🎯 **Quick Start**
- [📁 Project Structure Guide](overview/PROJECT_STRUCTURE.md) - **START HERE** för projektöversikt
- [📋 Current Status](overview/CURRENT_STATUS.md) - Nuvarande utvecklingsstatus
- [🏗️ Architecture](overview/ARCHITECTURE.md) - Systemarkitektur

## 📚 **Documentation Categories**

### 📋 **Overview** - Projektöversikt
- [📁 Project Structure Guide](overview/PROJECT_STRUCTURE.md) - Komplett projektstruktur
- [📋 Current Status](overview/CURRENT_STATUS.md) - Nuvarande utvecklingsstatus
- [🏗️ Architecture](overview/ARCHITECTURE.md) - Systemarkitektur

### 🏗️ **Architecture** - Arkitektur och Design
- [📊 Data Flow](architecture/DATA_FLOW.md) - Dataflöde genom systemet
- [🎨 Frontend Architecture](architecture/FRONTEND_ARCHITECTURE.md) - Frontend design
- [🤖 ML Workflow](architecture/ML_WORKFLOW.md) - ML pipeline arkitektur

### 🚀 **Deployment** - Deployment och Infrastructure
- [🚀 Deployment Guide](deployment/DEPLOYMENT.md) - Deployment instruktioner
- [📋 Deployment Plan](deployment/DEPLOYMENT_PLAN.md) - Deployment strategi
- [🐳 Docker Setup](deployment/DOCKER_SETUP.md) - Docker konfiguration
- [☁️ GCP Current State](deployment/GCP_CURRENT_STATE.md) - GCP infrastruktur status

### 🔧 **Development** - Utvecklingsguider
- [🌐 Web App Development Plan](development/WEB_APP_DEVELOPMENT_PLAN.md) - Frontend utveckling
- [🔐 OAuth Production Plan](development/OAUTH_PRODUCTION_PLAN.md) - OAuth implementation
- [📚 Lessons Learned](development/LESSONS_LEARNED.md) - Utvecklingslärdomar

### 🔄 **CI/CD** - Automation och Pipeline
- [🔄 CI/CD Pipeline](cicd/CICD_PIPELINE.md) - Continuous Integration/Deployment

### 📋 **Architecture Decisions** - ADRs
- [🔐 Google Auth Implementation](decisions/016-google-auth-implementation.md)
- [🎛️ Control Panel Frontend](decisions/017-kontrollpanel-frontend-implementation.md)
- [🔑 OAuth Implementation Complete](decisions/018-oauth-implementation-complete.md)
- [🚀 Monorepo Vercel Deployment](decisions/019-monorepo-vercel-deployment.md)

## 🚀 **Development Commands**

### **Data Pipeline**
```bash
# Smart data collection
python -m data_pipeline.ingestion.main --smart --limit 100

# Data processing
python -m data_pipeline.processing.main --transform-all

# ML training
python -m data_pipeline.training.main --data data/games_clean.json
```

### **Web Application**
```bash
# Start API
python -m web_app.api.main

# Start frontend
cd web_app/frontend && npm run dev
```

### **Testing**
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=data_pipeline --cov-report=html
```

### **Docker**
```bash
# Build all services
make build

# Start development
make dev

# Run tests
make test
```

## 📞 **Need Help?**

1. **Project overview**: [overview/PROJECT_STRUCTURE.md](overview/PROJECT_STRUCTURE.md)
2. **Architecture questions**: [decisions/](decisions/)
3. **API documentation**: Visit `/docs` endpoint when API is running
4. **Frontend issues**: Check `web_app/frontend/README.md`
5. **Test failures**: Check `tests/README.md`
6. **Data issues**: Check `data/` directory

---

**Last updated**: 2024-09-24
**Status**: ✅ Production Ready
