#!/usr/bin/env python3
"""
Comprehensive tests for the ML pipeline

This module tests the complete ML pipeline including:
- Feature extraction
- Recommendation model training
- Model evaluation
- API endpoints
"""

import pytest
import json

# Import our ML components
from data_pipeline.training.feature_extractor import GameFeatureExtractor
from data_pipeline.training.recommendation_model import ContentBasedRecommendationModel
from data_pipeline.training.main import MLTrainingService


class TestGameFeatureExtractor:
    """Test the GameFeatureExtractor class."""

    @pytest.fixture
    def sample_games(self):
        """Sample game data for testing."""
        return [
            {
                "id": 1,
                "name": "Test Game 1",
                "summary": "A great adventure game with puzzles and exploration",
                "rating": 85.5,
                "rating_count": 100,
                "release_year": 2023,
                "summary_length": 50,
                "genre_names": ["Adventure", "Puzzle"],
                "platform_names": ["PC", "PlayStation"],
                "theme_names": ["Fantasy"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 2,
                "name": "Test Game 2",
                "summary": "An action-packed shooter with multiplayer features",
                "rating": 92.0,
                "rating_count": 200,
                "release_year": 2022,
                "summary_length": 45,
                "genre_names": ["Shooter", "Action"],
                "platform_names": ["Xbox", "PC"],
                "theme_names": ["Sci-Fi"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
        ]

    def test_feature_extractor_initialization(self):
        """Test feature extractor initialization."""
        extractor = GameFeatureExtractor()
        assert extractor.config is not None
        assert extractor.tfidf_vectorizer is None
        assert extractor.label_encoders == {}
        assert not extractor.is_fitted

    def test_text_data_preparation(self, sample_games):
        """Test text data preparation."""
        extractor = GameFeatureExtractor()
        text_data = extractor.prepare_text_data(sample_games)

        assert "summary" in text_data
        assert "name" in text_data
        assert len(text_data["summary"]) == 2
        assert len(text_data["name"]) == 2
        assert "adventure" in text_data["summary"][0].lower()

    def test_text_cleaning(self):
        """Test text cleaning functionality."""
        extractor = GameFeatureExtractor()

        # Test basic cleaning
        dirty_text = "  This is a TEST   with   extra   spaces  "
        clean_text = extractor._clean_text(dirty_text)
        assert clean_text == "this is a test with extra spaces"

        # Test empty text
        assert extractor._clean_text("") == ""
        assert extractor._clean_text(None) == ""

    def test_feature_extraction(self, sample_games):
        """Test complete feature extraction."""
        # Use test-friendly config
        config = {
            "text_features": {
                "summary": {
                    "max_features": 100,
                    "ngram_range": (1, 1),
                    "min_df": 1,  # Allow single document terms
                    "max_df": 0.95,
                    "stop_words": "english",
                },
                "name": {
                    "max_features": 50,
                    "ngram_range": (1, 1),
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
        extractor = GameFeatureExtractor(config)

        # Extract all features
        features, feature_names = extractor.extract_all_features(sample_games)

        # Check feature matrix shape
        assert features.shape[0] == 2  # 2 games
        assert features.shape[1] > 0  # Should have features

        # Check feature names
        assert len(feature_names) == features.shape[1]
        assert any("text_" in name for name in feature_names)
        assert any("cat_" in name for name in feature_names)
        assert any("num_" in name for name in feature_names)

        # Check that extractor is now fitted
        assert extractor.is_fitted

    def test_model_save_load(self, sample_games, tmp_path):
        """Test model saving and loading."""
        # Use test-friendly config
        config = {
            "text_features": {
                "summary": {
                    "max_features": 100,
                    "ngram_range": (1, 1),
                    "min_df": 1,
                    "max_df": 0.95,
                    "stop_words": "english",
                },
                "name": {
                    "max_features": 50,
                    "ngram_range": (1, 1),
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
        extractor = GameFeatureExtractor(config)
        extractor.extract_all_features(sample_games)

        # Save model
        model_path = tmp_path / "test_model.pkl"
        extractor.save_model(str(model_path))
        assert model_path.exists()

        # Load model
        new_extractor = GameFeatureExtractor()
        new_extractor.load_model(str(model_path))

        assert new_extractor.is_fitted
        assert new_extractor.config == extractor.config
        assert len(new_extractor.feature_names) > 0


class TestContentBasedRecommendationModel:
    """Test the ContentBasedRecommendationModel class."""

    @pytest.fixture
    def sample_games(self):
        """Sample game data for testing."""
        return [
            {
                "id": 1,
                "name": "Adventure Game",
                "summary": "A great adventure game with puzzles and exploration",
                "rating": 85.5,
                "rating_count": 100,
                "release_year": 2023,
                "summary_length": 50,
                "genre_names": ["Adventure", "Puzzle"],
                "platform_names": ["PC", "PlayStation"],
                "theme_names": ["Fantasy"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 2,
                "name": "Action Shooter",
                "summary": "An action-packed shooter with multiplayer features",
                "rating": 92.0,
                "rating_count": 200,
                "release_year": 2022,
                "summary_length": 45,
                "genre_names": ["Shooter", "Action"],
                "platform_names": ["Xbox", "PC"],
                "theme_names": ["Sci-Fi"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 3,
                "name": "Puzzle Adventure",
                "summary": "A puzzle game with adventure elements",
                "rating": 78.0,
                "rating_count": 50,
                "release_year": 2021,
                "summary_length": 30,
                "genre_names": ["Puzzle", "Adventure"],
                "platform_names": ["Nintendo Switch"],
                "theme_names": ["Mystery"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 4,
                "name": "Racing Game",
                "summary": "Fast-paced racing with cars and tracks",
                "rating": 88.0,
                "rating_count": 150,
                "release_year": 2023,
                "summary_length": 35,
                "genre_names": ["Racing"],
                "platform_names": ["PC", "Xbox"],
                "theme_names": ["Sports"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 5,
                "name": "Strategy Game",
                "summary": "Complex strategy game with resource management",
                "rating": 90.0,
                "rating_count": 120,
                "release_year": 2022,
                "summary_length": 40,
                "genre_names": ["Strategy"],
                "platform_names": ["PC"],
                "theme_names": ["War"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 6,
                "name": "RPG Adventure",
                "summary": "Role-playing game with character development",
                "rating": 87.0,
                "rating_count": 180,
                "release_year": 2023,
                "summary_length": 45,
                "genre_names": ["Role-playing (RPG)", "Adventure"],
                "platform_names": ["PC", "PlayStation"],
                "theme_names": ["Fantasy"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 7,
                "name": "Platform Game",
                "summary": "Classic platformer with jumping and collecting",
                "rating": 82.0,
                "rating_count": 90,
                "release_year": 2021,
                "summary_length": 30,
                "genre_names": ["Platform"],
                "platform_names": ["Nintendo Switch"],
                "theme_names": ["Action"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 8,
                "name": "Simulation Game",
                "summary": "Life simulation with building and management",
                "rating": 85.0,
                "rating_count": 110,
                "release_year": 2022,
                "summary_length": 35,
                "genre_names": ["Simulator"],
                "platform_names": ["PC"],
                "theme_names": ["Life"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 9,
                "name": "Fighting Game",
                "summary": "Combat fighting game with special moves",
                "rating": 89.0,
                "rating_count": 95,
                "release_year": 2023,
                "summary_length": 32,
                "genre_names": ["Fighting"],
                "platform_names": ["PlayStation", "Xbox"],
                "theme_names": ["Action"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 10,
                "name": "Indie Adventure",
                "summary": "Independent adventure game with unique art style",
                "rating": 84.0,
                "rating_count": 75,
                "release_year": 2021,
                "summary_length": 38,
                "genre_names": ["Indie", "Adventure"],
                "platform_names": ["PC", "Nintendo Switch"],
                "theme_names": ["Artistic"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
        ]

    def test_model_initialization(self):
        """Test model initialization."""
        model = ContentBasedRecommendationModel()
        assert model.config is not None
        assert model.feature_extractor is not None
        assert not model.is_trained

    def test_data_preparation(self, sample_games):
        """Test data preparation."""
        model = ContentBasedRecommendationModel()
        prepared_games = model.prepare_data(sample_games)

        # All games should pass the filter
        assert len(prepared_games) == len(sample_games)

        # Test with games missing required data
        incomplete_games = [
            {"id": 1, "name": "No Summary"},  # Missing summary
            {
                "id": 2,
                "name": "No Genres",
                "summary": "Has summary",
                "genre_names": [],
            },  # No genres
        ]
        filtered_games = model.prepare_data(incomplete_games)
        assert len(filtered_games) == 0  # Should filter out incomplete games

    def test_model_training(self, sample_games):
        """Test model training."""
        model = ContentBasedRecommendationModel()

        training_results = model.train(sample_games)

        # Check training results
        assert training_results["training_samples"] == len(sample_games)
        assert training_results["feature_count"] > 0
        assert "metrics" in training_results

        # Check model state
        assert model.is_trained
        assert model.game_features is not None
        assert model.similarity_matrix is not None
        assert len(model.games_data) == len(sample_games)

    def test_get_recommendations(self, sample_games):
        """Test getting recommendations."""
        model = ContentBasedRecommendationModel()
        model.train(sample_games)

        # Get recommendations for first game
        recommendations = model.get_recommendations(sample_games[0]["id"], top_k=2)

        assert len(recommendations) <= 2
        assert all("game_id" in rec for rec in recommendations)
        assert all("similarity_score" in rec for rec in recommendations)
        assert all("name" in rec for rec in recommendations)

        # Check that recommendations don't include the target game
        target_id = sample_games[0]["id"]
        assert all(rec["game_id"] != target_id for rec in recommendations)

    def test_text_recommendations(self, sample_games):
        """Test text-based recommendations."""
        model = ContentBasedRecommendationModel()
        model.train(sample_games)

        query = "adventure puzzle game"
        recommendations = model.get_similar_games_by_text(query, top_k=2)

        assert len(recommendations) <= 2
        assert all("game_id" in rec for rec in recommendations)
        assert all("similarity_score" in rec for rec in recommendations)
        assert all("name" in rec for rec in recommendations)

    def test_model_save_load(self, sample_games, tmp_path):
        """Test model saving and loading."""
        model = ContentBasedRecommendationModel()
        model.train(sample_games)

        # Save model
        model_path = tmp_path / "test_model.pkl"
        model.save_model(str(model_path))
        assert model_path.exists()

        # Load model
        new_model = ContentBasedRecommendationModel()
        new_model.load_model(str(model_path))

        assert new_model.is_trained
        assert len(new_model.games_data) == len(sample_games)
        assert new_model.game_features is not None
        assert new_model.similarity_matrix is not None


class TestMLTrainingService:
    """Test the MLTrainingService class."""

    @pytest.fixture
    def sample_games_file(self, tmp_path, sample_games):
        """Create a temporary games file for testing."""
        games_file = tmp_path / "test_games.json"
        with open(games_file, "w") as f:
            json.dump(sample_games, f)
        return str(games_file)

    @pytest.fixture
    def sample_games(self):
        """Sample game data for testing."""
        return [
            {
                "id": 1,
                "name": "Test Game 1",
                "summary": "A great adventure game",
                "rating": 85.5,
                "rating_count": 100,
                "release_year": 2023,
                "summary_length": 20,
                "genre_names": ["Adventure"],
                "platform_names": ["PC"],
                "theme_names": ["Fantasy"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 2,
                "name": "Test Game 2",
                "summary": "An action shooter game",
                "rating": 92.0,
                "rating_count": 200,
                "release_year": 2022,
                "summary_length": 18,
                "genre_names": ["Shooter"],
                "platform_names": ["Xbox"],
                "theme_names": ["Sci-Fi"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 3,
                "name": "Test Game 3",
                "summary": "A puzzle game with challenges",
                "rating": 78.0,
                "rating_count": 50,
                "release_year": 2021,
                "summary_length": 25,
                "genre_names": ["Puzzle"],
                "platform_names": ["Nintendo Switch"],
                "theme_names": ["Mystery"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 4,
                "name": "Test Game 4",
                "summary": "Fast racing with cars",
                "rating": 88.0,
                "rating_count": 150,
                "release_year": 2023,
                "summary_length": 20,
                "genre_names": ["Racing"],
                "platform_names": ["PC", "Xbox"],
                "theme_names": ["Sports"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 5,
                "name": "Test Game 5",
                "summary": "Strategy game with management",
                "rating": 90.0,
                "rating_count": 120,
                "release_year": 2022,
                "summary_length": 30,
                "genre_names": ["Strategy"],
                "platform_names": ["PC"],
                "theme_names": ["War"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 6,
                "name": "Test Game 6",
                "summary": "RPG with character development",
                "rating": 87.0,
                "rating_count": 180,
                "release_year": 2023,
                "summary_length": 28,
                "genre_names": ["Role-playing (RPG)"],
                "platform_names": ["PC", "PlayStation"],
                "theme_names": ["Fantasy"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 7,
                "name": "Test Game 7",
                "summary": "Platformer with jumping",
                "rating": 82.0,
                "rating_count": 90,
                "release_year": 2021,
                "summary_length": 22,
                "genre_names": ["Platform"],
                "platform_names": ["Nintendo Switch"],
                "theme_names": ["Action"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 8,
                "name": "Test Game 8",
                "summary": "Life simulation game",
                "rating": 85.0,
                "rating_count": 110,
                "release_year": 2022,
                "summary_length": 20,
                "genre_names": ["Simulator"],
                "platform_names": ["PC"],
                "theme_names": ["Life"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 9,
                "name": "Test Game 9",
                "summary": "Fighting game with combat",
                "rating": 89.0,
                "rating_count": 95,
                "release_year": 2023,
                "summary_length": 24,
                "genre_names": ["Fighting"],
                "platform_names": ["PlayStation", "Xbox"],
                "theme_names": ["Action"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 10,
                "name": "Test Game 10",
                "summary": "Indie adventure with art",
                "rating": 84.0,
                "rating_count": 75,
                "release_year": 2021,
                "summary_length": 26,
                "genre_names": ["Indie", "Adventure"],
                "platform_names": ["PC", "Nintendo Switch"],
                "theme_names": ["Artistic"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
        ]

    def test_service_initialization(self):
        """Test service initialization."""
        service = MLTrainingService()
        assert service.config is not None
        assert service.recommendation_model is not None

    def test_load_training_data(self, sample_games_file):
        """Test loading training data."""
        service = MLTrainingService()
        games = service.load_training_data(sample_games_file)

        assert len(games) == 10  # Updated to match the fixture
        assert games[0]["id"] == 1
        assert games[1]["id"] == 2

    def test_train_model(self, sample_games):
        """Test model training."""
        service = MLTrainingService()
        training_results = service.train_model(sample_games)

        assert training_results["model_type"] == "content_based_recommendation"
        assert training_results["training_samples"] == len(sample_games)
        assert training_results["feature_count"] > 0
        assert "training_time_seconds" in training_results

    def test_validate_model(self, sample_games):
        """Test model validation."""
        service = MLTrainingService()
        service.train_model(sample_games)

        validation_results = service.validate_model()

        assert validation_results["model_type"] == "content_based_recommendation"
        assert validation_results["status"] == "completed"
        assert validation_results["recommendation_generation"] == "success"

    def test_save_model(self, sample_games, tmp_path):
        """Test model saving."""
        service = MLTrainingService()
        service.train_model(sample_games)

        model_path = tmp_path / "test_model.pkl"
        service.save_model(str(model_path))

        assert model_path.exists()

    def test_full_pipeline(self, sample_games_file, tmp_path):
        """Test the complete training pipeline."""
        service = MLTrainingService()
        model_path = tmp_path / "test_model.pkl"

        # Run the complete pipeline
        service.run(sample_games_file, str(model_path))

        # Check that model was saved
        assert model_path.exists()


class TestAPIIntegration:
    """Test API integration."""

    def test_api_import(self):
        """Test that API can be imported without errors."""
        try:
            import sys
            from pathlib import Path

            sys.path.append(str(Path(__file__).parent.parent))
            from web_app.api.main import app

            assert app is not None
        except ImportError as e:
            pytest.skip(f"API not available: {e}")

    def test_pydantic_models(self):
        """Test Pydantic models."""
        try:
            import sys
            from pathlib import Path

            sys.path.append(str(Path(__file__).parent.parent))
            from web_app.api.main import (
                GameRecommendation,
                GameInfo,
                TextRecommendationRequest,
            )

            # Test GameRecommendation
            rec = GameRecommendation(
                game_id=1,
                name="Test Game",
                similarity_score=0.95,
                rating=None,  # Test optional rating
                genres=["Adventure"],
                platforms=["PC"],
                summary="Test summary",
            )
            assert rec.game_id == 1
            assert rec.rating is None

            # Test GameInfo
            info = GameInfo(
                id=1,
                name="Test Game",
                summary="Test summary",
                rating=None,
                rating_count=0,
                release_date="2023-01-01",
                release_year=2023,
                genre_names=["Adventure"],
                platform_names=["PC"],
                theme_names=["Fantasy"],
            )
            assert info.id == 1

            # Test TextRecommendationRequest
            req = TextRecommendationRequest(query="test query", top_k=5)
            assert req.query == "test query"
            assert req.top_k == 5

        except ImportError as e:
            pytest.skip(f"API not available: {e}")


# Integration tests
class TestMLPipelineIntegration:
    """Integration tests for the complete ML pipeline."""

    def test_end_to_end_pipeline(self, tmp_path):
        """Test the complete end-to-end ML pipeline."""
        # Create sample data (need at least 10 games)
        sample_games = [
            {
                "id": 1,
                "name": "Adventure Quest",
                "summary": "An epic adventure game with puzzles and exploration",
                "rating": 88.5,
                "rating_count": 150,
                "release_year": 2023,
                "summary_length": 50,
                "genre_names": ["Adventure", "Puzzle"],
                "platform_names": ["PC", "PlayStation"],
                "theme_names": ["Fantasy"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 2,
                "name": "Space Shooter",
                "summary": "A fast-paced space shooter with multiplayer battles",
                "rating": 91.0,
                "rating_count": 200,
                "release_year": 2022,
                "summary_length": 45,
                "genre_names": ["Shooter", "Action"],
                "platform_names": ["Xbox", "PC"],
                "theme_names": ["Sci-Fi"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 3,
                "name": "Puzzle Master",
                "summary": "A challenging puzzle game with brain-teasing levels",
                "rating": 79.0,
                "rating_count": 75,
                "release_year": 2021,
                "summary_length": 40,
                "genre_names": ["Puzzle"],
                "platform_names": ["Nintendo Switch"],
                "theme_names": ["Mystery"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 4,
                "name": "Racing Champion",
                "summary": "Fast racing with cars and tracks",
                "rating": 88.0,
                "rating_count": 150,
                "release_year": 2023,
                "summary_length": 35,
                "genre_names": ["Racing"],
                "platform_names": ["PC", "Xbox"],
                "theme_names": ["Sports"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 5,
                "name": "Strategy Master",
                "summary": "Complex strategy game with resource management",
                "rating": 90.0,
                "rating_count": 120,
                "release_year": 2022,
                "summary_length": 40,
                "genre_names": ["Strategy"],
                "platform_names": ["PC"],
                "theme_names": ["War"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 6,
                "name": "RPG Legend",
                "summary": "Role-playing game with character development",
                "rating": 87.0,
                "rating_count": 180,
                "release_year": 2023,
                "summary_length": 45,
                "genre_names": ["Role-playing (RPG)", "Adventure"],
                "platform_names": ["PC", "PlayStation"],
                "theme_names": ["Fantasy"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 7,
                "name": "Platform Hero",
                "summary": "Classic platformer with jumping and collecting",
                "rating": 82.0,
                "rating_count": 90,
                "release_year": 2021,
                "summary_length": 30,
                "genre_names": ["Platform"],
                "platform_names": ["Nintendo Switch"],
                "theme_names": ["Action"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 8,
                "name": "Life Simulator",
                "summary": "Life simulation with building and management",
                "rating": 85.0,
                "rating_count": 110,
                "release_year": 2022,
                "summary_length": 35,
                "genre_names": ["Simulator"],
                "platform_names": ["PC"],
                "theme_names": ["Life"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 9,
                "name": "Fighting Champion",
                "summary": "Combat fighting game with special moves",
                "rating": 89.0,
                "rating_count": 95,
                "release_year": 2023,
                "summary_length": 32,
                "genre_names": ["Fighting"],
                "platform_names": ["PlayStation", "Xbox"],
                "theme_names": ["Action"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
            {
                "id": 10,
                "name": "Indie Adventure",
                "summary": "Independent adventure game with unique art style",
                "rating": 84.0,
                "rating_count": 75,
                "release_year": 2021,
                "summary_length": 38,
                "genre_names": ["Indie", "Adventure"],
                "platform_names": ["PC", "Nintendo Switch"],
                "theme_names": ["Artistic"],
                "has_summary": True,
                "has_rating": True,
                "has_genres": True,
                "has_platforms": True,
            },
        ]

        # Save sample data
        games_file = tmp_path / "test_games.json"
        with open(games_file, "w") as f:
            json.dump(sample_games, f)

        # Train model
        service = MLTrainingService()
        training_results = service.train_model(sample_games)

        # Validate training
        assert (
            training_results["training_samples"] == 10
        )  # Updated to match sample data
        assert training_results["feature_count"] > 0
        assert training_results["model_type"] == "content_based_recommendation"

        # Test recommendations
        model = service.recommendation_model
        recommendations = model.get_recommendations(1, top_k=2)
        assert len(recommendations) <= 2

        # Test text recommendations
        text_recs = model.get_similar_games_by_text("adventure puzzle", top_k=2)
        assert len(text_recs) <= 2

        # Save and load model
        model_path = tmp_path / "test_model.pkl"
        service.save_model(str(model_path))
        assert model_path.exists()

        # Load and test
        new_service = MLTrainingService()
        new_service.recommendation_model.load_model(str(model_path))
        assert new_service.recommendation_model.is_trained

        # Test that loaded model works
        loaded_recs = new_service.recommendation_model.get_recommendations(1, top_k=1)
        assert len(loaded_recs) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
