# Documentation Index - IGDB Game Recommendation System

**Datum:** 2025-01-23
**Status:** ✅ Updated with Cloud Run Jobs pipeline automation
**Senast uppdaterad:** 2025-01-23

## 📚 **Dokumentationsöversikt**

Detta är den centrala dokumentationskatalogen för IGDB Game Recommendation System. Dokumentationen har genomgått en strikt revision och rensning - alla föråldrade och duplicerade dokument har tagits bort.

## 🎯 **Huvuddokument**

### **Systemöversikt**
- **[CURRENT_STATUS.md](CURRENT_STATUS.md)** - Aktuell projektstatus och funktionalitet
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Systemarkitektur och komponenter
- **[DATA_FLOW.md](DATA_FLOW.md)** - Dataflöde och pipeline-arkitektur

### **Deployment & Infrastructure**
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Komplett deployment guide med Cloud Run Jobs
- **[DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md)** - Detaljerad 4-stegs implementation plan med Terraform och Cloud Run
- **[WEB_APP_DEVELOPMENT_PLAN.md](WEB_APP_DEVELOPMENT_PLAN.md)** - Plan för web-applikation och kontrollpanel utveckling
- **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Docker containerization setup
- **[FRONTEND_ARCHITECTURE.md](FRONTEND_ARCHITECTURE.md)** - Frontend arkitektur och deployment
- **[CICD_PIPELINE.md](CICD_PIPELINE.md)** - CI/CD pipeline dokumentation

### **Kunskapsbank**
- **[LESSONS_LEARNED.md](LESSONS_LEARNED.md)** - Centraliserad kunskapsbank för problem och lösningar (NY)
- **[GCP_CURRENT_STATE.md](GCP_CURRENT_STATE.md)** - Aktuell GCP miljöstatus

## 🏗️ **Architecture Decision Records (ADRs)**

Alla beslut dokumenteras i `decisions/` katalogen:

- **[ADR-001: Project Structure](decisions/001-project-structure.md)**
- **[ADR-002: Development Workflow](decisions/002-development-workflow.md)**
- **[ADR-003: Documentation Strategy](decisions/003-documentation-strategy.md)**
- **[ADR-004: ML Strategy](decisions/004-ml-strategy.md)**
- **[ADR-005: Docker Strategy](decisions/005-docker-strategy.md)**
- **[ADR-006: Data Management](decisions/006-data-management.md)**
- **[ADR-007: ML Pipeline Implementation](decisions/007-ml-pipeline-implementation.md)**
- **[ADR-008: Option B Lite Implementation](decisions/008-option-b-lite-implementation.md)**
- **[ADR-009: Frontend Scalability Strategy](decisions/009-frontend-scalability-strategy.md)**
- **[ADR-010: Docker Deployment Lessons](decisions/010-docker-deployment-lessons.md)**
- **[ADR-011: App Engine Frontend Deployment](decisions/011-app-engine-frontend-deployment.md)**

## 🚨 **Kända Problem**

### **App Engine Frontend Deployment**
- **Status**: ❌ **NON-FUNCTIONAL**
- **Error**: `Cannot find module '/workspace/server.js'`
- **Impact**: Frontend kan inte deployas via GitHub Actions
- **Solution**: Switch to Cloud Run deployment
- **Dokumentation**: [LESSONS_LEARNED.md](LESSONS_LEARNED.md)

### **Docker Build Context Issues**
- **Status**: ✅ **RESOLVED**
- **Issue**: Docker build context problems i CI/CD
- **Solution**: Proper .dockerignore configuration
- **Dokumentation**: [ADR-010](decisions/010-docker-deployment-lessons.md)

## 📊 **Dokumentationsstatus**

| Dokument | Status | Senast uppdaterad | Nästa review |
|----------|--------|-------------------|---------------|
| CURRENT_STATUS.md | ✅ Updated | 2025-09-18 | 2025-09-25 |
| ARCHITECTURE.md | ✅ Current | 2025-09-18 | 2025-09-25 |
| DATA_FLOW.md | ✅ Current | 2025-09-18 | 2025-09-25 |
| DEPLOYMENT.md | ✅ Updated | 2025-01-23 | 2025-02-23 |
| DEPLOYMENT_PLAN.md | ✅ New | 2025-01-23 | 2025-02-23 |
| DOCKER_SETUP.md | ✅ Current | 2025-09-18 | 2025-09-25 |
| FRONTEND_ARCHITECTURE.md | ✅ Updated | 2025-09-18 | 2025-09-25 |
| LESSONS_LEARNED.md | ✅ New | 2025-09-18 | 2025-09-25 |
| GCP_CURRENT_STATE.md | ✅ Current | 2025-09-18 | 2025-09-25 |
| CICD_PIPELINE.md | ✅ Updated | 2025-09-18 | 2025-09-25 |
| ML_WORKFLOW.md | ✅ Current | 2025-09-18 | 2025-09-25 |

## 🔄 **Dokumentationsprocess**

### **Uppdateringsschema**
- **Månatlig review**: Alla dokument reviewas månadsvis
- **Status tracking**: Status-sektioner i alla dokument
- **Last updated**: Spåra när dokument senast uppdaterades
- **Next review**: Planera nästa review-datum

### **Nya dokument**
- **Skapa ADR**: För alla arkitekturella beslut
- **Uppdatera index**: Lägg till nya dokument i denna README
- **Referenser**: Lägg till referenser till relevanta dokument
- **Status**: Lägg till status-sektion i alla nya dokument

### **Dokumentationsstandarder**
- **Status-sektioner**: ✅ Working, ❌ Broken, ⚠️ Needs Review
- **Last updated**: Datum när dokument senast uppdaterades
- **Next review**: Nästa planerade review-datum
- **Referenser**: Länkar till relevanta dokument och ADRs

## 🎯 **Snabbstart**

### **För nya utvecklare**
1. **Läs [CURRENT_STATUS.md](CURRENT_STATUS.md)** för projektöversikt
2. **Läs [ARCHITECTURE.md](ARCHITECTURE.md)** för systemförståelse
3. **Läs [DEPLOYMENT.md](DEPLOYMENT.md)** för deployment-strategi
4. **Läs [LESSONS_LEARNED.md](LESSONS_LEARNED.md)** för kända problem

### **För deployment**
1. **Läs [DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md)** för detaljerad implementation plan
2. **Läs [DEPLOYMENT.md](DEPLOYMENT.md)** för deployment guide
3. **Läs [GCP_CURRENT_STATE.md](GCP_CURRENT_STATE.md)** för GCP status
4. **Läs [LESSONS_LEARNED.md](LESSONS_LEARNED.md)** för kända problem

### **För problemlösning**
1. **Läs [LESSONS_LEARNED.md](LESSONS_LEARNED.md)** för centraliserad kunskapsbank
2. **Läs relevanta ADRs** för specifika problem
3. **Läs [GCP_CURRENT_STATE.md](GCP_CURRENT_STATE.md)** för GCP status
4. **Dokumentera nya problem** i LESSONS_LEARNED.md

## 📋 **Dokumentationschecklist**

### **För nya dokument**
- [ ] Lägg till status-sektion
- [ ] Lägg till "Last updated" datum
- [ ] Lägg till "Next review" datum
- [ ] Lägg till referenser till relevanta dokument
- [ ] Uppdatera denna README med nytt dokument

### **För uppdateringar**
- [ ] Uppdatera "Last updated" datum
- [ ] Uppdatera status-sektion om nödvändigt
- [ ] Lägg till referenser till nya dokument
- [ ] Uppdatera denna README om strukturen ändras

### **För månatlig review**
- [ ] Review alla dokument för aktuellhet
- [ ] Uppdatera status-sektioner
- [ ] Planera nästa review-datum
- [ ] Uppdatera denna README

## 🔗 **Användbara länkar**

- **GCP Console**: https://console.cloud.google.com/home/dashboard?project=igdb-recommendation-system
- **Cloud Run**: https://console.cloud.google.com/run?project=igdb-recommendation-system
- **App Engine**: https://console.cloud.google.com/appengine?project=igdb-recommendation-system
- **Storage**: https://console.cloud.google.com/storage/browser?project=igdb-recommendation-system
- **Artifact Registry**: https://console.cloud.google.com/artifacts?project=igdb-recommendation-system

---
