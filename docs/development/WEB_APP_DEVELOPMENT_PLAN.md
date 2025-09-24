# Web Application Development Plan - IGDB Game Recommendation System

**Datum:** 2025-09-24
**Status:** ✅ **IN PROGRESS**
**Senast uppdaterad:** 2025-09-24
**Nästa granskning:** 2025-10-01

## 🎯 **Översikt**

Detta dokument beskriver handlingsplanen för att bygga ut admin-kontrollpanelen till en heltäckande hub för att övervaka och styra hela IGDB Game Recommendation System (data pipeline, ML-modell, monitoring, resurser). Sök/rekommendations-UI är deprioriterat till förmån för funktionalitet och skalbarhet.

> **📋 Bakgrund**: Steg 1 (Google OAuth2) och delar av Steg 2 (frontend dashboard) från ursprunglig plan är klara. Fokus är nu på att ge full end-to-end-kontroll via admin-panelen innan skalbarhetstester (5k+ spel).

## 🏗️ **Nuvarande Systemstatus**

### **✅ Redo för Utveckling:**
- **Backend (FastAPI)**: Deployat på Cloud Run (`https://igdb-api-d6xpjrmqsa-ew.a.run.app`). Endpoints: `/login`, `/auth/callback`, `/logout`, `/admin/status` (OAuth-skyddade). Secrets i `.env.local`.
- **Frontend (Next.js)**: Deployat på Vercel (`https://igdb-frontend.vercel.app/admin`). Grundläggande dashboard visar spelantal (~1,242) och modell-status.
- **Pipeline**: Automatiserad via Cloud Run Jobs (`igdb-ingestion`, `igdb-processing`, `igdb-training`) och Scheduler.
- **Data**: 1,242 spel i GCS (`games_clean.json`); SQLite för pipeline.
- **CI/CD**: GitHub Actions med Terraform, bandit/safety-scanning, Vercel-builds.
- **Monitoring**: Alerts för errors/job-failures; latens-alert förberedd.

### **❌ Gap att Adressera:**
- **Pipeline-Hantering**: Ingen UI för att trigga/övervaka jobs.
- **Real-Time Monitoring**: Ingen live-data för requests/latens.
- **Data-Insikter**: Ingen visualisering av datakvalitet/trender.
- **Systemhälsa**: Ingen detaljerad översikt av resurser/health.
- **Skalbarhet**: Ej testat för >2,000 spel.

## 📋 **3-Stegs Handlingsplan**

### **Steg 1: Backend API Expansion**
**Mål**: Skapa endpoints för pipeline-hantering, monitoring, data-insikter och systemhälsa.
**Tid**: 2-3 timmar
**Status**: 📋 **PLANNED**
**Kostnad**: ~$0.05/månad (Monitoring/Logging API-calls)

#### **Tekniska Detaljer:**
1. **Dependencies**: Lägg till i `web_app/requirements.txt`:
   ```
   google-cloud-monitoring==2.16.0
   google-cloud-logging==3.8.0
   google-cloud-run==0.10.0
   ```
2. **Endpoints**:
   - `/admin/pipeline/trigger/{job_name}`: Trigga job (t.ex. `igdb-ingestion`).
   - `/admin/pipeline/status`: Visa status för alla jobs.
   - `/admin/pipeline/history`: Visa job-historik.
   - `/admin/monitoring/metrics`: Hämta requests/latens (cachea med in-memory).
   - `/admin/monitoring/logs`: Hämta senaste loggar.
   - `/admin/data/insights`: Visa datakvalitet (completeness, freshness).
   - `/admin/system/health`: Kontrollera API/GCS/SQLite-status.
3. **Implementation**:
   ```python
   from google.cloud import monitoring_v3, run_v2, logging_v2

   @app.post("/admin/pipeline/trigger/{job_name}", dependencies=[Depends(get_current_user)])
   async def trigger_pipeline_job(job_name: str):
       client = run_v2.JobsClient()
       request = run_v2.ExecuteJobRequest(name=f"projects/igdb-recommendation-system/locations/europe-west1/jobs/{job_name}")
       client.execute_job(request)
       return {"status": f"Triggered {job_name}"}

   @app.get("/admin/monitoring/metrics", dependencies=[Depends(get_current_user)])
   async def get_system_metrics():
       client = monitoring_v3.MetricServiceClient()
       project_name = "projects/igdb-recommendation-system"
       query = client.query_time_series(
           request={
               "name": project_name,
               "filter": 'metric.type="run.googleapis.com/request_count" AND resource.type="cloud_run_revision"',
               "interval": monitoring_v3.TimeInterval(end_time={"seconds": int(time.time())}, start_time={"seconds": int(time.time()) - 3600})
           }
       )
       return {"requests": [point.value.int64_value for point in query.points]}
   ```

#### **Success-Kriterier:**
- ✅ Endpoints implementerade och OAuth-skyddade.
- ✅ Pipeline-triggers fungerar (`gcloud run jobs execute`).
- ✅ Metrics/loggar hämtas korrekt.
- ✅ Dokumentation uppdaterad.

#### **Dokumentation:**
- **DEPLOYMENT.md**: Lägg till "Admin API Endpoints".
- **LESSONS_LEARNED.md**: Logga API-issues.

---

### **Steg 2: Frontend Dashboard Expansion**
**Mål**: Bygg ut `/admin` med sektioner för pipeline, monitoring, data-insikter och systemhälsa.
**Tid**: 3-4 timmar
**Status**: 🟡 **IN PROGRESS**
**Kostnad**: ~$0.02/månad (Vercel API-calls)

#### **Tekniska Detaljer:**
1. **Dependencies**: Lägg till i `web_app/frontend/package.json`:
   ```
   "@tanstack/react-query": "^5.0.0",
   "chart.js": "^4.4.0",
   "react-chartjs-2": "^5.2.0"
   ```
2. **Layout**: Uppdatera `src/app/admin/layout.tsx` med sektioner:
   - System Overview
   - Pipeline Management
   - Monitoring & Logs
   - Data Insights
3. **Komponenter**:
   - `PipelineManager.tsx`: Job-status, trigger-knappar, historik.
   - `MonitoringDashboard.tsx`: Grafer för requests/latens (Chart.js, `useSWR`).
   - `DataInsights.tsx`: Statistik för spelantal, datakvalitet, trender.
   ```tsx
   import { Line } from "react-chartjs-2";
   import useSWR from "swr";

   export function MonitoringDashboard() {
       const { data } = useSWR("/admin/monitoring/metrics", { refreshInterval: 60000 });
       return (
           <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
               <Line data={{
                   labels: data?.requests.map((_, i) => i),
                   datasets: [{ label: "Requests", data: data?.requests, borderColor: "#3b82f6" }]
               }} />
           </div>
       );
   }
   ```

#### **Success-Kriterier:**
- ✅ Dashboard visar pipeline-status, metrics, loggar, datakvalitet.
- ✅ Real-time updates via `useSWR`.
- ✅ Responsiv design (mobil).
- ✅ Dokumentation uppdaterad.

#### **Dokumentation:**
- **FRONTEND_ARCHITECTURE.md**: Lägg till "Admin Dashboard Expansion".
- **LESSONS_LEARNED.md**: Logga UI-issues.

---

### **Steg 3: GCP Integration, Skalbarhetstest och Dokumentation**
**Mål**: Konfigurera GCP-tillstånd, testa med 5k+ spel, och slutför dokumentation.
**Tid**: 3-5 timmar
**Status**: 📋 **PLANNED**
**Kostnad**: ~$5/TB för BigQuery (om aktiverad)

#### **Tekniska Detaljer:**
1. **Terraform**:
   ```hcl
   resource "google_project_iam_member" "monitoring_viewer" {
       project = "igdb-recommendation-system"
       role    = "roles/monitoring.viewer"
       member  = "serviceAccount:github-actions@igdb-recommendation-system.iam.gserviceaccount.com"
   }
   resource "google_project_iam_member" "run_admin" {
       project = "igdb-recommendation-system"
       role    = "roles/run.admin"
       member  = "serviceAccount:github-actions@igdb-recommendation-system.iam.gserviceaccount.com"
   }
   ```
2. **Skalbarhetstest**:
   - Kör: `gcloud run jobs update igdb-ingestion --region europe-west1 --set-env-vars="LIMIT=5000"`.
   - Verifiera: `gsutil cat gs://igdb-recommendation-system-data/games_clean.json | jq length`.
   - Om query >10s, migrera till BigQuery:
     ```bash
     bq mk --dataset igdb-recommendation-system:games_dataset
     bq load --source_format=NEWLINE_DELIMITED_JSON games_dataset.games gs://igdb-recommendation-system-data/games_clean.json
     ```
3. **Testning**:
   - Simulera job-execution; verifiera dashboard-data och loggar.

#### **Success-Kriterier:**
- ✅ GCP-tillstånd konfigurerade.
- ✅ System hanterar 5k+ spel (training <5min).
- ✅ Dashboard visar uppdaterad data.
- ✅ Dokumentation komplett.

#### **Dokumentation:**
- **CURRENT_STATUS.md**: "Admin Dashboard Complete".
- **ADR-020**: "Skalbarhet och BigQuery".
- **LESSONS_LEARNED.md**: Logga skalbarhet-issues.

## 🔧 **Tekniska Krav**
- **Backend**: `google-cloud-monitoring`, `google-cloud-run`, `google-cloud-logging`.
- **Frontend**: `@tanstack/react-query`, `chart.js`, `react-chartjs-2`.
- **Infrastructure**: Terraform för IAM; BigQuery för skalbarhet.
- **Säkerhet**: OAuth-scopes (`openid email profile`), session-hantering.

## 📊 **Tidsuppskattning**
| Steg | Beskrivning | Tid | Status | Beroenden |
|------|-------------|-----|--------|-----------|
| 1 | Backend API Expansion | 2-3 timmar | 📋 Planned | GCP APIs |
| 2 | Frontend Dashboard Expansion | 3-4 timmar | 🟡 In Progress | Steg 1 |
| 3 | GCP Integration, Skalbarhetstest | 3-5 timmar | 📋 Planned | Steg 1-2 |
| **Totalt** | **Komplett Dashboard** | **8-12 timmar** | **✅ In Progress** | |

## 🚨 **Risker och Mitigering**
- **API Rate-Limits**: Cachea Monitoring-data; använd `useSWR` för frontend.
- **IAM-Fel**: Testa SA-tillstånd lokalt innan Terraform-apply.
- **Skalbarhet**: Testa stegvis (2k, 5k spel); ha BigQuery som fallback.
- **Rollback**: Revert kod via Git; rensa data med `gsutil rm`.

## 📚 **Dokumentation som Uppdateras**
- **DEPLOYMENT.md**: Admin-endpoints, GCP-integration.
- **FRONTEND_ARCHITECTURE.md**: Dashboard-expansion.
- **ARCHITECTURE.md**: Pipeline/monitoring-integration.
- **CURRENT_STATUS.md**: Projektstatus.
- **ADR-020**: Skalbarhet och BigQuery.
- **LESSONS_LEARNED.md**: OAuth, API, skalbarhet-issues.

## 💡 **Lärdomar från Tidigare Steg**
- **OAuth**: Använd UserInfo API; konfigurera dev/prod URIs.
- **Session**: Ladda `.env.local` i main.py; använd `hasattr(oauth, 'google')`.
- **Vercel**: Placera `vercel.json` i `web_app/frontend/`; exkludera stora filer.
- **Monorepo**: Anpassa pre-commit hooks för ML-modeller.

## 🔗 **Referenser**
- [DEPLOYMENT.md](DEPLOYMENT.md)
- [FRONTEND_ARCHITECTURE.md](FRONTEND_ARCHITECTURE.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [LESSONS_LEARNED.md](LESSONS_LEARNED.md)
- [OAUTH_PRODUCTION_PLAN.md](OAUTH_PRODUCTION_PLAN.md)

## 🎯 **Nästa Steg**
1. Börja med Steg 1: Implementera backend-endpoints.
2. Testa lokalt: Verifiera triggers och metrics via Swagger (`/docs`).
3. Iterera: Bygg ut frontend parallellt med Steg 2.
4. Dokumentera: Uppdatera docs för varje steg.

**Plan skapad**: 2025-09-24
**Plan godkänd**: Väntar på godkännande
**Plan start**: Väntar på start-signal
