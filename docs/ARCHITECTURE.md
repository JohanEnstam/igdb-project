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

## Infrastructure

### Current Implementation

- **SQLite**: Local data storage for development
- **Pickle**: Model serialization and storage
- **FastAPI**: Local API serving
- **Docker**: Containerization (configured)

### Future GCP Services

- **Cloud Storage**: Raw data storage
- **BigQuery**: Processed data warehouse
- **Cloud Run**: Model serving and API hosting
- **Cloud Functions**: Event-driven processing
- **Cloud Composer**: Data pipeline orchestration

### Deployment

- **Terraform**: Infrastructure as Code (Future)
- **Docker**: Containerization (Ready)
- **GitHub Actions**: CI/CD automation (Future)
