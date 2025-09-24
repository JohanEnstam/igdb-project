# 🔌 Web App - API Module

**Syfte**: FastAPI backend för spelrekommendationer

## 📁 Innehåll

- `main.py` - FastAPI application med alla endpoints

## 🚀 Användning

```bash
# Starta API lokalt
python -m web_app.api.main

# Starta med uvicorn direkt
uvicorn web_app.api.main:app --reload --port 8000
```

## 🔧 Konfiguration

- **Port**: 8000 (local) / 8080 (Cloud Run)
- **Environment**: `.env.local` för OAuth credentials
- **Models**: Runtime loading från Cloud Storage

## 📊 API Endpoints

### **Public Endpoints**
- `GET /games/{id}/recommendations` - Get similar games by ID
- `POST /recommendations/text` - Text-based recommendations
- `GET /games/search` - Search games by name/summary
- `GET /games/{id}` - Get game details
- `GET /genres`, `/platforms` - List available options
- `GET /model/status` - Model health check
- `GET /health` - System health check

### **Authentication Endpoints**
- `GET /login` - Initiate Google OAuth flow
- `GET /auth/callback` - Handle OAuth callback
- `POST /logout` - Clear session and logout

### **Protected Admin Endpoints**
- `GET /admin/status` - Admin-only system overview (requires Google OAuth)

## 🔧 Features

- ✅ Google OAuth2 authentication
- ✅ Session-based user management
- ✅ Cloud Storage model integration
- ✅ CORS middleware
- ✅ Comprehensive error handling
- ✅ Admin dashboard integration
