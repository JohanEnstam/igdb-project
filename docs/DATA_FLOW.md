# Data Flow Documentation

## Data Pipeline Flow

### 1. Ingestion Phase
```
External API (IGDB) → Raw JSON Data → Cloud Storage Bucket
```
- **Frequency**: Daily/hourly depending on API limits
- **Data Format**: JSON responses from IGDB API
- **Storage**: Raw data in Cloud Storage for backup and reprocessing

### 2. Processing Phase
```
Raw Data → Data Validation → Cleaning → Transformation → BigQuery
```
- **Validation**: Check data quality and completeness
- **Cleaning**: Remove duplicates, handle missing values
- **Transformation**: Normalize data structure for ML training
- **Storage**: Processed data in BigQuery for analytics and training

### 3. Training Phase
```
BigQuery Data → Feature Engineering → Model Training → Trained Model
```
- **Feature Engineering**: Create features for recommendation algorithm
- **Training**: Train ML model (collaborative filtering, content-based, etc.)
- **Output**: Serialized model ready for serving

### 4. Deployment Phase
```
Trained Model → Model Serving → API Endpoints
```
- **Model Serving**: Deploy model to Cloud Run
- **API Endpoints**: Expose model predictions via REST API
- **Monitoring**: Track model performance and drift

## Web Application Flow

### 1. User Request
```
User → Frontend → API Gateway → Recommendation Service
```

### 2. Recommendation Generation
```
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
