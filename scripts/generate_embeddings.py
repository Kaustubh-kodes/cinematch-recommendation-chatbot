"""
CineMatch Embedding Generation Script
Generates dense 384-dimensional vector embeddings for all movies in data/movies.csv
using the pre-trained SentenceTransformer ('all-MiniLM-L6-v2') model and saves them locally
to models/movie_embeddings.npy.

Embeddings are computed once and stored. Never recomputed during runtime searches.
"""

import os
import sys
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# Define Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "movies.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")
EMBEDDINGS_PATH = os.path.join(MODELS_DIR, "movie_embeddings.npy")

MODEL_NAME = "all-MiniLM-L6-v2"

def main():
    print(f"=== CineMatch Offline Embedding Generator ===")
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    if not os.path.exists(DATA_PATH):
        print(f"[ERROR] Movie dataset not found at {DATA_PATH}. Please run scripts/prepare_data.py first.")
        sys.exit(1)
        
    print(f"1. Loading movie dataset from: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    print(f"   Loaded {len(df)} movies.")
    
    if "combined_text" not in df.columns:
        print("[ERROR] 'combined_text' column missing in movies.csv.")
        sys.exit(1)
        
    texts = df["combined_text"].fillna("").tolist()
    
    print(f"2. Initializing pre-trained SentenceTransformer: '{MODEL_NAME}'")
    model = SentenceTransformer(MODEL_NAME)
    
    print(f"3. Generating embeddings for {len(texts)} movies (batch_size=32, normalize_embeddings=True)...")
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True
    ).astype(np.float32)
    
    print(f"   Embeddings matrix shape: {embeddings.shape}")
    
    print(f"4. Saving embeddings to local file: {EMBEDDINGS_PATH}")
    np.save(EMBEDDINGS_PATH, embeddings)
    
    print(f"[SUCCESS] Saved {len(embeddings)} movie embeddings to {EMBEDDINGS_PATH}")
    print(f"File size: {os.path.getsize(EMBEDDINGS_PATH) / 1024:.1f} KB")

if __name__ == "__main__":
    main()
