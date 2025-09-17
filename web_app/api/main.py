#!/usr/bin/env python3
"""
FastAPI Web Application for Game Recommendation System

This module provides REST API endpoints for game recommendations,
game search, and model management.

Usage:
    uvicorn web_app.api.main:app --reload
"""

import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Query, Path as PathParam
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Add project root to path for imports - MUST be before importing our modules
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import our recommendation model
from data_pipeline.training.recommendation_model import (  # noqa: E402
    ContentBasedRecommendationModel,
)

# Import model registry for cloud storage integration
from web_app.model_registry import ModelRegistry  # noqa: E402

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="IGDB Game Recommendation API",
    description="API for game recommendations using content-based filtering",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instance
recommendation_model = None
games_data = []
model_registry = None


# Pydantic models for API requests/responses
class GameRecommendation(BaseModel):
    """Model for game recommendation response."""

    game_id: int = Field(..., description="Unique game identifier")
    name: str = Field(..., description="Game name")
    similarity_score: float = Field(..., description="Similarity score (0-1)")
    rating: Optional[float] = Field(None, description="Game rating")
    genres: List[str] = Field(..., description="Game genres")
    platforms: List[str] = Field(..., description="Available platforms")
    summary: str = Field(..., description="Game summary")


class TextRecommendationRequest(BaseModel):
    """Model for text-based recommendation request."""

    query: str = Field(..., description="Text query for recommendations", min_length=1)
    top_k: int = Field(default=10, description="Number of recommendations", ge=1, le=50)


class GameSearchRequest(BaseModel):
    """Model for game search request."""

    query: str = Field(..., description="Search query", min_length=1)
    limit: int = Field(default=20, description="Maximum results", ge=1, le=100)


class GameInfo(BaseModel):
    """Model for game information."""

    id: int = Field(..., description="Unique game identifier")
    name: str = Field(..., description="Game name")
    summary: str = Field(..., description="Game summary")
    rating: Optional[float] = Field(None, description="Game rating")
    rating_count: int = Field(..., description="Number of ratings")
    release_date: str = Field(..., description="Release date")
    release_year: int = Field(..., description="Release year")
    genre_names: List[str] = Field(..., description="Game genres")
    platform_names: List[str] = Field(..., description="Available platforms")
    theme_names: List[str] = Field(..., description="Game themes")


class ModelStatus(BaseModel):
    """Model for model status response."""

    is_loaded: bool = Field(..., description="Whether model is loaded")
    games_count: int = Field(..., description="Number of games in model")
    feature_count: int = Field(..., description="Number of features")
    model_type: str = Field(..., description="Type of recommendation model")


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    global recommendation_model, games_data, model_registry

    logger.info("=== API STARTUP DEBUG ===")
    logger.info(f"PORT environment variable: {os.environ.get('PORT', 'NOT SET')}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(
        f"Files in /app: {os.listdir('/app') if os.path.exists('/app') else 'NOT FOUND'}"
    )
    logger.info(
        f"Files in /app/data: {os.listdir('/app/data') if os.path.exists('/app/data') else 'NOT FOUND'}"
    )
    logger.info(
        f"Files in /app/models: {os.listdir('/app/models') if os.path.exists('/app/models') else 'NOT FOUND'}"
    )
    logger.info("Starting up Game Recommendation API with Cloud Storage integration")

    try:
        # Initialize model registry
        model_registry = ModelRegistry()
        health_status = model_registry.health_check()
        logger.info(f"Model registry health: {health_status}")

        # Load games data from Cloud Storage or local fallback
        logger.info("Loading games data...")
        games_data = model_registry.get_games_data()
        if games_data:
            logger.info(f"Loaded {len(games_data)} games successfully")
        else:
            logger.warning("Failed to load games data")

        # Load recommendation model from Cloud Storage or local fallback
        logger.info("Loading recommendation model...")
        model_path = model_registry.get_model_path("recommendation_model.pkl")
        feature_extractor_path = model_registry.get_model_path(
            "recommendation_model_feature_extractor.pkl"
        )

        if model_path and feature_extractor_path:
            # Copy feature extractor to expected location for load_model
            expected_feature_extractor_path = model_path.replace(
                ".pkl", "_feature_extractor.pkl"
            )
            try:
                import shutil

                shutil.copy2(feature_extractor_path, expected_feature_extractor_path)
                logger.info(
                    f"Copied feature extractor to {expected_feature_extractor_path}"
                )
            except Exception as e:
                logger.error(f"Failed to copy feature extractor: {e}")
                return

            recommendation_model = ContentBasedRecommendationModel()
            recommendation_model.load_model(model_path)
            logger.info("Loaded recommendation model successfully")

            # Clean up temporary files if they were downloaded
            temp_files = [
                model_path,
                feature_extractor_path,
                expected_feature_extractor_path,
            ]
            for temp_path in temp_files:
                if temp_path and temp_path.startswith("/tmp"):
                    try:
                        os.unlink(temp_path)
                        logger.info(f"Cleaned up temporary model file: {temp_path}")
                    except Exception as e:
                        logger.warning(f"Failed to clean up temp file {temp_path}: {e}")
        else:
            logger.warning(
                f"Failed to load recommendation model. Model: {model_path}, Feature Extractor: {feature_extractor_path}"
            )

    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "IGDB Game Recommendation API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint."""
    health_info = {
        "status": "healthy",
        "model_loaded": str(recommendation_model is not None),
        "games_count": str(len(games_data)),
        "port": str(os.environ.get("PORT", "8080")),
    }

    # Add model registry health if available
    if model_registry:
        registry_health = model_registry.health_check()
        health_info["gcs_available"] = str(registry_health.get("gcs_available", False))
        health_info["data_accessible"] = str(
            registry_health.get("data_accessible", False)
        )
        health_info["models_accessible"] = str(
            registry_health.get("models_accessible", False)
        )

    return health_info


@app.get("/model/status", response_model=ModelStatus)
async def get_model_status():
    """Get the current status of the recommendation model."""
    if not recommendation_model:
        raise HTTPException(status_code=503, detail="Recommendation model not loaded")

    return ModelStatus(
        is_loaded=True,
        games_count=len(recommendation_model.games_data),
        feature_count=recommendation_model.game_features.shape[1]
        if recommendation_model.game_features is not None
        else 0,
        model_type="content_based_recommendation",
    )


@app.get("/games/{game_id}/recommendations", response_model=List[GameRecommendation])
async def get_game_recommendations(
    game_id: int = PathParam(..., description="Game ID to get recommendations for"),
    top_k: int = Query(
        default=10, description="Number of recommendations", ge=1, le=50
    ),
):
    """Get recommendations for a specific game."""
    if not recommendation_model:
        raise HTTPException(status_code=503, detail="Recommendation model not loaded")

    try:
        recommendations = recommendation_model.get_recommendations(game_id, top_k=top_k)

        return [
            GameRecommendation(
                game_id=rec["game_id"],
                name=rec["name"],
                similarity_score=rec["similarity_score"],
                rating=rec["rating"],
                genres=rec["genres"],
                platforms=rec["platforms"],
                summary=rec["summary"],
            )
            for rec in recommendations
        ]

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting recommendations for game {game_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/recommendations/text", response_model=List[GameRecommendation])
async def get_text_recommendations(request: TextRecommendationRequest):
    """Get recommendations based on text query."""
    if not recommendation_model:
        raise HTTPException(status_code=503, detail="Recommendation model not loaded")

    try:
        logger.info(f"Getting text recommendations for query: '{request.query}'")
        recommendations = recommendation_model.get_similar_games_by_text(
            request.query, top_k=request.top_k
        )

        logger.info(f"Found {len(recommendations)} text-based recommendations")

        return [
            GameRecommendation(
                game_id=rec["game_id"],
                name=rec["name"],
                similarity_score=rec["similarity_score"],
                rating=rec["rating"],
                genres=rec["genres"],
                platforms=rec["platforms"],
                summary=rec["summary"],
            )
            for rec in recommendations
        ]

    except Exception as e:
        logger.error(f"Error getting text recommendations: {str(e)}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/games/search", response_model=List[GameInfo])
async def search_games(
    query: str = Query(..., description="Search query", min_length=1),
    limit: int = Query(default=20, description="Maximum results", ge=1, le=100),
):
    """Search for games by name or summary."""
    if not games_data:
        raise HTTPException(status_code=503, detail="Games data not loaded")

    query_lower = query.lower()
    matching_games = []

    for game in games_data:
        # Search in name and summary
        name_match = query_lower in game.get("name", "").lower()
        summary_match = query_lower in game.get("summary", "").lower()

        if name_match or summary_match:
            matching_games.append(game)

            if len(matching_games) >= limit:
                break

    return [
        GameInfo(
            id=game["id"],
            name=game["name"],
            summary=game.get("summary", ""),
            rating=game.get("rating", 0),
            rating_count=game.get("rating_count", 0),
            release_date=game.get("release_date", ""),
            release_year=game.get("release_year", 0),
            genre_names=game.get("genre_names", []),
            platform_names=game.get("platform_names", []),
            theme_names=game.get("theme_names", []),
        )
        for game in matching_games
    ]


@app.get("/games/{game_id}", response_model=GameInfo)
async def get_game_info(game_id: int = PathParam(..., description="Game ID")):
    """Get detailed information about a specific game."""
    if not games_data:
        raise HTTPException(status_code=503, detail="Games data not loaded")

    game = next((g for g in games_data if g["id"] == game_id), None)
    if not game:
        raise HTTPException(status_code=404, detail=f"Game with ID {game_id} not found")

    return GameInfo(
        id=game["id"],
        name=game["name"],
        summary=game.get("summary", ""),
        rating=game.get("rating", 0),
        rating_count=game.get("rating_count", 0),
        release_date=game.get("release_date", ""),
        release_year=game.get("release_year", 0),
        genre_names=game.get("genre_names", []),
        platform_names=game.get("platform_names", []),
        theme_names=game.get("theme_names", []),
    )


@app.get("/games", response_model=List[GameInfo])
async def list_games(
    limit: int = Query(default=50, description="Maximum results", ge=1, le=200),
    offset: int = Query(default=0, description="Number of results to skip", ge=0),
):
    """List games with pagination."""
    if not games_data:
        raise HTTPException(status_code=503, detail="Games data not loaded")

    start_idx = offset
    end_idx = min(offset + limit, len(games_data))

    games_slice = games_data[start_idx:end_idx]

    return [
        GameInfo(
            id=game["id"],
            name=game["name"],
            summary=game.get("summary", ""),
            rating=game.get("rating", 0),
            rating_count=game.get("rating_count", 0),
            release_date=game.get("release_date", ""),
            release_year=game.get("release_year", 0),
            genre_names=game.get("genre_names", []),
            platform_names=game.get("platform_names", []),
            theme_names=game.get("theme_names", []),
        )
        for game in games_slice
    ]


@app.get("/genres", response_model=List[str])
async def list_genres():
    """Get list of all available genres."""
    if not games_data:
        raise HTTPException(status_code=503, detail="Games data not loaded")

    genres = set()
    for game in games_data:
        genres.update(game.get("genre_names", []))

    return sorted(list(genres))


@app.get("/platforms", response_model=List[str])
async def list_platforms():
    """Get list of all available platforms."""
    if not games_data:
        raise HTTPException(status_code=503, detail="Games data not loaded")

    platforms = set()
    for game in games_data:
        platforms.update(game.get("platform_names", []))

    return sorted(list(platforms))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Default to 8080 for Cloud Run
    uvicorn.run(
        "web_app.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info",
    )
