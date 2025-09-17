#!/usr/bin/env python3
"""
SmartIngestion - Intelligent data ingestion with re-fetching avoidance

This module provides smart ingestion capabilities that avoid unnecessary
re-fetching of data from the IGDB API. It integrates with DataManager
to provide efficient data collection for the recommendation system.

Key Features:
- Avoid re-fetching existing data
- Batch processing with configurable limits
- Rate limiting compliance
- Error handling and retry logic
- Integration with DataManager
"""

import logging
import time
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from data_pipeline.shared.data_manager import DataManager
from data_pipeline.ingestion.main import IGDBDataIngestion

logger = logging.getLogger(__name__)


class SmartIngestion:
    """
    Smart ingestion system that avoids unnecessary re-fetching.

    Integrates with DataManager to provide efficient data collection
    while respecting IGDB API rate limits and avoiding duplicate work.
    """

    def __init__(
        self,
        data_manager: DataManager,
        igdb_client: Optional[IGDBDataIngestion] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        """
        Initialize SmartIngestion with DataManager.

        Args:
            data_manager: DataManager instance for database operations
            igdb_client: IGDB API client (optional, will create if None)
            client_id: IGDB client ID (required if igdb_client is None)
            client_secret: IGDB client secret (required if igdb_client is None)

        Example:
            >>> dm = DataManager("data/games.db")
            >>> si = SmartIngestion(dm, client_id="xxx", client_secret="yyy")
            >>> count = si.fetch_if_needed(100)
        """
        self.data_manager = data_manager

        if igdb_client:
            self.igdb_client = igdb_client
        else:
            if not client_id or not client_secret:
                raise ValueError(
                    "client_id and client_secret are required when igdb_client is not provided"
                )
            self.igdb_client = IGDBDataIngestion(client_id, client_secret)
            # Authenticate the client
            self.igdb_client.authenticate()

        logger.info("SmartIngestion initialized")

    def fetch_if_needed(self, target_count: int = 100) -> int:
        """
        Fetch games from IGDB only if needed to reach target count.

        Args:
            target_count: Desired number of games in database

        Returns:
            Current number of games in database after fetch

        Example:
            >>> current_count = si.fetch_if_needed(100)
            >>> print(f"Database now has {current_count} games")
        """
        try:
            # Check current database count
            current_count = self.data_manager.count_games()

            if current_count >= target_count:
                logger.info(f"✅ Already have {current_count} games, no need to fetch")
                return current_count

            # Calculate how many more games needed
            needed = target_count - current_count
            logger.info(f"📥 Need {needed} more games, fetching from IGDB...")

            # Generate batch ID for tracking
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

            # Log ingestion start
            self.data_manager.log_ingestion(
                batch_id=batch_id,
                games_fetched=0,
                games_new=0,
                games_updated=0,
                status="started",
            )

            # Fetch from IGDB with rate limiting
            games = self.igdb_client.fetch_games_sample(needed)

            if not games:
                logger.warning("No games fetched from IGDB")
                self.data_manager.log_ingestion(
                    batch_id=batch_id,
                    games_fetched=0,
                    games_new=0,
                    games_updated=0,
                    status="error",
                    error_message="No games fetched from IGDB",
                )
                return current_count

            # Save to database (automatic deduplication)
            saved_count = self.data_manager.save_games(games)

            # Log successful completion
            self.data_manager.log_ingestion(
                batch_id=batch_id,
                games_fetched=len(games),
                games_new=saved_count,  # Assuming all are new for simplicity
                games_updated=0,
                status="completed",
            )

            # Return new count
            new_count = self.data_manager.count_games()
            logger.info(
                f"✅ Successfully fetched {saved_count} games. Database now has {new_count} games"
            )

            return new_count

        except Exception as e:
            logger.error(f"Error in smart ingestion: {e}")

            # Log error
            self.data_manager.log_ingestion(
                batch_id=batch_id if "batch_id" in locals() else "unknown",
                games_fetched=0,
                games_new=0,
                games_updated=0,
                status="error",
                error_message=str(e),
            )
            raise

    def fetch_with_strategy(
        self, strategy: str = "balanced", target_count: int = 100
    ) -> int:
        """
        Fetch games using different strategies.

        Args:
            strategy: Fetching strategy ("balanced", "high_rated", "recent")
            target_count: Desired number of games

        Returns:
            Current number of games in database

        Example:
            >>> count = si.fetch_with_strategy("high_rated", 200)
        """
        try:
            current_count = self.data_manager.count_games()

            if current_count >= target_count:
                logger.info(f"✅ Already have {current_count} games, no need to fetch")
                return current_count

            needed = target_count - current_count
            logger.info(f"📥 Fetching {needed} games using '{strategy}' strategy...")

            # Generate batch ID
            batch_id = f"{strategy}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

            # Log start
            self.data_manager.log_ingestion(
                batch_id=batch_id,
                games_fetched=0,
                games_new=0,
                games_updated=0,
                status="started",
            )

            # Fetch based on strategy
            if strategy == "high_rated":
                games = self._fetch_high_rated_games(needed)
            elif strategy == "recent":
                games = self._fetch_recent_games(needed)
            else:  # balanced
                games = self.igdb_client.fetch_games_sample(needed, strategy=strategy)

            if not games:
                logger.warning(f"No games fetched using '{strategy}' strategy")
                self.data_manager.log_ingestion(
                    batch_id=batch_id,
                    games_fetched=0,
                    games_new=0,
                    games_updated=0,
                    status="error",
                    error_message=f"No games fetched using '{strategy}' strategy",
                )
                return current_count

            # Save to database
            saved_count = self.data_manager.save_games(games)

            # Log completion
            self.data_manager.log_ingestion(
                batch_id=batch_id,
                games_fetched=len(games),
                games_new=saved_count,
                games_updated=0,
                status="completed",
            )

            new_count = self.data_manager.count_games()
            logger.info(
                f"✅ Successfully fetched {saved_count} games using '{strategy}' strategy. Database now has {new_count} games"
            )

            return new_count

        except Exception as e:
            logger.error(f"Error in strategy-based fetch: {e}")
            self.data_manager.log_ingestion(
                batch_id=batch_id if "batch_id" in locals() else "unknown",
                games_fetched=0,
                games_new=0,
                games_updated=0,
                status="error",
                error_message=str(e),
            )
            raise

    def _fetch_high_rated_games(self, count: int) -> List[Dict[str, Any]]:
        """
        Fetch high-rated games from IGDB.

        Args:
            count: Number of games to fetch

        Returns:
            List of high-rated games
        """
        logger.info(f"Fetching {count} high-rated games...")

        # Use IGDB client with high rating filter
        query = f"""
        fields id,name,summary,genres,platforms,themes,rating,rating_count,first_release_date;
        where rating >= 80 & summary != null;
        limit {count};
        sort rating desc;
        """

        return self.igdb_client._make_request("games", query)

    def _fetch_recent_games(self, count: int) -> List[Dict[str, Any]]:
        """
        Fetch recent games from IGDB.

        Args:
            count: Number of games to fetch

        Returns:
            List of recent games
        """
        logger.info(f"Fetching {count} recent games...")

        # Use IGDB client with recent release filter
        current_timestamp = int(time.time())
        one_year_ago = current_timestamp - (365 * 24 * 60 * 60)

        query = f"""
        fields id,name,summary,genres,platforms,themes,rating,rating_count,first_release_date;
        where first_release_date >= {one_year_ago} & summary != null;
        limit {count};
        sort first_release_date desc;
        """

        return self.igdb_client._make_request("games", query)

    def get_ingestion_summary(self) -> Dict[str, Any]:
        """
        Get summary of ingestion activities.

        Returns:
            Dictionary with ingestion summary

        Example:
            >>> summary = si.get_ingestion_summary()
            >>> print(f"Total batches: {summary['total_batches']}")
        """
        try:
            stats = self.data_manager.get_ingestion_stats()
            current_count = self.data_manager.count_games()

            summary = {
                "current_games": current_count,
                "total_batches": stats.get("total_batches", 0),
                "total_fetched": stats.get("total_fetched", 0),
                "total_games_fetched": stats.get(
                    "total_fetched", 0
                ),  # Alias for compatibility
                "total_new": stats.get("total_new", 0),
                "total_games_new": stats.get("total_new", 0),  # Alias for compatibility
                "total_updated": stats.get("total_updated", 0),
                "total_games_updated": stats.get(
                    "total_updated", 0
                ),  # Alias for compatibility
                "efficiency": self._calculate_efficiency(stats),
            }

            logger.info(f"Ingestion summary: {summary}")
            return summary

        except Exception as e:
            logger.error(f"Error getting ingestion summary: {e}")
            raise

    def _calculate_efficiency(self, stats: Dict[str, Any]) -> float:
        """
        Calculate ingestion efficiency (new games / total fetched).

        Args:
            stats: Ingestion statistics

        Returns:
            Efficiency percentage
        """
        total_fetched = stats.get("total_fetched", 0)
        total_new = stats.get("total_new", 0)

        if total_fetched == 0:
            return 100.0

        efficiency = (total_new / total_fetched) * 100
        return round(efficiency, 2)

    def smart_ingest(self, target_count: int = 100, strategy: str = "balanced") -> int:
        """
        Smart ingestion with strategy support.

        Args:
            target_count: Target number of games in database
            strategy: Fetching strategy (balanced, high_rated, recent)

        Returns:
            Final count of games in database
        """
        if strategy == "balanced":
            return self.fetch_if_needed(target_count)
        else:
            return self.fetch_with_strategy(strategy, target_count)

    def close(self) -> None:
        """Close the DataManager connection."""
        if self.data_manager:
            self.data_manager.close()

    def __enter__(self):
        """Context manager entry point."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        self.close()


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Example usage
    with DataManager("data/games.db") as dm:
        si = SmartIngestion(dm)

        # Test smart ingestion
        print("Testing smart ingestion...")
        count = si.fetch_if_needed(10)
        print(f"Database now has {count} games")

        # Test strategy-based fetching
        print("\nTesting high-rated strategy...")
        count = si.fetch_with_strategy("high_rated", 15)
        print(f"Database now has {count} games")

        # Get summary
        summary = si.get_ingestion_summary()
        print(f"\nIngestion summary: {summary}")
