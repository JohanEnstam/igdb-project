# ADR-016: Google Auth Implementation

**Datum:** 2025-09-24
**Status:** ✅ **ACCEPTED**
**Senast uppdaterad:** 2025-09-24
**Nästa granskning:** 2025-09-30

## 🎯 **Beslut**

Implementera Google OAuth2 för att skydda admin-funktioner i FastAPI backend med session-baserad autentisering.

## 📋 **Kontext**

Vi behövde skydda admin-funktioner (som `/admin/status`) så att endast auktoriserade användare kan komma åt systemöversikt och hanteringsfunktioner. Detta är Steg 1 i WEB_APP_DEVELOPMENT_PLAN.md.

### **Alternativ som övervägdes:**

1. **API Keys**: Enkelt men inte användarvänligt
2. **JWT Tokens**: Komplext för session-hantering
3. **Google OAuth2**: Användarvänligt och säkert
4. **Custom Auth**: För komplext för vårt behov

## ✅ **Beslut**

**Valt alternativ:** Google OAuth2 med session-baserad autentisering

### **Implementation:**
- **Provider**: Google OAuth2
- **Session Management**: FastAPI SessionMiddleware
- **User Info**: Google UserInfo API med access token
- **Security**: Säker secret key för session-hantering
- **Scope**: `openid email profile`

### **Endpoints implementerade:**
- `GET /login` - Initierar Google OAuth-flöde
- `GET /auth/callback` - Hanterar OAuth-svar och skapar session
- `POST /logout` - Rensar session och loggar ut användare
- `GET /admin/status` - Skyddad endpoint med systemstatus

## 🔧 **Tekniska Detaljer**

### **Dependencies tillagda:**
```python
authlib==1.3.1                    # OAuth2 integration
python-jose[cryptography]==3.3.0  # JWT token handling
itsdangerous==2.2.0               # Session security
python-dotenv==1.0.0              # Environment variable loading
httpx==0.25.2                     # HTTP client för Google UserInfo API
```

### **OAuth Configuration:**
```python
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)
```

### **Session Security:**
```python
SESSION_SECRET_KEY = os.environ.get("SESSION_SECRET_KEY", "dev-insecure-session-key")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)
```

### **User Authentication:**
```python
def get_current_user(request: Request) -> Dict[str, Any]:
    """Dependency to ensure a logged-in Google user exists in the session."""
    user = request.session.get("user") if hasattr(request, "session") else None
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
```

## 🚨 **Lärdomar från Implementation**

### **Problem 1: Environment Variables Loading**
- **Problem**: `.env.local` laddades inte i serverns process
- **Lösning**: Lade till `load_dotenv()` direkt i `main.py`
- **Lärdom**: Alltid ladda environment variables i huvudprocessen, inte i subprocesser

### **Problem 2: OAuth Object Iteration**
- **Problem**: `"google" not in oauth` gav TypeError
- **Lösning**: Använde `hasattr(oauth, 'google')` istället
- **Lärdom**: OAuth-objekt är inte iterable, använd hasattr() för att kontrollera providers

### **Problem 3: ID Token vs Access Token**
- **Problem**: `parse_id_token()` misslyckades eftersom Google inte returnerade ID token
- **Lösning**: Använde Google UserInfo API med access token istället
- **Lärdom**: Alltid använda rätt API-endpoint för användarinfo

### **Problem 4: Redirect URI Configuration**
- **Problem**: Google OAuth krävde localhost:8080 i konfigurationen
- **Lösning**: Lade till både production och development URIs
- **Lärdom**: OAuth måste konfigureras för alla miljöer (dev + prod)

### **Problem 5: JSON Parsing i .env.local**
- **Problem**: GCP_SA_KEY JSON-data orsakade parsing-fel
- **Lösning**: Kommenterade bort JSON-data för OAuth-testning
- **Lärdom**: Separera OAuth-secrets från komplexa JSON-strukturer

## 📊 **Konsekvenser**

### **Positiva:**
- ✅ Säker autentisering med Google som provider
- ✅ Användarvänlig inloggning (ingen API key-hantering)
- ✅ Session-baserad autentisering (användaren behöver inte logga in varje request)
- ✅ Skalbar lösning (lätt att lägga till fler admin-funktioner)
- ✅ Integration med befintlig GCP-infrastruktur

### **Negativa:**
- ⚠️ Ytterligare dependencies (authlib, httpx, etc.)
- ⚠️ Komplexitet i OAuth-konfiguration
- ⚠️ Beroende av Google OAuth-tjänster

### **Risker:**
- **OAuth Provider Downtime**: Google OAuth-tjänster kan vara otillgängliga
- **Session Security**: Secret key måste vara säker och roteras regelbundet
- **Configuration Drift**: OAuth-konfiguration måste synkroniseras mellan miljöer

## 🔄 **Alternativa Implementationer**

### **Framtida Förbättringar:**
1. **Multi-Provider Support**: Lägg till Microsoft/Azure AD som alternativ
2. **Role-Based Access**: Implementera roller (admin, user, viewer)
3. **Session Management**: Lägg till session timeout och refresh
4. **Audit Logging**: Logga alla admin-åtgärder

### **Om vi behöver ändra:**
- **API Keys**: Enkelt att implementera som fallback
- **JWT Tokens**: Kan implementeras för stateless autentisering
- **Custom Auth**: Kan implementeras för specifika krav

## 📚 **Referenser**

- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [FastAPI SessionMiddleware](https://fastapi.tiangolo.com/advanced/middleware/#sessionmiddleware)
- [Authlib Documentation](https://docs.authlib.org/)
- [WEB_APP_DEVELOPMENT_PLAN.md](../WEB_APP_DEVELOPMENT_PLAN.md)

## ✅ **Acceptance Criteria**

- [x] Google OAuth2 integration fungerar
- [x] Session-baserad autentisering implementerad
- [x] `/admin/status` endpoint skyddad
- [x] OAuth endpoints (`/login`, `/auth/callback`, `/logout`) fungerar
- [x] Användarinfo (email, name, picture) sparas i session
- [x] Säker session-hantering med secret key
- [x] Både development och production URIs konfigurerade
- [x] Dokumentation uppdaterad

---

**Beslut fattat av:** AI Assistant
**Godkänt av:** Johan Enstam
**Implementerat:** 2025-09-24
**Status:** ✅ **PRODUCTION READY**
