# Web Application Development Plan - IGDB Game Recommendation System

**Datum:** 2025-09-23  
**Status:** 📋 **PLANNED**  
**Senast uppdaterad:** 2025-09-23  
**Nästa granskning:** 2025-09-30

## 🎯 **Översikt**

Detta dokument beskriver den detaljerade handlingsplanen för att utveckla web-applikationen med användarvänlig sök/rekommendation och en Google Auth-skyddad kontrollpanel för att övervaka och hantera hela systemet.

> **📋 Bakgrund**: Baserat på framgångsrik slutföring av alla 4 steg i DEPLOYMENT_PLAN.md är systemet nu produktionsklart med CI/CD, monitoring och säkerhet. Fokus skiftar nu till att bygga ut användargränssnittet och kontrollpanelen.

## 🏗️ **Nuvarande Systemstatus**

### **✅ Redo för Utveckling:**
- **Backend (FastAPI)**: Deployat på Cloud Run (`igdb-api-staging`)
- **Frontend (Next.js)**: MVP på Cloud Run (`igdb-frontend`) med `src/app/` struktur
- **Pipeline**: Automatiserad via Cloud Run Jobs och Scheduler
- **Data**: 1,242 spel i GCS (`games_clean.json`)
- **CI/CD**: Komplett med Terraform, monitoring och säkerhetsscanning
- **Secrets**: Hanterade via GCP Secret Manager

### **❌ Gap att Adressera:**
- **Google Auth**: Inget autentiseringslager för admin-funktioner
- **Kontrollpanel**: Saknas UI för översikt och hantering
- **Skalbarhet**: Ej testat för >2,000 spel
- **Admin Endpoints**: Saknas `/admin/*` endpoints i backend

## 📋 **4-Stegs Handlingsplan**

### **Steg 1: Implementera Google Auth i Backend och Grundläggande Admin-Endpoints**
**Mål**: Lägg till Google OAuth2 i FastAPI för att skydda `/admin/*`-rutter och skapa endpoints för översikt.  
**Tid**: 3-4 timmar  
**Status**: 📋 **PLANNED**

#### **Tekniska Detaljer:**
1. **Dependencies**: Lägg till `authlib==1.3.1` och `python-jose[cryptography]==3.3.0` i `web_app/requirements.txt`
2. **FastAPI Integration**: Använd `authlib` med GCP Secret Manager för secrets
3. **Admin Endpoints**: Skapa `/admin/status` med spelantal och modell-status
4. **OAuth Configuration**: Konfigurera Google OAuth2 i GCP Console

#### **Success-Kriterier:**
- ✅ `/admin/status` kräver Google-login
- ✅ Oskyddade rutter (`/games`) förblir öppna
- ✅ Endpoint returnerar spelantal (~1,242) och modell-status
- ✅ Dokumentation uppdaterad

#### **Implementation Steps:**
```python
# Exempel implementation i web_app/api/main.py
from authlib.integrations.starlette_client import OAuth
from google.cloud import secretmanager

@app.get("/admin/status", dependencies=[Depends(get_current_user)])
async def admin_status():
    registry = ModelRegistry()
    return {
        "status": registry.health_check(),
        "spelvantal": len(registry.get_games_data()),
        "modell": "content_based_recommendation"
    }
```

---

### **Steg 2: Bygg Kontrollpanel-Frontend i Next.js**
**Mål**: Skapa skyddade admin-sidor i `src/app/admin/` med Google Auth och grundläggande dashboard.  
**Tid**: 4-6 timmar  
**Status**: 📋 **PLANNED**

#### **Tekniska Detaljer:**
1. **Dependencies**: Installera `@react-oauth/google` och `axios`
2. **Admin Layout**: Skapa `src/app/admin/layout.tsx` för auth-skydd
3. **Dashboard**: Implementera `src/app/admin/page.tsx` med spelantal och modell-status
4. **Terraform Integration**: Uppdatera Cloud Run service med `NEXT_PUBLIC_GOOGLE_CLIENT_ID`

#### **Success-Kriterier:**
- ✅ Admin-sida skyddad med Google Auth
- ✅ Dashboard visar spelantal och modell-status
- ✅ Responsiv design för mobil
- ✅ Dokumentation uppdaterad

#### **Implementation Steps:**
```tsx
// Exempel implementation i src/app/admin/page.tsx
export default function AdminDashboard() {
  const [status, setStatus] = useState<any>(null);
  const login = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      const res = await axios.get("/admin/status", {
        headers: { Authorization: `Bearer ${tokenResponse.access_token}` }
      });
      setStatus(res.data);
    }
  });
  // ... rest of component
}
```

---

### **Steg 3: Integrera Övervakning och Hantering i Kontrollpanel**
**Mål**: Lägg till endpoints och frontend-komponenter för att visa belastning och trigga pipeline-jobs.  
**Tid**: 3-4 timmar  
**Status**: 📋 **PLANNED**

#### **Tekniska Detaljer:**
1. **Monitoring Endpoints**: Implementera `/admin/monitoring` med GCP Monitoring API
2. **Pipeline Triggers**: Skapa `/admin/pipeline/trigger` för job-execution
3. **Frontend Charts**: Använd Chart.js för belastningsgrafer
4. **IAM Configuration**: Uppdatera Terraform för Monitoring API-åtkomst

#### **Success-Kriterier:**
- ✅ Monitoring visar belastning (requests/60s)
- ✅ Pipeline-triggers fungerar från panel
- ✅ Grafer visas i frontend
- ✅ Dokumentation uppdaterad

#### **Implementation Steps:**
```python
# Exempel implementation för monitoring
@app.get("/admin/monitoring", dependencies=[Depends(get_current_user)])
async def admin_monitoring():
    client = monitoring_v3.MetricServiceClient()
    # Query Cloud Run metrics
    return {"requests": [point.value.int64_value for point in query.points]}
```

---

### **Steg 4: Testa med Fler Spel och Slutför Dokumentation**
**Mål**: Validera systemet med 5,000+ spel och dokumentera allt.  
**Tid**: 2-4 timmar  
**Status**: 📋 **PLANNED**

#### **Tekniska Detaljer:**
1. **Skalbarhetstest**: Uppdatera ingestion med `--limit 5000`
2. **Performance Validation**: Verifiera training-tid <5min
3. **BigQuery Migration**: Om nödvändigt för >10k spel
4. **Dokumentation**: Uppdatera alla docs och skapa ADR

#### **Success-Kriterier:**
- ✅ System hanterar 5k+ spel stabilt
- ✅ Kontrollpanel visar uppdaterat spelantal
- ✅ Dokumentation komplett
- ✅ ADR skapad för panel-design

#### **Implementation Steps:**
```bash
# Exempel för skalbarhetstest
gcloud run jobs update igdb-ingestion --region europe-west1 \
  --set-env-vars="LIMIT=5000"
gcloud run jobs execute igdb-ingestion --region europe-west1
```

## 🔧 **Tekniska Krav**

### **Backend (FastAPI):**
- Google OAuth2 med `authlib`
- GCP Secret Manager integration
- Admin endpoints med auth-skydd
- GCP Monitoring API integration

### **Frontend (Next.js):**
- Google Auth med `@react-oauth/google`
- Admin-sidor i `src/app/admin/`
- Chart.js för visualisering
- Responsiv design

### **Infrastructure:**
- Terraform-uppdateringar för secrets
- IAM-konfiguration för Monitoring API
- Cloud Run environment variables

## 📊 **Tidsuppskattning**

| Steg | Beskrivning | Tid | Status |
|------|-------------|-----|--------|
| 1 | Google Auth + Admin Endpoints | 3-4 timmar | 📋 Planned |
| 2 | Kontrollpanel Frontend | 4-6 timmar | 📋 Planned |
| 3 | Monitoring + Pipeline Integration | 3-4 timmar | 📋 Planned |
| 4 | Skalbarhetstest + Dokumentation | 2-4 timmar | 📋 Planned |
| **Totalt** | **Komplett Implementation** | **12-18 timmar** | **📋 Planned** |

## 🎯 **Success-Kriterier för Hela Projektet**

### **Funktionalitet:**
- ✅ Användarvänlig sök och rekommendationer
- ✅ Google Auth-skyddad kontrollpanel
- ✅ Real-time monitoring av belastning
- ✅ Pipeline-hantering från panel
- ✅ Skalbarhet för 5k+ spel

### **Teknisk Kvalitet:**
- ✅ Säker autentisering och auktorisering
- ✅ Responsiv och tillgänglig UI
- ✅ Robust error handling
- ✅ Komplett dokumentation
- ✅ CI/CD-integration

### **Produktionsklarhet:**
- ✅ Stabilt system under belastning
- ✅ Monitoring och alerting
- ✅ Säkerhetsscanning
- ✅ Backup och recovery-planer

## 🚨 **Risker och Mitigering**

### **Tekniska Risker:**
- **OAuth Configuration**: Testa auth-flow lokalt först
- **API Rate Limits**: Implementera caching för Monitoring API
- **Skalbarhet**: Testa stegvis med ökande spelantal

### **Operativa Risker:**
- **Tidsöverskridning**: Max 1 timme debugging per issue
- **Dokumentation**: Uppdatera docs parallellt med utveckling
- **Rollback**: Ha fallback-planer redo

## 📚 **Dokumentation som Uppdateras**

### **Teknisk Dokumentation:**
- `DEPLOYMENT.md` - Google Auth setup
- `FRONTEND_ARCHITECTURE.md` - Kontrollpanel
- `ARCHITECTURE.md` - Monitoring integration
- `CURRENT_STATUS.md` - Projektstatus

### **ADR (Architecture Decision Records):**
- `ADR-016: Google Auth Implementation`
- `ADR-017: Kontrollpanel Design`
- `ADR-018: Monitoring Integration`

### **Lärdomar:**
- `LESSONS_LEARNED.md` - Auth- och skalbarhetsissues

## 🔗 **Referenser**

- **[DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md)** - Slutförd 4-stegs deployment plan
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Aktuell deployment status
- **[FRONTEND_ARCHITECTURE.md](FRONTEND_ARCHITECTURE.md)** - Frontend arkitektur
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Systemarkitektur
- **[LESSONS_LEARNED.md](LESSONS_LEARNED.md)** - Tidigare lärdomar

## 🎯 **Nästa Steg**

1. **Börja med Steg 1**: Implementera Google Auth i backend
2. **Testa lokalt**: Verifiera auth-flow innan deployment
3. **Iterativ utveckling**: Implementera steg för steg med verifiering
4. **Dokumentera**: Uppdatera docs parallellt med utveckling

---

**Plan skapad**: 2025-09-23  
**Plan godkänd**: Väntar på godkännande  
**Plan start**: Väntar på start-signal
