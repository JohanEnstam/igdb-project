# OAuth Production Deployment Plan

**Datum:** 2025-01-23
**Status:** 🔄 Ready for Production Testing
**Senast uppdaterad:** 2025-01-23

## 🎯 **Översikt**

Detta dokument beskriver vad som behöver göras för att pusha OAuth-implementationen till produktion och säkerställa att allt som fungerar lokalt även fungerar i produktion.

## 🔍 **Nuvarande Läge**

### ✅ **Vad som fungerar lokalt:**
- **Backend OAuth**: Komplett Google OAuth2-implementation med session-hantering
- **Frontend Admin Panel**: Fullständig integration med backend OAuth
- **Session Management**: Robust logout-funktionalitet med session cleanup
- **Admin Endpoints**: Skyddade endpoints med OAuth-autentisering

### 📊 **Commit Status:**
- **22 commits** ahead of origin/main
- **Working tree clean** - inga uncommitted changes
- **Alla pre-commit hooks** passerar

## 🔐 **Secrets som behövs för produktion**

### **Backend Secrets (för Cloud Run API):**
```bash
# Redan konfigurerade i Terraform:
IGDB_CLIENT_ID=your_igdb_client_id
IGDB_CLIENT_SECRET=your_igdb_client_secret

# Nya secrets som behöver läggas till:
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
SESSION_SECRET_KEY=your_secure_session_secret_key
```

### **Frontend Secrets (för Cloud Run Frontend):**
```bash
# Ingen .env.local fil finns - alla secrets hanteras via backend API
# Frontend använder backend OAuth endpoints
```

### **GitHub Actions Secrets:**
```bash
# Redan konfigurerat:
GCP_SA_KEY=service_account_key_for_gcp_access

# Inga nya secrets behövs för GitHub Actions
```

## 🏗️ **Terraform-konfiguration**

### **Nuvarande Status:**
- ✅ **Artifact Registry**: `igdb-repo` konfigurerad
- ✅ **Cloud Run Frontend**: `igdb-frontend` konfigurerad
- ✅ **Cloud Run Backend**: `igdb-api-staging` (befintlig)
- ✅ **Secret Manager**: IAM bindings för IGDB secrets
- ❌ **OAuth Secrets**: Saknas i Terraform

### **Vad som behöver uppdateras:**

#### **1. Lägg till OAuth secrets i Secret Manager:**
```hcl
# Lägg till i main.tf
resource "google_secret_manager_secret" "google_client_id" {
  secret_id = "GOOGLE_CLIENT_ID"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "google_client_secret" {
  secret_id = "GOOGLE_CLIENT_SECRET"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "session_secret_key" {
  secret_id = "SESSION_SECRET_KEY"
  replication {
    auto {}
  }
}
```

#### **2. Lägg till IAM bindings för OAuth secrets:**
```hcl
# Lägg till i main.tf
resource "google_secret_manager_secret_iam_member" "api_oauth_secret_access" {
  secret_id = "GOOGLE_CLIENT_ID"
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:18815352760-compute@developer.gserviceaccount.com"
}

resource "google_secret_manager_secret_iam_member" "api_oauth_secret_access_secret" {
  secret_id = "GOOGLE_CLIENT_SECRET"
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:18815352760-compute@developer.gserviceaccount.com"
}

resource "google_secret_manager_secret_iam_member" "api_session_secret_access" {
  secret_id = "SESSION_SECRET_KEY"
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:18815352760-compute@developer.gserviceaccount.com"
}
```

#### **3. Uppdatera Cloud Run API service med OAuth secrets:**
```hcl
# Lägg till i befintlig google_cloud_run_v2_service.frontend eller skapa ny för API
resource "google_cloud_run_v2_service" "api" {
  name     = "igdb-api"
  location = "europe-west1"
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
    containers {
      image = "europe-west1-docker.pkg.dev/igdb-recommendation-system/igdb-repo/igdb-api:latest"
      ports {
        container_port = 8080
      }
      env {
        name = "GOOGLE_CLIENT_ID"
        value_source {
          secret_key_ref {
            secret  = "GOOGLE_CLIENT_ID"  # pragma: allowlist secret
            version = "latest"
          }
        }
      }
      env {
        name = "GOOGLE_CLIENT_SECRET"
        value_source {
          secret_key_ref {
            secret  = "GOOGLE_CLIENT_SECRET"  # pragma: allowlist secret
            version = "latest"
          }
        }
      }
      env {
        name = "SESSION_SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = "SESSION_SECRET_KEY"  # pragma: allowlist secret
            version = "latest"
          }
        }
      }
      # ... andra environment variables
    }
  }
}
```

## 🚀 **Deployment Plan**

### **Steg 1: Förbered Secrets**
```bash
# 1. Skapa secrets i Google Secret Manager
gcloud secrets create GOOGLE_CLIENT_ID --data-file=- <<< "your_google_client_id"
gcloud secrets create GOOGLE_CLIENT_SECRET --data-file=- <<< "your_google_client_secret"
gcloud secrets create SESSION_SECRET_KEY --data-file=- <<< "your_secure_session_secret_key"

# 2. Verifiera att secrets skapades
gcloud secrets list
```

### **Steg 2: Uppdatera Terraform**
```bash
# 1. Lägg till OAuth secrets och IAM bindings i main.tf
# 2. Planera ändringar
terraform plan

# 3. Applicera ändringar
terraform apply
```

### **Steg 3: Pusha kod till GitHub**
```bash
# 1. Pusha alla commits
git push origin main

# 2. Verifiera att GitHub Actions körs
gh run list

# 3. Kontrollera deployment status
gh run view <latest-run-id>
```

### **Steg 4: Verifiera produktion**
```bash
# 1. Testa OAuth login
curl -X GET "https://igdb-api-staging-d6xpjrmqsa-ew.a.run.app/auth/login"

# 2. Testa admin endpoints
curl -X GET "https://igdb-api-staging-d6xpjrmqsa-ew.a.run.app/admin/status" \
  -H "Authorization: Bearer <token>"

# 3. Testa frontend admin panel
open "https://igdb-frontend-d6xpjrmqsa-ew.a.run.app/admin"
```

## 🔧 **Konfiguration som behöver uppdateras**

### **Google OAuth Console:**
- ✅ **Production URI**: `https://igdb-api-staging-d6xpjrmqsa-ew.a.run.app/auth/callback`
- ✅ **Development URI**: `http://localhost:8080/auth/callback`
- ✅ **Authorized JavaScript Origins**: Både production och localhost
- ✅ **Scopes**: `openid email profile`

### **Frontend Environment Variables:**
- ✅ **NEXT_PUBLIC_API_URL**: `https://igdb-api-staging-d6xpjrmqsa-ew.a.run.app`
- ✅ **Inga lokala secrets**: Alla secrets hanteras via backend

## 🧪 **Testning Plan**

### **Lokalt (Redan testat):**
- ✅ OAuth login flow
- ✅ Admin panel funktionalitet
- ✅ Session management
- ✅ Logout funktionalitet

### **Produktion (Att testa):**
- 🔄 OAuth login via production URL
- 🔄 Admin panel via production URL
- 🔄 Session persistence mellan requests
- 🔄 Logout funktionalitet i produktion
- 🔄 Error handling för OAuth failures

## 🚨 **Potentiella Problem**

### **1. CORS Issues:**
- **Problem**: Frontend och backend på olika domäner
- **Lösning**: CORS är redan konfigurerat i backend

### **2. Session Cookie Issues:**
- **Problem**: Cookies fungerar inte över domäner
- **Lösning**: Sessions hanteras via backend, inte frontend

### **3. OAuth Redirect URI:**
- **Problem**: Production URL inte konfigurerad i Google Console
- **Lösning**: Verifiera att production URI är tillagd

### **4. Secret Access:**
- **Problem**: Cloud Run kan inte komma åt secrets
- **Lösning**: Verifiera IAM bindings i Terraform

## 📋 **Checklist för Production Deployment**

### **Före Push:**
- [ ] OAuth secrets skapade i Google Secret Manager
- [ ] Terraform uppdaterad med OAuth secrets och IAM bindings
- [ ] Google OAuth Console konfigurerad med production URI
- [ ] Lokala tester passerar

### **Efter Push:**
- [ ] GitHub Actions deployment lyckas
- [ ] Cloud Run services startar utan fel
- [ ] OAuth login fungerar i produktion
- [ ] Admin panel fungerar i produktion
- [ ] Logout fungerar korrekt
- [ ] Error handling fungerar

## 🎯 **Nästa Steg**

1. **Skapa OAuth secrets** i Google Secret Manager
2. **Uppdatera Terraform** med OAuth-konfiguration
3. **Pusha kod** till GitHub
4. **Verifiera deployment** via GitHub Actions
5. **Testa OAuth** i produktion
6. **Dokumentera resultat** och eventuella problem

## 📚 **Referenser**

- [ADR-018: OAuth Implementation Complete](docs/decisions/018-oauth-implementation-complete.md)
- [DEPLOYMENT.md](docs/DEPLOYMENT.md)
- [CURRENT_STATUS.md](docs/CURRENT_STATUS.md)
- [Terraform Configuration](infrastructure/terraform/main.tf)

---

**Senast uppdaterad:** 2025-01-23
**Uppdaterad av:** AI Assistant
**Nästa review:** Efter production deployment
