import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

# Resolve python paths to import src package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.recommendation.hybrid import HybridRecommender
from src.nlp.llm_service import LLMService

# Setup logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Request & Response schemas
class ContentRecommendRequest(BaseModel):
    item_id: int
    media_type: str = "movie"  # "movie" or "book"
    top_k: int = 10

class CollabRecommendRequest(BaseModel):
    user_id: int
    media_type: str = "movie"
    method: str = "svd"  # "svd" or "item_item"
    top_k: int = 10

class HybridRecommendRequest(BaseModel):
    user_id: Optional[int] = None
    item_id: Optional[int] = None
    preferences: Optional[dict] = None
    media_type: str = "movie"
    method: str = "svd"
    top_k: int = 10
    weights: Optional[dict] = None

class ExtractRequest(BaseModel):
    text: str

class ChatTurn(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[int] = None
    media_type: str = "movie"
    history: List[dict] = []

# Engine cache dictionary
engines = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler to load datasets and pre-fit recommendation models on startup."""
    logger.info("Starting up FastAPI Backend, loading datasets...")
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "processed"))
    
    # Path checks
    movies_path = os.path.join(data_dir, "movies_processed.csv")
    movie_ratings_path = os.path.join(data_dir, "movie_ratings_train.csv")
    books_path = os.path.join(data_dir, "books_processed.csv")
    book_ratings_path = os.path.join(data_dir, "book_ratings_train.csv")
    
    # Load Movies
    if os.path.exists(movies_path) and os.path.exists(movie_ratings_path):
        logger.info("Loading Movie recommendation engine...")
        movies_df = pd.read_csv(movies_path)
        movie_ratings_df = pd.read_csv(movie_ratings_path)
        
        movie_engine = HybridRecommender(
            id_col='movieId', user_col='userId', title_col='title', 
            genre_col='genres', rating_col='rating', num_factors=30
        )
        movie_engine.fit(movies_df, movie_ratings_df)
        engines['movie'] = {
            'engine': movie_engine,
            'metadata': movies_df,
            'id_col': 'movieId'
        }
    else:
        logger.warning(f"Movie datasets not found at {data_dir}. Run preprocessing first.")
        
    # Load Books
    if os.path.exists(books_path) and os.path.exists(book_ratings_path):
        logger.info("Loading Book recommendation engine...")
        books_df = pd.read_csv(books_path)
        book_ratings_df = pd.read_csv(book_ratings_path)
        
        book_engine = HybridRecommender(
            id_col='book_id', user_col='user_id', title_col='title', 
            genre_col='genres', rating_col='rating', num_factors=20
        )
        book_engine.fit(books_df, book_ratings_df)
        engines['book'] = {
            'engine': book_engine,
            'metadata': books_df,
            'id_col': 'book_id'
        }
    else:
        logger.warning(f"Book datasets not found at {data_dir}. Run preprocessing first.")

    # Initialize LLM Service
    engines['llm'] = LLMService()
    
    logger.info("FastAPI initialization complete.")
    yield
    logger.info("Shutting down backend...")
    engines.clear()

# Initialize FastAPI App
app = FastAPI(
    title="CineMatch API", 
    description="Hybrid AI Movie & Book Recommendation Engine Backend",
    lifespan=lifespan
)

# Enable CORS for Next.js app on port 3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins like ["http://localhost:3000"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dynamic import helper for pandas (loaded on demand to speed up script loading)
import pandas as pd

def get_engine(media_type: str):
    if media_type not in engines:
        raise HTTPException(status_code=503, detail=f"Recommendation engine for '{media_type}' is not loaded.")
    return engines[media_type]

def get_llm():
    if 'llm' not in engines:
        raise HTTPException(status_code=503, detail="LLM service is not loaded.")
    return engines['llm']

@app.get("/health")
def health_check():
    """Simple API status health check."""
    return {
        "status": "healthy",
        "engines_loaded": list(engines.keys())
    }

@app.post("/recommend/content")
def recommend_content(req: ContentRecommendRequest):
    """Computes TF-IDF content similarity recommendations for a specific item."""
    data = get_engine(req.media_type)
    engine = data['engine'].content_rec
    try:
        recs = engine.recommend_by_item(item_id=req.item_id, top_k=req.top_k)
        return {"recommendations": recs}
    except Exception as e:
        logger.error(f"Error in content recommend: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend/collaborative")
def recommend_collaborative(req: CollabRecommendRequest):
    """Computes Collaborative SVD or Item-Item recommendations for a specific user."""
    data = get_engine(req.media_type)
    engine = data['engine'].collab_rec
    metadata = data['metadata']
    try:
        recs = engine.recommend_collaborative(
            user_id=req.user_id, method=req.method, top_k=req.top_k, 
            items_metadata_df=metadata
        )
        return {"recommendations": recs}
    except Exception as e:
        logger.error(f"Error in collab recommend: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend/hybrid")
def recommend_hybrid(req: HybridRecommendRequest):
    """Blends content similarity, collaborative ratings predictions, and explicit preferences."""
    data = get_engine(req.media_type)
    engine = data['engine']
    try:
        recs = engine.recommend_hybrid(
            user_id=req.user_id, item_id=req.item_id, preferences=req.preferences,
            method=req.method, top_k=req.top_k, weights=req.weights
        )
        return {"recommendations": recs}
    except Exception as e:
        logger.error(f"Error in hybrid recommend: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/preferences/extract")
def extract_preferences(req: ExtractRequest, llm=Depends(get_llm)):
    """Extracts structured preferences from natural language prompts using LLM parser."""
    try:
        prefs = llm.get_provider().extract_preferences(req.text)
        return {"preferences": prefs}
    except Exception as e:
        logger.error(f"Error in preference extraction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
def chat_recommend(req: ChatRequest, llm=Depends(get_llm)):
    """Conversational endpoint that extracts preferences, fetches items from ML engine, and explains them."""
    try:
        provider = llm.get_provider()
        media_type = req.media_type
        
        # 1. Extract preferences from user message
        prefs = provider.extract_preferences(req.message)
        
        # 2. Get recommendations from ML Hybrid Engine
        data = get_engine(media_type)
        engine = data['engine']
        
        recs = engine.recommend_hybrid(
            user_id=req.user_id, preferences=prefs, top_k=5
        )
        
        # 3. Generate chat reply integrating the recommendations
        reply = provider.generate_chat_reply(
            message=req.message, history=req.history, recommendations=recs
        )
        
        # 4. Generate grounded explanations for the top 3 recommendations
        for r in recs[:3]:
            r['explanation'] = provider.generate_explanation(
                title=r['title'], genres=r['genres'], evidence=r['evidence']
            )
            
        return {
            "reply": reply,
            "preferences": prefs,
            "recommendations": recs
        }
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/items/{media_type}/{item_id}")
def get_item_details(media_type: str, item_id: int):
    """Fetches details of a specific item from metadata."""
    data = get_engine(media_type)
    metadata = data['metadata']
    id_col = data['id_col']
    
    item_rows = metadata[metadata[id_col] == item_id]
    if item_rows.empty:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found.")
        
    row = item_rows.iloc[0]
    
    # Return common representation
    details = {
        "id": int(item_id),
        "title": str(row.get("title", "")),
        "genres": str(row.get("genres", "")),
        "rating": float(row.get("average_rating", 3.5)) if "average_rating" in row else float(row.get("rating", 3.5)),
    }
    
    if "authors" in row:
        details["author_director"] = str(row["authors"])
    elif "director" in row:
        details["author_director"] = str(row["director"])
    else:
        details["author_director"] = "Unknown"
        
    return details

@app.get("/users/{user_id}/recommendations")
def get_user_default_recommendations(user_id: int, media_type: str = "movie"):
    """Helper endpoint to fetch default recommendations for an existing user."""
    data = get_engine(media_type)
    engine = data['engine']
    try:
        recs = engine.recommend_hybrid(user_id=user_id, top_k=10)
        return {"recommendations": recs}
    except Exception as e:
        logger.error(f"Error fetching user recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info("Running uvicorn server directly...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
