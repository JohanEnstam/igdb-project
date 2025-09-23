# Data Ingestion Service Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY data_pipeline/shared/ /app/data_pipeline/shared/
COPY data_pipeline/ingestion/ /app/data_pipeline/ingestion/

# Create data directory
RUN mkdir -p /app/data

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Environment variables for GCS integration
ENV DATA_BUCKET=igdb-recommendation-system-data
ENV GCS_PREFIX=raw/

# No health check for batch jobs

# Default command
ENTRYPOINT ["python", "-m", "data_pipeline.ingestion.main"]
CMD ["--smart", "--limit", "100"]
