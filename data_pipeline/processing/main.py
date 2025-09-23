#!/usr/bin/env python3
"""
Data Processing Pipeline - ETL for IGDB game data

This script transforms raw IGDB data into clean, ML-ready format.
It handles the Extract-Transform-Load pipeline for the recommendation system.

Usage:
    python -m data_pipeline.processing.main --transform-all
    python -m data_pipeline.processing.main --quality-report
"""

import argparse
import logging
import os
from typing import List, Dict, Any
from pathlib import Path
from google.cloud import storage

from data_pipeline.shared.data_manager import DataManager
from data_pipeline.processing.data_transformer import DataTransformer

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def transform_all_games(db_path: str = "data/games.db") -> None:
    """
    Transform all games in database to clean format.

    Args:
        db_path: Path to SQLite database
    """
    logger.info("🚀 Starting ETL transformation of all games...")

    with DataManager(db_path) as dm:
        # Get all raw games
        raw_games = dm.get_games()
        logger.info(f"📥 Found {len(raw_games)} raw games to transform")

        if not raw_games:
            logger.warning("No games found in database")
            return

        # Transform games
        transformer = DataTransformer()
        clean_games = transformer.transform_batch(raw_games)

        # Generate quality report
        report = transformer.get_data_quality_report(clean_games)

        logger.info("📊 Data Quality Report:")
        logger.info(f"   - Total games: {report['total_games']}")
        logger.info(f"   - Quality score: {report['quality_score']}/100")
        logger.info(f"   - Games with summaries: {report['has_summary']}")
        logger.info(f"   - Games with ratings: {report['has_rating']}")
        logger.info(f"   - Games with genres: {report['has_genres']}")
        logger.info(f"   - Games with platforms: {report['has_platforms']}")
        logger.info(f"   - Average rating: {report['avg_rating']}")
        logger.info(f"   - Average genres per game: {report['avg_genres_per_game']}")
        logger.info(
            f"   - Average platforms per game: {report['avg_platforms_per_game']}"
        )

        # Save transformed data
        save_transformed_data(clean_games)

        logger.info("✅ ETL transformation complete!")


def save_transformed_data(clean_games: List[Dict[str, Any]]) -> None:
    """
    Save transformed data to files locally and optionally to GCS.

    Args:
        clean_games: List of cleaned game data
    """
    import json
    import pandas as pd

    # Ensure data directory exists
    Path("data").mkdir(exist_ok=True)

    # Save as JSON
    json_path = "data/games_clean.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(clean_games, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"💾 Saved {len(clean_games)} clean games to {json_path}")

    # Save as CSV for easy analysis
    csv_path = "data/games_clean.csv"
    df = pd.DataFrame(clean_games)
    df.to_csv(csv_path, index=False)

    logger.info(f"💾 Saved {len(clean_games)} clean games to {csv_path}")
    
    # Upload to GCS if configured
    bucket_name = os.getenv("DATA_BUCKET")
    gcs_prefix = os.getenv("GCS_PREFIX", "processed/")
    
    if bucket_name:
        try:
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            
            # Upload JSON
            json_blob_name = f"{gcs_prefix}games_clean.json"
            json_blob = bucket.blob(json_blob_name)
            json_blob.upload_from_filename(json_path)
            logger.info(f"☁️ Uploaded JSON to gs://{bucket_name}/{json_blob_name}")
            
            # Upload CSV
            csv_blob_name = f"{gcs_prefix}games_clean.csv"
            csv_blob = bucket.blob(csv_blob_name)
            csv_blob.upload_from_filename(csv_path)
            logger.info(f"☁️ Uploaded CSV to gs://{bucket_name}/{csv_blob_name}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to upload to GCS: {e}")
            print(f"⚠️ Continuing without GCS upload...")


def generate_quality_report(db_path: str = "data/games.db") -> None:
    """
    Generate quality report for current data.

    Args:
        db_path: Path to SQLite database
    """
    logger.info("📊 Generating data quality report...")

    with DataManager(db_path) as dm:
        raw_games = dm.get_games()

        if not raw_games:
            logger.warning("No games found in database")
            return

        transformer = DataTransformer()
        clean_games = transformer.transform_batch(raw_games)
        report = transformer.get_data_quality_report(clean_games)

        print("\n" + "=" * 50)
        print("📊 DATA QUALITY REPORT")
        print("=" * 50)
        print(f"Total games: {report['total_games']}")
        print(f"Quality score: {report['quality_score']}/100")
        print()
        print("Data completeness:")
        print(f"  📝 Summaries: {report['has_summary']}")
        print(f"  ⭐ Ratings: {report['has_rating']}")
        print(f"  🎭 Genres: {report['has_genres']}")
        print(f"  🖥️ Platforms: {report['has_platforms']}")
        print()
        print("Statistics:")
        print(f"  Average rating: {report['avg_rating']}")
        print(f"  Average genres per game: {report['avg_genres_per_game']}")
        print(f"  Average platforms per game: {report['avg_platforms_per_game']}")
        print("=" * 50)


def main():
    """Main function to run data processing pipeline."""
    parser = argparse.ArgumentParser(description="IGDB Data Processing Pipeline")
    parser.add_argument(
        "--transform-all",
        action="store_true",
        help="Transform all games to clean format",
    )
    parser.add_argument(
        "--quality-report", action="store_true", help="Generate data quality report"
    )
    parser.add_argument(
        "--db-path", type=str, default="data/games.db", help="Path to SQLite database"
    )

    args = parser.parse_args()

    if args.transform_all:
        transform_all_games(args.db_path)
    elif args.quality_report:
        generate_quality_report(args.db_path)
    else:
        print("❌ Please specify --transform-all or --quality-report")
        parser.print_help()


if __name__ == "__main__":
    main()
