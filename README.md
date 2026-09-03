# CineMatch — Find your match

> **An AI-powered semantic movie recommendation platform powered by Sentence Transformers, Vectorized Cosine Similarity, and Google Gemini Intent Understanding across a 250,000+ movie catalog. Zero cloud database dependency.**

🌐 **Live Demo:** [https://kaustubh-kodes.github.io/cinematch-recommendation-chatbot/](https://kaustubh-kodes.github.io/cinematch-recommendation-chatbot/)  
📂 **GitHub Repository:** [https://github.com/Kaustubh-kodes/cinematch-recommendation-chatbot](https://github.com/Kaustubh-kodes/cinematch-recommendation-chatbot)

---

## 🎬 1. What CineMatch Does

Traditional movie recommenders rely on rigid genre dropdowns or keyword filters that fail to capture human nuance. **CineMatch** allows users to describe exactly what they want to watch in **natural language**:

* *"I want a dark psychological thriller with a shocking ending"*
* *"I want something like Interstellar but more emotional and less focused on science"*
* *"I want a funny feel-good movie to watch with my friends"*
* *"I want a slow emotional movie about loneliness and relationships"*

CineMatch analyzes the emotional tone, themes, pacing, and narrative tropes of your prompt, extracts underlying intent via **Google Gemini**, and performs **semantic vector similarity search** across a **250,000+ movie catalog** to return ranked, grounded recommendations with factual **"Why this matches"** explanations.

---

## 🏛️ 2. Architecture: Zero Cloud Database / 100% Embedded

CineMatch is built to be completely self-contained with **zero external cloud database servers**:
* ❌ **NO** MongoDB / PostgreSQL / MySQL / Firebase
* ❌ **NO** Pinecone / ChromaDB / Weaviate / LangChain
* ✅ **100% Embedded & Local**: 250,000+ movie records stored in a single SQLite file (`data/movies.db`), vector embeddings in `models/movie_embeddings.npy`.

### End-to-End Execution Flow

```
USER NATURAL LANGUAGE PROMPT
           ↓
[Google Gemini API (Flash 3.7 / 3.5)]
           ↓  (Extracts Structured Intent JSON: genres, mood, themes, pacing, avoid)
ENHANCED SEMANTIC SEARCH QUERY
           ↓
[Sentence Transformer: all-MiniLM-L6-v2]
           ↓  (Encodes query into dense 384-dimensional unit vector)
VECTORIZED COSINE SIMILARITY (NumPy Dot Product)
           ↓  (Calculates dot product against models/movie_embeddings.npy)
SQL MULTI-ATTRIBUTE QUERYING & SCORING (250,000+ Movies)
           ↓  (80% Semantic Similarity + 12% Normalized Rating + 8% Popularity)
GROUNDED MATCH REASON GENERATION
           ↓  (Generates factual explanation using local metadata)
FASTAPI BACKEND → REACT / NEXT.JS FRONTEND
```

---

## 🧠 3. How the ML Recommendation Engine Works

1. **Pre-trained Sentence Transformer**: Uses `all-MiniLM-L6-v2`, mapping sentences to a 384-dimensional dense vector space tuned for semantic search.
2. **Offline Embeddings Generation**: Metadata (`title`, `genres`, `overview`, `keywords`, `cast`, `director`) is concatenated into an information-dense string and pre-encoded into `models/movie_embeddings.npy`.
3. **High-Performance Vectorized Search**: Embeddings are L2-normalized so cosine similarity is computed in milliseconds via a single NumPy matrix-vector dot product:
   $$\text{Cosine Similarity}(\mathbf{u}, \mathbf{v}) = \mathbf{u} \cdot \mathbf{v}$$
4. **Intelligent Score Blending**:
   $$\text{Final Score} = 0.80 \times \text{Similarity} + 0.12 \times \text{Rating}_{\text{norm}} + 0.08 \times \text{Votes}_{\text{norm}}$$
   This ensures semantic match is the dominant factor while prioritizing critically acclaimed cinema.

---

## ⚡ 4. How Google Gemini is Used

Gemini is strictly used as an **Intent Understanding and Query Enhancement layer**:
* 🚫 Gemini does **NOT** invent or hallucinate the final movie list.
* 🚫 Gemini does **NOT** query an external database.
* ✅ Gemini extracts structured signals and produces a rich `enhanced_query` optimized for embedding matching.

### Structured Intent JSON Schema

```json
{
  "genres": ["Sci-Fi", "Drama"],
  "mood": ["emotional", "thoughtful"],
  "themes": ["space exploration", "human connection", "family"],
  "pacing": "moderate",
  "tone": ["emotional", "thoughtful"],
  "keywords": ["space", "relationships", "family", "emotional journey"],
  "avoid": ["highly technical science"],
  "similar_movies": ["Interstellar"],
  "ending_preference": "beautiful",
  "enhanced_query": "An emotional and thoughtful science fiction drama involving space, human relationships and family, with less technical scientific focus and a beautiful or emotionally satisfying ending."
}
```

---

## 🛡️ 5. Graceful Offline Fallback

If the Gemini API key is missing, network is unavailable, or rate limits occur:
1. CineMatch **never crashes**.
2. It automatically activates the deterministic offline intent extractor.
3. The user's raw prompt is fed directly to the `SentenceTransformer` and evaluated against the local vector database with zero disruption.

---

## 🚀 6. Project Directory Structure

```
cinematch/
├── data/
│   ├── movies.db                  # Embedded SQLite database (250,000+ movies)
│   └── movies.csv                 # Local curated CSV metadata
├── models/
│   └── movie_embeddings.npy       # Precomputed 384d float32 embeddings
├── backend/
│   ├── main.py                    # FastAPI application & endpoints (GET /, POST /recommend)
│   ├── recommender.py             # Hybrid SentenceTransformer + SQLite engine
│   ├── gemini_service.py          # Gemini intent understanding & query enhancer
│   ├── requirements.txt           # Backend dependencies
│   └── .env.example               # Environment variables template
├── scripts/
│   ├── ingest_250k_movies.py      # Streams and ingests 250,000+ movies into SQLite
│   ├── prepare_data.py            # Prepares local movies.csv dataset
│   └── generate_embeddings.py     # Generates and saves movie_embeddings.npy offline
├── frontend/                      # Modern Next.js / React UI
│   ├── src/app/page.tsx           # Search UI, movie cards, user profile, watchlist
│   └── next.config.ts             # Export configuration
├── README.md                      # Documentation
└── requirements.txt               # Root dependencies
```

---

## 🛠️ 7. Setup & Installation Guide

### Prerequisites
* Python 3.10+
* Node.js 18+ and npm

### Step 1: Install Dependencies
```bash
git clone https://github.com/Kaustubh-kodes/cinematch-recommendation-chatbot.git
cd cinematch-recommendation-chatbot

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Ingest 250,000+ Movies & Precompute Embeddings
```bash
# 1. Download official IMDb stream and build SQLite database (takes ~15 seconds)
python scripts/ingest_250k_movies.py

# 2. Generate curated local vector embeddings (runs once)
python scripts/generate_embeddings.py
```

### Step 3: Configure Gemini API Key (Optional)
```bash
cp .env.example .env
# Add your key to .env:
# GEMINI_API_KEY="AIzaSy..."
```

### Step 4: Start the Backend & Frontend
```bash
# Terminal 1: Start FastAPI Backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start Next.js Frontend
cd ../frontend
npm install
npm run dev
```

* Frontend: `http://localhost:3000`
* Backend API Docs: `http://localhost:8000/docs`

---

## 📡 8. API Reference

### `GET /`
Returns backend health, loaded dataset count (`250,000+`), and ML model status.

### `POST /recommend`
Submits a natural language prompt and returns ranked movie matches.

#### Request:
```json
{
  "prompt": "I want a dark psychological thriller with a shocking ending",
  "limit": 10
}
```

#### Response:
```json
{
  "success": true,
  "original_prompt": "I want a dark psychological thriller with a shocking ending",
  "enhanced_query": "A dark, intense psychological thriller exploring paranoia, deception, and moral ambiguity with a shocking twist ending.",
  "intent": {
    "genres": ["Thriller", "Mystery", "Drama"],
    "mood": ["dark", "intense"],
    "ending_preference": "shocking"
  },
  "recommendations": [
    {
      "rank": 1,
      "id": 13,
      "title": "Shutter Island",
      "year": 2010,
      "genres": ["Mystery", "Thriller"],
      "overview": "In 1954, a U.S. Marshal investigates the disappearance of a murderer who escaped from a hospital for the criminally insane...",
      "rating": 8.2,
      "poster_path": "https://image.tmdb.org/t/p/w500/kve20tXwUZpu4GUX8l6X7Z4QIIL.jpg",
      "similarity_score": 0.92,
      "final_score": 0.94,
      "match_reason": "Strong match for your request with Thriller narrative, a dark tone and themes of mind games."
    }
  ],
  "total_results": 1
}
```

---

## 📜 9. License & Credits
Developed by **Kaustubh Tiwari** as part of the CineMatch AI project.
