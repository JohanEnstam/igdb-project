# System Architecture

## High-Level Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   External API  │───▶│  Data Pipeline  │───▶│   ML Models     │
│   (Game Data)   │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Data Storage  │    │  Model Serving  │
                       │   (BigQuery)     │    │   (Cloud Run)   │
                       └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Web App API   │◀───│   Web Frontend  │
                       │   (FastAPI)     │    │    (React)      │
                       └─────────────────┘    └─────────────────┘
```

## Data Pipeline (Factory)

### Components
1. **Ingestion**: Collect data from external APIs
2. **Processing**: Clean and transform raw data
3. **Training**: Train ML models on processed data
4. **Deployment**: Serve trained models

### Data Flow
```
External API → Raw Data → Cleaned Data → Training Data → Trained Model → Model Serving
```

## Web Application (Store)

### Components
1. **API**: Backend serving recommendations
2. **Frontend**: User interface for search and recommendations
3. **Deployment**: Application hosting and scaling

### Request Flow
```
User → Frontend → API → Model Serving → Recommendations → User
```

## Infrastructure

### GCP Services
- **Cloud Storage**: Raw data storage
- **BigQuery**: Processed data warehouse
- **Cloud Run**: Model serving and API hosting
- **Cloud Functions**: Event-driven processing
- **Cloud Composer**: Data pipeline orchestration

### Deployment
- **Terraform**: Infrastructure as Code
- **Docker**: Containerization
- **GitHub Actions**: CI/CD automation
