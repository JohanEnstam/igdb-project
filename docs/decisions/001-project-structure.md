# ADR-001: Project Structure

## Status
Accepted

## Context
Starting fresh after a messy PoC that became unstructured. Need clear separation between data pipeline and web application.

## Decision
Separate the project into two main pipelines:

```
igdb-project/
├── data-pipeline/          # Factory pipeline
│   ├── ingestion/         # API data collection
│   ├── processing/        # Data cleaning & transformation
│   ├── training/          # ML model training
│   └── deployment/        # Model serving setup
├── web-app/               # Store pipeline
│   ├── api/              # Backend API
│   ├── frontend/         # User interface
│   └── deployment/       # App deployment
├── shared/               # Shared code (utils, configs)
├── infrastructure/       # Terraform/Pulumi for GCP
└── docs/                # Documentation
```

## Rationale
- **Clear separation of concerns**: Data pipeline vs user-facing app
- **Independent scaling**: Can scale data processing separately from web traffic
- **Team organization**: Different teams can work on different pipelines
- **Deployment flexibility**: Can deploy data pipeline updates without affecting web app

## Consequences
- ✅ Clear mental model for developers
- ✅ Easier to reason about system components
- ✅ Better CI/CD pipeline separation
- ❌ Slightly more complex initial setup
- ❌ Need to manage shared code carefully
