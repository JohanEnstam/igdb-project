# IGDB Game Recommendation System

Ett komplett system för att samla speldata från externa API:er, träna ML-modeller och servera spelrekommendationer via en web-applikation.

## Arkitektur

Projektet är uppdelat i två huvudsakliga pipelines:

### 🏭 Data Pipeline (Fabriks-pipeline)

- **Ingestion**: Samlar data från externa API:er
- **Processing**: Städar och transformerar rådata
- **Training**: Tränar ML-modeller för spelrekommendationer
- **Deployment**: Distribuerar tränade modeller

### 🏪 Web App (Butiks-pipeline)

- **API**: Backend som serverar rekommendationer
- **Frontend**: Användargränssnitt för sökning och rekommendationer
- **Deployment**: Applikationsdistribution

## Projektstruktur

```text
igdb-project/
├── data-pipeline/          # Fabriks-pipeline
│   ├── ingestion/         # API data collection
│   ├── processing/        # Data cleaning & transformation
│   ├── training/          # ML model training
│   └── deployment/        # Model serving setup
├── web-app/               # Butiks-pipeline
│   ├── api/              # Backend API
│   ├── frontend/         # User interface
│   └── deployment/       # App deployment
├── shared/               # Delad kod (utils, configs)
├── infrastructure/       # Terraform/Pulumi för GCP
└── docs/                # Dokumentation
```

## Teknisk Stack

- **Cloud**: Google Cloud Platform (GCP)
- **Data Pipeline**: Python, SQLite, Cloud Storage
- **ML**: scikit-learn, TF-IDF vectorization, content-based filtering
- **Web App**: FastAPI (backend), React/Vue (frontend - coming next)
- **Infrastructure**: Docker, GitHub Actions, Cloud Run
- **CI/CD**: GitHub Actions (CI ✓, CD ✓, Test ✓)
- **Security**: Bandit, Safety, pre-commit hooks

## Utvecklingsprocess

1. **Lokal utveckling** → **Staging** → **Production**
2. **Feature branches** för varje komponent
3. **Separate CI/CD pipelines** för data-pipeline och web-app
4. **Automated testing** på både kod och data quality

## Kom igång

```bash
# Klona repository
git clone <repository-url>
cd igdb-project

# Installera dependencies
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Kör lokalt
python -m web_app.api.main
# API:n körs på http://localhost:8000

# Eller med Docker
docker run --rm -p 8080:8080 -e PORT=8080 \
  gcr.io/igdb-recommendation-system/igdb-api:latest
```

## Status

✅ **Phase 4 Complete** - Complete ML Pipeline + Cloud Storage Integration + Fully Functional CI/CD

### **What's Working**
- **Complete ML Pipeline**: TF-IDF vectorization, content-based recommendations
- **Cloud Storage Integration**: Professional data separation with GCS buckets
- **Model Registry**: Runtime loading from Cloud Storage with graceful fallback
- **FastAPI Web Application**: REST API with recommendation endpoints
- **CI/CD Infrastructure**: All pipelines working (CI ✓, CD ✓, Test ✓)
- **Docker Containerization**: All services containerized and tested
- **Security**: Zero vulnerabilities (bandit + safety)
- **Testing**: 66 comprehensive tests (100% pass rate)

### **Quick Start**
```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Train ML model with real data
python -m data_pipeline.training.main --data data/games_clean.json --model models/recommendation_model.pkl

# Start recommendation API locally
python -m web_app.api.main

# Test recommendations via API
curl "http://localhost:8000/games/239060/recommendations?top_k=5"

# Test Cloud Storage integration
curl "http://localhost:8080/health"
# Returns: {"status":"healthy","gcs_available":"True","data_accessible":"True"}

# Run tests
pytest tests/ -v
```

### **Docker & CI/CD**
```bash
# Run API container locally (port 8080 for Cloud Run compatibility)
docker run --rm -p 8080:8080 -e PORT=8080 \
  gcr.io/igdb-recommendation-system/igdb-api:latest

# Check CI/CD status (all pipelines working!)
gh run list --limit 5
```

### **Next Steps**
🎯 **Phase 5**: Frontend Development - Build user interface for recommendations

See `docs/CURRENT_STATUS.md` for detailed next steps and decision points.

## Licens

TBD
