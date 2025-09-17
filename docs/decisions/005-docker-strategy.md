# ADR-005: Docker-First Development Strategy

## Status
Accepted

## Context
Need to choose development environment strategy that ensures:
- Environment consistency between local development and production
- Professional project structure from day one
- Easy integration testing and full stack development
- Scalable architecture for team collaboration

## Decision
Implement **Docker-First Development** with **Dual Environment** approach.

### Development Strategy: Docker-First
```bash
# Primary development environment
docker-compose up --build
docker-compose run data-pipeline python -m data_pipeline.ingestion.main --mock
```

### Dual Environment Approach
```bash
# Virtual Environment (IDE Integration)
source venv/bin/activate
pip install -e .
python -m data_pipeline.ingestion.main --mock

# Docker Environment (Integration Testing)
docker-compose up --build
docker-compose run data-pipeline python -m data_pipeline.ingestion.main --mock
```

### Project Structure: setup.py
```python
# setup.py for modular architecture
from setuptools import setup, find_packages

setup(
    name="igdb-recommendation-system",
    packages=find_packages(),
    install_requires=["requests", "python-dotenv", "pandas", "scikit-learn"],
    entry_points={
        "console_scripts": [
            "igdb-ingest=data_pipeline.ingestion.main:main",
            "igdb-train=data_pipeline.training.main:main",
            "igdb-serve=web_app.api.main:main"
        ]
    }
)
```

## Rationale

### Why Docker-First?
- **Environment Consistency**: Same Python version, dependencies, and paths everywhere
- **Production Simulation**: Test against production-like environment from day one
- **Team Collaboration**: Easy to share and reproduce development environment
- **Integration Testing**: Full stack testing capabilities
- **Deployment Readiness**: Smooth transition to production deployment

### Why Dual Environment?
- **Virtual Environment**: IDE integration, debugging, pre-commit hooks
- **Docker Environment**: Integration testing, full stack development
- **Best of Both**: Fast iteration + environment consistency
- **Professional Workflow**: Industry standard approach

### Why setup.py?
- **Modular Architecture**: Easy imports between components
- **Entry Points**: CLI commands for all components
- **Development Mode**: pip install -e . for live reloading
- **Docker Integration**: Works seamlessly with containers
- **Professional Structure**: Standard for Python projects

## Consequences

### Positive
- ✅ Environment consistency from day one
- ✅ Professional project structure
- ✅ Easy integration testing
- ✅ Smooth deployment to production
- ✅ Team collaboration friendly
- ✅ Industry standard approach

### Negative
- ❌ Initial setup complexity
- ❌ Docker learning curve
- ❌ Slower iteration compared to pure terminal
- ❌ Resource overhead (Docker daemon)

### Risks
- **Docker Complexity**: May slow down initial development
- **Learning Curve**: Team needs Docker knowledge
- **Resource Usage**: Docker consumes system resources
- **Debugging**: More complex debugging in containers

## Implementation Plan

### Phase 1: Project Structure
```bash
# Create setup.py
# Install in development mode
pip install -e .

# Test modular imports
python -c "from data_pipeline.ingestion import IGDBDataIngestion"
```

### Phase 2: Docker Environment
```dockerfile
# Dockerfile.dev
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["python", "-m", "data_pipeline.ingestion.main", "--mock"]
```

### Phase 3: Full Stack Integration
```yaml
# docker-compose.yml
version: '3.8'
services:
  data-pipeline:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
    environment:
      - PYTHONPATH=/app
```

## Development Workflow

### Daily Development
```bash
# 1. IDE Development (Virtual Environment)
source venv/bin/activate
pip install -e .
python -m data_pipeline.ingestion.main --mock

# 2. Integration Testing (Docker)
docker-compose up --build
docker-compose run data-pipeline python -m data_pipeline.ingestion.main --mock

# 3. Quality Checks
pre-commit run --all-files
pytest

# 4. Commit
git add .
git commit -m "Add feature"
```

### Team Collaboration
```bash
# New team member setup
git clone <repository>
cd igdb-project
python3 -m venv venv
source venv/bin/activate
pip install -e .
docker-compose up --build
```

## Future Considerations
- **CI/CD Integration**: GitHub Actions with Docker
- **Production Deployment**: GCP with containerized services
- **Monitoring**: Container health checks and logging
- **Scaling**: Multi-container orchestration

## Success Metrics
- **Development**: Consistent environment across team members
- **Testing**: Full stack integration testing working
- **Deployment**: Smooth transition to production
- **Collaboration**: Easy onboarding for new team members
