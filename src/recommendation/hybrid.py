import logging
import pandas as pd
import numpy as np
from src.recommendation.content_based import ContentBasedRecommender
from src.recommendation.collaborative import CollaborativeRecommender

logger = logging.getLogger(__name__)

class HybridRecommender:
    """
    Hybrid Recommender combining Content-Based Filtering, Collaborative Filtering (SVD/Item-Item),
    and Explicit User Preferences, with robust cold-start fallbacks and modular weights.
    """
    
    def __init__(self, id_col='movieId', user_col='userId', title_col='title', genre_col='genres', rating_col='rating', num_factors=30):
        self.id_col = id_col
        self.user_col = user_col
        self.title_col = title_col
        self.genre_col = genre_col
        self.rating_col = rating_col
        
        # Sub-recommenders
        self.content_rec = ContentBasedRecommender(id_col=id_col, title_col=title_col, genre_col=genre_col)
        self.collab_rec = CollaborativeRecommender(user_col=user_col, item_col=id_col, rating_col=rating_col, num_factors=num_factors)
        
        # Popularity Baseline Cache
        self.popularity_scores = {}
        self.global_average_rating = 3.5

    def fit(self, items_df, ratings_df):
        """Fits both content-based and collaborative filtering modules, and computes popularity baseline."""
        logger.info("Fitting Hybrid Recommender...")
        
        # Fit sub-models
        self.content_rec.fit(items_df)
        self.collab_rec.fit(ratings_df)
        
        # Compute popularity baseline
        logger.info("Computing popularity scores for baseline...")
        rating_counts = ratings_df.groupby(self.id_col).size()
        rating_averages = ratings_df.groupby(self.id_col)[self.rating_col].mean()
        self.global_average_rating = ratings_df[self.rating_col].mean()
        
        # Popularity formula: log(1 + count) * average_rating
        raw_pop = {}
        for item_id in items_df[self.id_col]:
            count = rating_counts.get(item_id, 0)
            avg_rating = rating_averages.get(item_id, self.global_average_rating)
            raw_pop[item_id] = np.log1p(count) * avg_rating
            
        # Normalize popularity scores to 0-1
        max_pop = max(raw_pop.values()) if raw_pop else 1.0
        min_pop = min(raw_pop.values()) if raw_pop else 0.0
        pop_range = max_pop - min_pop if max_pop - min_pop > 0 else 1.0
        
        self.popularity_scores = {iid: (val - min_pop) / pop_range for iid, val in raw_pop.items()}
        logger.info("Hybrid Recommender fit complete.")
        return self

    def recommend_hybrid(self, user_id=None, item_id=None, preferences=None, method='svd', top_k=10, weights=None):
        """
        Generates hybrid recommendations by combining content, collaborative, and preference signals.
        weights: dict with 'content', 'collaborative', 'preference' summing to 1.0.
        """
        # Default Weights
        if weights is None:
            weights = {'content': 0.4, 'collaborative': 0.4, 'preference': 0.2}
            
        # Normalize weights to make sure they sum to 1.0
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
            
        # Check if user is known
        is_known_user = user_id is not None and user_id in self.collab_rec.user_to_idx
        
        # CASE 1: Absolute Cold Start (No User ID, No item ID, No Preferences)
        if not is_known_user and item_id is None and (preferences is None or not preferences):
            logger.info("Cold Start: Returning Popularity Baseline recommendations.")
            return self._recommend_popularity_baseline(top_k)
            
        # CASE 2: New User with explicit preferences (No rating history)
        if not is_known_user and item_id is None and preferences is not None:
            logger.info(f"Cold Start: New user with preferences. Running Content Preference recommendations.")
            # Retrieve recommendations based on profile query
            content_recs = self.content_rec.recommend_by_profile(preferences, top_k=top_k * 2)
            
            # Combine content similarity score with popularity boost
            hybrid_recs = []
            for r in content_recs:
                iid = r['item_id']
                content_score = r['score']
                pop_score = self.popularity_scores.get(iid, 0.0)
                
                # Hybridize: 70% content match, 30% popularity signal
                final_score = 0.7 * content_score + 0.3 * pop_score
                
                r['score'] = final_score
                r['evidence']['content_score'] = round(content_score, 4)
                r['evidence']['collaborative_score'] = round(pop_score, 4)  # Treat popularity as collab signal proxy in cold start
                r['evidence']['final_score'] = round(final_score, 4)
                hybrid_recs.append(r)
                
            hybrid_recs = sorted(hybrid_recs, key=lambda x: x['score'], reverse=True)[:top_k]
            return hybrid_recs

        # CASE 3: Standard Hybrid Recommendation for Existing Users
        logger.info(f"Generating Hybrid recommendations for User: {user_id}, Item Context: {item_id}, Preferences: {preferences}")
        
        # 1. Identify items the user has already rated (exclude from recommendations)
        rated_item_ids = set()
        if is_known_user:
            u_idx = self.collab_rec.user_to_idx[user_id]
            user_ratings = self.collab_rec.user_item_matrix[u_idx].toarray().ravel()
            rated_indices = np.where(user_ratings > 0)[0]
            rated_item_ids = {self.collab_rec.idx_to_item[idx] for idx in rated_indices}
            
        # 2. Get items metadata dataframe
        items_df = self.content_rec.items_df.copy()
        
        # 3. Pre-calculate content similarity scores if item context is provided
        item_similarities = {}
        if item_id is not None and item_id in self.content_rec.id_to_idx:
            item_idx = self.content_rec.id_to_idx[item_id]
            query_vec = self.content_rec.tfidf_matrix[item_idx]
            sims = self.content_rec._get_similarity_scores(query_vec)
            item_similarities = {self.content_rec.idx_to_id[i]: sims[i] for i in range(len(sims))}
        elif is_known_user:
            u_ratings = self.collab_rec.ratings_df[
                (self.collab_rec.ratings_df[self.user_col] == user_id) & 
                (self.collab_rec.ratings_df[self.rating_col] >= 4.0)
            ]
            if not u_ratings.empty:
                highly_rated_ids = u_ratings[self.id_col].values
                valid_indices = [self.content_rec.id_to_idx[iid] for iid in highly_rated_ids if iid in self.content_rec.id_to_idx]
                if valid_indices:
                    avg_vec = self.content_rec.tfidf_matrix[valid_indices].mean(axis=0)
                    avg_vec = np.asarray(avg_vec)
                    sims = self.content_rec._get_similarity_scores(avg_vec)
                    item_similarities = {self.content_rec.idx_to_id[i]: sims[i] for i in range(len(sims))}

        # Exclusions list
        exclude_ids = rated_item_ids.copy()
        if item_id is not None:
            exclude_ids.add(item_id)
            
        # Apply genre exclusions (avoid list)
        avoid_genres = set(preferences.get('avoid', [])) if preferences is not None else set()
        if avoid_genres:
            genre_mask = items_df[self.genre_col].fillna("").apply(lambda x: len(avoid_genres.intersection(str(x).split('|'))) > 0)
            candidates_df = items_df[~genre_mask & ~items_df[self.id_col].isin(exclude_ids)].copy()
        else:
            candidates_df = items_df[~items_df[self.id_col].isin(exclude_ids)].copy()
            
        if candidates_df.empty:
            return []
            
        # 4. Vectorized Scoring
        # A. Content Scores
        candidates_df['content_score'] = candidates_df[self.id_col].map(item_similarities).fillna(0.0)
        
        # B. Collaborative Scores
        pred_ratings = np.full(len(candidates_df), 3.5)
        if is_known_user:
            collab_indices = [self.collab_rec.item_to_idx[iid] if iid in self.collab_rec.item_to_idx else -1 for iid in candidates_df[self.id_col]]
            collab_indices = np.array(collab_indices)
            valid_mask = collab_indices != -1
            
            if method == 'svd':
                pred_ratings = np.full(len(candidates_df), self.collab_rec.user_means[u_idx])
                pred_ratings[valid_mask] = self.collab_rec.svd_predicted_ratings[u_idx, collab_indices[valid_mask]]
            else:
                all_pred = self.collab_rec.predict_all_ratings_item_item(user_id)
                pred_ratings = np.full(len(candidates_df), 3.5)
                pred_ratings[valid_mask] = all_pred[collab_indices[valid_mask]]
                
            candidates_df['collab_score'] = np.clip((pred_ratings - 1.0) / 4.0, 0.0, 1.0)
        else:
            candidates_df['collab_score'] = candidates_df[self.id_col].map(self.popularity_scores).fillna(0.0)
            
        # C. Preference Scores
        pref_genres = set(preferences.get('genres', [])) if preferences is not None else set()
        if pref_genres:
            match_counts = candidates_df[self.genre_col].fillna("").apply(lambda x: len(pref_genres.intersection(str(x).split('|'))))
            candidates_df['pref_score'] = match_counts / len(pref_genres)
        else:
            candidates_df['pref_score'] = 0.0
            
        # Hard filter: minimum rating check
        min_rating = preferences.get('minimum_rating', 0.0) if preferences is not None else 0.0
        if min_rating > 0.0:
            if is_known_user:
                candidates_df['rating_for_filter'] = pred_ratings
            else:
                rating_averages = self.collab_rec.ratings_df.groupby(self.id_col)[self.rating_col].mean()
                candidates_df['rating_for_filter'] = candidates_df[self.id_col].map(rating_averages).fillna(self.global_average_rating)
                
            candidates_df = candidates_df[candidates_df['rating_for_filter'] >= min_rating]
            
        if candidates_df.empty:
            return []
            
        # Calculate final combined score
        candidates_df['final_score'] = (
            weights['content'] * candidates_df['content_score'] +
            weights['collaborative'] * candidates_df['collab_score'] +
            weights['preference'] * candidates_df['pref_score']
        )
        
        # Sort and take top_k
        candidates_df = candidates_df.sort_values(by='final_score', ascending=False).head(top_k)
        
        similar_to_list = []
        if item_id is not None:
            ref_title = items_df[items_df[self.id_col] == item_id].iloc[0][self.title_col]
            similar_to_list.append(ref_title)
        elif is_known_user and 'highly_rated_ids' in locals() and len(highly_rated_ids) > 0:
            top_rated_id = highly_rated_ids[0]
            matching_rows = items_df[items_df[self.id_col] == top_rated_id]
            if not matching_rows.empty:
                similar_to_list.append(matching_rows.iloc[0][self.title_col])
                
        # 5. Format Output
        recommendations = []
        for idx, row in candidates_df.iterrows():
            iid = row[self.id_col]
            cand_genres = set(str(row[self.genre_col]).split('|'))
            matched = list(pref_genres.intersection(cand_genres))
            
            recommendations.append({
                "item_id": int(iid),
                "title": row[self.title_col],
                "genres": row[self.genre_col],
                "score": float(row['final_score']),
                "evidence": {
                    "content_score": round(float(row['content_score']), 4),
                    "collaborative_score": round(float(row['collab_score']), 4),
                    "preference_score": round(float(row['pref_score']), 4),
                    "final_score": round(float(row['final_score']), 4),
                    "matched_genres": matched,
                    "similar_to": similar_to_list
                }
            })
            
        return recommendations

    def _recommend_popularity_baseline(self, top_k=10):
        """Generates popularity + quality baseline recommendations."""
        items_df = self.content_rec.items_df
        recommendations = []
        
        # Sort items by their pre-calculated popularity scores
        sorted_items = sorted(self.popularity_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        for iid, score in sorted_items:
            item_row = items_df[items_df[self.id_col] == iid].iloc[0]
            recommendations.append({
                "item_id": int(iid),
                "title": item_row[self.title_col],
                "genres": item_row[self.genre_col],
                "score": score,
                "evidence": {
                    "content_score": 0.0,
                    "collaborative_score": round(score, 4),  # Popularity acts as basic collab signal
                    "preference_score": 0.0,
                    "final_score": round(score, 4),
                    "matched_genres": [],
                    "similar_to": []
                }
            })
            
        return recommendations
