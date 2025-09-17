"""
Unit tests for DataManager class.

Tests database operations, CRUD functionality, and data integrity.
"""

import pytest
import sqlite3
import json
import tempfile
import os

from data_pipeline.shared.data_manager import DataManager


class TestDataManager:
    """Test suite for DataManager class."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database file for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            return tmp.name

    @pytest.fixture
    def data_manager(self, temp_db_path):
        """Create a DataManager instance with temporary database."""
        dm = DataManager(temp_db_path)
        yield dm
        dm.close()
        # Clean up temporary file
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)

    def test_init_creates_database(self, temp_db_path):
        """Test that DataManager creates database file on initialization."""
        # Create DataManager (file will be created)
        dm = DataManager(temp_db_path)

        # Check that file was created
        assert os.path.exists(temp_db_path)

        # Clean up
        dm.close()
        os.unlink(temp_db_path)

    def test_create_tables(self, data_manager):
        """Test that all required tables are created."""
        # Check that tables exist
        cursor = data_manager.db.cursor()

        # Check games table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='games'"
        )
        assert cursor.fetchone() is not None

        # Check ingestion_log table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='ingestion_log'"
        )
        assert cursor.fetchone() is not None

        # Check processing_status table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='processing_status'"
        )
        assert cursor.fetchone() is not None

    def test_create_indexes(self, data_manager):
        """Test that indexes are created."""
        cursor = data_manager.db.cursor()

        # Check that indexes exist
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_games_name'"
        )
        assert cursor.fetchone() is not None

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_games_rating'"
        )
        assert cursor.fetchone() is not None

    def test_save_games_new(self, data_manager):
        """Test saving new games to database."""
        games = [
            {
                "id": 1,
                "name": "Test Game 1",
                "summary": "A test game",
                "genres": [{"id": 1, "name": "Action"}],
                "platforms": [{"id": 1, "name": "PC"}],
                "themes": [{"id": 1, "name": "Fantasy"}],
                "rating": 85.5,
                "rating_count": 100,
                "first_release_date": 1609459200,  # 2021-01-01
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

        result = data_manager.save_games(games)

        # Check return values (save_games returns int, not dict)
        assert result == 2

        # Check that games were saved
        cursor = data_manager.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM games")
        count = cursor.fetchone()[0]
        assert count == 2

        # Check specific game data
        cursor.execute("SELECT * FROM games WHERE id = 1")
        game = cursor.fetchone()
        assert game["name"] == "Test Game 1"
        assert game["rating"] == 85.5
        assert json.loads(game["genres"]) == [{"id": 1, "name": "Action"}]

    def test_save_games_update_existing(self, data_manager):
        """Test updating existing games."""
        # Save initial game
        initial_game = {
            "id": 1,
            "name": "Original Name",
            "summary": "Original summary",
            "genres": [],
            "platforms": [],
            "themes": [],
            "rating": 80.0,
            "rating_count": 50,
            "first_release_date": 1609459200,
        }
        data_manager.save_games([initial_game])

        # Update the game
        updated_game = {
            "id": 1,
            "name": "Updated Name",
            "summary": "Updated summary",
            "genres": [{"id": 1, "name": "Action"}],
            "platforms": [{"id": 1, "name": "PC"}],
            "themes": [{"id": 1, "name": "Fantasy"}],
            "rating": 90.0,
            "rating_count": 100,
            "first_release_date": 1609459200,
        }

        result = data_manager.save_games([updated_game])

        # Check return values (save_games returns int, not dict)
        assert result == 1

        # Check that game was updated
        cursor = data_manager.db.cursor()
        cursor.execute("SELECT * FROM games WHERE id = 1")
        game = cursor.fetchone()
        assert game["name"] == "Updated Name"
        assert game["rating"] == 90.0
        assert json.loads(game["genres"]) == [{"id": 1, "name": "Action"}]

    def test_save_games_skip_invalid(self, data_manager):
        """Test that games without ID are skipped."""
        games = [
            {
                "name": "Game without ID",
                "summary": "This should be skipped",
            },
            {
                "id": 1,
                "name": "Valid Game",
                "summary": "This should be saved",
                "genres": [],
                "platforms": [],
                "themes": [],
            },
        ]

        result = data_manager.save_games(games)

        # Check return values (save_games returns int, not dict)
        assert result == 1

        # Check that only valid game was saved
        cursor = data_manager.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM games")
        count = cursor.fetchone()[0]
        assert count == 1

    def test_get_games_basic(self, data_manager):
        """Test basic game retrieval."""
        # Add test games
        games = [
            {
                "id": 1,
                "name": "High Rated Game",
                "summary": "A highly rated game",
                "genres": [{"id": 1, "name": "Action"}],
                "platforms": [{"id": 1, "name": "PC"}],
                "themes": [{"id": 1, "name": "Fantasy"}],
                "rating": 95.0,
                "rating_count": 1000,
                "first_release_date": 1609459200,
            },
            {
                "id": 2,
                "name": "Low Rated Game",
                "summary": "A low rated game",
                "genres": [{"id": 2, "name": "Puzzle"}],
                "platforms": [{"id": 2, "name": "Mobile"}],
                "themes": [{"id": 2, "name": "Casual"}],
                "rating": 60.0,
                "rating_count": 100,
                "first_release_date": 1609459200,
            },
        ]
        data_manager.save_games(games)

        # Test basic retrieval
        retrieved_games = data_manager.get_games()
        assert len(retrieved_games) == 2

        # Test limit
        limited_games = data_manager.get_games(limit=1)
        assert len(limited_games) == 1
        assert (
            limited_games[0]["name"] == "High Rated Game"
        )  # Should be sorted by rating

    def test_get_games_filters(self, data_manager):
        """Test game retrieval with filters."""
        # Add test games
        games = [
            {
                "id": 1,
                "name": "Action Game",
                "summary": "An action game",
                "genres": [{"id": 1, "name": "Action"}],
                "platforms": [{"id": 1, "name": "PC"}],
                "themes": [{"id": 1, "name": "Fantasy"}],
                "rating": 90.0,
                "rating_count": 1000,
                "first_release_date": 1609459200,
            },
            {
                "id": 2,
                "name": "Puzzle Game",
                "summary": "A puzzle game",
                "genres": [{"id": 2, "name": "Puzzle"}],
                "platforms": [{"id": 2, "name": "Mobile"}],
                "themes": [{"id": 2, "name": "Casual"}],
                "rating": 70.0,
                "rating_count": 100,
                "first_release_date": 1609459200,
            },
        ]
        data_manager.save_games(games)

        # Test genre filter
        action_games = data_manager.get_games(genre="Action")
        assert len(action_games) == 1
        assert action_games[0]["name"] == "Action Game"

        # Test rating filter
        high_rated_games = data_manager.get_games(min_rating=80.0)
        assert len(high_rated_games) == 1
        assert high_rated_games[0]["name"] == "Action Game"

        # Test platform filter
        pc_games = data_manager.get_games(platform="PC")
        assert len(pc_games) == 1
        assert pc_games[0]["name"] == "Action Game"

    def test_count_games(self, data_manager):
        """Test game counting functionality."""
        # Initially should be 0
        assert data_manager.count_games() == 0

        # Add games
        games = [
            {
                "id": 1,
                "name": "Game 1",
                "summary": "First game",
                "genres": [],
                "platforms": [],
                "themes": [],
            },
            {
                "id": 2,
                "name": "Game 2",
                "summary": "Second game",
                "genres": [],
                "platforms": [],
                "themes": [],
            },
        ]
        data_manager.save_games(games)

        # Should now be 2
        assert data_manager.count_games() == 2

    def test_log_ingestion(self, data_manager):
        """Test ingestion logging functionality."""
        batch_id = "test_batch_001"

        # Log ingestion
        data_manager.log_ingestion(batch_id, 100, 95, 5, "completed")

        # Check that log was created
        cursor = data_manager.db.cursor()
        cursor.execute("SELECT * FROM ingestion_log WHERE batch_id = ?", (batch_id,))
        log = cursor.fetchone()

        assert log is not None
        assert log["batch_id"] == batch_id
        assert log["games_fetched"] == 100
        assert log["games_new"] == 95
        assert log["games_updated"] == 5
        assert log["status"] == "completed"

    def test_log_ingestion_error(self, data_manager):
        """Test ingestion error logging."""
        batch_id = "error_batch_001"

        # Log ingestion error
        error_message = "API rate limit exceeded"
        data_manager.log_ingestion(batch_id, 50, 0, 0, "error", error_message)

        # Check that error was logged
        cursor = data_manager.db.cursor()
        cursor.execute("SELECT * FROM ingestion_log WHERE batch_id = ?", (batch_id,))
        log = cursor.fetchone()

        assert log is not None
        assert log["status"] == "error"
        assert log["error_message"] == error_message

    def test_context_manager(self, temp_db_path):
        """Test DataManager as context manager."""
        with DataManager(temp_db_path) as dm:
            # Should be able to use the manager
            assert dm.count_games() == 0

            # Add a game
            games = [
                {
                    "id": 1,
                    "name": "Context Game",
                    "summary": "A game saved in context",
                    "genres": [],
                    "platforms": [],
                    "themes": [],
                }
            ]
            dm.save_games(games)
            assert dm.count_games() == 1

        # After context exit, connection should be closed
        # (We can't easily test this without accessing private attributes)

    def test_database_error_handling(self, temp_db_path):
        """Test error handling in database operations."""
        # Create a DataManager
        dm = DataManager(temp_db_path)

        # Close the connection to simulate an error
        dm.db.close()

        # Try to save games - should raise an error
        games = [{"id": 1, "name": "Test Game", "summary": "Test"}]

        with pytest.raises(sqlite3.Error):
            dm.save_games(games)

        # Clean up
        os.unlink(temp_db_path)

    def test_json_field_handling(self, data_manager):
        """Test that JSON fields are properly handled."""
        games = [
            {
                "id": 1,
                "name": "JSON Test Game",
                "summary": "Testing JSON fields",
                "genres": [
                    {"id": 1, "name": "Action"},
                    {"id": 2, "name": "Adventure"},
                ],
                "platforms": [
                    {"id": 1, "name": "PC"},
                    {"id": 2, "name": "PlayStation"},
                ],
                "themes": [
                    {"id": 1, "name": "Fantasy"},
                    {"id": 2, "name": "Medieval"},
                ],
                "rating": 85.0,
                "rating_count": 500,
                "first_release_date": 1609459200,
            }
        ]

        data_manager.save_games(games)

        # Retrieve and check JSON fields
        retrieved_games = data_manager.get_games()
        assert len(retrieved_games) == 1

        game = retrieved_games[0]
        assert len(game["genres"]) == 2
        assert game["genres"][0]["name"] == "Action"
        assert len(game["platforms"]) == 2
        assert game["platforms"][0]["name"] == "PC"
        assert len(game["themes"]) == 2
        assert game["themes"][0]["name"] == "Fantasy"
