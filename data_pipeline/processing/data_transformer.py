#!/usr/bin/env python3
"""
DataTransformer - ETL pipeline for IGDB game data

This module handles the transformation of raw IGDB data into a clean,
ML-ready format. It resolves ID references to human-readable names and
standardizes data formats.

Key Features:
- Resolve genre/platform/theme IDs to names
- Standardize date formats
- Clean and normalize text data
- Create ML-ready feature vectors
- Handle missing data gracefully
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DataTransformer:
    """
    Transform raw IGDB data into clean, ML-ready format.

    Handles ID resolution, data cleaning, and feature engineering
    for the recommendation system.
    """

    def __init__(self):
        """Initialize DataTransformer with reference data."""
        self.genre_lookup: Dict[int, str] = {}
        self.platform_lookup: Dict[int, str] = {}
        self.theme_lookup: Dict[int, str] = {}
        self._load_reference_data()

    def _load_reference_data(self) -> None:
        """
        Load reference data for ID resolution.

        This should be populated from IGDB API calls to genres/platforms/themes.
        """
        # TODO: Load from IGDB API or cached files
        # For now, use some common mappings
        self.genre_lookup = {
            2: "Point-and-click",
            4: "Fighting",
            5: "Shooter",
            7: "Music",
            8: "Platform",
            9: "Puzzle",
            10: "Racing",
            11: "Real Time Strategy (RTS)",
            12: "Role-playing (RPG)",
            13: "Simulator",
            14: "Sport",
            15: "Strategy",
            16: "Turn-based strategy (TBS)",
            24: "Tactical",
            25: "Hack and slash/Beat 'em up",
            26: "Quiz/Trivia",
            30: "Pinball",
            31: "Adventure",
            32: "Indie",
            33: "Arcade",
        }

        self.platform_lookup = {
            1: "Nintendo Entertainment System",
            2: "Super Nintendo Entertainment System",
            3: "Nintendo Game Boy",
            4: "Nintendo Game Boy Color",
            5: "Nintendo Game Boy Advance",
            6: "PC (Microsoft Windows)",
            7: "PlayStation",
            8: "PlayStation 2",
            9: "PlayStation 3",
            11: "Xbox",
            12: "Xbox 360",
            13: "Xbox One",
            14: "Sega Genesis",
            15: "Sega Saturn",
            16: "Sega Dreamcast",
            48: "PlayStation 4",
            49: "Xbox One",
            130: "Nintendo Switch",
            167: "PlayStation 5",
            169: "PlayStation 5",
        }

        self.theme_lookup = {
            1: "Action",
            2: "Fantasy",
            3: "Science fiction",
            4: "Horror",
            5: "Thriller",
            6: "Survival",
            7: "Historical",
            8: "Stealth",
            9: "Comedy",
            10: "Business",
            11: "Drama",
            12: "Non-fiction",
            13: "Sandbox",
            14: "Educational",
            15: "Kids",
            16: "Party",
            17: "Fighting",
            18: "Action-adventure",
            19: "Massively Multiplayer Online (MMO)",
            20: "Racing",
            21: "Sports",
            22: "Simulation",
            23: "Strategy",
            24: "Turn-based strategy",
            25: "Real-time strategy",
            26: "Tactical",
            27: "Shooter",
            28: "Puzzle",
            29: "Music",
            30: "Party",
            31: "Platform",
            32: "Adventure",
            33: "Indie",
            34: "Arcade",
            35: "Visual Novel",
            36: "Card & Board Game",
            37: "MOBA",
            38: "Battle Royale",
        }

    def transform_game(self, raw_game: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a single raw game record into clean format.

        Args:
            raw_game: Raw game data from IGDB API

        Returns:
            Cleaned game data ready for ML

        Example:
            >>> transformer = DataTransformer()
            >>> clean_game = transformer.transform_game(raw_game)
            >>> print(clean_game['genre_names'])
        """
        try:
            # Basic info
            clean_game = {
                "id": raw_game.get("id"),
                "name": (raw_game.get("name") or "").strip(),
                "summary": (raw_game.get("summary") or "").strip(),
                "rating": self._clean_rating(raw_game.get("rating")),
                "rating_count": raw_game.get("rating_count") or 0,
                "release_date": self._clean_release_date(
                    raw_game.get("first_release_date")
                ),
                "release_year": self._extract_year(raw_game.get("first_release_date")),
            }

            # Resolve IDs to names
            clean_game["genre_names"] = self._resolve_genres(raw_game.get("genres", []))
            clean_game["platform_names"] = self._resolve_platforms(
                raw_game.get("platforms", [])
            )
            clean_game["theme_names"] = self._resolve_themes(raw_game.get("themes", []))

            # Keep original IDs for reference
            clean_game["genre_ids"] = raw_game.get("genres", [])
            clean_game["platform_ids"] = raw_game.get("platforms", [])
            clean_game["theme_ids"] = raw_game.get("themes", [])

            # Text processing
            clean_game["summary_length"] = len(clean_game["summary"])
            clean_game["name_length"] = len(clean_game["name"])

            # Quality indicators
            clean_game["has_summary"] = bool(clean_game["summary"])
            clean_game["has_rating"] = clean_game["rating"] is not None
            clean_game["has_genres"] = len(clean_game["genre_names"]) > 0
            clean_game["has_platforms"] = len(clean_game["platform_names"]) > 0

            return clean_game

        except Exception as e:
            logger.error(
                f"Error transforming game {raw_game.get('id', 'unknown')}: {e}"
            )
            # Return empty dict on error
            return {}

    def _clean_rating(self, rating: Optional[float]) -> Optional[float]:
        """Clean and normalize rating values."""
        if rating is None:
            return None

        # Round to 1 decimal place
        return round(float(rating), 1)

    def _clean_release_date(self, timestamp: Optional[int]) -> Optional[str]:
        """Convert Unix timestamp to readable date."""
        if timestamp is None or timestamp <= 0:
            return None

        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d")
        except (ValueError, OSError):
            return None

    def _extract_year(self, timestamp: Optional[int]) -> Optional[int]:
        """Extract year from release date."""
        if timestamp is None or timestamp <= 0:
            return None

        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.year
        except (ValueError, OSError):
            return None

    def _resolve_genres(self, genre_ids: List) -> List[str]:
        """Resolve genre IDs to names."""
        resolved = []
        for gid in genre_ids:
            if isinstance(gid, int):
                resolved.append(self.genre_lookup.get(gid, f"Unknown Genre {gid}"))
            elif isinstance(gid, dict) and "id" in gid:
                resolved.append(
                    self.genre_lookup.get(gid["id"], f"Unknown Genre {gid['id']}")
                )
            else:
                resolved.append(f"Unknown Genre {gid}")
        return resolved

    def _resolve_platforms(self, platform_ids: List) -> List[str]:
        """Resolve platform IDs to names."""
        resolved = []
        for pid in platform_ids:
            if isinstance(pid, int):
                resolved.append(
                    self.platform_lookup.get(pid, f"Unknown Platform {pid}")
                )
            elif isinstance(pid, dict) and "id" in pid:
                resolved.append(
                    self.platform_lookup.get(pid["id"], f"Unknown Platform {pid['id']}")
                )
            else:
                resolved.append(f"Unknown Platform {pid}")
        return resolved

    def _resolve_themes(self, theme_ids: List) -> List[str]:
        """Resolve theme IDs to names."""
        resolved = []
        for tid in theme_ids:
            if isinstance(tid, int):
                resolved.append(self.theme_lookup.get(tid, f"Unknown Theme {tid}"))
            elif isinstance(tid, dict) and "id" in tid:
                resolved.append(
                    self.theme_lookup.get(tid["id"], f"Unknown Theme {tid['id']}")
                )
            else:
                resolved.append(f"Unknown Theme {tid}")
        return resolved

    def transform_batch(self, raw_games: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform a batch of raw games.

        Args:
            raw_games: List of raw game data from IGDB API

        Returns:
            List of cleaned game data

        Example:
            >>> transformer = DataTransformer()
            >>> clean_games = transformer.transform_batch(raw_games)
            >>> print(f"Transformed {len(clean_games)} games")
        """
        clean_games = []

        for raw_game in raw_games:
            clean_game = self.transform_game(raw_game)
            if (
                clean_game and clean_game.get("id") is not None
            ):  # Only add if transformation succeeded and has ID
                clean_games.append(clean_game)

        logger.info(
            f"Transformed {len(clean_games)}/{len(raw_games)} games successfully"
        )
        return clean_games

    def get_data_quality_report(
        self, clean_games: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate data quality report for transformed games.

        Args:
            clean_games: List of cleaned game data

        Returns:
            Dictionary with quality metrics

        Example:
            >>> report = transformer.get_data_quality_report(clean_games)
            >>> print(f"Quality score: {report['quality_score']}")
        """
        if not clean_games:
            return {"quality_score": 0, "total_games": 0}

        total_games = len(clean_games)

        # Calculate quality metrics
        has_summary = sum(1 for g in clean_games if g["has_summary"])
        has_rating = sum(1 for g in clean_games if g["has_rating"])
        has_genres = sum(1 for g in clean_games if g["has_genres"])
        has_platforms = sum(1 for g in clean_games if g["has_platforms"])

        # Quality score (0-100)
        quality_score = (
            (has_summary / total_games) * 25
            + (has_rating / total_games) * 25
            + (has_genres / total_games) * 25
            + (has_platforms / total_games) * 25
        )

        return {
            "total_games": total_games,
            "quality_score": round(quality_score, 1),
            "has_summary": f"{has_summary}/{total_games} ({has_summary/total_games*100:.1f}%)",
            "has_rating": f"{has_rating}/{total_games} ({has_rating/total_games*100:.1f}%)",
            "has_genres": f"{has_genres}/{total_games} ({has_genres/total_games*100:.1f}%)",
            "has_platforms": f"{has_platforms}/{total_games} ({has_platforms/total_games*100:.1f}%)",
            "avg_rating": round(
                sum(g["rating"] for g in clean_games if g["rating"]) / has_rating, 1
            )
            if has_rating
            else 0,
            "avg_genres_per_game": round(
                sum(len(g["genre_names"]) for g in clean_games) / total_games, 1
            ),
            "avg_platforms_per_game": round(
                sum(len(g["platform_names"]) for g in clean_games) / total_games, 1
            ),
        }


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Example usage
    transformer = DataTransformer()

    # Sample raw data
    raw_game = {
        "id": 239060,
        "name": "Grand Theft Auto V: Story Mode",
        "summary": "Grand Theft Auto V: Story Mode is an add-on...",
        "genres": [5, 33],
        "platforms": [169, 167],
        "themes": [1, 38],
        "rating": 99.94058315831364,
        "rating_count": 9,
        "first_release_date": 1647302400,
    }

    # Transform
    clean_game = transformer.transform_game(raw_game)
    print("Transformed game:")
    print(json.dumps(clean_game, indent=2, default=str))

    # Quality report
    report = transformer.get_data_quality_report([clean_game])
    print(f"\nQuality report: {report}")
