# 🧠 ML Workflow Documentation - IGDB Game Recommendation System

## Overview

This document provides a comprehensive overview of the complete Machine Learning workflow in the IGDB Game Recommendation System. The system implements a content-based recommendation approach using TF-IDF features, categorical features, and cosine similarity.

## Architecture Overview

The ML workflow is divided into four main phases:

1. **Data Ingestion** - Smart collection from IGDB API
2. **Data Processing** - Transformation to ML-ready format
3. **ML Training** - Feature extraction and model training
4. **Model Serving** - Runtime loading and API serving

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   IGDB API      │───▶│  SmartIngestion │───▶│   SQLite DB     │
│   (External)    │    │  (Rate Limited) │    │   (Local Dev)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Cloud Storage  │    │ DataTransformer │
                       │   (Data Bucket)│    │  (ID Resolution)│
                       └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ GameFeatureExtr │───▶│RecommendationMod│
                       │ (TF-IDF + Cat)  │    │ (Cosine Similar)│
                       └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Cloud Storage  │    │   ModelRegistry │
                       │ (Models Bucket) │    │ (Runtime Load)  │
                       └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   FastAPI App   │◀───│   Web Frontend  │
                       │ (Real-time API) │    │   (Future)      │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Cloud Run     │
                       │   (GCP Deploy)  │
                       └─────────────────┘
```

---

## 📊 Phase 1: Data Ingestion (SmartIngestion)

### Components

- **SmartIngestion** (`data_pipeline/ingestion/smart_ingestion.py`)
- **IGDBDataIngestion** (`data_pipeline/ingestion/main.py`)
- **DataManager** (`data_pipeline/shared/data_manager.py`)

### Process Flow

```text
IGDB API → Rate Limiting → Smart Fetching → SQLite Database → Cloud Storage
```

### Key Features

#### Smart Fetching
- **Avoids re-fetching**: Checks existing data before making API calls
- **Efficiency tracking**: Logs ingestion efficiency (new games / total fetched)
- **Batch tracking**: Each ingestion session gets a unique batch ID

#### Rate Limiting
- **IGDB API limit**: 4 requests/second
- **Respectful fetching**: Built-in delays between requests
- **Error handling**: Retry logic for failed requests

#### Fetching Strategies

1. **Balanced Strategy** (default)
   ```python
   # General game sampling across all criteria
   query = "fields id,name,summary,genres,platforms,themes,rating,rating_count,first_release_date; where summary != null; limit {count};"
   ```

2. **High-Rated Strategy**
   ```python
   # Games with rating >= 80
   query = "fields id,name,summary,genres,platforms,themes,rating,rating_count,first_release_date; where rating >= 80 & summary != null; limit {count}; sort rating desc;"
   ```

3. **Recent Strategy**
   ```python
   # Games released in the last year
   current_timestamp = int(time.time())
   one_year_ago = current_timestamp - (365 * 24 * 60 * 60)
   query = "fields id,name,summary,genres,platforms,themes,rating,rating_count,first_release_date; where first_release_date >= {one_year_ago} & summary != null; limit {count}; sort first_release_date desc;"
   ```

4. **Representative Strategy**
   ```python
   # Stratified sampling across genres, ratings, and platforms
   strategies = [
       ("high_rated", 25%),      # rating >= 80
       ("genre_diverse", 35%),   # rating 60-85
       ("platform_diverse", 25%), # rating 50-80
       ("recent_games", 15%)     # last year
   ]
   ```

### Data Storage

- **Local Development**: SQLite database (`data/games.db`)
- **Production**: Cloud Storage (`gs://igdb-recommendation-system-data`)
- **Deduplication**: Database constraints prevent duplicate games
- **Batch Logging**: All ingestion activities logged with metadata

### Usage Examples

```python
# Basic smart ingestion
with DataManager("data/games.db") as dm:
    si = SmartIngestion(dm, client_id="xxx", client_secret="yyy")
    count = si.fetch_if_needed(100)  # Fetch up to 100 games

# Strategy-based fetching
count = si.fetch_with_strategy("high_rated", 200)

# Representative dataset for ML training
count = si.fetch_representative_dataset(2000)

# Get ingestion summary
summary = si.get_ingestion_summary()
print(f"Efficiency: {summary['efficiency']}%")
```

---

## 🔄 Phase 2: Data Processing (DataTransformer)

### Components

- **DataTransformer** (`data_pipeline/processing/data_transformer.py`)

### Process Flow

```text
Raw IGDB Data → ID Resolution → Data Cleaning → Feature Engineering → ML-Ready Data
```

### Transformations

#### ID Resolution
Converts IGDB API IDs to human-readable names:

```python
# Genre ID resolution
genre_lookup = {
    2: "Point-and-click",
    4: "Fighting",
    5: "Shooter",
    7: "Music",
    8: "Platform",
    9: "Puzzle",
    10: "Racing",
    11: "Real Time Strategy (RTS)",
    12: "Role-playing (RPG)",
    # ... more mappings
}

# Platform ID resolution
platform_lookup = {
    6: "PC (Microsoft Windows)",
    7: "PlayStation",
    8: "PlayStation 2",
    9: "PlayStation 3",
    48: "PlayStation 4",
    130: "Nintendo Switch",
    167: "PlayStation 5",
    # ... more mappings
}
```

#### Data Cleaning
- **Text normalization**: Lowercase, strip whitespace
- **Missing value handling**: Default values for missing fields
- **Date conversion**: Unix timestamps to readable dates
- **Rating normalization**: Round to 1 decimal place

#### Feature Engineering

```python
# Quality indicators
clean_game["has_summary"] = bool(clean_game["summary"])
clean_game["has_rating"] = clean_game["rating"] is not None
clean_game["has_genres"] = len(clean_game["genre_names"]) > 0
clean_game["has_platforms"] = len(clean_game["platform_names"]) > 0

# Text length features
clean_game["summary_length"] = len(clean_game["summary"])
clean_game["name_length"] = len(clean_game["name"])

# Date features
clean_game["release_year"] = extract_year(release_timestamp)
clean_game["release_date"] = format_date(release_timestamp)
```

### Output Format

```json
{
  "id": 239060,
  "name": "Grand Theft Auto V: Story Mode",
  "summary": "Grand Theft Auto V: Story Mode is an add-on...",
  "genre_names": ["Shooter", "Arcade"],
  "platform_names": ["PlayStation 5", "Xbox One"],
  "theme_names": ["Action", "Battle Royale"],
  "rating": 99.9,
  "rating_count": 9,
  "release_date": "2022-03-15",
  "release_year": 2022,
  "summary_length": 45,
  "name_length": 28,
  "has_summary": true,
  "has_rating": true,
  "has_genres": true,
  "has_platforms": true,
  "genre_ids": [5, 33],
  "platform_ids": [169, 167],
  "theme_ids": [1, 38]
}
```

### Data Quality Report

```python
# Generate quality metrics
report = transformer.get_data_quality_report(clean_games)
# Returns:
{
  "total_games": 1230,
  "quality_score": 87.5,  # 0-100 scale
  "has_summary": "1150/1230 (93.5%)",
  "has_rating": "980/1230 (79.7%)",
  "has_genres": "1200/1230 (97.6%)",
  "has_platforms": "1180/1230 (95.9%)",
  "avg_rating": 72.3,
  "avg_genres_per_game": 2.8,
  "avg_platforms_per_game": 3.2
}
```

---

## 🤖 Phase 3: ML Training (FeatureExtractor + RecommendationModel)

### Components

- **GameFeatureExtractor** (`data_pipeline/training/feature_extractor.py`)
- **ContentBasedRecommendationModel** (`data_pipeline/training/recommendation_model.py`)
- **MLTrainingService** (`data_pipeline/training/main.py`)

### Process Flow

```text
Clean Data → Feature Extraction → Model Training → Validation → Model Serialization
```

### Feature Extraction

#### Text Features (TF-IDF)

```python
# Summary features
summary_config = {
    "max_features": 1000,
    "ngram_range": (1, 2),  # Unigrams and bigrams
    "min_df": 2,            # Ignore terms appearing in <2 documents
    "max_df": 0.95,         # Ignore terms appearing in >95% of documents
    "stop_words": "english"
}

# Name features
name_config = {
    "max_features": 500,
    "ngram_range": (1, 2),
    "min_df": 1,
    "max_df": 0.9,
    "stop_words": "english"
}

# Combined text processing
combined_text = " ".join([summary_text, name_text])
tfidf_matrix = TfidfVectorizer(**summary_config).fit_transform(combined_text)
```

#### Categorical Features

```python
# Label encoding for categorical variables
categorical_features = ["genre_names", "platform_names", "theme_names"]

# Handle multiple values per game
for feature_name in categorical_features:
    values = game.get(feature_name, [])
    if isinstance(values, list):
        # Join multiple values with separator
        feature_values.append("|".join(str(v) for v in values))
    else:
        feature_values.append(str(values) if values else "")

# Encode with LabelEncoder
le = LabelEncoder()
encoded_col = le.fit_transform(feature_values)
```

#### Numerical Features

```python
# StandardScaler normalization
numerical_features = [
    "rating",           # Game rating (0-100)
    "rating_count",     # Number of ratings
    "release_year",     # Year of release
    "summary_length"    # Length of summary text
]

# Scale features to mean=0, std=1
scaler = StandardScaler()
scaled_features = scaler.fit_transform(numerical_matrix)
```

### Model Architecture

#### Content-Based Filtering

```python
class ContentBasedRecommendationModel:
    def __init__(self, config=None):
        self.config = config or self._get_default_config()
        self.feature_extractor = GameFeatureExtractor()
        self.similarity_matrix = None

    def _get_default_config(self):
        return {
            "similarity_weights": {
                "text_similarity": 0.4,        # TF-IDF features
                "categorical_similarity": 0.3,  # Genres/platforms/themes
                "rating_similarity": 0.3       # Rating-based weighting
            },
            "min_rating_threshold": 70.0,
            "max_recommendations": 20
        }
```

#### Training Process

```python
def train(self, games):
    # 1. Prepare and filter data
    self.games_data = self.prepare_data(games)

    # 2. Extract all features
    self.game_features, feature_names = self.feature_extractor.extract_all_features(
        self.games_data
    )

    # 3. Calculate similarity matrix
    self.similarity_matrix = cosine_similarity(self.game_features)

    # 4. Calculate training metrics
    training_metrics = self._calculate_training_metrics()

    return {
        "training_samples": len(self.games_data),
        "feature_count": self.game_features.shape[1],
        "metrics": training_metrics
    }
```

#### Training Metrics

```python
def _calculate_training_metrics(self):
    # Remove self-similarity (diagonal)
    np.fill_diagonal(self.similarity_matrix, 0)

    return {
        "avg_similarity": float(np.mean(self.similarity_matrix)),
        "max_similarity": float(np.max(self.similarity_matrix)),
        "min_similarity": float(np.min(self.similarity_matrix)),
        "rating_stats": {
            "avg_rating": np.mean(ratings),
            "min_rating": np.min(ratings),
            "max_rating": np.max(ratings),
            "games_with_ratings": len(ratings)
        }
    }
```

### Model Performance

- **Training time**: <0.5s on 1230 games
- **Model size**: ~23MB (serialized)
- **Feature count**: ~1500+ features (text + categorical + numerical)
- **Memory usage**: Efficient sparse matrices for TF-IDF
- **Scalability**: Linear scaling with data size

### Model Serialization

```python
# Save model and feature extractor
model_data = {
    "config": self.config,
    "games_data": self.games_data,
    "game_features": self.game_features,
    "similarity_matrix": self.similarity_matrix,
    "is_trained": self.is_trained
}

# Save separately for modularity
pickle.dump(model_data, open("recommendation_model.pkl", "wb"))
self.feature_extractor.save_model("recommendation_model_feature_extractor.pkl")
```

---

## 🚀 Phase 4: Model Serving (ModelRegistry + FastAPI)

### Components

- **ModelRegistry** (`web_app/model_registry.py`)
- **FastAPI Application** (`web_app/api/main.py`)

### Process Flow

```text
Cloud Storage → Runtime Loading → Model Initialization → API Endpoints → Real-time Recommendations
```

### Model Loading

#### Cloud Storage Integration

```python
class ModelRegistry:
    def __init__(self,
                 data_bucket="igdb-recommendation-system-data",
                 models_bucket="igdb-recommendation-system-models"):
        self.storage_client = storage.Client()
        self.data_bucket = self.storage_client.bucket(data_bucket)
        self.models_bucket = self.storage_client.bucket(models_bucket)

    def get_games_data(self):
        # Download from Cloud Storage with local fallback
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_file:
            if self._download_file(self.data_bucket, "games_clean.json", tmp_file.name):
                with open(tmp_file.name, "r") as f:
                    games_data = json.load(f)
                return games_data
            else:
                return self._load_local_games_data()  # Graceful fallback
```

#### Runtime Initialization

```python
@app.on_event("startup")
async def startup_event():
    global recommendation_model, games_data, model_registry

    # Initialize model registry
    model_registry = ModelRegistry()

    # Load games data
    games_data = model_registry.get_games_data()

    # Load recommendation model
    model_path = model_registry.get_model_path("recommendation_model.pkl")
    feature_extractor_path = model_registry.get_model_path(
        "recommendation_model_feature_extractor.pkl"
    )

    # Initialize and load model
    recommendation_model = ContentBasedRecommendationModel()
    recommendation_model.load_model(model_path)
```

### API Endpoints

#### Recommendation Endpoints

1. **Game-based Recommendations**
   ```python
   @app.get("/games/{game_id}/recommendations")
   async def get_game_recommendations(game_id: int, top_k: int = 10):
       recommendations = recommendation_model.get_recommendations(game_id, top_k=top_k)
       return [GameRecommendation(**rec) for rec in recommendations]
   ```

2. **Text-based Recommendations**
   ```python
   @app.post("/recommendations/text")
   async def get_text_recommendations(request: TextRecommendationRequest):
       recommendations = recommendation_model.get_similar_games_by_text(
           request.query, top_k=request.top_k
       )
       return [GameRecommendation(**rec) for rec in recommendations]
   ```

#### Search Endpoints

3. **Game Search**
   ```python
   @app.get("/games/search")
   async def search_games(query: str, limit: int = 20):
       query_lower = query.lower()
       matching_games = []

       for game in games_data:
           name_match = query_lower in game.get("name", "").lower()
           summary_match = query_lower in game.get("summary", "").lower()

           if name_match or summary_match:
               matching_games.append(game)
               if len(matching_games) >= limit:
                   break

       return [GameInfo(**game) for game in matching_games]
   ```

#### Metadata Endpoints

4. **Game Information**
   ```python
   @app.get("/games/{game_id}")
   async def get_game_info(game_id: int):
       game = next((g for g in games_data if g["id"] == game_id), None)
       if not game:
           raise HTTPException(status_code=404, detail="Game not found")
       return GameInfo(**game)
   ```

5. **Lists and Status**
   ```python
   @app.get("/genres")          # List all genres
   @app.get("/platforms")      # List all platforms
   @app.get("/model/status")    # Model health and metrics
   @app.get("/health")         # API health check
   ```

### Recommendation Generation

#### Game-based Recommendations

```python
def get_recommendations(self, game_id: int, top_k: int = 10):
    # Find game index in training data
    game_idx = None
    for i, game in enumerate(self.games_data):
        if game["id"] == game_id:
            game_idx = i
            break

    if game_idx is None:
        raise ValueError(f"Game with ID {game_id} not found")

    # Get similarity scores
    similarities = self.similarity_matrix[game_idx]

    # Sort by similarity (descending)
    similar_indices = np.argsort(similarities)[::-1]

    # Build recommendations list
    recommendations = []
    for idx in similar_indices:
        if idx == game_idx:  # Skip the game itself
            continue

        similarity_score = similarities[idx]
        game = self.games_data[idx]

        recommendations.append({
            "game_id": game["id"],
            "name": game["name"],
            "similarity_score": float(similarity_score),
            "rating": game.get("rating", 0),
            "genres": game.get("genre_names", []),
            "platforms": game.get("platform_names", []),
            "summary": game.get("summary", "")[:200] + "..."
        })

        if len(recommendations) >= top_k:
            break

    return recommendations
```

#### Text-based Recommendations

```python
def get_similar_games_by_text(self, query_text: str, top_k: int = 10):
    # Create dummy game with query text
    dummy_game = {
        "id": -1,
        "name": "Query",
        "summary": query_text,
        "genre_names": [],
        "platform_names": [],
        "theme_names": [],
        "rating": 0,
        "rating_count": 0,
        "release_year": 2024,
        "summary_length": len(query_text)
    }

    # Extract features using fitted feature extractor
    query_features, _ = self.feature_extractor.extract_all_features([dummy_game])

    # Calculate similarity with all games
    similarities = cosine_similarity(query_features, self.game_features)[0]

    # Get top-k similar games
    similar_indices = np.argsort(similarities)[::-1]
    recommendations = []

    for idx in similar_indices:
        similarity_score = similarities[idx]
        game = self.games_data[idx]

        recommendations.append({
            "game_id": game["id"],
            "name": game["name"],
            "similarity_score": float(similarity_score),
            "rating": game.get("rating", 0),
            "genres": game.get("genre_names", []),
            "platforms": game.get("platform_names", []),
            "summary": game.get("summary", "")[:200] + "..."
        })

        if len(recommendations) >= top_k:
            break

    return recommendations
```

### Performance Characteristics

- **Response time**: <100ms per recommendation
- **Memory usage**: Efficient sparse matrices
- **Scalability**: Same code works for 100 games and 350k games
- **Concurrent requests**: FastAPI handles multiple requests efficiently
- **Graceful fallback**: Local data if Cloud Storage unavailable

### Health Monitoring

```python
@app.get("/health")
async def health_check():
    health_info = {
        "status": "healthy",
        "model_loaded": str(recommendation_model is not None),
        "games_count": str(len(games_data)),
        "port": str(os.environ.get("PORT", "8080"))
    }

    # Add Cloud Storage status
    if model_registry:
        registry_health = model_registry.health_check()
        health_info["gcs_available"] = str(registry_health.get("gcs_available", False))
        health_info["data_accessible"] = str(registry_health.get("data_accessible", False))
        health_info["models_accessible"] = str(registry_health.get("models_accessible", False))

    return health_info
```

---

## 📈 Performance & Scaling

### Current Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Training Time | <0.5s | On 1230 games |
| Model Size | ~23MB | Serialized pickle |
| Feature Count | ~1500+ | Text + categorical + numerical |
| Response Time | <100ms | Per recommendation |
| Memory Usage | Efficient | Sparse TF-IDF matrices |
| Concurrent Requests | High | FastAPI async handling |

### Scaling Characteristics

#### Linear Scaling
- **Training time**: Scales linearly with number of games
- **Memory usage**: Scales linearly with feature count
- **Response time**: Constant regardless of dataset size
- **Storage**: Models and data scale proportionally

#### Cloud Scaling
- **Horizontal scaling**: Multiple Cloud Run instances
- **Auto-scaling**: Based on request volume
- **Load balancing**: Automatic request distribution
- **Resource optimization**: Right-sized containers

### Data Quality Impact

```python
# Quality filtering during training
def prepare_data(self, games):
    filtered_games = []
    for game in games:
        # Must have summary and at least one genre
        if (game.get("has_summary", False) and
            game.get("has_genres", False) and
            game.get("summary", "").strip()):
            filtered_games.append(game)

    return filtered_games
```

**Quality Requirements**:
- Summary text: Required for TF-IDF features
- Genres: Required for categorical features
- Rating: Optional but improves recommendations
- Platforms: Optional but adds diversity

---

## 🛠️ Development Workflow

### Local Development

```bash
# 1. Data Ingestion
python -m data_pipeline.ingestion.main --smart --limit 100

# 2. Data Processing
python -m data_pipeline.processing.main --batch-size 100

# 3. ML Training
python -m data_pipeline.training.main --data-path data/games_clean.json

# 4. API Serving
uvicorn web_app.api.main:app --reload
```

### Docker Development

```bash
# Build all services
docker build -f data_pipeline/ingestion/Dockerfile -t igdb-ingestion .
docker build -f data_pipeline/processing/Dockerfile -t igdb-processing .
docker build -f data_pipeline/training/Dockerfile -t igdb-training .
docker build -f web_app/Dockerfile -t igdb-api .

# Run with docker-compose
docker-compose up
```

### Production Deployment

```bash
# CI/CD Pipeline (GitHub Actions)
# 1. Build containers
# 2. Run tests
# 3. Push to Container Registry
# 4. Deploy to Cloud Run
# 5. Health checks
```

### Testing

```bash
# Unit tests
pytest tests/

# Integration tests
pytest tests/integration/

# API tests
curl http://localhost:8000/health
curl http://localhost:8000/games/123/recommendations
```

---

## 🎯 Key Technical Decisions

### Algorithm Choice: Content-Based Filtering

**Why Content-Based?**
- **No user data required**: Works without user interaction history
- **Interpretable**: Easy to understand why games are recommended
- **Fast inference**: Cosine similarity is computationally efficient
- **Cold start friendly**: Works for new games immediately

**Alternative Approaches Considered**:
- **Collaborative Filtering**: Requires user interaction data
- **Deep Learning**: More complex, harder to interpret
- **Hybrid Approaches**: Future enhancement opportunity

### Feature Engineering Strategy

**Text Features (TF-IDF)**:
- **Robust**: Handles varying text lengths and quality
- **Scalable**: Efficient sparse matrix representation
- **Interpretable**: Can identify important terms

**Categorical Features**:
- **Label Encoding**: Simple and effective for genres/platforms
- **Multi-value handling**: Games can have multiple genres/platforms
- **Unknown category handling**: Graceful fallback for new categories

**Numerical Features**:
- **StandardScaler**: Normalizes different scales (rating vs year)
- **Missing value handling**: Default values for incomplete data
- **Feature selection**: Only meaningful numerical features included

### Model Architecture

**Cosine Similarity**:
- **Intuitive**: Measures angle between feature vectors
- **Efficient**: Fast computation with numpy/scikit-learn
- **Normalized**: Results in 0-1 similarity scores
- **Scalable**: Works with any number of features

**Similarity Matrix Pre-computation**:
- **Fast inference**: Pre-computed during training
- **Memory trade-off**: Stores N×N matrix for N games
- **Update strategy**: Retrain when new games added

### Deployment Strategy

**Cloud Storage Integration**:
- **Separation of concerns**: Data separate from application code
- **Runtime loading**: Models loaded at application startup
- **Graceful fallback**: Local data if cloud unavailable
- **Version management**: Easy model updates

**Container Architecture**:
- **Microservices**: Separate containers for each phase
- **Consistent environment**: Same code works locally and in cloud
- **Scalable**: Independent scaling of each service
- **CI/CD friendly**: Automated build and deployment

---

## 🔮 Future Enhancements

### Model Improvements

1. **Hybrid Approaches**
   - Combine content-based with collaborative filtering
   - User preference learning
   - Session-based recommendations

2. **Advanced Features**
   - Image features from game screenshots
   - Temporal features (release trends)
   - Social features (community ratings)

3. **Model Optimization**
   - Incremental learning for new games
   - Online learning for user feedback
   - A/B testing framework

### Infrastructure Enhancements

1. **Real-time Processing**
   - Stream processing for new games
   - Event-driven model updates
   - Real-time feature computation

2. **Advanced Monitoring**
   - Model performance tracking
   - Recommendation quality metrics
   - User engagement analytics

3. **Scalability Improvements**
   - Distributed training
   - Model serving optimization
   - Caching strategies

---

## 📚 References

- [IGDB API Documentation](https://api-docs.igdb.com/)
- [scikit-learn TF-IDF](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Cloud Storage](https://cloud.google.com/storage)
- [Content-Based Filtering](https://en.wikipedia.org/wiki/Recommender_system#Content-based_filtering)

---

*This document is maintained as part of the IGDB Game Recommendation System project. Last updated: 2024*
