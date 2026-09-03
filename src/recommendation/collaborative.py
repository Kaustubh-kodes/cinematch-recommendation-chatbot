import logging
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class CollaborativeRecommender:
    """
    Collaborative Filtering Recommender implementing two competing approaches:
    1. Item-Item Collaborative Filtering (Neighborhood-based)
    2. SVD Matrix Factorization (Latent Factor model)
    """
    
    def __init__(self, user_col='userId', item_col='movieId', rating_col='rating', num_factors=30):
        self.user_col = user_col
        self.item_col = item_col
        self.rating_col = rating_col
        self.num_factors = num_factors
        
        # Mappings
        self.user_to_idx = {}
        self.idx_to_user = {}
        self.item_to_idx = {}
        self.idx_to_item = {}
        
        # Data and Matrices
        self.ratings_df = None
        self.user_item_matrix = None  # Sparse CSR matrix
        self.item_similarity_matrix = None  # Item-Item Cosine Similarity matrix
        
        # SVD Components
        self.user_means = None
        self.svd_predicted_ratings = None

    def fit(self, ratings_df):
        """Fits both Item-Item CF and SVD models on the ratings dataframe."""
        logger.info(f"Fitting Collaborative Filtering models on {len(ratings_df)} ratings...")
        self.ratings_df = ratings_df.copy()
        
        # 1. Create unique ID mappings
        unique_users = sorted(self.ratings_df[self.user_col].unique())
        unique_items = sorted(self.ratings_df[self.item_col].unique())
        
        self.user_to_idx = {uid: idx for idx, uid in enumerate(unique_users)}
        self.idx_to_user = {idx: uid for idx, uid in enumerate(unique_users)}
        self.item_to_idx = {iid: idx for idx, iid in enumerate(unique_items)}
        self.idx_to_item = {idx: iid for idx, iid in enumerate(unique_items)}
        
        n_users = len(unique_users)
        n_items = len(unique_items)
        logger.info(f"Dimensions: Users={n_users}, Items={n_items}")
        
        # 2. Build Sparse User-Item Matrix
        rows = self.ratings_df[self.user_col].map(self.user_to_idx).values
        cols = self.ratings_df[self.item_col].map(self.item_to_idx).values
        ratings = self.ratings_df[self.rating_col].values
        
        self.user_item_matrix = csr_matrix((ratings, (rows, cols)), shape=(n_users, n_items))
        
        # 3. Train Item-Item Collaborative Filtering (Cosine Similarity)
        # Cosine similarity of items (columns of the user-item matrix)
        logger.info("Computing Item-Item Cosine Similarity Matrix...")
        # Shape: (n_items, n_items)
        self.item_similarity_matrix = cosine_similarity(self.user_item_matrix.T, dense_output=True)
        # Fill diagonal with 0 to prevent recommending the same item
        np.fill_diagonal(self.item_similarity_matrix, 0)
        
        # 4. Train SVD Matrix Factorization
        logger.info("Computing SVD Decomposition...")
        # Make a dense copy for SVD normalization
        dense_matrix = self.user_item_matrix.toarray().astype(float)
        
        # Zero ratings mean unrated; calculate user means only over rated items
        self.user_means = np.zeros(n_users)
        for u_idx in range(n_users):
            user_ratings = dense_matrix[u_idx]
            rated_indices = user_ratings > 0
            if np.any(rated_indices):
                self.user_means[u_idx] = user_ratings[rated_indices].mean()
                # Subtract user mean from rated items to center ratings
                dense_matrix[u_idx, rated_indices] -= self.user_means[u_idx]
        
        # Run SVD
        # k (num_factors) must be less than min(n_users, n_items)
        k = min(self.num_factors, n_users - 1, n_items - 1)
        if k < 1:
            k = 1
        
        try:
            # We use scipy svds
            u, s, vt = svds(dense_matrix, k=k)
            s_diag = np.diag(s)
            
            # Reconstruct prediction matrix
            reconstructed = np.dot(np.dot(u, s_diag), vt)
            
            # Add user means back
            self.svd_predicted_ratings = reconstructed + self.user_means[:, np.newaxis]
        except Exception as e:
            logger.error(f"SVD decomposition failed: {e}. Falling back to default user means.")
            self.svd_predicted_ratings = np.tile(self.user_means[:, np.newaxis], (1, n_items))
            
        logger.info("Collaborative Filtering fit complete.")
        return self

    def predict_rating_item_item(self, user_id, item_id, k_neighbors=30):
        """Predicts a rating using Item-Item similarity based on user's history."""
        # Check cold start
        if user_id not in self.user_to_idx or item_id not in self.item_to_idx:
            return 3.5  # Neutral fallback
            
        u_idx = self.user_to_idx[user_id]
        i_idx = self.item_to_idx[item_id]
        
        # Get items rated by user
        user_ratings = self.user_item_matrix[u_idx].toarray().ravel()
        rated_indices = np.where(user_ratings > 0)[0]
        
        if len(rated_indices) == 0:
            return 3.5  # No rating history
            
        # Get similarities of target item to items rated by user
        sim_scores = self.item_similarity_matrix[i_idx, rated_indices]
        
        # Top-k similar neighbors
        top_indices = np.argsort(sim_scores)[::-1][:k_neighbors]
        
        top_sims = sim_scores[top_indices]
        top_ratings = user_ratings[rated_indices[top_indices]]
        
        sim_sum = np.sum(np.abs(top_sims))
        if sim_sum == 0:
            # If no items are similar, return user mean rating
            rated_vals = user_ratings[rated_indices]
            return float(rated_vals.mean())
            
        predicted = np.dot(top_sims, top_ratings) / sim_sum
        return float(predicted)

    def predict_rating_svd(self, user_id, item_id):
        """Predicts rating using reconstructed SVD matrix."""
        if user_id not in self.user_to_idx or item_id not in self.item_to_idx:
            return 3.5
            
        u_idx = self.user_to_idx[user_id]
        i_idx = self.item_to_idx[item_id]
        return float(self.svd_predicted_ratings[u_idx, i_idx])

    def predict_all_ratings_item_item(self, user_id):
        """Predicts ratings for all items for user_id in a vectorized way."""
        if user_id not in self.user_to_idx:
            return np.full(len(self.idx_to_item), 3.5)
            
        u_idx = self.user_to_idx[user_id]
        user_ratings = self.user_item_matrix[u_idx].toarray().ravel()
        rated_mask = user_ratings > 0
        
        if not np.any(rated_mask):
            return np.full(len(self.idx_to_item), 3.5)
            
        S_rated = self.item_similarity_matrix[:, rated_mask]  # Shape: (n_items, n_rated)
        ratings_rated = user_ratings[rated_mask]  # Shape: (n_rated,)
        
        k = min(30, S_rated.shape[1])
        if k > 0:
            partition_idx = np.argpartition(S_rated, -k, axis=1)[:, -k:]
            row_indices = np.arange(S_rated.shape[0])[:, np.newaxis]
            S_top_k = np.zeros_like(S_rated)
            S_top_k[row_indices, partition_idx] = S_rated[row_indices, partition_idx]
        else:
            S_top_k = S_rated
            
        numerator = S_top_k.dot(ratings_rated)
        denominator = np.sum(np.abs(S_top_k), axis=1)
        
        user_mean = ratings_rated.mean()
        pred_ratings = np.zeros_like(numerator)
        zero_denom = denominator == 0
        pred_ratings[~zero_denom] = numerator[~zero_denom] / denominator[~zero_denom]
        pred_ratings[zero_denom] = user_mean
        
        return pred_ratings

    def recommend_collaborative(self, user_id, method='svd', top_k=10, items_metadata_df=None, title_col='title', genre_col='genres'):
        """
        Generates recommendations of unrated items for user_id.
        Excludes items already rated by this user.
        """
        if self.user_item_matrix is None:
            raise ValueError("Recommender has not been fitted. Call fit() first.")
            
        if user_id not in self.user_to_idx:
            logger.warning(f"User ID {user_id} not found in collaborative model. Returning cold start list.")
            return []
            
        u_idx = self.user_to_idx[user_id]
        
        # Get items already rated by user
        user_ratings = self.user_item_matrix[u_idx].toarray().ravel()
        unrated_indices = np.where(user_ratings == 0)[0]
        
        if len(unrated_indices) == 0:
            logger.warning(f"User {user_id} has rated all items! Returning empty list.")
            return []
            
        scores = []
        if method == 'svd':
            # Fast lookup from reconstructed SVD matrix
            scores = self.svd_predicted_ratings[u_idx, unrated_indices]
        elif method == 'item_item':
            # Fast vectorized prediction for all items
            all_ratings = self.predict_all_ratings_item_item(user_id)
            scores = all_ratings[unrated_indices]
        else:
            raise ValueError(f"Unknown collaborative method: {method}")
            
        # Sort unrated items by predicted score
        sorted_rel_indices = np.argsort(scores)[::-1]
        
        recommendations = []
        for idx in sorted_rel_indices:
            i_idx = unrated_indices[idx]
            cand_id = self.idx_to_item[i_idx]
            pred_score = float(scores[idx])
            
            # Normalize prediction to 0-1 scale for standard output formatting (ratings are typically 1-5 scale)
            norm_score = max(0.0, min(1.0, (pred_score - 1.0) / 4.0))
            
            item_title = f"Item {cand_id}"
            item_genres = "None"
            
            # Find item details from metadata if provided
            if items_metadata_df is not None:
                item_row = items_metadata_df[items_metadata_df[self.item_col] == cand_id]
                if not item_row.empty:
                    item_title = item_row.iloc[0][title_col]
                    item_genres = item_row.iloc[0][genre_col]
            
            recommendations.append({
                "item_id": int(cand_id),
                "title": item_title,
                "genres": item_genres,
                "score": norm_score,  # Normalized score
                "raw_rating": round(pred_score, 2),  # Raw scale prediction (1-5)
                "evidence": {
                    "content_score": 0.0,
                    "collaborative_score": round(norm_score, 4),
                    "preference_score": 0.0,
                    "final_score": round(norm_score, 4),
                    "matched_genres": [],
                    "similar_to": []
                }
            })
            
            if len(recommendations) >= top_k:
                break
                
        return recommendations
