# 📁 IGDB Project Structure Guide

## 🎯 **Quick Navigation**

| Mapp | Syfte | Viktiga Filer |
|------|-------|---------------|
| [`data_pipeline/`](#data_pipeline) | Data collection, processing, ML training | `ingestion/`, `processing/`, `training/` |
| [`web_app/`](#web_app) | Web application (API + Frontend) | `api/`, `frontend/` |
| [`tests/`](#tests) | All testing code | `test_*.py`, `fixtures/` |
| [`docs/`](#docs) | Documentation and decisions | `decisions/`, `ARCHITECTURE.md` |
| [`infrastructure/`](#infrastructure) | Cloud infrastructure (Terraform) | `terraform/` |
| [`data/`](#data) | Production data storage | `games.db`, `games_clean.json` |
| [`models/`](#models) | Trained ML models | `*.pkl` files |

---

## 🏭 **data_pipeline/** - Factory Pipeline

**Syfte**: Samlar, bearbetar och tränar ML-modeller på speldata

```
data_pipeline/
├── ingestion/          # 📥 Data Collection
│   ├── main.py         # CLI för datahämtning
│   ├── smart_ingestion.py  # Intelligent datahämtning
│   └── Dockerfile      # Container för datahämtning
├── processing/         # 🔄 Data Processing
│   ├── main.py         # CLI för databearbetning
│   ├── data_transformer.py  # Data cleaning & transformation
│   └── Dockerfile      # Container för bearbetning
├── training/           # 🤖 ML Training
│   ├── main.py         # CLI för modellträning
│   ├── recommendation_model.py  # ML modell implementation
│   ├── feature_extractor.py    # Feature engineering
│   └── Dockerfile      # Container för träning
└── shared/             # 🔧 Shared Utilities
    └── data_manager.py # Database operations
```

**Kommandon**:
```bash
# Data hämtning
python -m data_pipeline.ingestion.main --smart --limit 100

# Data bearbetning
python -m data_pipeline.processing.main --transform-all

# ML träning
python -m data_pipeline.training.main --data data/games_clean.json
```

---

## 🏪 **web_app/** - Store Pipeline

**Syfte**: Serverar spelrekommendationer via web API och frontend

```
web_app/
├── api/                # 🔌 Backend API
│   └── main.py         # FastAPI application
├── frontend/           # 🎨 Frontend (Next.js)
│   ├── src/app/        # Next.js app router
│   ├── src/components/ # React components
│   └── package.json    # Node.js dependencies
├── model_registry.py   # Cloud Storage integration
└── requirements.txt    # Python dependencies
```

**Kommandon**:
```bash
# Starta API lokalt
python -m web_app.api.main

# Starta frontend
cd web_app/frontend && npm run dev
```

---

## 🧪 **tests/** - Testing Suite

**Syfte**: Alla tester för att säkerställa kodkvalitet

```
tests/
├── fixtures/           # 📁 Test Data
│   ├── mock_games.json # Mock data för tester
│   ├── test_*.db       # Test databaser
│   └── games_sample.json # Sample data
├── integration/        # 🔗 Integration Tests
│   └── test_data_pipeline.py
├── test_data_manager.py     # DataManager tests
├── test_data_transformer.py # DataTransformer tests
├── test_ml_pipeline.py      # ML pipeline tests
└── test_smart_ingestion.py  # SmartIngestion tests
```

**Kommandon**:
```bash
# Kör alla tester
pytest tests/ -v

# Kör integration tester
pytest tests/integration/ -v
```

---

## 📚 **docs/** - Documentation

**Syfte**: Projekt-dokumentation och beslut

```
docs/
├── decisions/          # 📋 Architecture Decision Records
│   ├── 016-google-auth-implementation.md
│   ├── 017-kontrollpanel-frontend-implementation.md
│   ├── 018-oauth-implementation-complete.md
│   └── 019-monorepo-vercel-deployment.md
├── ARCHITECTURE.md     # System architecture
├── CURRENT_STATUS.md   # Project status
├── DATA_FLOW.md        # Data flow documentation
└── README.md           # Documentation overview
```

---

## ☁️ **infrastructure/** - Cloud Infrastructure

**Syfte**: Infrastructure as Code för GCP

```
infrastructure/
└── terraform/          # 🏗️ Terraform configurations
    └── main.tf         # GCP resources
```

---

## 💾 **data/** - Production Data

**Syfte**: Produktionsdata och databaser

```
data/
├── games.db            # SQLite database med speldata
├── games_clean.json    # Cleaned game data (JSON)
├── games_clean.csv     # Cleaned game data (CSV)
├── genres.json         # Genre definitions
└── platforms.json     # Platform definitions
```

---

## 🤖 **models/** - ML Models

**Syfte**: Tränade ML-modeller

```
models/
├── recommendation_model.pkl              # Main recommendation model
├── recommendation_model_feature_extractor.pkl  # Feature extractor
└── test_model_feature_extractor.pkl     # Test model
```

---

## 🔧 **Root Configuration Files**

**Syfte**: Projekt-konfiguration (måste vara i root)

| Fil | Syfte |
|-----|-------|
| `docker-compose.yml` | Docker services orchestration |
| `requirements.txt` | Python production dependencies |
| `setup.py` | Python package configuration |
| `Makefile` | Development commands |
| `pytest.ini` | Test configuration |
| `.pre-commit-config.yaml` | Code quality hooks |

---

## 🚀 **Quick Start Commands**

### **Development Setup**
```bash
# Install dependencies
pip install -e .

# Start data pipeline
python -m data_pipeline.ingestion.main --smart --limit 100

# Start web API
python -m web_app.api.main

# Run tests
pytest tests/ -v
```

### **Docker Setup**
```bash
# Build all services
make build

# Start development environment
make dev

# Run tests in containers
make test
```

### **Production Deployment**
```bash
# Deploy to GCP
make prod

# Check deployment status
curl https://igdb-api-d6xpjrmqsa-ew.a.run.app/health
```

---

## 🎯 **Navigation Tips**

1. **Start här**: `README.md` för projektöversikt
2. **Arkitektur**: `docs/ARCHITECTURE.md` för systemdesign
3. **Status**: `docs/CURRENT_STATUS.md` för nuvarande utveckling
4. **API**: `web_app/api/main.py` för backend endpoints
5. **Frontend**: `web_app/frontend/src/` för UI komponenter
6. **Tests**: `tests/` för alla tester
7. **Data**: `data/` för produktionsdata

---

## 📞 **Need Help?**

- **Architecture questions**: Check `docs/decisions/` ADRs
- **API documentation**: Visit `/docs` endpoint when API is running
- **Frontend issues**: Check `web_app/frontend/README.md`
- **Test failures**: Check `tests/` directory for test files
- **Data issues**: Check `data/` directory for data files
