import pytest
import pandas as pd
import numpy as np
from src.data.preprocessing import DataPreprocessor
from src.recommendation.content_based import ContentBasedRecommender
from src.recommendation.collaborative import CollaborativeRecommender
from src.recommendation.hybrid import HybridRecommender
from src.nlp.llm_service import MockProvider

# Sample Mock Data for Testing
@pytest.fixture
def sample_items():
    return pd.DataFrame([
        {"movieId": 1, "title": "Toy Story", "genres": "Animation|Children", "combined_text": "toy story animation children disney"},
        {"movieId": 2, "title": "Jumanji", "genres": "Adventure|Fantasy", "combined_text": "jumanji adventure fantasy board game"},
        {"movieId": 3, "title": "Heat", "genres": "Action|Crime", "combined_text": "heat action crime pacino de niro"},
        {"movieId": 4, "title": "Star Wars", "genres": "Action|Sci-Fi", "combined_text": "star wars action scifi space jedi"}
    ])

@pytest.fixture
def sample_ratings():
    return pd.DataFrame([
        {"userId": 1, "movieId": 1, "rating": 5.0, "timestamp": 10000},
        {"userId": 1, "movieId": 2, "rating": 4.0, "timestamp": 10002},
        {"userId": 2, "movieId": 1, "rating": 3.0, "timestamp": 10005},
        {"userId": 2, "movieId": 3, "rating": 5.0, "timestamp": 10008},
        {"userId": 3, "movieId": 4, "rating": 5.0, "timestamp": 10010}
    ])

# 1. Test Preprocessing
def test_clean_text():
    preprocessor = DataPreprocessor()
    assert preprocessor.clean_text("Hello, World!") == "hello world"
    assert preprocessor.clean_text("Sci-Fi!") == "scifi"
    assert preprocessor.clean_text(np.nan) == ""

def test_preprocess_movies(sample_items):
    preprocessor = DataPreprocessor()
    tags_df = pd.DataFrame([
        {"userId": 1, "movieId": 1, "tag": "pixar", "timestamp": 10000},
        {"userId": 1, "movieId": 1, "tag": "fun", "timestamp": 10002}
    ])
    processed = preprocessor.preprocess_movies(sample_items, tags_df)
    assert "combined_text" in processed.columns
    # Check that tags were merged
    assert "pixar" in processed.iloc[0]["combined_text"]

# 2. Test Content Recommender
def test_content_recommender(sample_items):
    recommender = ContentBasedRecommender(id_col='movieId', title_col='title', genre_col='genres')
    recommender.fit(sample_items)
    assert recommender.tfidf_matrix.shape == (4, len(recommender.vectorizer.vocabulary_))
    
    # Recommend similar to Toy Story (id 1)
    recs = recommender.recommend_by_item(item_id=1, top_k=2)
    assert len(recs) == 2
    # Ensure it didn't recommend Toy Story itself
    assert all(r["item_id"] != 1 for r in recs)

def test_content_profile_search(sample_items):
    recommender = ContentBasedRecommender(id_col='movieId', title_col='title', genre_col='genres')
    recommender.fit(sample_items)
    
    # Search for Sci-Fi / space keywords
    prefs = {"genres": ["Sci-Fi"], "keywords": ["space"]}
    recs = recommender.recommend_by_profile(prefs, top_k=1)
    assert len(recs) == 1
    # Star Wars has Sci-Fi and space in keywords
    assert recs[0]["item_id"] == 4

# 3. Test Collaborative Recommender
def test_collaborative_recommender(sample_ratings):
    recommender = CollaborativeRecommender(user_col='userId', item_col='movieId', rating_col='rating', num_factors=2)
    recommender.fit(sample_ratings)
    
    # Predict rating for User 1 on Movie 3
    rating_ii = recommender.predict_rating_item_item(user_id=1, item_id=3)
    rating_svd = recommender.predict_rating_svd(user_id=1, item_id=3)
    
    assert 1.0 <= rating_ii <= 5.0
    assert 1.0 <= rating_svd <= 5.0

# 4. Test Hybrid Recommender & Cold Start Fallbacks
def test_hybrid_recommender(sample_items, sample_ratings):
    hybrid = HybridRecommender(id_col='movieId', user_col='userId', title_col='title', genre_col='genres', rating_col='rating', num_factors=2)
    hybrid.fit(sample_items, sample_ratings)
    
    # Existing user hybrid recs
    recs = hybrid.recommend_hybrid(user_id=1, top_k=2)
    assert len(recs) <= 2
    
    # Cold start: new user with no preferences -> popularity baseline fallback
    recs_cold = hybrid.recommend_hybrid(user_id=999, top_k=2)
    assert len(recs_cold) == 2
    assert "collaborative_score" in recs_cold[0]["evidence"]

# 5. Test LLM Mock Preference Parser
def test_mock_llm_parser():
    provider = MockProvider()
    prefs = provider.extract_preferences("I want a mind-bending sci-fi movie like Inception but avoid horror rating >= 4.0")
    
    assert "Sci-Fi" in prefs["genres"]
    assert "Horror" in prefs["avoid"]
    assert "Inception" in prefs["similar_to"]
    assert "mind-bending" in prefs["keywords"]
    assert prefs["minimum_rating"] == 4.0

# 6. Test FastAPI endpoints
from fastapi.testclient import TestClient
from backend.main import app

def test_api_endpoints():
    with TestClient(app) as client:
        # Check health
        res = client.get("/health")
        assert res.status_code == 200
        assert "status" in res.json()
