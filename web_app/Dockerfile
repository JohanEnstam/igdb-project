# Web App API Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app/
COPY web_app/requirements.txt /app/web_app/
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r web_app/requirements.txt

# Copy application code
COPY data_pipeline/ /app/data_pipeline/
COPY web_app/ /app/web_app/
COPY shared/ /app/shared/

# Create data and models directories (empty - loaded at runtime)
RUN mkdir -p /app/data /app/models

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port (Cloud Run uses PORT env var)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command
CMD ["python", "-m", "web_app.api.main"]
