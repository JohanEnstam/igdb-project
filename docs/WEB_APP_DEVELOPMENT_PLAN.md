# Web Application Development Plan - IGDB Game Recommendation System

**Datum:** 2025-09-23  
**Status:** ✅ **COMPLETED**  
**Senast uppdaterad:** 2025-09-24  
**Nästa granskning:** 2025-10-01

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

### **✅ Gap Adresserade:**
- **Google Auth**: ✅ Komplett OAuth2-implementation med session-hantering
- **Kontrollpanel**: ✅ Admin dashboard med riktig backend-data
- **Skalbarhet**: ✅ Testat med 1,242 spel och fungerar perfekt
- **Admin Endpoints**: ✅ `/admin/status` endpoint med systemöversikt

## 📋 **4-Stegs Handlingsplan**

### **Steg 1: Implementera Google Auth i Backend och Grundläggande Admin-Endpoints**
**Mål**: Lägg till Google OAuth2 i FastAPI för att skydda `/admin/*`-rutter och skapa endpoints för översikt.  
**Tid**: 3-4 timmar  
**Status**: ✅ **COMPLETED** (2025-09-24)

#### **Tekniska Detaljer:**
1. **Dependencies**: Kontrollera befintliga i `web_app/requirements.txt` innan installation. Lägg till senaste kompatibla versioner av `authlib` och `python-jose[cryptography]` via pip install
2. **FastAPI Integration**: Använd `authlib` med GCP Secret Manager för secrets
3. **Admin Endpoints**: Skapa `/admin/status` med spelantal och modell-status
4. **OAuth Configuration**: Konfigurera Google OAuth2 i GCP Console med `redirect_uri` till backend-URL (`https://igdb-api-staging-d6xpjrmqsa-ew.a.run.app/callback`). Använd `SessionMiddleware` med secret från Secret Manager för prod-säkerhet

#### **Success-Kriterier:**
- ✅ Admin-sida skyddad med Google Auth
- ✅ Dashboard visar spelantal och modell-status
- ✅ Responsiv design för mobil
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
**Status**: ✅ **COMPLETED**

#### **Tekniska Detaljer:**
1. **Dependencies**: Kontrollera befintliga i `web_app/frontend/package.json` innan installation. Lägg till senaste kompatibla versioner av `@react-oauth/google` och `axios` via npm install
2. **Admin Layout**: Skapa `src/app/admin/layout.tsx` för auth-skydd
3. **Dashboard**: Implementera `src/app/admin/page.tsx` med spelantal och modell-status. Använd befintlig `src/components/ui/` för Card/Buttons från Shadcn/ui
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

### **Steg 2: Bygg Kontrollpanel-Frontend i Next.js**
**Mål**: Skapa admin-sidor med Google Auth och dashboard för systemöversikt.  
**Tid**: 4-5 timmar  
**Status**: ✅ **COMPLETED** (2025-09-24)

#### **Tekniska Detaljer:**
1. **Next.js Admin Pages**: Skapa `src/app/admin/` med auth-skydd
2. **Google Auth Integration**: Använd `@react-oauth/google` med session-baserad auth
3. **Admin Dashboard**: Visa systemstatus, spelantal och användarinfo
4. **API Proxying**: Next.js API routes som proxy till backend för CORS-hantering

#### **Success-Kriterier:**
- ✅ Admin-sidor skyddade med Google Auth
- ✅ Dashboard visar riktig backend-data
- ✅ Responsiv design för mobil
- ✅ Komplett logout-funktionalitet

#### **Implementation Steps:**
```tsx
// Implementerat i src/app/admin/layout.tsx
export default function AdminLayout({ children }: AdminLayoutProps) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<any>(null);
  
  const login = () => {
    window.location.href = "/api/auth/login";
  };
  
  // Auth check och dashboard rendering
}
```

---

### **Steg 3: Mock Data Cleanup & Production Readiness**
**Mål**: Ersätt all mock-data med riktig backend-integration och säkerställ produktionsklarhet.  
**Tid**: 2-3 timmar  
**Status**: ✅ **COMPLETED** (2025-09-24)

#### **Tekniska Detaljer:**
1. **Data Integration**: Uppdatera alla komponenter för att använda riktig backend-data
2. **OAuth Flow Fix**: Implementera korrekt Authorization Code Flow med state validation
3. **Session Management**: Robust cookie-hantering mellan frontend och backend
4. **Error Handling**: Komplett felhantering för auth-fel och API-anrop

#### **Success-Kriterier:**
- ✅ Alla komponenter använder riktig backend-data
- ✅ OAuth-flöde fungerar perfekt med proper state validation
- ✅ Logout-funktionalitet fungerar korrekt
- ✅ Admin dashboard visar live systemstatus

---

### **Steg 4: Integrera Övervakning och Hantering i Kontrollpanel**
**Mål**: Lägg till endpoints och frontend-komponenter för att visa belastning och trigga pipeline-jobs.  
**Tid**: 3-4 timmar  
**Status**: 📋 **PLANNED**

#### **Tekniska Detaljer:**
1. **Monitoring Endpoints**: Implementera `/admin/monitoring` med GCP Monitoring API
2. **Pipeline Triggers**: Skapa `/admin/pipeline/trigger` för job-execution
3. **Frontend Charts**: Använd Chart.js för belastningsgrafer
4. **IAM Configuration**: Uppdatera Terraform för Monitoring API-åtkomst. Ge SA `roles/monitoring.viewer` via Terraform

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
3. **BigQuery Migration**: Implementera för 5k+ spel om query-tid på GCS JSON >10s; migrera till BigQuery för skalbarhet
4. **Dokumentation**: Uppdatera alla docs och skapa ADR

#### **Skalbarhetstest Detaljer:**
- **Stegvis Test**: Börja med 2k, sedan 5k spel via --limit
- **Verifiering**: Kontrollera GCS-fil med `gsutil cat gs://igdb-recommendation-system-data/games_clean.json | jq length`
- **Optimering**: Om training >5min, använd BigQuery för query (skapa dataset `games_dataset`)

#### **Success-Kriterier:**
- ✅ System hanterar 5k+ spel stabilt
- ✅ Kontrollpanel visar uppdaterat spelantal (aktuellt ~1,242; mål 5,000+ efter test)
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
- IAM för Monitoring: Ge SA `roles/monitoring.viewer` via Terraform

### **Frontend (Next.js):**
- Google Auth med `@react-oauth/google`
- Admin-sidor i `src/app/admin/`
- Chart.js för visualisering
- Responsiv design

### **Infrastructure:**
- Terraform-uppdateringar för secrets
- IAM-konfiguration för Monitoring API
- Cloud Run environment variables

### **Kostnads- och Prestandaestimat:**
- **Auth**: Gratis (OAuth-tokens), +$0.01/1000 calls
- **Monitoring API**: ~$0.10/månad för queries
- **BigQuery (om migrering)**: ~$5/TB query; gratis för små dataset
- **Prestanda för 5k Spel**: Förväntad training-tid <5min; testa med `time gcloud run jobs execute igdb-training`

## 📊 **Tidsuppskattning**

| Steg | Beskrivning | Tid | Beroenden | Status |
|------|-------------|-----|-----------|--------|
| 1 | Google Auth + Admin Endpoints | 3-4 timmar | GCP Secret Manager access | 📋 Planned |
| 2 | Kontrollpanel Frontend | 4-6 timmar | Steg 1 completion | 📋 Planned |
| 3 | Monitoring + Pipeline Integration | 3-4 timmar | Steg 2 completion | 📋 Planned |
| 4 | Skalbarhetstest + Dokumentation | 2-4 timmar | Steg 3 completion | 📋 Planned |
| **Totalt** | **Komplett Implementation** | **12-18 timmar** | **+2 timmar buffer för BigQuery** | **📋 Planned** |

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

### **Rollback-strategier:**
- **Steg 1**: Om auth misslyckas, revert backend-kod och redeploy via CI/CD. Använd `terraform destroy` för IAM-ändringar
- **Steg 2**: Revert frontend-kod; testa lokalt med `npm run dev` innan push
- **Steg 3**: Om monitoring-integration felar, revert API-calls; fallback till Console för manuella checks
- **Steg 4**: Om skalbarhetstest misslyckas, revert till --limit 1000; rensa extra data via `gsutil rm`

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
- **Kodbas-Verifiering**: Alltid verifiera data-volym med `jq length` istället för `wc -l`

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
**Plan uppdaterad**: 2025-09-23 (baserat på Grok's feedback)  
**Plan godkänd**: Väntar på godkännande  
**Plan start**: Väntar på start-signal  
**Kostnad**: +$0.20/månad för auth/monitoring
