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
- **Data Pipeline**: Python, Apache Airflow/Cloud Composer
- **ML**: scikit-learn, TensorFlow/PyTorch
- **Web App**: TBD (React/Vue + FastAPI/Flask)
- **Infrastructure**: Terraform/Pulumi
- **CI/CD**: GitHub Actions

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

# Installera dependencies (kommer senare)
# pip install -r requirements.txt

# Kör lokalt (kommer senare)
# python -m data_pipeline.ingestion.main
```

## Status

✅ **Phase 2 Complete** - Data management and smart ingestion pipeline implemented

### **What's Working**
- **DataManager**: SQLite database with automatic deduplication
- **SmartIngestion**: Intelligent data fetching with re-fetching avoidance
- **IGDB Integration**: Robust API client with rate limiting (4 req/s)
- **Testing**: 24 comprehensive unit tests
- **Code Quality**: Pre-commit hooks, type hints, documentation

### **Quick Start**
```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Test smart ingestion (requires IGDB API credentials)
python -m data_pipeline.ingestion.main --smart --limit 100

# Run tests
pytest tests/ -v
```

### **Next Steps**
🎯 **Phase 3**: End-to-end testing with real IGDB API, ML pipeline development

See `docs/CURRENT_STATUS.md` for detailed next steps and decision points.

## Licens

TBD
