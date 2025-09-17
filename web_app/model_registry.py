#!/usr/bin/env python3
"""
Model Registry for Cloud Storage Integration

This module handles loading models and data from Google Cloud Storage
at runtime, enabling separation of data from application code.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import json

try:
    from google.cloud import storage

    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    logging.warning(
        "Google Cloud Storage not available. Install with: pip install google-cloud-storage"
    )

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Registry for managing models and data from Cloud Storage."""

    def __init__(
        self,
        data_bucket: str = "igdb-recommendation-system-data",
        models_bucket: str = "igdb-recommendation-system-models",
        project_id: Optional[str] = None,
    ):
        """
        Initialize Model Registry.

        Args:
            data_bucket: Cloud Storage bucket for data files
            models_bucket: Cloud Storage bucket for model files
            project_id: GCP project ID (auto-detected if None)
        """
        self.data_bucket_name = data_bucket
        self.models_bucket_name = models_bucket
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")

        if GCS_AVAILABLE:
            try:
                # Handle credentials from environment variable (for CI)
                credentials_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
                if credentials_json:
                    import json
                    import tempfile

                    # Create temporary credentials file
                    with tempfile.NamedTemporaryFile(
                        mode="w", suffix=".json", delete=False
                    ) as f:
                        json.dump(json.loads(credentials_json), f)
                        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f.name

                self.storage_client = storage.Client(project=self.project_id)
                self.data_bucket = self.storage_client.bucket(data_bucket)
                self.models_bucket = self.storage_client.bucket(models_bucket)
                logger.info(f"Connected to GCS buckets: {data_bucket}, {models_bucket}")
            except Exception as e:
                logger.error(f"Failed to connect to GCS: {e}")
                self.storage_client = None
                self.data_bucket = None
                self.models_bucket = None
        else:
            self.storage_client = None
            self.data_bucket = None
            self.models_bucket = None

    def _download_file(self, bucket, blob_name: str, local_path: str) -> bool:
        """
        Download a file from Cloud Storage to local path.

        Args:
            bucket: Cloud Storage bucket
            blob_name: Name of blob in bucket
            local_path: Local file path to save to

        Returns:
            True if successful, False otherwise
        """
        if not self.storage_client or not bucket:
            logger.error("GCS not available")
            return False

        try:
            blob = bucket.blob(blob_name)
            blob.download_to_filename(local_path)
            logger.info(f"Downloaded {blob_name} to {local_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download {blob_name}: {e}")
            return False

    def get_games_data(self) -> Optional[list]:
        """
        Load games data from Cloud Storage.

        Returns:
            List of game data or None if failed
        """
        if not self.storage_client:
            logger.warning("GCS not available, trying local fallback")
            return self._load_local_games_data()

        try:
            with tempfile.NamedTemporaryFile(
                mode="w+", suffix=".json", delete=False
            ) as tmp_file:
                if self._download_file(
                    self.data_bucket, "games_clean.json", tmp_file.name
                ):
                    with open(tmp_file.name, "r") as f:
                        games_data = json.load(f)
                    os.unlink(tmp_file.name)  # Clean up temp file
                    logger.info(f"Loaded {len(games_data)} games from Cloud Storage")
                    return games_data
                else:
                    logger.warning("Failed to download from GCS, trying local fallback")
                    return self._load_local_games_data()
        except Exception as e:
            logger.error(f"Error loading games data: {e}")
            return self._load_local_games_data()

    def _load_local_games_data(self) -> Optional[list]:
        """Fallback to local games data if GCS fails."""
        try:
            games_file = Path("data/games_clean.json")
            if games_file.exists():
                with open(games_file, "r") as f:
                    games_data = json.load(f)
                logger.info(f"Loaded {len(games_data)} games from local file")
                return games_data
            else:
                logger.warning("No local games data found")
                return None
        except Exception as e:
            logger.error(f"Failed to load local games data: {e}")
            return None

    def get_model_path(
        self, model_name: str = "recommendation_model.pkl"
    ) -> Optional[str]:
        """
        Download model from Cloud Storage and return local path.

        Args:
            model_name: Name of model file in bucket

        Returns:
            Local path to model file or None if failed
        """
        if not self.storage_client:
            logger.warning("GCS not available, trying local fallback")
            return self._get_local_model_path(model_name)

        try:
            with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp_file:
                if self._download_file(self.models_bucket, model_name, tmp_file.name):
                    logger.info(f"Downloaded {model_name} to {tmp_file.name}")
                    return tmp_file.name
                else:
                    logger.warning("Failed to download from GCS, trying local fallback")
                    return self._get_local_model_path(model_name)
        except Exception as e:
            logger.error(f"Error downloading model {model_name}: {e}")
            return self._get_local_model_path(model_name)

    def _get_local_model_path(self, model_name: str) -> Optional[str]:
        """Fallback to local model if GCS fails."""
        try:
            model_file = Path(f"models/{model_name}")
            if model_file.exists():
                logger.info(f"Using local model: {model_file}")
                return str(model_file)
            else:
                logger.warning(f"No local model found: {model_name}")
                return None
        except Exception as e:
            logger.error(f"Failed to get local model path: {e}")
            return None

    def get_feature_extractor_path(self) -> Optional[str]:
        """Get path to feature extractor model."""
        return self.get_model_path("recommendation_model_feature_extractor.pkl")

    def health_check(self) -> Dict[str, Any]:
        """
        Check health of model registry.

        Returns:
            Dictionary with health status information
        """
        health = {
            "gcs_available": GCS_AVAILABLE,
            "storage_client": self.storage_client is not None,
            "data_bucket": self.data_bucket is not None,
            "models_bucket": self.models_bucket is not None,
            "project_id": self.project_id,
        }

        if self.storage_client:
            try:
                # Test data bucket access
                data_blob = self.data_bucket.blob("games_clean.json")
                health["data_accessible"] = data_blob.exists()

                # Test models bucket access
                model_blob = self.models_bucket.blob("recommendation_model.pkl")
                health["models_accessible"] = model_blob.exists()
            except Exception as e:
                health["error"] = str(e)
                health["data_accessible"] = False
                health["models_accessible"] = False
        else:
            health["data_accessible"] = False
            health["models_accessible"] = False

        return health
