#!/usr/bin/env python3
"""
IGDB Data Ingestion Script

This script fetches game data from IGDB API using stratified sampling
for development dataset (2000 games) or full dataset for production.

Usage:
    python -m data_pipeline.ingestion.main --local  # Development mode
    python -m data_pipeline.ingestion.main --full    # Production mode
"""

import argparse
import json
import os
import time
from typing import Dict, List, Any, Optional
import requests
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IGDBDataIngestion:
    """Handles data ingestion from IGDB API with rate limiting and error handling."""

    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize IGDB data ingestion.

        Args:
            client_id: IGDB API client ID
            client_secret: IGDB API client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.igdb.com/v4"
        self.access_token: Optional[str] = None
        self.rate_limit_delay = 1 / 4  # 4 requests per second (IGDB API limit)

    def authenticate(self) -> bool:
        """
        Authenticate with IGDB API and get access token.

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            auth_url = "https://id.twitch.tv/oauth2/token"
            auth_data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
            }

            response = requests.post(auth_url, data=auth_data)
            response.raise_for_status()

            auth_response = response.json()
            self.access_token = auth_response["access_token"]

            print("✅ Successfully authenticated with IGDB API")
            return True

        except requests.RequestException as e:
            print(f"❌ Authentication failed: {e}")
            return False

    def _make_request(
        self, endpoint: str, data: str, max_retries: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Make authenticated request to IGDB API with rate limiting and retry logic.

        Args:
            endpoint: API endpoint (e.g., 'games', 'genres')
            data: Query data for the request
            max_retries: Maximum number of retry attempts

        Returns:
            List of game data dictionaries
        """
        if not self.access_token:
            raise ValueError("Not authenticated. Call authenticate() first.")

        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "text/plain",
        }

        url = f"{self.base_url}/{endpoint}"

        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Making request to {endpoint} (attempt {attempt + 1})")
                response = requests.post(url, headers=headers, data=data, timeout=30)

                # Handle rate limiting (429)
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 1))
                    logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue

                # Handle other HTTP errors
                response.raise_for_status()

                # Rate limiting - always wait between requests
                time.sleep(self.rate_limit_delay)

                result = response.json()
                logger.info(
                    f"✅ Successfully fetched {len(result)} records from {endpoint}"
                )
                return result

            except requests.exceptions.Timeout:
                logger.warning(f"⏰ Request timeout (attempt {attempt + 1})")
                if attempt < max_retries:
                    time.sleep(2**attempt)  # Exponential backoff
                    continue

            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Request failed: {e}")
                if attempt < max_retries:
                    time.sleep(2**attempt)  # Exponential backoff
                    continue

            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON decode error: {e}")
                return []

        logger.error(f"❌ All {max_retries + 1} attempts failed for {endpoint}")
        return []

    def fetch_genres(self) -> List[Dict[str, Any]]:
        """
        Fetch all available genres from IGDB.

        Returns:
            List of genre dictionaries
        """
        print("📋 Fetching genres...")

        query = "fields id,name,slug; limit 50;"
        genres = self._make_request("genres", query)

        print(f"✅ Fetched {len(genres)} genres")
        return genres

    def fetch_platforms(self) -> List[Dict[str, Any]]:
        """
        Fetch all available platforms from IGDB.

        Returns:
            List of platform dictionaries
        """
        print("🖥️ Fetching platforms...")

        query = "fields id,name,slug; limit 50;"
        platforms = self._make_request("platforms", query)

        print(f"✅ Fetched {len(platforms)} platforms")
        return platforms

    def fetch_games_sample(self, sample_size: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch sample of games for development and testing.

        Args:
            sample_size: Number of games to fetch (default: 10 for testing)

        Returns:
            List of game dictionaries
        """
        logger.info(f"🎮 Fetching {sample_size} games for testing...")

        # Query for games with all fields (as requested)
        query = f"""
        fields *;
        where rating != null & summary != null;
        limit {sample_size};
        sort rating desc;
        """

        games = self._make_request("games", query)

        if not games:
            logger.error("❌ No games fetched")
            return []

        logger.info(f"✅ Successfully fetched {len(games)} games")
        return games

    def fetch_games_full(self) -> List[Dict[str, Any]]:
        """
        Fetch full dataset of games (350k+ games).
        WARNING: This will take several hours and use significant API quota.

        Returns:
            List of all game dictionaries
        """
        print("🎮 Fetching FULL dataset (350k+ games)...")
        print("⚠️ WARNING: This will take 3+ hours and use significant API quota!")

        # Query for all games with essential fields
        query = """
        fields id,name,summary,genres,platforms,themes,release_dates,rating,
        rating_count;
        where rating != null & summary != null;
        limit 500;
        sort rating desc;
        """

        all_games = []
        offset = 0

        while True:
            # Add offset to query
            current_query = query + f" offset {offset};"

            games_batch = self._make_request("games", current_query)

            if not games_batch:
                print("✅ No more games available")
                break

            all_games.extend(games_batch)
            offset += 500

            # Progress update every 5000 games
            if len(all_games) % 5000 == 0:
                print(f"📊 Fetched {len(all_games)} games...")

        print(f"✅ Fetched {len(all_games)} games total")
        return all_games

    def save_data(self, data: List[Dict[str, Any]], filename: str) -> None:
        """
        Save data to JSON file.

        Args:
            data: Data to save
            filename: Output filename
        """
        os.makedirs("data", exist_ok=True)
        filepath = os.path.join("data", filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"💾 Saved {len(data)} records to {filepath}")


def create_mock_data() -> List[Dict[str, Any]]:
    """
    Create mock game data for development when API is not available.

    Returns:
        List of mock game dictionaries
    """
    print("🎭 Creating mock data for development...")

    mock_games = [
        {
            "id": 1,
            "name": "The Witcher 3: Wild Hunt",
            "summary": "An open-world action RPG set in a fantasy universe.",
            "genres": [{"id": 12, "name": "Role-playing (RPG)"}],
            "platforms": [{"id": 6, "name": "PC"}, {"id": 48, "name": "PlayStation 4"}],
            "themes": [{"id": 1, "name": "Action"}, {"id": 17, "name": "Fantasy"}],
            "rating": 95,
            "rating_count": 1000,
        },
        {
            "id": 2,
            "name": "Cyberpunk 2077",
            "summary": "An open-world action-adventure story set in Night City.",
            "genres": [
                {"id": 12, "name": "Role-playing (RPG)"},
                {"id": 5, "name": "Shooter"},
            ],
            "platforms": [{"id": 6, "name": "PC"}, {"id": 48, "name": "PlayStation 4"}],
            "themes": [
                {"id": 1, "name": "Action"},
                {"id": 27, "name": "Science fiction"},
            ],
            "rating": 78,
            "rating_count": 500,
        },
        {
            "id": 3,
            "name": "Minecraft",
            "summary": "A sandbox game where players can build and explore.",
            "genres": [
                {"id": 25, "name": "Simulator"},
                {"id": 31, "name": "Adventure"},
            ],
            "platforms": [{"id": 6, "name": "PC"}, {"id": 48, "name": "PlayStation 4"}],
            "themes": [{"id": 17, "name": "Fantasy"}, {"id": 23, "name": "Family"}],
            "rating": 88,
            "rating_count": 2000,
        },
    ]

    print(f"✅ Created {len(mock_games)} mock games")
    return mock_games


def main():
    """Main function to run data ingestion."""
    parser = argparse.ArgumentParser(description="IGDB Data Ingestion")
    parser.add_argument(
        "--local", action="store_true", help="Development mode with sample data"
    )
    parser.add_argument(
        "--full", action="store_true", help="Production mode with full dataset"
    )
    parser.add_argument("--mock", action="store_true", help="Use mock data for testing")
    parser.add_argument(
        "--smart", action="store_true", help="Smart ingestion with DataManager"
    )
    parser.add_argument(
        "--limit", type=int, help="Limit number of games to fetch (for smart mode)"
    )

    args = parser.parse_args()

    if args.mock:
        # Use mock data for testing
        mock_games = create_mock_data()
        ingestion = IGDBDataIngestion("", "")  # Dummy credentials
        ingestion.save_data(mock_games, "mock_games.json")
        return

    # Load environment variables
    load_dotenv(".env.local")

    client_id = os.getenv("IGDB_CLIENT_ID")
    client_secret = os.getenv("IGDB_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("❌ Missing IGDB credentials in .env.local")
        print("Please create .env.local with:")
        print("IGDB_CLIENT_ID=your_client_id")
        print("IGDB_CLIENT_SECRET=your_client_secret")
        return

    # Initialize ingestion
    ingestion = IGDBDataIngestion(client_id, client_secret)

    # Authenticate
    if not ingestion.authenticate():
        return

    if args.local:
        # Development mode - fetch sample data
        print("🚀 Development mode: Fetching sample data...")

        # Fetch metadata first
        genres = ingestion.fetch_genres()
        platforms = ingestion.fetch_platforms()

        # Fetch games sample
        games = ingestion.fetch_games_sample(10)

        # Save data
        ingestion.save_data(genres, "genres.json")
        ingestion.save_data(platforms, "platforms.json")
        ingestion.save_data(games, "games_sample.json")

        print("✅ Development data ingestion complete!")

    elif args.full:
        # Production mode - fetch full dataset
        print("🚀 Production mode: Fetching full dataset...")

        # Fetch metadata first
        genres = ingestion.fetch_genres()
        platforms = ingestion.fetch_platforms()

        # Fetch all games
        games = ingestion.fetch_games_full()

        # Save data
        ingestion.save_data(genres, "genres.json")
        ingestion.save_data(platforms, "platforms.json")
        ingestion.save_data(games, "games_full.json")

        print("✅ Production data ingestion complete!")

    elif args.smart:
        print("🚀 Smart Ingestion Mode")
        print("Using DataManager with SQLite for intelligent data collection...")

        # Import here to avoid circular imports
        from data_pipeline.shared.data_manager import DataManager
        from data_pipeline.ingestion.smart_ingestion import SmartIngestion

        # Initialize DataManager and SmartIngestion
        with DataManager("data/games.db") as dm:
            si = SmartIngestion(dm, client_id=client_id, client_secret=client_secret)

            # Fetch games using smart ingestion
            target_count = args.limit or 100
            count = si.fetch_if_needed(target_count)

            print(f"✅ Smart ingestion complete! Database now has {count} games")

            # Show summary
            summary = si.get_ingestion_summary()
            print("📊 Ingestion Summary:")
            print(f"   - Current games: {summary['current_games']}")
            print(f"   - Total batches: {summary['total_batches']}")
            print(f"   - Efficiency: {summary['efficiency']}%")

    else:
        print("❌ Please specify --local, --full, --mock, or --smart")
        parser.print_help()


if __name__ == "__main__":
    main()
