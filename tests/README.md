# 🧪 Tests - Test Suite Overview

**Syfte**: Alla tester för att säkerställa kodkvalitet

## 📁 Struktur

```
tests/
├── fixtures/           # 📁 Test Data
│   ├── mock_games.json # Mock data för tester
│   ├── test_*.db       # Test databaser
│   └── games_sample.json # Sample data
├── integration/        # 🔗 Integration Tests
│   └── test_data_pipeline.py
├── test_data_manager.py     # DataManager tests
├── test_data_transformer.py # DataTransformer tests
├── test_ml_pipeline.py      # ML pipeline tests
└── test_smart_ingestion.py  # SmartIngestion tests
```

## 🚀 Användning

```bash
# Kör alla tester
pytest tests/ -v

# Kör integration tester
pytest tests/integration/ -v

# Kör med coverage
pytest tests/ --cov=data_pipeline --cov-report=html

# Kör specifika tester
pytest tests/test_data_manager.py -v
```

## 📊 Test Coverage

- ✅ **DataManager**: Database operations, CRUD functionality
- ✅ **DataTransformer**: Data cleaning och transformation
- ✅ **ML Pipeline**: Model training och validation
- ✅ **SmartIngestion**: Intelligent data collection
- ✅ **Integration**: End-to-end pipeline testing

## 🔧 Test Configuration

- **pytest.ini**: Test configuration i root
- **fixtures/**: Test data och mock objects
- **Coverage**: HTML reports i `htmlcov/`
