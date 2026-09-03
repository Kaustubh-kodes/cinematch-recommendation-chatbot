import os
import json
import re
import logging
from abc import ABC, abstractmethod
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List, Optional

logger = logging.getLogger(__name__)

class StructuredPreferences(BaseModel):
    genres: List[str] = Field(default=[], description="List of preferred genres extracted from the request.")
    similar_to: List[str] = Field(default=[], description="List of titles/items the user liked or wants similar recommendations for.")
    avoid: List[str] = Field(default=[], description="List of genres, keywords, or properties the user explicitly wants to avoid.")
    keywords: List[str] = Field(default=[], description="Key descriptive tags like 'mind-bending', 'scary', 'fast-paced'.")
    minimum_rating: Optional[float] = Field(default=0.0, description="Minimum rating out of 5.0 requested by user.")

class LLMProvider(ABC):
    """Abstract interface for LLM services to keep recommendation logic separate from providers."""
    
    @abstractmethod
    def extract_preferences(self, text: str) -> dict:
        """Parses natural language requests into structured user preferences."""
        pass
        
    @abstractmethod
    def generate_explanation(self, title: str, genres: str, evidence: dict) -> str:
        """Generates grounded explanations why an item was recommended based strictly on evidence."""
        pass
        
    @abstractmethod
    def generate_chat_reply(self, message: str, history: list, recommendations: list) -> str:
        """Converses with the user and integrates recommendations naturally."""
        pass

class GeminiProvider(LLMProvider):
    """Gemini-backed LLM implementation using Google GenAI SDK."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"Initialized GeminiProvider using model: {model_name}")

    def extract_preferences(self, text: str) -> dict:
        prompt = f"""
        You are CineMatch preference extraction engine. 
        Analyze the user prompt and extract structured preferences.
        User request: "{text}"
        
        Return a valid JSON object matching this schema:
        {{
            "genres": ["list of strings"],
            "similar_to": ["list of items liked"],
            "avoid": ["list of elements to avoid"],
            "keywords": ["descriptive keywords"],
            "minimum_rating": 0.0
        }}
        
        Rules:
        - Match genres to common terms (e.g. "sci fi" -> "Sci-Fi", "love story" -> "Romance", "wizards" -> "Fantasy").
        - Keep output strict and parse carefully. Return JSON only.
        """
        try:
            # We call Gemini with json constraint
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            data = json.loads(response.text)
            logger.info(f"Extracted preferences via Gemini: {data}")
            return data
        except Exception as e:
            logger.error(f"Gemini extraction failed: {e}. Falling back to empty structure.")
            return {"genres": [], "similar_to": [], "avoid": [], "keywords": [], "minimum_rating": 0.0}

    def generate_explanation(self, title: str, genres: str, evidence: dict) -> str:
        prompt = f"""
        You are CineMatch explainability layer. 
        Explain to the user why "{title}" was recommended.
        
        Item Details:
        - Title: {title}
        - Genres: {genres}
        
        Model Match Evidence:
        {json.dumps(evidence, indent=2)}
        
        Rules:
        1. Ground your explanation STRICTLY on the evidence provided (e.g. content_score similarity, collaborative signal, or matched_genres).
        2. Do NOT hallucinate or make up plots, directors, authors, or facts about "{title}".
        3. Make the tone friendly, conversational, and direct (max 3 sentences).
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini explanation generation failed: {e}")
            return f"Recommended based on content similarity ({evidence.get('content_score', 0)*100:.0f}%) and genre overlap."

    def generate_chat_reply(self, message: str, history: list, recommendations: list) -> str:
        # Build conversational history context
        history_str = ""
        for turn in history:
            role = "User" if turn.get("role") == "user" else "Assistant"
            history_str += f"{role}: {turn.get('content')}\n"
            
        recs_str = ""
        for idx, r in enumerate(recommendations, 1):
            recs_str += f"{idx}. {r['title']} (Match score: {r['score']*100:.0f}%)\n"
            
        prompt = f"""
        You are CineMatch recommendation assistant. Talk to the user.
        
        Chat History:
        {history_str}
        
        Latest User Message: "{message}"
        
        Here are the recommendations calculated independently by the ML Engine:
        {recs_str}
        
        Rules:
        1. Talk about the recommended items. You MUST mention the items recommended above.
        2. Keep the conversation engaging and ask follow-up questions to understand their mood.
        3. Do NOT make up any details not present in the titles.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini chat response failed: {e}")
            return "Based on your request, I recommend looking at: " + ", ".join(r['title'] for r in recommendations)

class MockProvider(LLMProvider):
    """Rule-based LLM mockup ensuring offline functionality without API keys."""
    
    def __init__(self):
        logger.info("Initialized MockProvider (Offline Mode)")

    def extract_preferences(self, text: str) -> dict:
        text_lower = text.lower()
        genres = []
        avoid = []
        similar_to = []
        keywords = []
        minimum_rating = 0.0
        
        # Simple rule-based parser
        genre_keywords = {
            "Sci-Fi": ["sci-fi", "scifi", "science fiction", "space", "interstellar", "alien"],
            "Action": ["action", "explosions", "fight", "superhero"],
            "Comedy": ["comedy", "funny", "laugh", "hilarious"],
            "Drama": ["drama", "emotional", "sad", "serious"],
            "Thriller": ["thriller", "suspense", "tension"],
            "Romance": ["romance", "love story", "romantic"],
            "Fantasy": ["fantasy", "magic", "wizard", "witches", "dungeons"],
            "Mystery": ["mystery", "detective", "puzzle", "investigation"],
            "Horror": ["horror", "scary", "ghost", "spooky"],
            "Non-Fiction": ["non-fiction", "biography", "true story", "history"]
        }
        
        for genre, keys in genre_keywords.items():
            if any(k in text_lower for k in keys):
                if "avoid" in text_lower and any(text_lower.find(k) > text_lower.find("avoid") for k in keys):
                    avoid.append(genre)
                else:
                    genres.append(genre)
                    
        # Extract title references: "like X" or "similar to X"
        matches = re.findall(r'(?:like|similar to|about)\s+([a-zA-Z0-9\s\-\:\'\"]+)', text, re.IGNORECASE)
        if matches:
            titles = []
            for m in matches:
                # Split at common transition keywords to isolate the title
                parts = re.split(r'\b(?:but|and|avoid|with|without|rating|stars)\b', m, flags=re.IGNORECASE)
                titles.append(parts[0].strip())
            similar_to = [t for t in titles if len(t) > 2]
            
        # Parse rating requests
        rating_match = re.search(r'(?:rating|stars)\s*(?:>=|>|above)?\s*([0-5](?:\.[0-9])?)', text_lower)
        if rating_match:
            try:
                minimum_rating = float(rating_match.group(1))
            except ValueError:
                pass
                
        # Parse simple mood keywords
        moods = ["mind-bending", "fast-paced", "slow-burn", "scary", "thought-provoking", "uplifting"]
        for m in moods:
            if m in text_lower:
                keywords.append(m)
                
        data = {
            "genres": genres,
            "similar_to": [s[:30] for s in similar_to],  # Cap title length
            "avoid": avoid,
            "keywords": keywords,
            "minimum_rating": minimum_rating
        }
        logger.info(f"Rule-based extracted preferences: {data}")
        return data

    def generate_explanation(self, title: str, genres: str, evidence: dict) -> str:
        content_pct = int(evidence.get("content_score", 0.0) * 100)
        collab_pct = int(evidence.get("collaborative_score", 0.0) * 100)
        pref_pct = int(evidence.get("preference_score", 0.0) * 100)
        
        reasons = []
        if content_pct > 30:
            reasons.append(f"shows a {content_pct}% match in narrative style and content elements")
        if collab_pct > 30:
            reasons.append(f"has strong rating patterns matching your profile ({collab_pct}% match)")
        if pref_pct > 30:
            reasons.append(f"matches your explicitly requested genres ({genres})")
            
        if not reasons:
            reasons.append("is currently highly trending in our catalogue")
            
        reason_str = ", and ".join(reasons)
        return f"\"{title}\" is recommended because it {reason_str}. It aligns with your search context."

    def generate_chat_reply(self, message: str, history: list, recommendations: list) -> str:
        if not recommendations:
            return "I couldn't find any specific items matching those exact criteria. Try adjusting your preferences or genres!"
            
        titles = [f"**{r['title']}** ({r['genres']})" for r in recommendations]
        titles_bullet = "\n".join(f"- {t}" for t in titles)
        
        reply = f"Here are the top matches I found using our machine learning scoring engine:\n\n{titles_bullet}\n\nWould you like me to explain why any of these specific recommendations are relevant to you?"
        return reply

class LLMService:
    """Service wrapper that manages LLM providers dynamically."""
    
    def __init__(self):
        # Read API key from environment variable
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        
        if api_key:
            self.provider = GeminiProvider(api_key=api_key)
        else:
            self.provider = MockProvider()

    def get_provider(self) -> LLMProvider:
        return self.provider
