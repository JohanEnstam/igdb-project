# System Architecture

## High-Level Overview

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   External API  │───▶│  Data Pipeline  │───▶│   ML Pipeline   │
│   (IGDB API)    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Data Storage  │    │  Trained Model │
                       │   (SQLite)      │    │   (Pickle)      │
                       └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Web App API   │◀───│   Web Frontend  │
                       │   (FastAPI)     │    │    (Future)     │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   CI/CD Pipeline│
                       │ (GitHub Actions)│
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Cloud Run     │
                       │   (GCP)         │
                       └─────────────────┘
```

## Data Pipeline (Factory)

### Data Pipeline Components

1. **Ingestion**: Collect data from IGDB API using SmartIngestion
2. **Processing**: Clean and transform raw data using DataTransformer
3. **Training**: Train ML models on processed data using MLTrainingService
4. **Deployment**: Serve trained models via FastAPI

### Data Flow

```text
IGDB API → Raw Data → Cleaned Data → Feature Extraction → Trained Model → API Serving
```

### ML Pipeline Components

1. **GameFeatureExtractor**: Extracts TF-IDF, categorical, and numerical features
2. **ContentBasedRecommendationModel**: Implements cosine similarity recommendations
3. **MLTrainingService**: Orchestrates training pipeline with validation
4. **Model Persistence**: Saves/loads models using pickle

## Web Application (Store)

### Web App Components

1. **API**: FastAPI backend serving recommendations
2. **Frontend**: User interface for search and recommendations (Future)
3. **Deployment**: Application hosting and scaling (Future)

### Request Flow

```text
User → API → ML Model → Recommendations → User
```

### API Endpoints

- `GET /games/{id}/recommendations` - Get similar games by ID
- `POST /recommendations/text` - Text-based recommendations
- `GET /games/search` - Search games by name/summary
- `GET /games/{id}` - Get game details
- `GET /genres`, `/platforms` - List available options
- `GET /model/status` - Model health check

## CI/CD Pipeline

### GitHub Actions Workflows

#### **CI Pipeline** (Continuous Integration)
- **Tests**: Unit tests, integration tests (41s)
- **Linting**: Black formatting, Flake8, pre-commit hooks
- **Container Builds**: All 4 services (ingestion, processing, training, api)
- **Container Registry**: Push to Google Container Registry (GCR)
- **Security**: Trivy vulnerability scanning (currently disabled)

#### **CD Pipeline** (Continuous Deployment)
- **Environment Management**: Staging/production environments
- **GCP Authentication**: Service account with environment secrets
- **Cloud Run Deployment**: Automated deployment to GCP
- **Health Checks**: Container startup and endpoint validation

### Container Architecture

#### **Docker Services**
1. **igdb-ingestion**: Data collection from IGDB API
2. **igdb-processing**: Data cleaning and transformation
3. **igdb-training**: ML model training pipeline
4. **igdb-api**: FastAPI web application (port 8080)

#### **Container Registry**
- **Registry**: `gcr.io/igdb-recommendation-system/`
- **Images**: Automatically built and pushed on main branch
- **Tags**: Latest, commit SHA, branch names

## Infrastructure

### Current Implementation

- **SQLite**: Local data storage for development
- **Pickle**: Model serialization and storage
- **FastAPI**: Local API serving (port 8000) / Cloud Run (port 8080)
- **Docker**: Containerization (fully configured)
- **GitHub Actions**: CI/CD automation (working)
- **Google Container Registry**: Image storage (working)
- **Cloud Run**: Deployment target (configuration issues)

### Future GCP Services

- **Cloud Storage**: Raw data storage
- **BigQuery**: Processed data warehouse
- **Cloud Functions**: Event-driven processing
- **Cloud Composer**: Data pipeline orchestration

### Deployment Status

- **Docker**: ✅ Fully working
- **GitHub Actions**: ✅ CI working, CD has Cloud Run issues
- **Container Registry**: ✅ Working
- **Cloud Run**: ❌ Deployment timeout issues
- **Terraform**: Future infrastructure as code
