"""
IGDB Data Ingestion Package

This package handles data collection from IGDB API including:
- Authentication with IGDB API
- Rate-limited data fetching
- Stratified sampling for development
- Full dataset collection for production
- Mock data generation for testing
"""

from .main import IGDBDataIngestion, create_mock_data

__all__ = ["IGDBDataIngestion", "create_mock_data"]
