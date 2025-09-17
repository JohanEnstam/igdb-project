#!/usr/bin/env python3
"""
FastAPI Web Application for Game Recommendation System

This module provides REST API endpoints for game recommendations,
game search, and model management.

Usage:
    uvicorn web_app.api.main:app --reload
"""

import logging
import json
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
from data_pipeline.training.recommendation_model import (
    ContentBasedRecommendationModel,
)  # noqa: E402

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
    global recommendation_model, games_data

    logger.info("Starting up Game Recommendation API")

    try:
        # Load games data
        games_file = Path("data/games_clean.json")
        if games_file.exists():
            with open(games_file, "r") as f:
                games_data = json.load(f)
            logger.info(f"Loaded {len(games_data)} games from data file")
        else:
            logger.warning("Games data file not found")

        # Load recommendation model
        model_file = Path("models/recommendation_model.pkl")
        if model_file.exists():
            recommendation_model = ContentBasedRecommendationModel()
            recommendation_model.load_model(str(model_file))
            logger.info("Loaded recommendation model successfully")
        else:
            logger.warning("Recommendation model not found")

    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")


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
    return {"status": "healthy", "model_loaded": str(recommendation_model is not None)}


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
    uvicorn.run(
        "web_app.api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
