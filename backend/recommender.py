"""
CineMatch Local ML Recommendation Engine
Uses Sentence Transformers ('all-MiniLM-L6-v2') and Vectorized Cosine Similarity
over local pre-computed NumPy embeddings and CSV metadata.

NO DATABASE REQUIRED:
- Metadata: data/movies.csv
- Embeddings: models/movie_embeddings.npy
- Model: all-MiniLM-L6-v2
"""

import os
import logging
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

logger = logging.getLogger("cinematch.recommender")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "movies.csv")
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "models", "movie_embeddings.npy")
MODEL_NAME = "all-MiniLM-L6-v2"

class MovieRecommender:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.embeddings: Optional[np.ndarray] = None
        self.model: Optional[SentenceTransformer] = None
        self.is_loaded = False
        
        self.load_resources()

    def load_resources(self):
        """Loads dataset, embeddings, and Sentence Transformer model once on startup."""
        try:
            logger.info("Loading CineMatch local resources...")
            
            # 1. Load movies.csv
            if not os.path.exists(DATA_PATH):
                raise FileNotFoundError(f"Movie dataset not found at {DATA_PATH}. Run scripts/prepare_data.py first.")
            self.df = pd.read_csv(DATA_PATH)
            logger.info(f"Loaded {len(self.df)} movies from local CSV.")

            # 2. Load Sentence Transformer model
            logger.info(f"Loading SentenceTransformer model: '{MODEL_NAME}'...")
            self.model = SentenceTransformer(MODEL_NAME)
            
            # 3. Load or generate embeddings
            if os.path.exists(EMBEDDINGS_PATH):
                self.embeddings = np.load(EMBEDDINGS_PATH).astype(np.float32)
                logger.info(f"Loaded pre-computed embeddings from {EMBEDDINGS_PATH} with shape: {self.embeddings.shape}")
            else:
                logger.warning(f"Embeddings file not found at {EMBEDDINGS_PATH}. Generating dynamically once...")
                texts = self.df["combined_text"].fillna("").tolist()
                self.embeddings = self.model.encode(
                    texts,
                    batch_size=32,
                    show_progress_bar=False,
                    normalize_embeddings=True,
                    convert_to_numpy=True
                ).astype(np.float32)
                os.makedirs(os.path.dirname(EMBEDDINGS_PATH), exist_ok=True)
                np.save(EMBEDDINGS_PATH, self.embeddings)
                logger.info("Saved newly generated embeddings locally.")

            # Ensure embeddings are normalized for exact dot-product cosine similarity
            norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            self.embeddings = self.embeddings / norms

            self.is_loaded = True
            logger.info("CineMatch ML Recommendation Engine ready.")
        except Exception as e:
            logger.error(f"Failed to load MovieRecommender resources: {e}")
            raise e

    def generate_match_reason(self, movie: pd.Series, prompt: str, intent: Optional[Dict[str, Any]] = None) -> str:
        """
        Generates a factual, grounded explanation for why this movie matched the user request.
        Grounds explanations strictly in the movie's metadata (genres, director, themes) and intent.
        Never hallucinates facts.
        """
        title = movie.get("title", "")
        genres = str(movie.get("genres", "")).split(", ")
        director = movie.get("director", "")
        keywords = str(movie.get("keywords", "")).split(", ")

        matched_attributes = []
        
        if intent:
            target_genres = intent.get("genres", [])
            for g in genres:
                if any(tg.lower() in g.lower() for tg in target_genres):
                    matched_attributes.append(f"{g} storytelling")
                    break

            target_themes = intent.get("themes", [])
            for t in target_themes:
                if any(kw.lower() in t.lower() or t.lower() in kw.lower() for kw in keywords):
                    matched_attributes.append(f"themes of {t}")
                    break

            moods = intent.get("mood", [])
            if moods:
                matched_attributes.append(f"a {moods[0]} tone")

        if not matched_attributes:
            primary_genre = genres[0] if genres else "cinematic"
            matched_attributes.append(f"compelling {primary_genre} narrative")
            if keywords and keywords[0]:
                matched_attributes.append(f"elements of {keywords[0]}")

        reason_clause = " and ".join(matched_attributes[:2])
        director_clause = f" directed by {director}" if director and director != "nan" else ""
        
        return f"Strong match for your request with {reason_clause}{director_clause}."

    def recommend(self, prompt: str, limit: int = 10, intent: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Performs semantic vector cosine similarity matching against local dataset.
        Blends semantic similarity (80%), normalized IMDb rating (12%), and popularity (8%).
        """
        if not self.is_loaded or self.model is None or self.embeddings is None:
            raise RuntimeError("Recommendation engine resources are not initialized.")

        # Determine effective query (enhanced query from Gemini or raw prompt)
        search_query = prompt
        if intent and intent.get("enhanced_query"):
            search_query = intent["enhanced_query"]

        # 1. Encode user query into unit vector
        query_vec = self.model.encode(search_query, normalize_embeddings=True).astype(np.float32)
        
        # 2. Vectorized Cosine Similarity: Dot product of unit vectors
        cosine_sims = np.dot(self.embeddings, query_vec)

        # 3. Rating and Popularity normalizations
        ratings = self.df["rating"].fillna(7.0).to_numpy()
        normalized_ratings = (ratings - 5.0) / 5.0  # [0, 1] for ratings 5 to 10
        normalized_ratings = np.clip(normalized_ratings, 0.0, 1.0)

        vote_counts = self.df["vote_count"].fillna(100000).to_numpy()
        log_votes = np.log1p(vote_counts)
        normalized_votes = log_votes / (log_votes.max() or 1.0)

        # 4. Weighted Final Recommendation Score
        # Semantic similarity is the dominant factor (80%)
        final_scores = (
            0.80 * cosine_sims +
            0.12 * normalized_ratings +
            0.08 * normalized_votes
        )

        # 5. Apply avoid filter penalty if present in intent
        if intent and intent.get("avoid"):
            avoid_list = [a.lower() for a in intent["avoid"]]
            for idx, row in self.df.iterrows():
                row_text = (str(row.get("genres", "")) + " " + str(row.get("overview", ""))).lower()
                if any(av in row_text for av in avoid_list):
                    final_scores[idx] -= 0.35

        # 6. Rank top indices
        top_indices = np.argsort(final_scores)[::-1][:limit]

        results = []
        for rank, idx in enumerate(top_indices, start=1):
            row = self.df.iloc[idx]
            raw_sim = float(cosine_sims[idx])
            score = float(final_scores[idx])
            
            genres_list = [g.strip() for g in str(row.get("genres", "")).split(",") if g.strip()]
            match_reason = self.generate_match_reason(row, prompt, intent)

            results.append({
                "rank": rank,
                "id": int(row.get("id", idx)),
                "title": str(row.get("title", "Unknown Title")),
                "year": int(row.get("year", 2024)),
                "genres": genres_list,
                "overview": str(row.get("overview", "")),
                "rating": float(row.get("rating", 7.5)),
                "vote_count": int(row.get("vote_count", 0)),
                "director": str(row.get("director", "Unknown")),
                "cast": str(row.get("cast", "")),
                "poster_path": str(row.get("poster_path", "")),
                "similarity_score": round(max(0.0, min(1.0, raw_sim)), 2),
                "final_score": round(max(0.0, min(1.0, score)), 2),
                "match_reason": match_reason
            })

        return results
