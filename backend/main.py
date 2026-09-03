"""
CineMatch FastAPI Application
High-performance semantic movie recommendation API powered by Sentence Transformers,
NumPy Vectorized Cosine Similarity, and Google Gemini Intent Enhancement.

NO EXTERNAL DATABASE DEPENDENCY:
All movie data and embeddings are loaded locally from CSV and NumPy arrays.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from recommender import MovieRecommender
from gemini_service import GeminiService

load_dotenv()

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("cinematch.api")

# Global Service Holders
recommender: Optional[MovieRecommender] = None
gemini_service: Optional[GeminiService] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup & Shutdown lifecycle manager.
    Loads movies.csv, precomputed embeddings, and SentenceTransformer model into memory ONCE.
    """
    global recommender, gemini_service
    logger.info("Initializing CineMatch backend services...")
    
    try:
        recommender = MovieRecommender()
        gemini_service = GeminiService()
        logger.info("[STARTUP COMPLETE] All ML models and local datasets loaded successfully.")
    except Exception as e:
        logger.error(f"[STARTUP ERROR] Failed to initialize backend: {e}")
        raise e
        
    yield
    
    logger.info("Shutting down CineMatch backend services.")

# FastAPI App Instance
app = FastAPI(
    title="CineMatch AI Recommendation Engine",
    description="Intelligent natural language movie recommendation platform using Sentence Transformers & Gemini intent extraction.",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Configuration - Allow local Next.js frontend & GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Request & Response Models
# ============================================================================

class RecommendRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000, description="Natural language description of desired movie.")
    limit: Optional[int] = Field(default=10, ge=1, le=50, description="Maximum number of recommendations to return.")

class MovieItem(BaseModel):
    rank: int
    id: int
    title: str
    year: int
    genres: List[str]
    overview: str
    rating: float
    vote_count: Optional[int] = 0
    director: Optional[str] = "Unknown"
    cast: Optional[str] = ""
    poster_path: Optional[str] = ""
    similarity_score: float
    final_score: Optional[float] = None
    match_reason: str

class RecommendResponse(BaseModel):
    success: bool
    original_prompt: str
    enhanced_query: str
    intent: Optional[Dict[str, Any]] = None
    recommendations: List[MovieItem]
    total_results: int

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", tags=["Health"])
async def get_status():
    """Returns API health status, loaded dataset count, and ML model details."""
    global recommender, gemini_service
    return {
        "status": "online",
        "service": "CineMatch AI Recommendation Engine",
        "version": "2.0.0",
        "dataset": "Local CSV (data/movies.csv)",
        "movies_count": len(recommender.df) if recommender and recommender.df is not None else 0,
        "embedding_model": "all-MiniLM-L6-v2",
        "gemini_active": bool(gemini_service and gemini_service.client_initialized)
    }

@app.post("/recommend", response_model=RecommendResponse, tags=["Recommendations"])
async def recommend_movies(payload: RecommendRequest):
    """
    Main Semantic Recommendation Endpoint:
    1. Extracts intent & enhanced query via Gemini (with graceful offline fallback).
    2. Encodes enhanced query via Sentence Transformer.
    3. Runs vectorized cosine similarity against local NumPy embeddings.
    4. Blends ratings & popularity weights.
    5. Returns ranked movie recommendations with grounded match reasons.
    """
    global recommender, gemini_service
    
    if recommender is None or not recommender.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML Recommendation Engine is still initializing. Please retry in a few moments."
        )

    clean_prompt = payload.prompt.strip()
    if not clean_prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt cannot be empty."
        )

    try:
        logger.info(f"Processing recommendation request for prompt: '{clean_prompt}'")
        
        # 1. Intent Extraction & Query Enhancement via Gemini
        intent = gemini_service.enhance_query(clean_prompt) if gemini_service else None
        enhanced_query = intent.get("enhanced_query", clean_prompt) if intent else clean_prompt
        
        # 2. Local Semantic ML Recommendation
        recommendations = recommender.recommend(
            prompt=clean_prompt,
            limit=payload.limit,
            intent=intent
        )
        
        return RecommendResponse(
            success=True,
            original_prompt=clean_prompt,
            enhanced_query=enhanced_query,
            intent=intent,
            recommendations=recommendations,
            total_results=len(recommendations)
        )
        
    except Exception as e:
        logger.error(f"Error during recommendation pipeline: {e}", exc_info=True)
        # Safe non-crashing response fallback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating movie recommendations. Please try again."
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
