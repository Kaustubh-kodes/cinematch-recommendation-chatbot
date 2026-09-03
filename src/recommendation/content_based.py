import logging
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)

class ContentBasedRecommender:
    """
    Content-Based Recommender using sparse TF-IDF text features and 
    on-the-fly cosine similarity computation to avoid large dense matrices.
    """
    
    def __init__(self, id_col='movieId', title_col='title', genre_col='genres'):
        self.id_col = id_col
        self.title_col = title_col
        self.genre_col = genre_col
        
        self.vectorizer = TfidfVectorizer(stop_words='english', min_df=2)
        self.items_df = None
        self.tfidf_matrix = None
        self.id_to_idx = {}
        self.idx_to_id = {}

    def fit(self, items_df):
        """Fits TF-IDF vectorizer on the combined_text of items."""
        logger.info(f"Fitting TF-IDF on {len(items_df)} items...")
        self.items_df = items_df.copy()
        
        # Build mapping dictionaries
        self.id_to_idx = {row[self.id_col]: idx for idx, row in self.items_df.iterrows()}
        self.idx_to_id = {idx: row[self.id_col] for idx, row in self.items_df.iterrows()}
        
        # Fit vectorizer
        corpus = self.items_df['combined_text'].fillna('')
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        logger.info(f"TF-IDF matrix generated with shape: {self.tfidf_matrix.shape}")
        return self

    def _get_similarity_scores(self, query_vector):
        """
        Computes cosine similarity between query vector and all item vectors.
        Since TF-IDF outputs are L2-normalized, cosine similarity is simply the dot product.
        This calculation is highly efficient for sparse matrices.
        """
        import scipy.sparse
        
        # Check if query_vector is a dense numpy array or matrix
        if isinstance(query_vector, np.ndarray) or hasattr(query_vector, 'ndim') and not scipy.sparse.issparse(query_vector):
            # If it's a numpy matrix, convert to array and flatten
            if isinstance(query_vector, np.matrix):
                query_vector = np.asarray(query_vector)
            query_vector = query_vector.ravel()
            # Sparse matrix * dense vector -> dense 1D array
            scores = self.tfidf_matrix.dot(query_vector)
        else:
            # Query vector is sparse (1, D). Result is sparse (N, 1)
            scores = self.tfidf_matrix.dot(query_vector.T)
            if hasattr(scores, 'toarray'):
                scores = scores.toarray()
            scores = np.asarray(scores).ravel()
            
        return np.asarray(scores).ravel()

    def recommend_by_item(self, item_id, top_k=10):
        """
        Recommends items similar to the given item_id.
        Excludes the input item itself.
        """
        if self.tfidf_matrix is None:
            raise ValueError("Recommender has not been fitted. Call fit() first.")
            
        if item_id not in self.id_to_idx:
            logger.warning(f"Item ID {item_id} not found in training items. Returning popularity fallback.")
            return []
            
        # Get target item index and TF-IDF vector
        idx = self.id_to_idx[item_id]
        query_vector = self.tfidf_matrix[idx]
        
        # Calculate similarity scores
        scores = self._get_similarity_scores(query_vector)
        
        # Get sorted index rankings
        sorted_indices = np.argsort(scores)[::-1]
        
        target_row = self.items_df.iloc[idx]
        target_genres = set(str(target_row[self.genre_col]).split('|'))
        target_title = target_row[self.title_col]
        
        recommendations = []
        for rank_idx in sorted_indices:
            cand_id = self.idx_to_id[rank_idx]
            if cand_id == item_id:
                continue  # Skip target item
                
            score = float(scores[rank_idx])
            
            # Extract common metadata for structured evidence
            cand_row = self.items_df.iloc[rank_idx]
            cand_genres = set(str(cand_row[self.genre_col]).split('|'))
            matched_genres = list(target_genres.intersection(cand_genres))
            
            recommendations.append({
                "item_id": int(cand_id),
                "title": cand_row[self.title_col],
                "genres": cand_row[self.genre_col],
                "score": score,
                "evidence": {
                    "content_score": round(score, 4),
                    "collaborative_score": 0.0,
                    "preference_score": 0.0,
                    "final_score": round(score, 4),
                    "matched_genres": matched_genres,
                    "similar_to": [target_title]
                }
            })
            
            if len(recommendations) >= top_k:
                break
                
        return recommendations

    def recommend_by_profile(self, preferences, top_k=10):
        """
        Recommends items matching a user's explicit structured preference configuration.
        preferences: dict containing optional 'genres', 'similar_to', 'keywords'
        """
        if self.tfidf_matrix is None:
            raise ValueError("Recommender has not been fitted. Call fit() first.")
            
        # 1. Build search profile text
        pref_parts = []
        
        # Include genres
        if 'genres' in preferences and preferences['genres']:
            pref_parts.append(" ".join(preferences['genres']))
            
        # Include keywords
        if 'keywords' in preferences and preferences['keywords']:
            pref_parts.append(" ".join(preferences['keywords']))
            
        # Include metadata of items they liked
        liked_titles = []
        if 'similar_to' in preferences and preferences['similar_to']:
            liked_titles = preferences['similar_to']
            for item_name in liked_titles:
                # Try to locate the movie/book by title
                matching_items = self.items_df[
                    self.items_df[self.title_col].str.contains(item_name, case=False, na=False)
                ]
                if not matching_items.empty:
                    pref_parts.append(matching_items.iloc[0]['combined_text'])
                    
        query_text = " ".join(pref_parts)
        
        # Handle empty preference profiles
        if not query_text.strip():
            logger.warning("Empty preference profile provided. Returning empty list.")
            return []
            
        # 2. Vectorize the search query
        query_vector = self.vectorizer.transform([query_text])
        
        # 3. Compute similarities
        scores = self._get_similarity_scores(query_vector)
        
        # Avoid recommending the items explicitly listed in 'similar_to'
        sorted_indices = np.argsort(scores)[::-1]
        
        recommendations = []
        for rank_idx in sorted_indices:
            cand_id = self.idx_to_id[rank_idx]
            cand_row = self.items_df.iloc[rank_idx]
            cand_title = cand_row[self.title_col]
            
            # Skip if exact matching title in liked list
            if any(lt.lower() in cand_title.lower() for lt in liked_titles):
                continue
                
            score = float(scores[rank_idx])
            
            # Check genres matching preferences
            cand_genres = set(str(cand_row[self.genre_col]).split('|'))
            pref_genres = set(preferences.get('genres', []))
            matched_genres = list(pref_genres.intersection(cand_genres))
            
            recommendations.append({
                "item_id": int(cand_id),
                "title": cand_title,
                "genres": cand_row[self.genre_col],
                "score": score,
                "evidence": {
                    "content_score": round(score, 4),
                    "collaborative_score": 0.0,
                    "preference_score": round(score, 4),
                    "final_score": round(score, 4),
                    "matched_genres": matched_genres,
                    "similar_to": liked_titles
                }
            })
            
            if len(recommendations) >= top_k:
                break
                
        return recommendations
