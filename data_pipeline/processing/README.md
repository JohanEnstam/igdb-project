# 🔄 Data Pipeline - Processing Module

**Syfte**: Bearbetar och transformerar rådata till clean format

## 📁 Innehåll

- `main.py` - CLI för databearbetning
- `data_transformer.py` - Data cleaning & transformation logic
- `Dockerfile` - Container för bearbetning

## 🚀 Användning

```bash
# Transformera all data
python -m data_pipeline.processing.main --transform-all

# Generera kvalitetsrapport
python -m data_pipeline.processing.main --quality-report
```

## 🔧 Konfiguration

- **Input**: Raw data från `data/games.db`
- **Output**: Clean data till `data/games_clean.json` och `data/games_clean.csv`
- **Cloud Storage**: Optional upload till GCS

## 📊 Features

- ✅ Data cleaning och validation
- ✅ Feature engineering
- ✅ Quality reporting
- ✅ Cloud Storage integration
- ✅ Docker containerization
