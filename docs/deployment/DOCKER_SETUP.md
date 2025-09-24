# Docker Setup - Microservices Architecture

## 🐳 **Overview**

This document describes the Docker containerization setup for the IGDB Game Recommendation System using a microservices architecture.

## 🏗️ **Architecture**

### **Services**
1. **Data Ingestion Service** (`igdb-ingestion`)
   - Fetches game data from IGDB API
   - Handles rate limiting and error handling
   - Uses SmartIngestion for intelligent data collection

2. **Data Processing Service** (`igdb-processing`)
   - Cleans and transforms raw game data
   - Prepares data for ML training
   - Handles data validation and quality checks

3. **ML Training Service** (`igdb-training`)
   - Trains recommendation models
   - Validates model performance
   - Saves trained models for serving

## 🚀 **Quick Start**

### **Build All Services**
```bash
# Build ingestion service
docker build -f data_pipeline/ingestion/Dockerfile -t igdb-ingestion:latest .

# Build processing service
docker build -f data_pipeline/processing/Dockerfile -t igdb-processing:latest .

# Build training service
docker build -f data_pipeline/training/Dockerfile -t igdb-training:latest .
```

### **Run Individual Services**
```bash
# Run ingestion service
docker run --rm -v $(pwd)/data:/app/data \
  -e IGDB_CLIENT_ID=your_client_id \
  -e IGDB_CLIENT_SECRET=your_client_secret \
  igdb-ingestion:latest --smart --limit 100

# Run processing service
docker run --rm -v $(pwd)/data:/app/data \
  igdb-processing:latest --batch-size 100

# Run training service
docker run --rm -v $(pwd)/data:/app/data \
  igdb-training:latest --model-type collaborative_filtering
```

## 📁 **File Structure**

```
igdb-project/
├── data_pipeline/
│   ├── ingestion/
│   │   ├── Dockerfile          # Data ingestion service
│   │   ├── main.py
│   │   └── smart_ingestion.py
│   ├── processing/
│   │   ├── Dockerfile          # Data processing service
│   │   └── main.py
│   ├── training/
│   │   ├── Dockerfile          # ML training service
│   │   └── main.py
│   └── shared/
│       └── data_manager.py     # Shared SQLite database manager
├── requirements.txt            # Production dependencies
├── .dockerignore              # Docker build optimization
└── docs/
    └── DOCKER_SETUP.md        # This file
```

## 🔧 **Configuration**

### **Environment Variables**
- `IGDB_CLIENT_ID`: IGDB API client ID
- `IGDB_CLIENT_SECRET`: IGDB API client secret
- `DATABASE_URL`: SQLite database path (default: `/app/data/games.db`)

### **Volume Mounts**
- `./data:/app/data`: Mount local data directory for persistent storage

## 🏥 **Health Checks**

Each service includes a health check endpoint:
```bash
# Check service health
curl -f http://localhost:8000/health
```

## 🔒 **Security**

### **Non-root User**
All services run as non-root user `app` for security.

### **Minimal Base Image**
Uses `python:3.11-slim` for minimal attack surface.

### **Dependency Management**
Only production dependencies are installed in containers.

## 📊 **Resource Requirements**

### **Development (1000 games)**
- **Ingestion**: 512Mi RAM, 0.5 CPU
- **Processing**: 1Gi RAM, 1 CPU
- **Training**: 2Gi RAM, 2 CPU

### **Production (100,000+ games)**
- **Ingestion**: 1Gi RAM, 1 CPU
- **Processing**: 2Gi RAM, 2 CPU
- **Training**: 4Gi RAM, 4 CPU

## 🚀 **Next Steps**

1. **Docker Compose Setup** - Orchestrate multiple services
2. **GCP Cloud Run Deployment** - Deploy to production
3. **CI/CD Pipeline** - Automated builds and deployments
4. **Monitoring & Logging** - Production observability

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Permission Denied**
   ```bash
   # Fix data directory permissions
   sudo chown -R $USER:$USER data/
   ```

2. **Missing Environment Variables**
   ```bash
   # Check environment variables
   docker run --rm igdb-ingestion:latest env | grep IGDB
   ```

3. **Database Lock Issues**
   ```bash
   # Ensure only one service accesses database at a time
   # Use proper service orchestration
   ```

## 📚 **References**

- [Docker Documentation](https://docs.docker.com/)
- [Python Docker Best Practices](https://pythonspeed.com/docker/)
- [Microservices Architecture](https://microservices.io/)
- [GCP Cloud Run](https://cloud.google.com/run)
