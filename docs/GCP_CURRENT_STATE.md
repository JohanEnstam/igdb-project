# GCP Current State Documentation

**Datum:** 2025-09-23  
**Projekt:** igdb-recommendation-system  
**Projektnummer:** 18815352760  
**Region:** europe-west1 (primär)

## 📊 Översikt

Detta dokument beskriver den aktuella tillståndet av vår Google Cloud Platform miljö efter genomförd städning och inventering. **Uppdaterad efter GCP cleanup 2025-09-23.**

## 🧹 Cleanup av Experimentella Resurser

**Status:** ✅ Complete  
**Last Updated:** 2025-09-23  
**Next Review:** 2025-09-30  
**Description:** Rensade gamla Cloud Storage buckets, inaktiverade Compute Engine API, och uppdaterade Terraform state efter Steg 1-3 implementation.  
**Referenser:** [DEPLOYMENT.md](DEPLOYMENT.md), [LESSONS_LEARNED.md](LESSONS_LEARNED.md)

### Borttagna Resurser
- **Cloud Storage Buckets:**
  - `igdb-recommendation-system-test` (tom test bucket)
  - `igdb-recommendation-system.appspot.com` (tom App Engine bucket)
  - `igdb-recommendation-system_cloudbuild` (gammal Cloud Build artifact)
- **APIs:**
  - `compute.googleapis.com` (oavsiktligt aktiverad, inga instanser)
- **Terraform State:**
  - `google_storage_bucket.test_bucket` (borttagen från state)

## 🏗️ Projekt Information

- **Projektnamn:** igdb-recommendation-system
- **Projektnummer:** 18815352760
- **Skapad:** 2025-09-17T13:36:40.242638Z
- **Status:** ACTIVE
- **Primär region:** europe-west1

## ✅ Aktiverade APIs (32 st)

```
analyticshub.googleapis.com          Analytics Hub API
appengine.googleapis.com             App Engine Admin API
appenginereporting.googleapis.com    App Engine
artifactregistry.googleapis.com      Artifact Registry API
bigquery.googleapis.com              BigQuery API
bigqueryconnection.googleapis.com    BigQuery Connection API
bigquerydatapolicy.googleapis.com    BigQuery Data Policy API
bigquerymigration.googleapis.com    BigQuery Migration API
bigqueryreservation.googleapis.com   BigQuery Reservation API
bigquerystorage.googleapis.com       BigQuery Storage API
cloudapis.googleapis.com             Google Cloud APIs
cloudbuild.googleapis.com            Cloud Build API
cloudresourcemanager.googleapis.com  Cloud Resource Manager API
cloudscheduler.googleapis.com        Cloud Scheduler API
cloudtrace.googleapis.com            Cloud Trace API
containerregistry.googleapis.com     Container Registry API
dataform.googleapis.com              Dataform API
dataplex.googleapis.com              Cloud Dataplex API
datastore.googleapis.com             Cloud Datastore API
iam.googleapis.com                   Identity and Access Management (IAM) API
iamcredentials.googleapis.com        IAM Service Account Credentials API
logging.googleapis.com               Cloud Logging API
monitoring.googleapis.com            Cloud Monitoring API
pubsub.googleapis.com                Cloud Pub/Sub API
run.googleapis.com                   Cloud Run Admin API
secretmanager.googleapis.com         Secret Manager API
servicemanagement.googleapis.com     Service Management API
serviceusage.googleapis.com          Service Usage API
sql-component.googleapis.com         Cloud SQL
storage-api.googleapis.com           Google Cloud Storage JSON API
storage-component.googleapis.com     Cloud Storage
storage.googleapis.com               Cloud Storage API
```

**OBS:** Compute Engine API aktiverades oavsiktligt under inventeringen.

## 🚀 Cloud Run Services

### ✅ Fungerande Services

| Service | Region | URL | Status | Last Deployed |
|---------|--------|-----|--------|---------------|
| igdb-api-staging | europe-west1 | https://igdb-api-staging-d6xpjrmqsa-ew.a.run.app | ✅ Active | 2025-09-18T12:04:15Z |
| igdb-frontend | europe-west1 | https://igdb-frontend-d6xpjrmqsa-ew.a.run.app | ✅ Active | 2025-09-23T10:54:29Z |

## 🏃 Cloud Run Jobs

### ✅ Aktiva Jobs

| Job | Region | Status | Last Run | Created |
|-----|--------|--------|----------|---------|
| igdb-ingestion | europe-west1 | ✅ Active | 2025-09-23T11:20:02Z | 2025-09-23T11:04:51Z |
| igdb-processing | europe-west1 | ✅ Active | - | 2025-09-23T11:04:51Z |
| igdb-training | europe-west1 | ✅ Active | - | 2025-09-23T11:04:51Z |

## ⏰ Cloud Scheduler

### ✅ Aktiva Jobs

| Job | Region | Schedule | Status | Target |
|-----|--------|----------|--------|--------|
| igdb-ingestion-scheduler | europe-west1 | 0 2 * * * (Europe/Stockholm) | ✅ ENABLED | HTTP |

## 🏗️ App Engine

### Aktuell Status
- **Service:** default
- **Versions:** 1 (efter städning)
- **Status:** ❌ Fungerar inte

### Versions
| Version ID | Traffic Split | Status | Problem |
|------------|---------------|--------|---------|
| 20250918t163730 | 1.00 | SERVING | ❌ Service Unavailable - server.js not found |

### Problem
App Engine deployment misslyckas med fel:
```
Error: Cannot find module '/workspace/server.js'
```

**Orsak:** Next.js standalone output struktur är inte kompatibel med App Engine's förväntningar.

## 🗄️ Cloud Storage Buckets

### ✅ Aktiva Buckets (efter cleanup)

| Bucket Name | Location | Purpose | Status |
|-------------|----------|---------|--------|
| igdb-recommendation-system-data | europe-west1 | Game data storage | ✅ Active |
| igdb-recommendation-system-models | europe-west1 | ML models storage | ✅ Active |
| igdb-recommendation-system-tf-state | europe-west1 | Terraform state | ✅ Active |

### 📁 Bucket Contents

**igdb-recommendation-system-data:**
- `games_clean.json` - Cleaned game data

**igdb-recommendation-system-models:**
- `recommendation_model.pkl` - Trained ML model
- `recommendation_model_feature_extractor.pkl` - Feature extractor

**igdb-recommendation-system-tf-state:**
- Terraform state files för infrastruktur management

## 🐳 Artifact Registry

### ✅ Aktiva Docker Images

**Repository:** europe-west1-docker.pkg.dev/igdb-recommendation-system/igdb-repo

| Image | Tags | Size | Status |
|-------|------|------|--------|
| igdb-frontend | latest | ~50MB | ✅ Active |
| igdb-ingestion | latest | ~200MB | ✅ Active |
| igdb-processing | latest | ~200MB | ✅ Active |
| igdb-training | latest | ~200MB | ✅ Active |

**Total Size:** ~650MB (efter cleanup)  
**Status:** ✅ Clean och optimerad

## 👥 Service Accounts

| Display Name | Email | Status | Purpose |
|--------------|-------|--------|---------|
| App Engine default service account | igdb-recommendation-system@appspot.gserviceaccount.com | ✅ Active | App Engine operations |
| Default compute service account | 18815352760-compute@developer.gserviceaccount.com | ✅ Active | Compute operations |
| IGDB Pipeline Service Account | igdb-pipeline@igdb-recommendation-system.iam.gserviceaccount.com | ✅ Active | Data pipeline operations |
| GitHub Actions Service Account | github-actions@igdb-recommendation-system.iam.gserviceaccount.com | ✅ Active | CI/CD operations |

## 🔧 GitHub Actions Workflows

### Aktiva Workflows
- **CI Pipeline:** Backend testing and validation
- **CD Pipeline:** Backend deployment to Cloud Run
- **Test Pipeline:** Backend testing
- **Deploy Frontend to App Engine:** ❌ Non-functional (App Engine issues)

### Path Filtering
- Backend workflows: Trigger only on `data_pipeline/**`, `web_app/api/**`, `shared/**`
- Frontend workflow: Trigger only on `web_app/frontend/**`

## 💰 Kostnadsuppskattning (efter cleanup)

### Aktiva Resurser
- **Cloud Run Services:** ~$0.30/månad (2 services, low traffic)
- **Cloud Run Jobs:** ~$0.20/månad (3 jobs, scheduled runs)
- **Cloud Storage:** ~$0.10/månad (3 buckets, small data)
- **Artifact Registry:** ~$0.15/månad (650MB images)
- **Cloud Scheduler:** ~$0.05/månad (1 job)

**Total uppskattad kostnad:** ~$0.80/månad

### Besparingar från Cleanup
- **Borttagna buckets:** ~$0.10/månad
- **Inaktiverad Compute Engine API:** ~$0.05/månad
- **Optimerade Docker images:** ~$0.20/månad

**Total besparing:** ~$0.35/månad

## 🚨 Kända Problem

### 1. App Engine Frontend Deployment
**Problem:** Next.js standalone output inte kompatibel med App Engine
**Status:** ❌ Non-functional
**Impact:** Frontend kan inte deployas via App Engine
**Workaround:** Manuell deployment fungerar lokalt men inte via GitHub Actions

### 2. Docker Images Accumulation
**Problem:** 8GB Docker images från misslyckade deployments
**Status:** ⚠️ Needs cleanup
**Impact:** Onödig lagringskostnad

## 🎯 Rekommenderade Åtgärder

### Kortsiktigt (Denna vecka)
1. **Rensa Docker Images:** Ta bort gamla images från Artifact Registry
2. **Frontend Deployment:** Implementera Cloud Run för frontend
3. **Dokumentation:** Uppdatera deployment guides

### Medellångsiktigt (Nästa månad)
1. **Monitoring:** Implementera proper monitoring och alerting
2. **Cost Optimization:** Regular cleanup av onödiga resurser
3. **Security:** Review IAM permissions och secrets management

### Långsiktigt (Nästa kvartal)
1. **Multi-environment:** Staging och production environments
2. **Backup Strategy:** Implementera backup för kritiska data
3. **Performance:** Optimera för skalning

## 📋 Nästa Steg

1. **Docker Images Cleanup** - Ta bort gamla images
2. **Frontend Deployment Strategy** - Välj alternativ (Cloud Run/Vercel/Netlify)
3. **CI/CD Optimization** - Förbättra deployment pipeline
4. **Monitoring Setup** - Implementera proper observability

## 🔗 Användbara Länkar

- **GCP Console:** https://console.cloud.google.com/home/dashboard?project=igdb-recommendation-system
- **Cloud Run:** https://console.cloud.google.com/run?project=igdb-recommendation-system
- **App Engine:** https://console.cloud.google.com/appengine?project=igdb-recommendation-system
- **Storage:** https://console.cloud.google.com/storage/browser?project=igdb-recommendation-system
- **Artifact Registry:** https://console.cloud.google.com/artifacts?project=igdb-recommendation-system

---

**Senast uppdaterad:** 2025-09-23  
**Uppdaterad av:** AI Assistant  
**Nästa review:** 2025-09-30
