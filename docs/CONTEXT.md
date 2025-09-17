# Project Context for LLMs

## Project Overview
IGDB Game Recommendation System - A complete pipeline for collecting game data from external APIs, training ML models, and serving game recommendations via web application.

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
🚧 **Phase 1**: Setting up local development environment and basic project structure.

## Development Workflow
1. **Local**: Docker Compose for full stack
2. **Staging**: Automated deployment via GitHub Actions
3. **Production**: Terraform-managed GCP resources

## Important Decisions
- See `docs/decisions/` for Architecture Decision Records
- Project structure separates data pipeline from web app
- Infrastructure as Code approach for reproducibility
