# 🤖 Data Pipeline - Training Module

**Syfte**: Tränar ML-modeller för spelrekommendationer

## 📁 Innehåll

- `main.py` - CLI för modellträning
- `recommendation_model.py` - Content-based recommendation model
- `feature_extractor.py` - Feature engineering för ML
- `Dockerfile` - Container för träning

## 🚀 Användning

```bash
# Träna modell med clean data
python -m data_pipeline.training.main --data data/games_clean.json --model models/recommendation_model.pkl

# Träna med Cloud Storage data
python -m data_pipeline.training.main --gcs
```

## 🔧 Konfiguration

- **Input**: Clean data från `data/games_clean.json`
- **Output**: Trained models till `models/` directory
- **Cloud Storage**: Optional upload till GCS models bucket

## 📊 Features

- ✅ TF-IDF vectorization för text features
- ✅ Categorical encoding för genres/platforms
- ✅ Content-based filtering med cosine similarity
- ✅ Model validation och metrics
- ✅ Cloud Storage integration
- ✅ Docker containerization

## 🧠 ML Pipeline

1. **Feature Extraction**: TF-IDF + categorical + numerical features
2. **Model Training**: ContentBasedRecommendationModel
3. **Validation**: Training metrics och recommendation quality
4. **Persistence**: Pickle-based save/load
