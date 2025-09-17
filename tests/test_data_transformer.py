#!/usr/bin/env python3
"""
Tests for DataTransformer - ETL pipeline for IGDB game data

This module contains comprehensive tests for the DataTransformer class,
ensuring data quality and transformation accuracy.
"""

import pytest

from data_pipeline.processing.data_transformer import DataTransformer


class TestDataTransformer:
    """Test suite for DataTransformer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = DataTransformer()

        # Sample raw game data
        self.sample_raw_game = {
            "id": 12345,
            "name": "Test Game",
            "summary": "A test game for unit testing",
            "genres": [12, 31],  # RPG, Adventure
            "platforms": [6, 48],  # PC, PlayStation 4
            "themes": [1, 2],  # Action, Fantasy
            "rating": 85.5,
            "rating_count": 100,
            "first_release_date": 1609459200,  # 2021-01-01
        }

        # Sample raw game with mixed data types
        self.mixed_raw_game = {
            "id": 67890,
            "name": "Mixed Data Game",
            "summary": "Game with mixed data types",
            "genres": [5, {"id": 33, "name": "Arcade"}],  # Mixed int and dict
            "platforms": [6, {"id": 48, "name": "PlayStation 4"}],
            "themes": [1, 2],
            "rating": 78.123456789,
            "rating_count": 50,
            "first_release_date": 1640995200,  # 2022-01-01
        }

        # Sample raw game with missing data
        self.incomplete_raw_game = {
            "id": 11111,
            "name": "Incomplete Game",
            "summary": None,
            "genres": [],
            "platforms": [],
            "themes": [],
            "rating": None,
            "rating_count": None,
            "first_release_date": None,
        }

    def test_transformer_initialization(self):
        """Test DataTransformer initialization."""
        transformer = DataTransformer()

        # Check that lookup dictionaries are populated
        assert len(transformer.genre_lookup) > 0
        assert len(transformer.platform_lookup) > 0
        assert len(transformer.theme_lookup) > 0

        # Check specific mappings
        assert transformer.genre_lookup[12] == "Role-playing (RPG)"
        assert transformer.platform_lookup[6] == "PC (Microsoft Windows)"
        assert transformer.theme_lookup[1] == "Action"

    def test_transform_basic_game(self):
        """Test transformation of basic game data."""
        clean_game = self.transformer.transform_game(self.sample_raw_game)

        # Basic fields
        assert clean_game["id"] == 12345
        assert clean_game["name"] == "Test Game"
        assert clean_game["summary"] == "A test game for unit testing"
        assert clean_game["rating"] == 85.5  # Should be rounded to 1 decimal
        assert clean_game["rating_count"] == 100

        # Date fields
        assert clean_game["release_date"] == "2021-01-01"
        assert clean_game["release_year"] == 2021

        # Resolved names
        assert clean_game["genre_names"] == ["Role-playing (RPG)", "Adventure"]
        assert clean_game["platform_names"] == [
            "PC (Microsoft Windows)",
            "PlayStation 4",
        ]
        assert clean_game["theme_names"] == ["Action", "Fantasy"]

        # Original IDs preserved
        assert clean_game["genre_ids"] == [12, 31]
        assert clean_game["platform_ids"] == [6, 48]
        assert clean_game["theme_ids"] == [1, 2]

        # Quality indicators
        assert clean_game["has_summary"] is True
        assert clean_game["has_rating"] is True
        assert clean_game["has_genres"] is True
        assert clean_game["has_platforms"] is True

        # Text metrics
        assert clean_game["summary_length"] == len("A test game for unit testing")
        assert clean_game["name_length"] == len("Test Game")

    def test_transform_mixed_data_types(self):
        """Test transformation with mixed data types (int and dict)."""
        clean_game = self.transformer.transform_game(self.mixed_raw_game)

        # Should handle both int and dict formats
        assert "Shooter" in clean_game["genre_names"]
        assert "Arcade" in clean_game["genre_names"]
        assert "PC (Microsoft Windows)" in clean_game["platform_names"]
        assert "PlayStation 4" in clean_game["platform_names"]

        # Rating should be rounded
        assert clean_game["rating"] == 78.1

    def test_transform_incomplete_data(self):
        """Test transformation with missing/incomplete data."""
        clean_game = self.transformer.transform_game(self.incomplete_raw_game)

        # Basic fields
        assert clean_game["id"] == 11111
        assert clean_game["name"] == "Incomplete Game"
        assert clean_game["summary"] == ""

        # Missing data should be None or empty
        assert clean_game["rating"] is None
        assert clean_game["rating_count"] == 0
        assert clean_game["release_date"] is None
        assert clean_game["release_year"] is None

        # Empty lists
        assert clean_game["genre_names"] == []
        assert clean_game["platform_names"] == []
        assert clean_game["theme_names"] == []

        # Quality indicators should reflect missing data
        assert clean_game["has_summary"] is False
        assert clean_game["has_rating"] is False
        assert clean_game["has_genres"] is False
        assert clean_game["has_platforms"] is False

    def test_clean_rating(self):
        """Test rating cleaning functionality."""
        # Test normal rating
        assert self.transformer._clean_rating(85.5) == 85.5
        assert self.transformer._clean_rating(78.123456789) == 78.1

        # Test None rating
        assert self.transformer._clean_rating(None) is None

        # Test edge cases
        assert self.transformer._clean_rating(0.0) == 0.0
        assert self.transformer._clean_rating(100.0) == 100.0

    def test_clean_release_date(self):
        """Test release date cleaning functionality."""
        # Test valid timestamp
        assert self.transformer._clean_release_date(1609459200) == "2021-01-01"
        assert self.transformer._clean_release_date(1640995200) == "2022-01-01"

        # Test None
        assert self.transformer._clean_release_date(None) is None

        # Test invalid timestamp
        assert self.transformer._clean_release_date(-1) is None

    def test_extract_year(self):
        """Test year extraction functionality."""
        # Test valid timestamp
        assert self.transformer._extract_year(1609459200) == 2021
        assert self.transformer._extract_year(1640995200) == 2022

        # Test None
        assert self.transformer._extract_year(None) is None

        # Test invalid timestamp
        assert self.transformer._extract_year(-1) is None

    def test_resolve_genres(self):
        """Test genre ID resolution."""
        # Test integer IDs
        genres = self.transformer._resolve_genres([12, 31])
        assert genres == ["Role-playing (RPG)", "Adventure"]

        # Test mixed int and dict
        mixed_genres = self.transformer._resolve_genres(
            [5, {"id": 33, "name": "Arcade"}]
        )
        assert "Shooter" in mixed_genres
        assert "Arcade" in mixed_genres

        # Test unknown IDs
        unknown_genres = self.transformer._resolve_genres([999])
        assert unknown_genres == ["Unknown Genre 999"]

        # Test empty list
        assert self.transformer._resolve_genres([]) == []

    def test_resolve_platforms(self):
        """Test platform ID resolution."""
        # Test integer IDs
        platforms = self.transformer._resolve_platforms([6, 48])
        assert platforms == ["PC (Microsoft Windows)", "PlayStation 4"]

        # Test unknown IDs
        unknown_platforms = self.transformer._resolve_platforms([999])
        assert unknown_platforms == ["Unknown Platform 999"]

    def test_resolve_themes(self):
        """Test theme ID resolution."""
        # Test integer IDs
        themes = self.transformer._resolve_themes([1, 2])
        assert themes == ["Action", "Fantasy"]

        # Test unknown IDs
        unknown_themes = self.transformer._resolve_themes([999])
        assert unknown_themes == ["Unknown Theme 999"]

    def test_transform_batch(self):
        """Test batch transformation."""
        raw_games = [
            self.sample_raw_game,
            self.mixed_raw_game,
            self.incomplete_raw_game,
        ]
        clean_games = self.transformer.transform_batch(raw_games)

        # Should transform all games
        assert len(clean_games) == 3

        # Check first game
        assert clean_games[0]["name"] == "Test Game"
        assert clean_games[0]["has_summary"] is True

        # Check second game
        assert clean_games[1]["name"] == "Mixed Data Game"
        assert clean_games[1]["has_summary"] is True

        # Check third game
        assert clean_games[2]["name"] == "Incomplete Game"
        assert clean_games[2]["has_summary"] is False

    def test_transform_batch_with_errors(self):
        """Test batch transformation with error handling."""
        # Create a game that will cause an error
        error_game = {"id": "invalid", "name": None}  # Missing required fields

        raw_games = [self.sample_raw_game, error_game]
        clean_games = self.transformer.transform_batch(raw_games)

        # Should return both games (our transformer is robust)
        assert len(clean_games) == 2
        assert clean_games[0]["name"] == "Test Game"
        assert (
            clean_games[1]["id"] == "invalid"
        )  # Should handle invalid data gracefully

    def test_get_data_quality_report(self):
        """Test data quality report generation."""
        clean_games = [
            self.transformer.transform_game(self.sample_raw_game),
            self.transformer.transform_game(self.mixed_raw_game),
            self.transformer.transform_game(self.incomplete_raw_game),
        ]

        report = self.transformer.get_data_quality_report(clean_games)

        # Check report structure
        assert "total_games" in report
        assert "quality_score" in report
        assert "has_summary" in report
        assert "has_rating" in report
        assert "has_genres" in report
        assert "has_platforms" in report
        assert "avg_rating" in report
        assert "avg_genres_per_game" in report
        assert "avg_platforms_per_game" in report

        # Check values
        assert report["total_games"] == 3
        assert 0 <= report["quality_score"] <= 100
        assert report["avg_genres_per_game"] > 0
        assert report["avg_platforms_per_game"] > 0

    def test_get_data_quality_report_empty(self):
        """Test data quality report with empty data."""
        report = self.transformer.get_data_quality_report([])

        assert report["total_games"] == 0
        assert report["quality_score"] == 0

    def test_error_handling(self):
        """Test error handling in transformation."""
        # Test with completely invalid data
        invalid_game = {"invalid": "data"}

        clean_game = self.transformer.transform_game(invalid_game)

        # Our transformer is robust and handles invalid data gracefully
        # It should return a clean game structure with default values
        assert isinstance(clean_game, dict)
        assert clean_game["id"] is None
        assert clean_game["name"] == ""
        assert clean_game["summary"] == ""
        assert clean_game["has_summary"] is False
        assert clean_game["has_rating"] is False

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test very long strings
        long_game = self.sample_raw_game.copy()
        long_game["name"] = "A" * 1000
        long_game["summary"] = "B" * 10000

        clean_game = self.transformer.transform_game(long_game)

        assert clean_game["name_length"] == 1000
        assert clean_game["summary_length"] == 10000

        # Test extreme ratings
        extreme_game = self.sample_raw_game.copy()
        extreme_game["rating"] = 999.999999999

        clean_game = self.transformer.transform_game(extreme_game)
        assert clean_game["rating"] == 1000.0  # Should be rounded

        # Test negative rating
        negative_game = self.sample_raw_game.copy()
        negative_game["rating"] = -10.5

        clean_game = self.transformer.transform_game(negative_game)
        assert clean_game["rating"] == -10.5


class TestDataTransformerIntegration:
    """Integration tests for DataTransformer with real data."""

    def test_with_real_database_data(self):
        """Test DataTransformer with real database data."""
        from data_pipeline.shared.data_manager import DataManager

        # Use test database
        with DataManager("data/test_games.db") as dm:
            # Get a few games from database
            raw_games = dm.get_games(limit=5)

            if raw_games:
                transformer = DataTransformer()
                clean_games = transformer.transform_batch(raw_games)

                # Should transform successfully
                assert len(clean_games) > 0

                # Check quality
                report = transformer.get_data_quality_report(clean_games)
                assert report["total_games"] > 0
                assert report["quality_score"] > 0

    def test_performance_with_large_dataset(self):
        """Test performance with larger dataset."""
        # Create a large batch of test data
        large_batch = []
        for i in range(100):
            game = {
                "id": i,
                "name": f"Test Game {i}",
                "summary": f"This is test game number {i}",
                "genres": [12, 31],
                "platforms": [6, 48],
                "themes": [1, 2],
                "rating": 80.0 + (i % 20),
                "rating_count": 100 + i,
                "first_release_date": 1609459200 + (i * 86400),
            }
            large_batch.append(game)

        transformer = DataTransformer()

        # Time the transformation
        import time

        start_time = time.time()
        clean_games = transformer.transform_batch(large_batch)
        end_time = time.time()

        # Should complete in reasonable time (< 1 second for 100 games)
        assert end_time - start_time < 1.0
        assert len(clean_games) == 100

        # Check quality report
        report = transformer.get_data_quality_report(clean_games)
        assert report["total_games"] == 100
        assert report["quality_score"] > 90  # Should be high quality


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
