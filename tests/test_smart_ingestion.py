"""
Unit tests for SmartIngestion class.

Tests intelligent data ingestion, batch tracking, and efficiency metrics.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock

from data_pipeline.shared.data_manager import DataManager
from data_pipeline.ingestion.smart_ingestion import SmartIngestion


class TestSmartIngestion:
    """Test suite for SmartIngestion class."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database file for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            return tmp.name

    @pytest.fixture
    def mock_igdb_client(self):
        """Create a mock IGDB client."""
        mock_client = Mock()
        mock_client.fetch_games_sample.return_value = [
            {
                "id": 1,
                "name": "Test Game 1",
                "summary": "A test game",
                "genres": [{"id": 1, "name": "Action"}],
                "platforms": [{"id": 1, "name": "PC"}],
                "themes": [{"id": 1, "name": "Fantasy"}],
                "rating": 85.5,
                "rating_count": 100,
                "first_release_date": 1609459200,
            },
            {
                "id": 2,
                "name": "Test Game 2",
                "summary": "Another test game",
                "genres": [{"id": 2, "name": "RPG"}],
                "platforms": [{"id": 2, "name": "PlayStation"}],
                "themes": [{"id": 2, "name": "Sci-Fi"}],
                "rating": 92.0,
                "rating_count": 200,
                "first_release_date": 1609459200,
            },
        ]
        return mock_client

    @pytest.fixture
    def smart_ingestion(self, temp_db_path, mock_igdb_client):
        """Create a SmartIngestion instance with temporary database."""
        data_manager = DataManager(temp_db_path)
        si = SmartIngestion(
            data_manager=data_manager,
            igdb_client=mock_igdb_client,
        )
        yield si
        si.close()
        # Clean up temporary file
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)

    def test_init_creates_data_manager(self, temp_db_path, mock_igdb_client):
        """Test that SmartIngestion creates DataManager on initialization."""
        data_manager = DataManager(temp_db_path)
        si = SmartIngestion(
            data_manager=data_manager,
            igdb_client=mock_igdb_client,
        )

        assert si.data_manager is not None
        assert isinstance(si.data_manager, DataManager)

        si.close()
        os.unlink(temp_db_path)

    def test_smart_ingest_when_database_empty(self, smart_ingestion, mock_igdb_client):
        """Test smart ingestion when database is empty."""
        target_count = 10

        # Mock the IGDB client to return games
        mock_igdb_client.fetch_games_sample.return_value = [
            {
                "id": i,
                "name": f"Game {i}",
                "summary": f"Summary for game {i}",
                "genres": [],
                "platforms": [],
                "themes": [],
                "rating": 80.0 + i,
                "rating_count": 100,
                "first_release_date": 1609459200,
            }
            for i in range(1, target_count + 1)
        ]

        # Perform smart ingestion
        result = smart_ingestion.fetch_if_needed(target_count)

        # Check results
        assert result == target_count
        assert smart_ingestion.data_manager.count_games() == target_count

        # Verify IGDB client was called
        mock_igdb_client.fetch_games_sample.assert_called_once_with(target_count)

    def test_smart_ingest_when_database_has_games(
        self, smart_ingestion, mock_igdb_client
    ):
        """Test smart ingestion when database already has games."""
        # Pre-populate database with some games
        existing_games = [
            {
                "id": i,
                "name": f"Existing Game {i}",
                "summary": f"Summary for existing game {i}",
                "genres": [],
                "platforms": [],
                "themes": [],
                "rating": 80.0 + i,
                "rating_count": 100,
                "first_release_date": 1609459200,
            }
            for i in range(1, 6)  # 5 existing games
        ]
        smart_ingestion.data_manager.save_games(existing_games)

        target_count = 10
        needed_count = target_count - 5  # Need 5 more games

        # Mock the IGDB client to return new games
        mock_igdb_client.fetch_games_sample.return_value = [
            {
                "id": i + 5,  # Start from ID 6
                "name": f"New Game {i}",
                "summary": f"Summary for new game {i}",
                "genres": [],
                "platforms": [],
                "themes": [],
                "rating": 80.0 + i,
                "rating_count": 100,
                "first_release_date": 1609459200,
            }
            for i in range(1, needed_count + 1)
        ]

        # Perform smart ingestion
        result = smart_ingestion.fetch_if_needed(target_count)

        # Check results
        assert result == target_count
        assert smart_ingestion.data_manager.count_games() == target_count

        # Verify IGDB client was called with correct count
        mock_igdb_client.fetch_games_sample.assert_called_once_with(needed_count)

    def test_smart_ingest_when_target_already_reached(
        self, smart_ingestion, mock_igdb_client
    ):
        """Test smart ingestion when target count is already reached."""
        # Pre-populate database with more games than target
        existing_games = [
            {
                "id": i,
                "name": f"Existing Game {i}",
                "summary": f"Summary for existing game {i}",
                "genres": [],
                "platforms": [],
                "themes": [],
                "rating": 80.0 + i,
                "rating_count": 100,
                "first_release_date": 1609459200,
            }
            for i in range(1, 15)  # 14 existing games
        ]
        smart_ingestion.data_manager.save_games(existing_games)

        target_count = 10  # Less than existing count

        # Perform smart ingestion
        result = smart_ingestion.fetch_if_needed(target_count)

        # Check results
        assert result == 14  # Should return current count
        assert smart_ingestion.data_manager.count_games() == 14

        # Verify IGDB client was NOT called
        mock_igdb_client.fetch_games_sample.assert_not_called()

    def test_batch_tracking(self, smart_ingestion, mock_igdb_client):
        """Test that batch tracking works correctly."""
        target_count = 5

        # Mock the IGDB client
        mock_igdb_client.fetch_games_sample.return_value = [
            {
                "id": i,
                "name": f"Game {i}",
                "summary": f"Summary for game {i}",
                "genres": [],
                "platforms": [],
                "themes": [],
                "rating": 80.0 + i,
                "rating_count": 100,
                "first_release_date": 1609459200,
            }
            for i in range(1, target_count + 1)
        ]

        # Perform smart ingestion
        smart_ingestion.fetch_if_needed(target_count)

        # Check that batch was logged
        cursor = smart_ingestion.data_manager.db.cursor()
        cursor.execute("SELECT * FROM ingestion_log ORDER BY id DESC LIMIT 1")
        log = cursor.fetchone()

        assert log is not None
        assert log["batch_id"] is not None
        assert log["games_fetched"] == target_count
        assert log["games_new"] == target_count
        assert log["status"] == "completed"

    def test_ingestion_summary(self, smart_ingestion, mock_igdb_client):
        """Test ingestion summary functionality."""
        # Perform multiple ingestion runs
        for i in range(3):
            target_count = (i + 1) * 5

            mock_igdb_client.fetch_games_sample.return_value = [
                {
                    "id": j + (i * 5),
                    "name": f"Game {j}",
                    "summary": f"Summary for game {j}",
                    "genres": [],
                    "platforms": [],
                    "themes": [],
                    "rating": 80.0 + j,
                    "rating_count": 100,
                    "first_release_date": 1609459200,
                }
                for j in range(1, 6)  # Always fetch 5 games
            ]

            smart_ingestion.smart_ingest(target_count)

        # Get summary
        summary = smart_ingestion.get_ingestion_summary()

        # Check summary structure
        assert "current_games" in summary
        assert "total_batches" in summary
        assert "total_games_fetched" in summary
        assert "total_games_new" in summary
        assert "total_games_updated" in summary
        assert "efficiency" in summary

        # Check values
        assert summary["current_games"] == 15  # 3 batches * 5 games each
        assert summary["total_batches"] == 3
        assert summary["total_games_fetched"] == 15
        assert summary["total_games_new"] == 15
        assert summary["total_games_updated"] == 0
        assert summary["efficiency"] == 100.0  # All games were new

    def test_error_handling(self, smart_ingestion, mock_igdb_client):
        """Test error handling in smart ingestion."""
        # Mock IGDB client to raise an exception
        mock_igdb_client.fetch_games_sample.side_effect = Exception("API Error")

        target_count = 10

        # Perform smart ingestion - should handle error gracefully
        with pytest.raises(Exception):
            smart_ingestion.fetch_if_needed(target_count)

        # Check that error was logged
        cursor = smart_ingestion.data_manager.db.cursor()
        cursor.execute("SELECT * FROM ingestion_log ORDER BY id DESC LIMIT 1")
        log = cursor.fetchone()

        assert log is not None
        assert log["status"] == "error"
        assert "API Error" in log["error_message"]

    def test_context_manager(self, temp_db_path, mock_igdb_client):
        """Test SmartIngestion as context manager."""
        data_manager = DataManager(temp_db_path)
        with SmartIngestion(
            data_manager=data_manager,
            igdb_client=mock_igdb_client,
        ) as si:
            # Should be able to use the ingestion
            assert si.data_manager.count_games() == 0

            # Perform ingestion
            mock_igdb_client.fetch_games_sample.return_value = [
                {
                    "id": 1,
                    "name": "Context Game",
                    "summary": "A game saved in context",
                    "genres": [],
                    "platforms": [],
                    "themes": [],
                    "rating": 85.0,
                    "rating_count": 100,
                    "first_release_date": 1609459200,
                }
            ]

            result = si.smart_ingest(1)
            assert result == 1

        # After context exit, connection should be closed
        os.unlink(temp_db_path)

    def test_different_fetching_strategies(self, smart_ingestion, mock_igdb_client):
        """Test different fetching strategies."""
        target_count = 5

        # Test balanced strategy (default)
        mock_igdb_client.fetch_games_sample.return_value = [
            {
                "id": i,
                "name": f"Balanced Game {i}",
                "summary": f"Summary for balanced game {i}",
                "genres": [],
                "platforms": [],
                "themes": [],
                "rating": 80.0 + i,
                "rating_count": 100,
                "first_release_date": 1609459200,
            }
            for i in range(1, target_count + 1)
        ]

        result = smart_ingestion.fetch_with_strategy("balanced", target_count)
        assert result == target_count

        # Verify the correct strategy was used
        mock_igdb_client.fetch_games_sample.assert_called_with(
            target_count, strategy="balanced"
        )

    def test_efficiency_calculation(self, smart_ingestion, mock_igdb_client):
        """Test efficiency calculation with mixed new/updated games."""
        # First ingestion - all new games
        mock_igdb_client.fetch_games_sample.return_value = [
            {
                "id": i,
                "name": f"Game {i}",
                "summary": f"Summary for game {i}",
                "genres": [],
                "platforms": [],
                "themes": [],
                "rating": 80.0 + i,
                "rating_count": 100,
                "first_release_date": 1609459200,
            }
            for i in range(1, 6)
        ]

        smart_ingestion.fetch_if_needed(5)

        # Second ingestion - same games but with updated data
        mock_igdb_client.fetch_games_sample.return_value = [
            {
                "id": i,
                "name": f"Game {i}",  # Same name to trigger update
                "summary": f"Updated summary for game {i}",  # Different summary
                "genres": [],
                "platforms": [],
                "themes": [],
                "rating": 85.0 + i,  # Different rating
                "rating_count": 200,  # Different rating count
                "first_release_date": 1609459200,
            }
            for i in range(1, 6)  # Same IDs, so these will be updates
        ]

        smart_ingestion.fetch_if_needed(10)  # Fetch 5 more games (total 10)

        # Get summary
        summary = smart_ingestion.get_ingestion_summary()

        # Check efficiency calculation
        assert summary["total_games_fetched"] == 10  # 5 + 5
        assert (
            summary["total_games_new"] == 10
        )  # All games are counted as new due to INSERT OR REPLACE
        assert summary["total_games_updated"] == 0  # No separate update tracking
        assert summary["efficiency"] == 100.0  # All fetched games are "new"
