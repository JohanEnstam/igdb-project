# 📥 Data Pipeline - Ingestion Module

**Syfte**: Samlar speldata från IGDB API

## 📁 Innehåll

- `main.py` - CLI för datahämtning med olika strategier
- `smart_ingestion.py` - Intelligent datahämtning med DataManager
- `Dockerfile` - Container för datahämtning

## 🚀 Användning

```bash
# Smart ingestion (rekommenderat)
python -m data_pipeline.ingestion.main --smart --limit 100

# Mock data för testing
python -m data_pipeline.ingestion.main --mock

# Full production data
python -m data_pipeline.ingestion.main --full
```

## 🔧 Konfiguration

- **Environment**: `.env.local` med IGDB credentials
- **Database**: SQLite via DataManager
- **Output**: Raw data till `data/games.db`

## 📊 Features

- ✅ Smart ingestion med duplicat-hantering
- ✅ Batch tracking och efficiency metrics
- ✅ Graceful error handling
- ✅ Docker containerization
