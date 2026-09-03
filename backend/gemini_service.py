"""
CineMatch Gemini Intent & Query Enhancement Service
Extracts rich structured user preferences (genres, mood, themes, pacing, tone, avoid, similar movies)
and generates an enhanced semantic search query.

CRITICAL RULE:
Gemini is used ONLY for intent understanding and query enhancement.
Gemini does NOT hallucinate or return the final movie recommendations.
All recommendations are retrieved locally via SentenceTransformer and Cosine Similarity.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("cinematch.gemini")

GEMINI_MODELS = [
    "gemini-3.7-flash",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-2.5-flash",
    "gemini-1.5-flash"
]

EXTRACTION_SYSTEM_PROMPT = """You are the intent understanding engine for CineMatch, an AI movie recommendation platform.
Your task is to analyze the user's natural language request and convert it into a structured search profile and an enhanced descriptive query.

Extract and output strictly valid JSON matching this schema:
{
  "genres": ["list of strings, e.g. Sci-Fi, Drama, Thriller"],
  "mood": ["list of emotional descriptors, e.g. melancholic, thrilling, heartwarming"],
  "themes": ["list of core themes, e.g. space exploration, father-daughter bond, betrayal"],
  "pacing": "fast" | "moderate" | "slow-burn" | "any",
  "tone": ["list of tonal attributes, e.g. dark, realistic, whimsical, intense"],
  "keywords": ["specific subject tags, e.g. time dilation, black hole, artificial intelligence"],
  "avoid": ["elements the user explicitly dislikes or asked to exclude"],
  "similar_movies": ["movies or directors mentioned as reference points"],
  "ending_preference": "shocking" | "happy" | "bittersweet" | "open" | "none",
  "enhanced_query": "A rich, descriptive search query combining genres, themes, mood, tone, and character dynamics suitable for semantic embedding similarity matching."
}

Rules:
- NEVER invent or recommend specific movie titles in the JSON outside of similar_movies references from user prompt.
- 'enhanced_query' should be 1-3 information-dense sentences that summarize the user's ideal movie characteristics.
- Return ONLY the raw JSON object. Do not include markdown codeblocks or extra text.
"""

class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client_initialized = False
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.client_initialized = True
                logger.info("GeminiService initialized with provided API key.")
            except Exception as e:
                logger.warning(f"Failed to configure Google GenAI client: {e}")
        else:
            logger.info("GeminiService initialized in fallback mode (no API key set).")

    def enhance_query(self, prompt: str) -> Dict[str, Any]:
        """
        Processes the user's prompt through Gemini to extract intent and an enhanced search query.
        Gracefully falls back to heuristic extraction if Gemini is unavailable, rate-limited, or fails.
        """
        if not prompt or not prompt.strip():
            return self._fallback_extraction("")

        if self.client_initialized and self.api_key:
            for model_name in GEMINI_MODELS:
                try:
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=EXTRACTION_SYSTEM_PROMPT
                    )
                    
                    response = model.generate_content(
                        f"User request: \"{prompt}\"",
                        generation_config=genai.GenerationConfig(
                            response_mime_type="application/json",
                            temperature=0.2
                        )
                    )
                    
                    if response and response.text:
                        clean_text = response.text.strip()
                        if clean_text.startswith("```"):
                            clean_text = clean_text.strip("`").replace("json\n", "", 1).strip()
                        data = json.loads(clean_text)
                        
                        # Guarantee enhanced_query exists
                        if "enhanced_query" not in data or not data["enhanced_query"]:
                            data["enhanced_query"] = prompt
                            
                        logger.info(f"Gemini ({model_name}) successfully extracted intent: {data.get('genres')}")
                        return data
                except Exception as e:
                    logger.warning(f"Gemini model {model_name} extraction failed: {e}. Trying next fallback...")
                    continue

        # Clean fallback if Gemini fails or is not configured
        return self._fallback_extraction(prompt)

    def _fallback_extraction(self, prompt: str) -> Dict[str, Any]:
        """
        Deterministic, lightweight offline fallback to extract core signals without Gemini.
        Guarantees the system never crashes.
        """
        p_lower = prompt.lower()
        genres = []
        
        genre_map = {
            "sci-fi": "Sci-Fi", "science fiction": "Sci-Fi", "space": "Sci-Fi", "alien": "Sci-Fi",
            "thriller": "Thriller", "psychological": "Thriller", "suspense": "Thriller", "mystery": "Mystery",
            "drama": "Drama", "emotional": "Drama", "sad": "Drama", "crying": "Drama",
            "action": "Action", "fight": "Action", "hero": "Action",
            "comedy": "Comedy", "funny": "Comedy", "laugh": "Comedy", "friends": "Comedy",
            "horror": "Horror", "scary": "Horror", "spooky": "Horror",
            "romance": "Romance", "love": "Romance", "romantic": "Romance",
            "crime": "Crime", "mafia": "Crime", "heist": "Crime", "detective": "Crime",
            "animation": "Animation", "anime": "Animation", "ghibli": "Animation"
        }
        
        for k, v in genre_map.items():
            if k in p_lower and v not in genres:
                genres.append(v)
                
        mood = []
        if "dark" in p_lower or "disturbing" in p_lower:
            mood.append("dark")
        if "emotional" in p_lower or "heartbreaking" in p_lower or "lonely" in p_lower:
            mood.append("emotional")
        if "mind-bending" in p_lower or "twist" in p_lower or "confusing" in p_lower:
            mood.append("mind-bending")
        if "feel-good" in p_lower or "funny" in p_lower or "wholesome" in p_lower:
            mood.append("feel-good")

        return {
            "genres": genres,
            "mood": mood,
            "themes": ["cinematic storytelling"],
            "pacing": "moderate",
            "tone": mood or ["engaging"],
            "keywords": [w for w in prompt.split() if len(w) > 4][:5],
            "avoid": [],
            "similar_movies": [],
            "ending_preference": "none",
            "enhanced_query": prompt  # Direct raw prompt to SentenceTransformer
        }
