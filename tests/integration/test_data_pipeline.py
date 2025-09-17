#!/usr/bin/env python3
"""
Integration tests for data pipeline components.

These tests verify that the data pipeline components work together
end-to-end without requiring external services.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock

from data_pipeline.shared.data_manager import DataManager
from data_pipeline.ingestion.smart_ingestion import SmartIngestion


class TestDataPipelineIntegration:
    """Test data pipeline integration."""

    def test_data_manager_and_smart_ingestion_integration(self):
        """Test that DataManager and SmartIngestion work together."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name

        try:
            # Test DataManager initialization
            data_manager = DataManager(db_path)
            assert data_manager.count_games() == 0

            # Create mock IGDB client
            mock_igdb_client = Mock()
            mock_igdb_client.fetch_games_sample.return_value = []

            # Test SmartIngestion initialization
            smart_ingestion = SmartIngestion(data_manager, igdb_client=mock_igdb_client)
            assert smart_ingestion.data_manager.count_games() == 0

            # Test that they share the same database
            summary = smart_ingestion.get_ingestion_summary()
            assert summary["current_games"] == 0
            assert summary["total_batches"] == 0

        finally:
            # Cleanup
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_database_persistence(self):
        """Test that data persists across multiple operations."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name

        try:
            # First operation
            data_manager1 = DataManager(db_path)
            data_manager1.save_games(
                [{"id": 1, "name": "Test Game 1", "summary": "Test summary 1"}]
            )
            assert data_manager1.count_games() == 1

            # Second operation (new instance)
            data_manager2 = DataManager(db_path)
            assert data_manager2.count_games() == 1

            # Verify data integrity
            games = data_manager2.get_games()
            assert len(games) == 1
            assert games[0]["name"] == "Test Game 1"

        finally:
            # Cleanup
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_ingestion_logging(self):
        """Test that ingestion logging works correctly."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name

        try:
            data_manager = DataManager(db_path)

            # Log an ingestion
            data_manager.log_ingestion(
                batch_id="test_batch_001",
                games_fetched=5,
                games_new=3,
                games_updated=2,
                status="completed",
            )

            # Verify logging
            stats = data_manager.get_ingestion_stats()
            assert stats["total_batches"] == 1
            assert stats["total_fetched"] == 5
            assert stats["total_new"] == 3
            assert stats["total_updated"] == 2

        finally:
            # Cleanup
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_error_handling_integration(self):
        """Test error handling across components."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name

        try:
            data_manager = DataManager(db_path)

            # Test invalid data handling
            data_manager.save_games(
                [
                    {"id": 1, "name": "Valid Game"},  # Valid
                    {"name": "Invalid Game"},  # Missing ID
                    {"id": 2, "name": "Another Valid Game"},  # Valid
                ]
            )

            # Should save valid games and skip invalid ones
            assert data_manager.count_games() == 2

            # Verify only valid games were saved
            games = data_manager.get_games()
            game_names = [game["name"] for game in games]
            assert "Valid Game" in game_names
            assert "Another Valid Game" in game_names
            assert "Invalid Game" not in game_names

        finally:
            # Cleanup
            if os.path.exists(db_path):
                os.unlink(db_path)


if __name__ == "__main__":
    pytest.main([__file__])
