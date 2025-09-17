# Docker Compose Setup - Local Development

## 🐳 **Overview**

This document describes how to use Docker Compose for local development of the IGDB Game Recommendation System with microservices architecture.

## 🚀 **Quick Start**

### **Prerequisites**
- Docker and Docker Compose installed
- IGDB API credentials (create `.env` file)

### **Setup**
```bash
# 1. Clone repository
git clone <repository-url>
cd igdb-project

# 2. Create environment file
cp .env.example .env
# Edit .env with your IGDB credentials

# 3. Build and start services
make build
make up

# 4. Check status
make status
```

## 🏗️ **Architecture**

### **Services**
1. **data-ingestion** - Fetches game data from IGDB API
2. **data-processing** - Cleans and transforms data
3. **ml-training** - Trains recommendation models

### **Service Dependencies**
```
data-ingestion → data-processing → ml-training
```

### **Networking**
- All services communicate via `igdb-network`
- Services can reach each other by container name

## 📁 **File Structure**

```
igdb-project/
├── docker-compose.yml              # Main compose file
├── docker-compose.override.yml     # Development overrides
├── Makefile                        # Convenient commands
├── .env.example                    # Environment template
├── data/                           # Persistent data
│   ├── games.db                    # SQLite database
│   └── models/                     # Trained models
└── logs/                           # Application logs
```

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Required
IGDB_CLIENT_ID=your_client_id
IGDB_CLIENT_SECRET=your_client_secret

# Optional
DATABASE_URL=sqlite:///app/data/games.db
MODEL_STORAGE_PATH=/app/data/models
LOG_LEVEL=INFO
DEBUG=true
```

### **Volume Mounts**
- `./data:/app/data` - Persistent data storage
- `./logs:/app/logs` - Application logs
- `./data_pipeline:/app/data_pipeline` - Source code (development)

## 🛠️ **Available Commands**

### **Make Commands**
```bash
make help          # Show available commands
make build         # Build all images
make up            # Start all services
make down          # Stop all services
make logs          # Show logs
make clean         # Remove all containers/images
make test          # Run tests
make lint          # Run linting
make dev           # Start development environment
make prod          # Start production environment
```

### **Individual Services**
```bash
make ingestion     # Run data ingestion
make processing    # Run data processing
make training      # Run ML training
```

### **Database Commands**
```bash
make db-shell      # Open SQLite shell
```

## 🔍 **Monitoring**

### **Service Status**
```bash
# Check all services
make status

# View logs
make logs

# Follow specific service logs
docker-compose logs -f data-ingestion
```

### **Health Checks**
Each service includes health checks:
```bash
# Check service health
docker-compose ps
```

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Permission Denied**
   ```bash
   # Fix data directory permissions
   sudo chown -R $USER:$USER data/
   ```

2. **Port Conflicts**
   ```bash
   # Check if ports are in use
   lsof -i :8000
   ```

3. **Environment Variables**
   ```bash
   # Check environment variables
   docker-compose config
   ```

4. **Service Dependencies**
   ```bash
   # Check service dependencies
   docker-compose ps
   ```

### **Debugging**

1. **Service Logs**
   ```bash
   docker-compose logs data-ingestion
   ```

2. **Container Shell**
   ```bash
   docker-compose exec data-ingestion bash
   ```

3. **Database Access**
   ```bash
   make db-shell
   ```

## 🔄 **Development Workflow**

### **1. Start Development Environment**
```bash
make dev
```

### **2. Make Changes**
- Edit source code in `data_pipeline/`
- Changes are automatically reflected (volume mount)

### **3. Test Changes**
```bash
make test
make lint
```

### **4. Restart Services**
```bash
make down
make up
```

### **5. View Results**
```bash
make logs
make db-shell
```

## 🚀 **Production Deployment**

### **Local Production Test**
```bash
make prod
```

### **GCP Cloud Run Deployment**
```bash
# Deploy individual services
gcloud run deploy igdb-ingestion --source data_pipeline/ingestion/
gcloud run deploy igdb-processing --source data_pipeline/processing/
gcloud run deploy igdb-training --source data_pipeline/training/
```

## 📚 **References**

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Microservices Architecture](https://microservices.io/)
- [GCP Cloud Run](https://cloud.google.com/run)
