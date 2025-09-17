# Data Flow Documentation

## Data Pipeline Flow

### 1. Ingestion Phase

```text
External API (IGDB) → Smart Ingestion → Database → Cloud Storage
```

- **Frequency**: Smart fetching (avoid re-fetching existing data)
- **Data Format**: JSON responses from IGDB API
- **Deduplication**: Database constraints prevent duplicate games
- **Storage**: Primary in SQLite (dev), production in Cloud Storage
- **Rate Limiting**: 4 requests/second (IGDB API limit)
- **Scaling**: Same code works for 100 games and 350k games
- **Cloud Storage**: Data uploaded to `gs://igdb-recommendation-system-data`

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
Training Data → Feature Extraction → Model Training → Trained Model → Cloud Storage
```

- **Feature Extraction**:
  - Text features: TF-IDF vectorization of summaries/names (1000 features)
  - Categorical features: One-hot encoding for genres, platforms, themes
  - Numerical features: Rating, rating count, release year, summary length
- **Model Training**: Content-based recommendation model with cosine similarity
- **Output**: Serialized model (pickle) ready for serving (~23MB)
- **Performance**: <0.5s training on 1230 games
- **Scaling**: Same training pipeline for 100 games and 350k games
- **Cloud Storage**: Models uploaded to `gs://igdb-recommendation-system-models`

### 4. Deployment Phase

```text
Cloud Storage → Model Registry → Runtime Loading → FastAPI Serving → API Endpoints
```

- **Model Registry**: Cloud Storage integration with runtime loading
- **Runtime Loading**: Load trained model from Cloud Storage at startup
- **Graceful Fallback**: Local data backup if Cloud Storage unavailable
- **API Serving**: FastAPI application with recommendation endpoints
- **API Endpoints**:
  - `GET /games/{id}/recommendations` - Game-based recommendations
  - `POST /recommendations/text` - Text-based recommendations
  - `GET /games/search` - Game search functionality
  - `GET /health` - Health check with GCS connectivity status
- **Performance**: Real-time recommendations (<100ms response time)
- **Monitoring**: Model health check with Cloud Storage status

## Web Application Flow

### 1. User Request

```text
User → Frontend → API Gateway → Recommendation Service
```

### 2. Recommendation Generation

```text
User Query → Feature Extraction → Model Prediction → Ranking → Response
```

- **Feature Extraction**:
  - For game ID: Extract features from existing game data
  - For text query: Extract features from query text using same TF-IDF vectorizer
- **Model Prediction**: Cosine similarity calculation with trained model
- **Ranking**: Sort by similarity score, filter by top_k parameter
- **Response**: Return formatted recommendations with game details

## Data Dependencies

### External Dependencies

- **IGDB API**: Source of game data
- **Rate Limits**: API calls per hour/day
- **Data Schema**: Game metadata, reviews, ratings

### Internal Dependencies

- **Data Pipeline**: Must complete before model training
- **Model Training**: Must complete before web app can serve recommendations
- **Data Quality**: Processing must handle missing/invalid data gracefully
