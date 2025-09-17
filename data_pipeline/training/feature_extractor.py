#!/usr/bin/env python3
"""
Feature Extraction Module for Game Recommendation System

This module handles feature extraction from game data for ML models.
Supports text-based, categorical, and numerical feature extraction.
"""

import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import pickle

logger = logging.getLogger(__name__)


class GameFeatureExtractor:
    """
    Extracts and processes features from game data for ML models.

    Supports multiple feature types:
    - Text features (summaries, names)
    - Categorical features (genres, platforms, themes)
    - Numerical features (ratings, release year, etc.)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the feature extractor.

        Args:
            config: Configuration dictionary for feature extraction
        """
        self.config = config or self._get_default_config()
        self.tfidf_vectorizer = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_fitted = False

        logger.info("Initialized GameFeatureExtractor")

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for feature extraction."""
        return {
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
            "categorical_features": ["genre_names", "platform_names", "theme_names"],
            "numerical_features": [
                "rating",
                "rating_count",
                "release_year",
                "summary_length",
            ],
            "target_feature": "rating",
        }

    def prepare_text_data(self, games: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Prepare text data for TF-IDF vectorization.

        Args:
            games: List of game data dictionaries

        Returns:
            Dictionary with text data for each text feature
        """
        text_data = {}

        for feature_name in self.config["text_features"].keys():
            text_data[feature_name] = []

            for game in games:
                if feature_name == "summary":
                    text = game.get("summary", "")
                elif feature_name == "name":
                    text = game.get("name", "")
                else:
                    text = ""

                # Clean and preprocess text
                text = self._clean_text(text)
                text_data[feature_name].append(text)

        logger.info(f"Prepared text data for {len(text_data)} text features")
        return text_data

    def _clean_text(self, text: str) -> str:
        """
        Clean and preprocess text data.

        Args:
            text: Raw text string

        Returns:
            Cleaned text string
        """
        if not text:
            return ""

        # Basic text cleaning
        text = text.lower().strip()
        # Remove extra whitespace
        text = " ".join(text.split())

        return text

    def extract_text_features(self, games: List[Dict[str, Any]]) -> np.ndarray:
        """
        Extract text features using TF-IDF vectorization.

        Args:
            games: List of game data dictionaries

        Returns:
            TF-IDF feature matrix
        """
        text_data = self.prepare_text_data(games)

        # Combine all text features
        combined_text = []
        for i in range(len(games)):
            combined_text.append(
                " ".join([text_data[feature][i] for feature in text_data.keys()])
            )

        # Fit TF-IDF vectorizer
        if not self.is_fitted:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=self.config["text_features"]["summary"]["max_features"],
                ngram_range=self.config["text_features"]["summary"]["ngram_range"],
                min_df=self.config["text_features"]["summary"]["min_df"],
                max_df=self.config["text_features"]["summary"]["max_df"],
                stop_words=self.config["text_features"]["summary"]["stop_words"],
            )
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(combined_text)
            logger.info(
                f"Fitted TF-IDF vectorizer with {tfidf_matrix.shape[1]} features"
            )
        else:
            tfidf_matrix = self.tfidf_vectorizer.transform(combined_text)

        return tfidf_matrix.toarray()

    def extract_categorical_features(self, games: List[Dict[str, Any]]) -> np.ndarray:
        """
        Extract categorical features using label encoding.

        Args:
            games: List of game data dictionaries

        Returns:
            Categorical feature matrix
        """
        categorical_data = []

        for feature_name in self.config["categorical_features"]:
            feature_values = []

            for game in games:
                values = game.get(feature_name, [])
                if isinstance(values, list):
                    # Join multiple values with separator
                    feature_values.append("|".join(str(v) for v in values))
                else:
                    feature_values.append(str(values) if values else "")

            categorical_data.append(feature_values)

        # Convert to DataFrame for easier processing
        df = pd.DataFrame(categorical_data).T
        df.columns = self.config["categorical_features"]

        # Encode categorical features
        encoded_features = []

        for col in df.columns:
            if not self.is_fitted:
                le = LabelEncoder()
                encoded_col = le.fit_transform(df[col].fillna("unknown"))
                self.label_encoders[col] = le
            else:
                le = self.label_encoders[col]
                # Handle unseen categories
                encoded_col = []
                for val in df[col].fillna("unknown"):
                    if val in le.classes_:
                        encoded_col.append(le.transform([val])[0])
                    else:
                        encoded_col.append(0)  # Default to first class
                encoded_col = np.array(encoded_col)

            encoded_features.append(encoded_col)

        categorical_matrix = np.column_stack(encoded_features)
        logger.info(f"Extracted categorical features: {categorical_matrix.shape}")

        return categorical_matrix

    def extract_numerical_features(self, games: List[Dict[str, Any]]) -> np.ndarray:
        """
        Extract numerical features with scaling.

        Args:
            games: List of game data dictionaries

        Returns:
            Scaled numerical feature matrix
        """
        numerical_data = []

        for feature_name in self.config["numerical_features"]:
            feature_values = []

            for game in games:
                value = game.get(feature_name, 0)
                if value is None:
                    value = 0
                feature_values.append(float(value))

            numerical_data.append(feature_values)

        numerical_matrix = np.column_stack(numerical_data)

        # Scale numerical features
        if not self.is_fitted:
            numerical_matrix = self.scaler.fit_transform(numerical_matrix)
        else:
            numerical_matrix = self.scaler.transform(numerical_matrix)

        logger.info(f"Extracted numerical features: {numerical_matrix.shape}")
        return numerical_matrix

    def extract_all_features(
        self, games: List[Dict[str, Any]]
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Extract all features from game data.

        Args:
            games: List of game data dictionaries

        Returns:
            Tuple of (feature_matrix, feature_names)
        """
        logger.info(f"Extracting features from {len(games)} games")

        # Extract different feature types
        text_features = self.extract_text_features(games)
        categorical_features = self.extract_categorical_features(games)
        numerical_features = self.extract_numerical_features(games)

        # Combine all features
        feature_matrix = np.hstack(
            [text_features, categorical_features, numerical_features]
        )

        # Generate feature names
        feature_names = []

        # Text feature names
        if self.tfidf_vectorizer:
            text_feature_names = [
                f"text_{name}" for name in self.tfidf_vectorizer.get_feature_names_out()
            ]
            feature_names.extend(text_feature_names)

        # Categorical feature names
        for feature_name in self.config["categorical_features"]:
            feature_names.append(f"cat_{feature_name}")

        # Numerical feature names
        for feature_name in self.config["numerical_features"]:
            feature_names.append(f"num_{feature_name}")

        self.feature_names = feature_names
        self.is_fitted = True

        logger.info(f"Extracted {feature_matrix.shape[1]} total features")
        return feature_matrix, feature_names

    def get_game_similarity(
        self, game_features: np.ndarray, target_game_idx: int, top_k: int = 10
    ) -> List[Tuple[int, float]]:
        """
        Calculate similarity between a target game and all other games.

        Args:
            game_features: Feature matrix for all games
            target_game_idx: Index of the target game
            top_k: Number of similar games to return

        Returns:
            List of (game_index, similarity_score) tuples
        """
        if target_game_idx >= len(game_features):
            raise ValueError(f"Target game index {target_game_idx} out of range")

        # Calculate cosine similarity
        similarities = cosine_similarity(
            game_features[target_game_idx : target_game_idx + 1], game_features
        )[0]

        # Get top-k similar games (excluding the target game itself)
        similar_indices = np.argsort(similarities)[::-1]
        similar_games = []

        for idx in similar_indices:
            if idx != target_game_idx:
                similar_games.append((idx, similarities[idx]))
                if len(similar_games) >= top_k:
                    break

        return similar_games

    def save_model(self, filepath: str) -> None:
        """
        Save the fitted feature extractor to disk.

        Args:
            filepath: Path to save the model
        """
        model_data = {
            "config": self.config,
            "tfidf_vectorizer": self.tfidf_vectorizer,
            "label_encoders": self.label_encoders,
            "scaler": self.scaler,
            "feature_names": self.feature_names,
            "is_fitted": self.is_fitted,
        }

        with open(filepath, "wb") as f:
            pickle.dump(model_data, f)

        logger.info(f"Saved feature extractor model to {filepath}")

    def load_model(self, filepath: str) -> None:
        """
        Load a fitted feature extractor from disk.

        Args:
            filepath: Path to load the model from
        """
        with open(filepath, "rb") as f:
            model_data = pickle.load(f)

        self.config = model_data["config"]
        self.tfidf_vectorizer = model_data["tfidf_vectorizer"]
        self.label_encoders = model_data["label_encoders"]
        self.scaler = model_data["scaler"]
        self.feature_names = model_data["feature_names"]
        self.is_fitted = model_data["is_fitted"]

        logger.info(f"Loaded feature extractor model from {filepath}")
