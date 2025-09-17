# Project Context for LLMs

## Project Overview

**IGDB Game Recommendation System**
- A complete pipeline for collecting game data from external APIs, training ML models, and serving game recommendations via web application.

## Architecture Summary

- **Data Pipeline**: Ingestion → Processing → Training → Deployment
- **Web App**: API + Frontend serving recommendations
- **Infrastructure**: GCP-based with Terraform IaC
- **Development**: Local → Staging → Production workflow

## Key Technologies

- **Backend**: Python (FastAPI/Flask)
- **Frontend**: React/Vue (TBD)
- **ML**: scikit-learn, TensorFlow/PyTorch
- **Cloud**: Google Cloud Platform
- **IaC**: Terraform
- **CI/CD**: GitHub Actions

## Current Status

✅ **Phase 1 Complete**: Project structure, documentation, and development workflow established
✅ **Phase 2 Complete**: Data management and smart ingestion pipeline implemented
🎯 **Next**: End-to-end testing with real IGDB API, ML pipeline development

## Development Workflow

1. **Local**: Docker Compose for full stack
2. **Staging**: Automated deployment via GitHub Actions
3. **Production**: Terraform-managed GCP resources

## Important Decisions

- See `docs/decisions/` for Architecture Decision Records
- Project structure separates data pipeline from web app
- Infrastructure as Code approach for reproducibility
- **Middle Ground Approach**: Develop with 10-100 games, design for 350k scalability
- **Smart Data Management**: Avoid re-fetching with database-first approach
- **Python Package Structure**: Professional setup with `setup.py` and CLI entry points
- **SQLite-Only Strategy**: Single database for development and production
- **Comprehensive Testing**: 24 unit tests covering all core functionality
- **Pre-commit Quality**: Automated code formatting and linting
