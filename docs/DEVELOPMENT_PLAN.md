# Development Plan - IGDB Game Recommendation System

## Overview
This document outlines the complete development strategy from local development to production deployment, including ML model training and data pipeline implementation.

## Development Phases

### Phase 1: Foundation Complete ✅
**Goal**: Professional development with environment consistency

**Environment Setup**:
```bash
# Virtual environment for IDE integration
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Docker environment for full stack testing
docker-compose up --build
```

**Development Approach**:
- **Docker-first**: Containerized development for environment consistency
- **Virtual environment**: IDE integration and pre-commit hooks
- **IGDB API integration**: Real data ingestion with rate limiting (4 req/s)
- **Modular architecture**: setup.py for professional project structure
- **Smart data management**: Avoid re-fetching with database-first approach

**ML Strategy**:
- **Content-based filtering**: Primary recommendation approach
- **Middle ground approach**: Develop with 10-100 games, scale to 350k
- **Feature priority**: Genres → Text → Platforms → Themes
- **Training time**: <1 minute for 100 games, scalable to 350k

**Data Scope**:
```python
# Development dataset (100 games)
development_strategy = {
    'start_small': 100_games,          # Fast iteration
    'scale_up': 10000_games,           # Testing
    'production': 350000_games,        # Full dataset
    'smart_fetching': avoid_refetching # Database management
}
```

### Phase 2: Data Management & Smart Ingestion ✅
**Goal**: Implement smart data management and end-to-end pipeline

**Completed**:
- ✅ DataManager with SQLite backend
- ✅ SmartIngestion with re-fetching avoidance
- ✅ IGDB API integration with rate limiting
- ✅ Comprehensive test suite (24 tests)
- ✅ Pre-commit hooks and code quality
- ✅ Context manager support
- ✅ Batch tracking and efficiency metrics

**Docker Setup**:
```yaml
# docker-compose.yml for full stack development
version: '3.8'
services:
  data-pipeline:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
      - ./data:/app/data
    environment:
      - PYTHONPATH=/app
  web-app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - PYTHONPATH=/app
```

**Benefits**:
- Environment consistency from day one
- Full stack testing capabilities
- Easy deployment preparation
- Professional development workflow

### Phase 3: End-to-End Testing & ML Pipeline (Current)
**Goal**: Test complete pipeline with real data and build ML components

### Phase 4: Cloud Deployment (When Docker works)
**Goal**: Production deployment on GCP

**Infrastructure**:
- **Terraform**: Infrastructure as Code
- **GCP Services**: Cloud Storage, BigQuery, Cloud Run
- **CI/CD**: GitHub Actions for automated deployment

## ML Model Architecture

### Content-Based Filtering Approach
**Why**: No user data required, interpretable, fast inference

**Features**:
1. **Genre Features** (Priority 1)
   - One-hot encoding
   - Genre combinations
   - High impact, fast training

2. **Text Description** (Priority 2)
   - TF-IDF vectors
   - Text embeddings
   - High impact, slower training

3. **Platform Features** (Priority 3)
   - Multi-hot encoding
   - Practical constraints
   - Medium impact, fast training

4. **Theme Features** (Priority 4)
   - One-hot encoding
   - Atmospheric preferences
   - Medium impact, medium training

### Model Training Pipeline
```python
# Feature extraction
features = {
    'genres': extract_genres(games),
    'platforms': extract_platforms(games),
    'ratings': extract_ratings(games),
    'description': extract_text_features(games)
}

# Model training
model = ContentBasedModel(features)
model.train()
model.save('models/game_recommender.pkl')
```

## Data Pipeline Architecture

### Ingestion Phase
```python
# IGDB API integration
- Rate limiting: 30 requests/second
- Stratified sampling for development
- Full dataset (350k games) for production
- Local JSON storage for development
```

### Processing Phase
```python
# Data cleaning and transformation
- Remove duplicates and incomplete records
- Normalize text data
- Feature engineering
- Quality validation
```

### Training Phase
```python
# ML model training
- Feature extraction
- Model training
- Validation and testing
- Model serialization
```

### Deployment Phase
```python
# Model serving
- REST API endpoints
- Recommendation generation
- Performance monitoring
```

## Development Workflow

### Local Development
```bash
# 1. Create feature branch
git checkout -b feature/data-ingestion

# 2. Develop in virtual environment (IDE integration)
source venv/bin/activate
pip install -e .
python -m data_pipeline.ingestion.main --mock

# 3. Test in Docker environment (integration testing)
docker-compose up --build
docker-compose run data-pipeline python -m data_pipeline.ingestion.main --mock

# 4. Run quality checks
pre-commit run --all-files
pytest

# 5. Commit changes
git add .
git commit -m "Add data ingestion pipeline"
```

### Docker Development
```bash
# 1. Build and run full stack
docker-compose up --build

# 2. Test API endpoints
curl http://localhost:8000/api/recommendations?game_id=123

# 3. Test frontend
open http://localhost:3000
```

### Cloud Deployment
```bash
# 1. Push to GitHub
git push origin feature/data-ingestion

# 2. GitHub Actions automatically:
# - Run tests
# - Deploy to staging
# - Run data quality checks

# 3. Production deployment
git checkout main
git merge feature/data-ingestion
# Automatic production deployment
```

## Performance Expectations

### Training Times (MacBook Pro 2019)
- **2000 games**: 2-5 minutes
- **5000 games**: 5-10 minutes
- **350k games**: 2-4 hours (production)

### API Rate Limits
- **IGDB API**: 4 requests/second (updated from documentation)
- **Full dataset**: ~24 hours to fetch all games (350k games)
- **Development dataset**: ~25 seconds to fetch 100 games
- **Smart ingestion**: Avoids re-fetching existing data

## Success Metrics

### Development Phase
- [x] Data ingestion working with IGDB API
- [x] Smart data management with SQLite
- [x] Comprehensive test coverage (24 tests)
- [ ] ML model training on 100 games
- [ ] Recommendation accuracy >70%
- [ ] Training time <5 minutes

### Docker Phase
- [ ] Full stack running locally
- [ ] API endpoints responding
- [ ] Frontend displaying recommendations
- [ ] Docker containers stable

### Production Phase
- [ ] GCP deployment successful
- [ ] Full dataset (350k games) processed
- [ ] API response time <200ms
- [ ] 99% uptime

## Next Steps

1. ✅ **Set up virtual environment**
2. ✅ **Create data ingestion script**
3. ✅ **Integrate IGDB API**
4. ✅ **Implement DataManager with SQLite**
5. ✅ **Create SmartIngestion to avoid re-fetching**
6. ✅ **Build comprehensive test suite**
7. 🎯 **Test end-to-end pipeline with real IGDB API**
8. 🎯 **Build ML pipeline (feature extraction, model training)**
9. 🎯 **Test scaling to 10k games**
10. **Docker integration**
11. **Cloud deployment**

## Notes

- **Virtual environment**: Essential for isolated development
- **Docker**: Preparation for production deployment
- **Cloud**: Final destination for scalability
- **ML focus**: Content-based filtering for simplicity and performance
- **Data strategy**: Stratified sampling for representative development dataset
