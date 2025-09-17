#!/usr/bin/env python3
"""
ML Training Service

This service handles machine learning model training and validation
for the game recommendation system.

Usage:
    python -m data_pipeline.training.main
"""

import argparse
import logging
import json
import time
from pathlib import Path
from typing import List, Dict, Any

from .recommendation_model import ContentBasedRecommendationModel

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MLTrainingService:
    """Handles ML model training and validation."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the ML training service.

        Args:
            config: Configuration dictionary for the training service
        """
        self.config = config or {}
        self.recommendation_model = ContentBasedRecommendationModel(self.config)
        logger.info("Initialized ML Training Service")

    def load_training_data(self, data_path: str) -> List[Dict[str, Any]]:
        """
        Load training data from file.

        Args:
            data_path: Path to the training data file

        Returns:
            List of game data dictionaries
        """
        logger.info(f"Loading training data from {data_path}")

        data_file = Path(data_path)
        if not data_file.exists():
            raise FileNotFoundError(f"Training data file not found: {data_path}")

        with open(data_file, "r") as f:
            if data_file.suffix == ".json":
                games = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {data_file.suffix}")

        logger.info(f"Loaded {len(games)} games from training data")
        return games

    def train_model(self, games: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train ML model on game data.

        Args:
            games: List of processed game data

        Returns:
            Trained model metadata
        """
        logger.info(
            f"Training content-based recommendation model on {len(games)} games"
        )

        start_time = time.time()

        # Train the recommendation model
        training_results = self.recommendation_model.train(games)

        training_time = time.time() - start_time

        model_metadata = {
            "model_type": "content_based_recommendation",
            "training_samples": training_results["training_samples"],
            "feature_count": training_results["feature_count"],
            "training_time_seconds": training_time,
            "training_time_formatted": f"{int(training_time//60):02d}:{int(training_time%60):02d}",
            "metrics": training_results["metrics"],
        }

        logger.info(f"Model training completed: {model_metadata}")
        return model_metadata

    def validate_model(self, test_data_path: str = None) -> Dict[str, Any]:
        """
        Validate trained model.

        Args:
            test_data_path: Path to test data (optional, uses training data if not provided)

        Returns:
            Validation results
        """
        logger.info("Validating trained model")

        if not self.recommendation_model.is_trained:
            raise ValueError("Model must be trained before validation")

        # For now, we'll use a simple validation approach
        # In practice, you'd want separate test data
        validation_results = {
            "model_type": "content_based_recommendation",
            "validation_method": "similarity_quality_check",
            "status": "completed",
        }

        # Test recommendation generation
        try:
            # Get recommendations for a few sample games
            sample_games = self.recommendation_model.games_data[:5]
            for game in sample_games:
                recommendations = self.recommendation_model.get_recommendations(
                    game["id"], top_k=5
                )
                validation_results[f"sample_game_{game['id']}_recommendations"] = len(
                    recommendations
                )

            validation_results["recommendation_generation"] = "success"

        except Exception as e:
            validation_results["recommendation_generation"] = f"error: {str(e)}"

        logger.info(f"Model validation completed: {validation_results}")
        return validation_results

    def save_model(self, model_path: str) -> None:
        """
        Save the trained model to disk.

        Args:
            model_path: Path to save the model
        """
        logger.info(f"Saving trained model to {model_path}")
        self.recommendation_model.save_model(model_path)
        logger.info("Model saved successfully")

    def run(self, data_path: str, model_path: str = None):
        """
        Run the ML training service.

        Args:
            data_path: Path to training data
            model_path: Path to save the trained model
        """
        logger.info("Starting ML Training Service")

        try:
            # Load training data
            games = self.load_training_data(data_path)

            # Train model
            training_results = self.train_model(games)

            # Validate model
            self.validate_model()

            # Save model if path provided
            if model_path:
                self.save_model(model_path)

            # Print summary
            logger.info("=" * 50)
            logger.info("ML TRAINING SUMMARY")
            logger.info("=" * 50)
            logger.info(f"Training samples: {training_results['training_samples']}")
            logger.info(f"Feature count: {training_results['feature_count']}")
            logger.info(f"Training time: {training_results['training_time_formatted']}")
            logger.info(f"Model type: {training_results['model_type']}")
            logger.info("=" * 50)

        except Exception as e:
            logger.error(f"ML Training Service failed: {str(e)}")
            raise


def main():
    """Main function to run ML training."""
    parser = argparse.ArgumentParser(description="ML Training Service")
    parser.add_argument(
        "--data-path",
        type=str,
        default="data/games_clean.json",
        help="Path to training data file",
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default="models/recommendation_model.pkl",
        help="Path to save the trained model",
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (optional)",
    )

    args = parser.parse_args()

    # Load configuration if provided
    config = {}
    if args.config:
        with open(args.config, "r") as f:
            config = json.load(f)

    # Initialize training service
    service = MLTrainingService(config)

    # Run training
    service.run(args.data_path, args.model_path)


if __name__ == "__main__":
    main()
