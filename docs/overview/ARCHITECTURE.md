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
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Cloud Storage  │    │  Cloud Storage  │
                       │   (Data Bucket) │    │  (Models Bucket)│
                       └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Web App API   │◀───│   Web Frontend  │
                       │   (FastAPI)     │    │   (Next.js)     │
                       │ Runtime Loading │    │   (Vercel)      │
                       └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   CI/CD Pipeline│    │   Vercel CDN    │
                       │ (GitHub Actions)│    │   (Frontend)    │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Cloud Run     │
                       │   (GCP)         │
                       └─────────────────┘
```

## Project Structure (Monorepo)

### Repository Organization

```text
igdb-project/                    # Monorepo Root
├── data_pipeline/              # Data Pipeline (Factory)
│   ├── ingestion/             # IGDB API data collection
│   ├── processing/            # Data cleaning & transformation
│   ├── training/              # ML model training
│   └── deployment/            # Model serving setup
├── web_app/                   # Web Application (Store)
│   ├── api/                   # FastAPI backend
│   └── frontend/              # Next.js frontend (Vercel)
├── shared/                    # Shared utilities
├── infrastructure/            # Terraform/Pulumi for GCP
├── docs/                      # Documentation
├── tests/                     # Test suites
├── models/                    # ML model files
├── data/                      # Local data storage
├── vercel.json               # Vercel configuration (in frontend/)
├── .vercelignore             # Vercel file exclusions
└── .gitignore                # Git file exclusions
```

### Monorepo Benefits

- **Unified Development**: All components in single repository
- **Shared Dependencies**: Common utilities and configurations
- **Atomic Changes**: Related changes across components
- **Simplified CI/CD**: Single pipeline for entire system
- **Context Preservation**: Full system view in IDE

### Deployment Strategy

- **Frontend**: Vercel (Next.js) - `web_app/frontend/`
- **Backend**: Google Cloud Run (FastAPI) - `web_app/api/`
- **Data Pipeline**: Google Cloud Run Jobs - `data_pipeline/`
- **Infrastructure**: Terraform - `infrastructure/`

## Data Pipeline (Factory)

### Data Pipeline Components

1. **Ingestion**: Collect data from IGDB API using SmartIngestion
2. **Processing**: Clean and transform raw data using DataTransformer
3. **Training**: Train ML models on processed data using MLTrainingService
4. **Deployment**: Serve trained models via FastAPI

### Data Flow

```text
IGDB API → Raw Data → Cleaned Data → Feature Extraction → Trained Model → Cloud Storage → Runtime Loading → API Serving
```

### ML Pipeline Components

1. **GameFeatureExtractor**: Extracts TF-IDF, categorical, and numerical features
2. **ContentBasedRecommendationModel**: Implements cosine similarity recommendations
3. **MLTrainingService**: Orchestrates training pipeline with validation
4. **Model Persistence**: Saves/loads models using pickle

## Web Application (Store)

### Web App Components

1. **API**: FastAPI backend serving recommendations
2. **Model Registry**: Cloud Storage integration with runtime loading
3. **Frontend**: User interface for search and recommendations (Future)
4. **Deployment**: Application hosting and scaling (Future)

### Request Flow

#### **Public Requests**
```text
User → API → Model Registry → Cloud Storage → ML Model → Recommendations → User
```

#### **Admin Requests** ✅ **IMPLEMENTED**
```text
User → /login → Google OAuth → /auth/callback → Session Created → /admin/status → Protected Data
```

### API Endpoints

#### **Public Endpoints**
- `GET /games/{id}/recommendations` - Get similar games by ID
- `POST /recommendations/text` - Text-based recommendations
- `GET /games/search` - Search games by name/summary
- `GET /games/{id}` - Get game details
- `GET /genres`, `/platforms` - List available options
- `GET /model/status` - Model health check
- `GET /health` - System health check

#### **Authentication Endpoints** ✅ **IMPLEMENTED**
- `GET /login` - Initiate Google OAuth flow
- `GET /auth/callback` - Handle OAuth callback and create session
- `POST /logout` - Clear session and logout user

#### **Protected Admin Endpoints** ✅ **IMPLEMENTED**
- `GET /admin/status` - Admin-only system overview (requires Google OAuth)
  - Returns system status, games count, model info, and user info
  - Protected by `get_current_user` dependency

## CI/CD Pipeline

### GitHub Actions Workflows

#### **CI Pipeline** (Continuous Integration)
- **Tests**: Unit tests, integration tests (41s)
- **Linting**: Black formatting, Flake8, pre-commit hooks
- **Container Builds**: All 4 services (ingestion, processing, training, api)
- **Container Registry**: Push to Google Container Registry (GCR)
- **Health Checks**: API containers test with GCP credentials
- **Security**: Bandit security scanning, safety vulnerability checks

#### **CD Pipeline** (Continuous Deployment)
- **Environment Management**: Staging/production environments
- **GCP Authentication**: Service account with environment secrets
- **Cloud Run Deployment**: Automated deployment to GCP
- **Health Checks**: Container startup and endpoint validation

#### **Test Pipeline** (Comprehensive Testing)
- **Unit Tests**: All passing with 100% success rate
- **Integration Tests**: Mock services and API testing
- **Docker Tests**: All containers build and test successfully
- **Security Tests**: Zero vulnerabilities (bandit + safety)
- **Performance Tests**: Disabled until test directory created

### Container Architecture

#### **Docker Services**
1. **igdb-ingestion**: Data collection from IGDB API
2. **igdb-processing**: Data cleaning and transformation
3. **igdb-training**: ML model training pipeline
4. **igdb-api**: FastAPI web application (port 8080)

#### **Container Registry**
- **Registry**: `europe-west1-docker.pkg.dev/igdb-recommendation-system/igdb-repo/`
- **Images**: Automatically built and pushed on main branch
- **Tags**: Latest, commit SHA, branch names

## Infrastructure

### Current Implementation

- **SQLite**: Local data storage for development
- **Cloud Storage**: Production data and model storage
- **Pickle**: Model serialization and storage
- **FastAPI**: Local API serving (port 8000) / Cloud Run (port 8080)
- **Docker**: Containerization (fully configured)
- **GitHub Actions**: CI/CD automation (all pipelines working)
- **Google Container Registry**: Image storage (working)
- **Cloud Run**: Deployment target (working)

### Cloud Storage Integration

- **Data Bucket**: `gs://igdb-recommendation-system-data`
- **Models Bucket**: `gs://igdb-recommendation-system-models`
- **Runtime Loading**: API loads data/models from Cloud Storage at startup
- **Graceful Fallback**: Local data backup if Cloud Storage unavailable
- **Health Monitoring**: GCS connectivity and data accessibility checks

### Cloud Run Jobs Pipeline

#### **Pipeline Jobs**
1. **igdb-ingestion**:
   - **Purpose**: Data collection from IGDB API
   - **Schedule**: Daily at 02:00 Europe/Stockholm via Cloud Scheduler
   - **Resources**: 1 CPU, 1Gi memory, 1 hour timeout
   - **Output**: Smart ingestion to SQLite database
   - **GCS Integration**: Optional upload to data bucket

2. **igdb-processing**:
   - **Purpose**: Data cleaning and transformation
   - **Trigger**: Manual or scheduled execution
   - **Resources**: 1 CPU, 1Gi memory, 30 minutes timeout
   - **Input**: Raw data from ingestion
   - **Output**: Cleaned data to GCS data bucket

3. **igdb-training**:
   - **Purpose**: ML model training
   - **Trigger**: Manual or scheduled execution
   - **Resources**: 2 CPU, 2Gi memory, 1 hour timeout
   - **Input**: Cleaned data from processing
   - **Output**: Trained models to GCS models bucket

#### **Cloud Scheduler**
- **Job**: `igdb-ingestion-scheduler`
- **Schedule**: `0 2 * * *` (Daily at 02:00 Europe/Stockholm)
- **Target**: HTTP POST to Cloud Run Jobs API
- **Authentication**: OIDC token with service account
- **Status**: Active and functional

#### **Secret Management**
- **Secrets**: `IGDB_CLIENT_ID`, `IGDB_CLIENT_SECRET`
- **Access**: Cloud Run Jobs via Secret Manager
- **IAM**: Service account with `roles/secretmanager.secretAccessor`
- **Security**: Encrypted at rest and in transit

### Future GCP Services

- **BigQuery**: Processed data warehouse
- **Cloud Functions**: Event-driven processing
- **Cloud Composer**: Data pipeline orchestration
- **Cloud Monitoring**: Application observability

### Deployment Status

- **Docker**: ✅ Fully working
- **GitHub Actions**: ✅ All pipelines working (CI ✓, CD ✓, Test ✓)
- **Container Registry**: ✅ Working
- **Cloud Run**: ✅ Working
- **Cloud Storage**: ✅ Working
- **Security**: ✅ Zero vulnerabilities
- **Terraform**: Future infrastructure as code
