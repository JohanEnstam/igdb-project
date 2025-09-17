# Data Flow Documentation

## Data Pipeline Flow

### 1. Ingestion Phase

```text
External API (IGDB) → Smart Ingestion → Database → Cloud Storage Backup
```

- **Frequency**: Smart fetching (avoid re-fetching existing data)
- **Data Format**: JSON responses from IGDB API
- **Deduplication**: Database constraints prevent duplicate games
- **Storage**: Primary in SQLite (dev) / PostgreSQL (prod), backup in Cloud Storage
- **Rate Limiting**: 4 requests/second (IGDB API limit)
- **Scaling**: Same code works for 100 games and 350k games

### 2. Processing Phase

```text
Database → Data Validation → Cleaning → Transformation → Training Data
```

- **Validation**: Check data quality and completeness
- **Cleaning**: Remove duplicates, handle missing values
- **Transformation**: Normalize data structure for ML training
- **Storage**: Processed data ready for ML training (BigQuery in production)

### 3. Training Phase

```text
Training Data → Feature Engineering → Model Training → Trained Model
```

- **Feature Engineering**: Create features for recommendation algorithm
- **Training**: Train ML model (content-based filtering for game recommendations)
- **Output**: Serialized model ready for serving
- **Scaling**: Same training pipeline for 100 games and 350k games

### 4. Deployment Phase

```text
Trained Model → Model Serving → API Endpoints
```

- **Model Serving**: Deploy model to Cloud Run
- **API Endpoints**: Expose model predictions via REST API
- **Monitoring**: Track model performance and drift

## Web Application Flow

### 1. User Request

```text
User → Frontend → API Gateway → Recommendation Service
```

### 2. Recommendation Generation

```text
User Query → Feature Extraction → Model Prediction → Ranking → Response
```

- **Feature Extraction**: Convert user input to model features
- **Model Prediction**: Get recommendations from ML model
- **Ranking**: Sort and filter recommendations
- **Response**: Return formatted recommendations to user

## Data Dependencies

### External Dependencies

- **IGDB API**: Source of game data
- **Rate Limits**: API calls per hour/day
- **Data Schema**: Game metadata, reviews, ratings

### Internal Dependencies

- **Data Pipeline**: Must complete before model training
- **Model Training**: Must complete before web app can serve recommendations
- **Data Quality**: Processing must handle missing/invalid data gracefully
