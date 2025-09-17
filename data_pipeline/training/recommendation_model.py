#!/usr/bin/env python3
"""
Content-Based Recommendation Model

This module implements a content-based recommendation system for games
using TF-IDF features, categorical features, and cosine similarity.
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.metrics.pairwise import cosine_similarity
import pickle

from .feature_extractor import GameFeatureExtractor

logger = logging.getLogger(__name__)


class ContentBasedRecommendationModel:
    """
    Content-based recommendation model for games.

    Uses a hybrid approach combining:
    - Text similarity (summaries, names)
    - Categorical similarity (genres, platforms, themes)
    - Rating-based weighting
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the recommendation model.

        Args:
            config: Configuration dictionary for the model
        """
        self.config = config or self._get_default_config()
        self.feature_extractor = GameFeatureExtractor(self.config.get("feature_config"))
        self.games_data = []
        self.game_features = None
        self.similarity_matrix = None
        self.is_trained = False

        logger.info("Initialized ContentBasedRecommendationModel")

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for the model."""
        return {
            "feature_config": {
                "text_features": {
                    "summary": {
                        "max_features": 1000,
                        "ngram_range": (1, 2),
                        "min_df": 2,
                        "max_df": 0.95,
                        "stop_words": "english",
                    },
                    "name": {
                        "max_features": 500,
                        "ngram_range": (1, 2),
                        "min_df": 1,
                        "max_df": 0.9,
                        "stop_words": "english",
                    },
                },
                "categorical_features": [
                    "genre_names",
                    "platform_names",
                    "theme_names",
                ],
                "numerical_features": [
                    "rating",
                    "rating_count",
                    "release_year",
                    "summary_length",
                ],
                "target_feature": "rating",
            },
            "similarity_weights": {
                "text_similarity": 0.4,
                "categorical_similarity": 0.3,
                "rating_similarity": 0.3,
            },
            "min_rating_threshold": 70.0,
            "max_recommendations": 20,
        }

    def prepare_data(self, games: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepare and filter game data for training.

        Args:
            games: List of raw game data

        Returns:
            List of prepared game data
        """
        logger.info(f"Preparing data from {len(games)} games")

        # Filter games with minimum requirements
        filtered_games = []
        for game in games:
            # Must have summary and at least one genre
            if (
                game.get("has_summary", False)
                and game.get("has_genres", False)
                and game.get("summary", "").strip()
            ):
                filtered_games.append(game)

        logger.info(f"Filtered to {len(filtered_games)} games with required data")
        return filtered_games

    def train(self, games: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train the content-based recommendation model.

        Args:
            games: List of game data dictionaries

        Returns:
            Training results and metrics
        """
        logger.info("Starting model training")

        # Prepare data
        self.games_data = self.prepare_data(games)

        if len(self.games_data) < 10:
            raise ValueError("Need at least 10 games for training")

        # Extract features
        self.game_features, feature_names = self.feature_extractor.extract_all_features(
            self.games_data
        )

        # Calculate similarity matrix
        self.similarity_matrix = cosine_similarity(self.game_features)

        # Calculate training metrics
        training_metrics = self._calculate_training_metrics()

        self.is_trained = True

        logger.info(f"Model training completed with {len(self.games_data)} games")
        logger.info(f"Feature matrix shape: {self.game_features.shape}")

        return {
            "training_samples": len(self.games_data),
            "feature_count": self.game_features.shape[1],
            "metrics": training_metrics,
        }

    def _calculate_training_metrics(self) -> Dict[str, Any]:
        """
        Calculate training metrics for the model.

        Returns:
            Dictionary of training metrics
        """
        # Calculate average similarity scores
        np.fill_diagonal(self.similarity_matrix, 0)  # Remove self-similarity
        avg_similarity = np.mean(self.similarity_matrix)
        max_similarity = np.max(self.similarity_matrix)
        min_similarity = np.min(self.similarity_matrix)

        # Calculate rating statistics
        ratings = [
            g.get("rating", 0) for g in self.games_data if g.get("has_rating", False)
        ]
        rating_stats = {}
        if ratings:
            rating_stats = {
                "avg_rating": np.mean(ratings),
                "min_rating": np.min(ratings),
                "max_rating": np.max(ratings),
                "games_with_ratings": len(ratings),
            }

        return {
            "avg_similarity": float(avg_similarity),
            "max_similarity": float(max_similarity),
            "min_similarity": float(min_similarity),
            "rating_stats": rating_stats,
        }

    def get_recommendations(
        self, game_id: int, top_k: int = 10, exclude_played: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations for a specific game.

        Args:
            game_id: ID of the game to get recommendations for
            top_k: Number of recommendations to return
            exclude_played: Whether to exclude games with same genres/platforms

        Returns:
            List of recommended games with similarity scores
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before getting recommendations")

        # Find game index
        game_idx = None
        for i, game in enumerate(self.games_data):
            if game["id"] == game_id:
                game_idx = i
                break

        if game_idx is None:
            raise ValueError(f"Game with ID {game_id} not found in training data")

        # Get similarity scores
        similarities = self.similarity_matrix[game_idx]

        # Get top-k similar games
        similar_indices = np.argsort(similarities)[::-1]
        recommendations = []

        for idx in similar_indices:
            if idx == game_idx:  # Skip the game itself
                continue

            similarity_score = similarities[idx]
            game = self.games_data[idx]

            # Apply filters if requested
            if exclude_played:
                if self._should_exclude_game(self.games_data[game_idx], game):
                    continue

            recommendations.append(
                {
                    "game_id": game["id"],
                    "name": game["name"],
                    "similarity_score": float(similarity_score),
                    "rating": game.get("rating", 0),
                    "genres": game.get("genre_names", []),
                    "platforms": game.get("platform_names", []),
                    "summary": game.get("summary", "")[:200] + "..."
                    if len(game.get("summary", "")) > 200
                    else game.get("summary", ""),
                }
            )

            if len(recommendations) >= top_k:
                break

        logger.info(
            f"Generated {len(recommendations)} recommendations for game {game_id}"
        )
        return recommendations

    def _should_exclude_game(
        self, target_game: Dict[str, Any], candidate_game: Dict[str, Any]
    ) -> bool:
        """
        Determine if a candidate game should be excluded from recommendations.

        Args:
            target_game: The game we're getting recommendations for
            candidate_game: The candidate game to potentially exclude

        Returns:
            True if the game should be excluded
        """
        # Exclude games with identical genres (too similar)
        target_genres = set(target_game.get("genre_names", []))
        candidate_genres = set(candidate_game.get("genre_names", []))

        if (
            len(target_genres.intersection(candidate_genres))
            >= len(target_genres) * 0.8
        ):
            return True

        return False

    def get_similar_games_by_text(
        self, query_text: str, top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find games similar to a text query.

        Args:
            query_text: Text query to find similar games for
            top_k: Number of similar games to return

        Returns:
            List of similar games
        """
        if not self.is_trained:
            raise ValueError(
                "Model must be trained before getting text recommendations"
            )

        # Create a dummy game with the query text
        dummy_game = {
            "id": -1,
            "name": "Query",
            "summary": query_text,
            "genre_names": [],
            "platform_names": [],
            "theme_names": [],
            "rating": 0,
            "rating_count": 0,
            "release_year": 2024,
            "summary_length": len(query_text),
        }

        # Extract features for the query using the fitted feature extractor
        # We need to temporarily modify the feature extractor to handle new data
        original_is_fitted = self.feature_extractor.is_fitted
        self.feature_extractor.is_fitted = True  # Ensure it's marked as fitted

        try:
            # Extract features for the query
            query_features, _ = self.feature_extractor.extract_all_features(
                [dummy_game]
            )

            # Calculate similarity with all games
            similarities = cosine_similarity(query_features, self.game_features)[0]

            # Get top-k similar games
            similar_indices = np.argsort(similarities)[::-1]
            recommendations = []

            for idx in similar_indices:
                similarity_score = similarities[idx]
                game = self.games_data[idx]

                recommendations.append(
                    {
                        "game_id": game["id"],
                        "name": game["name"],
                        "similarity_score": float(similarity_score),
                        "rating": game.get("rating", 0),
                        "genres": game.get("genre_names", []),
                        "platforms": game.get("platform_names", []),
                        "summary": game.get("summary", "")[:200] + "..."
                        if len(game.get("summary", "")) > 200
                        else game.get("summary", ""),
                    }
                )

                if len(recommendations) >= top_k:
                    break

            logger.info(f"Generated {len(recommendations)} text-based recommendations")
            return recommendations

        finally:
            # Restore original state
            self.feature_extractor.is_fitted = original_is_fitted

    def evaluate_model(self, test_games: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate the model on test data.

        Args:
            test_games: List of test game data

        Returns:
            Evaluation metrics
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before evaluation")

        logger.info(f"Evaluating model on {len(test_games)} test games")

        # For content-based filtering, we'll evaluate based on similarity quality
        # This is a simplified evaluation - in practice, you'd need user interaction data

        evaluation_results = {
            "test_samples": len(test_games),
            "avg_recommendation_quality": 0.0,
            "coverage": 0.0,
        }

        # Calculate coverage (how many test games can we recommend for)
        covered_games = 0
        total_similarity_scores = []

        for test_game in test_games:
            try:
                recommendations = self.get_recommendations(
                    test_game["id"], top_k=5, exclude_played=False
                )

                if recommendations:
                    covered_games += 1
                    avg_similarity = np.mean(
                        [r["similarity_score"] for r in recommendations]
                    )
                    total_similarity_scores.append(avg_similarity)

            except ValueError:
                # Game not in training data
                continue

        if total_similarity_scores:
            evaluation_results["avg_recommendation_quality"] = np.mean(
                total_similarity_scores
            )

        evaluation_results["coverage"] = (
            covered_games / len(test_games) if test_games else 0
        )

        logger.info(f"Model evaluation completed: {evaluation_results}")
        return evaluation_results

    def save_model(self, filepath: str) -> None:
        """
        Save the trained model to disk.

        Args:
            filepath: Path to save the model
        """
        model_data = {
            "config": self.config,
            "games_data": self.games_data,
            "game_features": self.game_features,
            "similarity_matrix": self.similarity_matrix,
            "is_trained": self.is_trained,
        }

        # Save feature extractor separately
        feature_extractor_path = filepath.replace(".pkl", "_feature_extractor.pkl")
        self.feature_extractor.save_model(feature_extractor_path)

        with open(filepath, "wb") as f:
            pickle.dump(model_data, f)

        logger.info(f"Saved recommendation model to {filepath}")

    def load_model(self, filepath: str) -> None:
        """
        Load a trained model from disk.

        Args:
            filepath: Path to load the model from
        """
        with open(filepath, "rb") as f:
            model_data = pickle.load(f)

        self.config = model_data["config"]
        self.games_data = model_data["games_data"]
        self.game_features = model_data["game_features"]
        self.similarity_matrix = model_data["similarity_matrix"]
        self.is_trained = model_data["is_trained"]

        # Load feature extractor
        feature_extractor_path = filepath.replace(".pkl", "_feature_extractor.pkl")
        self.feature_extractor.load_model(feature_extractor_path)

        logger.info(f"Loaded recommendation model from {filepath}")
