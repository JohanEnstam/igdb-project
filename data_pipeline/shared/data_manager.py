#!/usr/bin/env python3
"""
DataManager - SQLite-based data management for IGDB game data

This module provides a robust data management layer for storing and retrieving
game data from the IGDB API. It handles deduplication, indexing, and provides
efficient querying capabilities for the recommendation system.

Key Features:
- SQLite-based storage for development and production
- Automatic deduplication via PRIMARY KEY constraints
- Proper indexing for fast queries
- Pipeline state tracking
- Smart ingestion support
"""

import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class DataManager:
    """
    SQLite-based data manager for IGDB game data.

    Provides CRUD operations, deduplication, and efficient querying
    for game recommendation system.
    """

    def __init__(self, db_path: str = "data/games.db"):
        """
        Initialize DataManager with SQLite database.

        Args:
            db_path: Path to SQLite database file

        Example:
            >>> dm = DataManager("data/games.db")
            >>> dm.create_tables()
        """
        self.db_path = db_path
        self.db: sqlite3.Connection = None  # type: ignore
        self._connect()
        self.create_tables()
        self.create_indexes()

    def _connect(self) -> None:
        """Establish connection to SQLite database."""
        try:
            # Ensure data directory exists
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

            connection = sqlite3.connect(self.db_path)
            connection.row_factory = sqlite3.Row  # Enable dict-like access
            self.db = connection
            logger.info(f"Connected to SQLite database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def create_tables(self) -> None:
        """
        Create database tables if they don't exist.

        Creates tables for games, ingestion tracking, and pipeline state.
        """
        try:
            # Games table with IGDB data
            self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    summary TEXT,
                    genres TEXT,  -- JSON string
                    platforms TEXT,  -- JSON string
                    themes TEXT,  -- JSON string
                    rating REAL,
                    rating_count INTEGER,
                    first_release_date INTEGER,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Ingestion tracking
            self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS ingestion_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id TEXT UNIQUE,
                    games_fetched INTEGER,
                    games_new INTEGER,
                    games_updated INTEGER,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    status TEXT,
                    error_message TEXT
                )
            """
            )

            # Pipeline state tracking
            self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS processing_status (
                    game_id INTEGER,
                    feature_extraction_status TEXT,
                    model_training_status TEXT,
                    last_processed_at TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES games (id)
                )
            """
            )

            self.db.commit()
            logger.info("Database tables created successfully")

        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {e}")
            raise

    def create_indexes(self) -> None:
        """
        Create indexes for efficient querying.

        Creates indexes on commonly queried fields for performance.
        """
        try:
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_games_rating ON games(rating)",
                "CREATE INDEX IF NOT EXISTS idx_games_name ON games(name)",
                "CREATE INDEX IF NOT EXISTS idx_games_genres ON games(genres)",
                "CREATE INDEX IF NOT EXISTS idx_games_platforms ON games(platforms)",
                "CREATE INDEX IF NOT EXISTS idx_games_themes ON games(themes)",
                "CREATE INDEX IF NOT EXISTS idx_games_created_at ON games(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_ingestion_batch_id ON ingestion_log(batch_id)",
                "CREATE INDEX IF NOT EXISTS idx_processing_game_id ON processing_status(game_id)",
            ]

            for index_sql in indexes:
                self.db.execute(index_sql)

            self.db.commit()
            logger.info("Database indexes created successfully")

        except sqlite3.Error as e:
            logger.error(f"Error creating indexes: {e}")
            raise

    def save_games(self, games: List[Dict[str, Any]]) -> int:
        """
        Save games to database with automatic deduplication.

        Args:
            games: List of game dictionaries from IGDB API

        Returns:
            Number of games saved

        Example:
            >>> games = [{"id": 1, "name": "Test Game", "rating": 85.5}]
            >>> saved_count = dm.save_games(games)
            >>> print(f"Saved {saved_count} games")
        """
        if not games:
            logger.warning("No games provided to save")
            return 0

        try:
            saved_count = 0

            for game in games:
                # Skip games without ID
                if not game.get("id"):
                    logger.warning(
                        f"Skipping game with no ID: {game.get('name', 'Unknown')}"
                    )
                    continue

                # Prepare data for insertion
                game_data = self._prepare_game_data(game)

                # Insert or replace (upsert) - automatic deduplication
                self.db.execute(
                    """
                    INSERT OR REPLACE INTO games
                    (id, name, summary, genres, platforms, themes, rating,
                     rating_count, first_release_date, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    game_data,
                )

                saved_count += 1

            self.db.commit()
            logger.info(f"Successfully saved {saved_count} games to database")
            return saved_count

        except sqlite3.Error as e:
            logger.error(f"Error saving games: {e}")
            self.db.rollback()
            raise

    def _prepare_game_data(self, game: Dict[str, Any]) -> Tuple:
        """
        Prepare game data for database insertion.

        Args:
            game: Raw game data from IGDB API

        Returns:
            Tuple of prepared data for SQL insertion
        """
        return (
            game.get("id"),
            game.get("name", ""),
            game.get("summary"),
            json.dumps(game.get("genres", [])),
            json.dumps(game.get("platforms", [])),
            json.dumps(game.get("themes", [])),
            game.get("rating"),
            game.get("rating_count"),
            game.get("first_release_date"),
            datetime.now().isoformat(),
        )

    def get_games(
        self,
        limit: Optional[int] = None,
        genre: Optional[str] = None,
        min_rating: Optional[float] = None,
        platform: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve games from database with optional filtering.

        Args:
            limit: Maximum number of games to return
            genre: Filter by genre (partial match)
            min_rating: Minimum rating threshold
            platform: Filter by platform (partial match)

        Returns:
            List of game dictionaries

        Example:
            >>> rpg_games = dm.get_games(limit=10, genre="RPG", min_rating=80.0)
            >>> print(f"Found {len(rpg_games)} RPG games with rating >= 80")
        """
        try:
            query = "SELECT * FROM games WHERE 1=1"
            params = []

            if genre:
                query += " AND genres LIKE ?"
                params.append(f"%{genre}%")

            if min_rating is not None:
                query += " AND rating >= ?"
                params.append(str(min_rating))

            if platform:
                query += " AND platforms LIKE ?"
                params.append(f"%{platform}%")

            query += " ORDER BY rating DESC"

            if limit:
                query += " LIMIT ?"
                params.append(str(limit))

            cursor = self.db.execute(query, params)
            games = []

            for row in cursor.fetchall():
                game = dict(row)
                # Parse JSON fields
                game["genres"] = json.loads(game["genres"]) if game["genres"] else []
                game["platforms"] = (
                    json.loads(game["platforms"]) if game["platforms"] else []
                )
                game["themes"] = json.loads(game["themes"]) if game["themes"] else []
                games.append(game)

            logger.info(f"Retrieved {len(games)} games from database")
            return games

        except sqlite3.Error as e:
            logger.error(f"Error retrieving games: {e}")
            raise

    def count_games(self) -> int:
        """
        Get total number of games in database.

        Returns:
            Total count of games

        Example:
            >>> total_games = dm.count_games()
            >>> print(f"Database contains {total_games} games")
        """
        try:
            cursor = self.db.execute("SELECT COUNT(*) FROM games")
            count = cursor.fetchone()[0]
            logger.debug(f"Database contains {count} games")
            return count
        except sqlite3.Error as e:
            logger.error(f"Error counting games: {e}")
            raise

    def get_game_by_id(self, game_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific game by ID.

        Args:
            game_id: IGDB game ID

        Returns:
            Game dictionary or None if not found

        Example:
            >>> game = dm.get_game_by_id(12345)
            >>> if game:
            ...     print(f"Found game: {game['name']}")
        """
        try:
            cursor = self.db.execute("SELECT * FROM games WHERE id = ?", (game_id,))
            row = cursor.fetchone()

            if row:
                game = dict(row)
                # Parse JSON fields
                game["genres"] = json.loads(game["genres"]) if game["genres"] else []
                game["platforms"] = (
                    json.loads(game["platforms"]) if game["platforms"] else []
                )
                game["themes"] = json.loads(game["themes"]) if game["themes"] else []
                return game

            return None

        except sqlite3.Error as e:
            logger.error(f"Error retrieving game {game_id}: {e}")
            raise

    def log_ingestion(
        self,
        batch_id: str,
        games_fetched: int,
        games_new: int,
        games_updated: int,
        status: str = "completed",
        error_message: Optional[str] = None,
    ) -> None:
        """
        Log ingestion batch details.

        Args:
            batch_id: Unique identifier for this ingestion batch
            games_fetched: Number of games fetched from API
            games_new: Number of new games added
            games_updated: Number of games updated
            status: Batch status (started, completed, failed)
            error_message: Error message if batch failed

        Example:
            >>> dm.log_ingestion("batch_001", 100, 95, 5, "completed")
        """
        try:
            self.db.execute(
                """
                INSERT OR REPLACE INTO ingestion_log
                (batch_id, games_fetched, games_new, games_updated,
                 started_at, completed_at, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    batch_id,
                    games_fetched,
                    games_new,
                    games_updated,
                    datetime.now().isoformat(),
                    datetime.now().isoformat() if status == "completed" else None,
                    status,
                    error_message,
                ),
            )

            self.db.commit()
            logger.info(f"Logged ingestion batch {batch_id}: {status}")

        except sqlite3.Error as e:
            logger.error(f"Error logging ingestion: {e}")
            raise

    def get_ingestion_stats(self) -> Dict[str, Any]:
        """
        Get ingestion statistics.

        Returns:
            Dictionary with ingestion statistics

        Example:
            >>> stats = dm.get_ingestion_stats()
            >>> print(f"Total batches: {stats['total_batches']}")
        """
        try:
            cursor = self.db.execute(
                """
                SELECT
                    COUNT(*) as total_batches,
                    SUM(games_fetched) as total_fetched,
                    SUM(games_new) as total_new,
                    SUM(games_updated) as total_updated
                FROM ingestion_log
                WHERE status = 'completed'
            """
            )

            row = cursor.fetchone()
            stats = dict(row) if row else {}

            # Add current game count
            stats["current_games"] = self.count_games()

            logger.info(f"Ingestion stats: {stats}")
            return stats

        except sqlite3.Error as e:
            logger.error(f"Error getting ingestion stats: {e}")
            raise

    def close(self) -> None:
        """Close database connection."""
        if self.db:
            self.db.close()
            logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Example usage
    with DataManager("data/games.db") as dm:
        # Test data
        test_games = [
            {
                "id": 1,
                "name": "Test Game 1",
                "summary": "A test game",
                "genres": [{"id": 1, "name": "RPG"}],
                "platforms": [{"id": 1, "name": "PC"}],
                "themes": [{"id": 1, "name": "Fantasy"}],
                "rating": 85.5,
                "rating_count": 1000,
            },
            {
                "id": 2,
                "name": "Test Game 2",
                "summary": "Another test game",
                "genres": [{"id": 2, "name": "Action"}],
                "platforms": [{"id": 2, "name": "PlayStation"}],
                "themes": [{"id": 2, "name": "Sci-Fi"}],
                "rating": 78.2,
                "rating_count": 500,
            },
        ]

        # Save test games
        saved_count = dm.save_games(test_games)
        print(f"Saved {saved_count} test games")

        # Test queries
        all_games = dm.get_games()
        print(f"Total games in database: {len(all_games)}")

        rpg_games = dm.get_games(genre="RPG")
        print(f"RPG games: {len(rpg_games)}")

        high_rated = dm.get_games(min_rating=80.0)
        print(f"High-rated games (>=80): {len(high_rated)}")

        # Test logging
        dm.log_ingestion("test_batch", 2, 2, 0, "completed")

        # Get stats
        stats = dm.get_ingestion_stats()
        print(f"Ingestion stats: {stats}")
