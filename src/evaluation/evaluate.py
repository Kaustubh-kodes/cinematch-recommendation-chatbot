import os
import logging
import numpy as np
import pandas as pd
from src.recommendation.hybrid import HybridRecommender
from src.evaluation.metrics import precision_at_k, recall_at_k, ndcg_at_k

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RecommenderEvaluator:
    """Runs comparative evaluation across baseline, content-based, collaborative, and hybrid engines."""
    
    def __init__(self, data_dir="data"):
        self.data_dir = os.path.abspath(data_dir)
        self.processed_dir = os.path.join(self.data_dir, "processed")

    def run_evaluation(self, media_type='movie', sample_size=100, k=10):
        """Runs offline comparative evaluation for the specified media type."""
        logger.info(f"Starting comparative evaluation for {media_type.upper()}S (K={k}, sample_size={sample_size})...")
        
        # 1. Setup column mappings and file names
        if media_type == 'movie':
            id_col, user_col, title_col, genre_col, rating_col = 'movieId', 'userId', 'title', 'genres', 'rating'
            train_file = "movie_ratings_train.csv"
            test_file = "movie_ratings_test.csv"
            meta_file = "movies_processed.csv"
            num_factors = 30
        else:
            id_col, user_col, title_col, genre_col, rating_col = 'book_id', 'user_id', 'title', 'genres', 'rating'
            train_file = "book_ratings_train.csv"
            test_file = "book_ratings_test.csv"
            meta_file = "books_processed.csv"
            num_factors = 20
            
        # 2. Load datasets
        train_df = pd.read_csv(os.path.join(self.processed_dir, train_file))
        test_df = pd.read_csv(os.path.join(self.processed_dir, test_file))
        meta_df = pd.read_csv(os.path.join(self.processed_dir, meta_file))
        
        # 3. Fit Hybrid Recommender (which internalizes Content-Based and Collaborative)
        hybrid_engine = HybridRecommender(
            id_col=id_col, user_col=user_col, title_col=title_col, 
            genre_col=genre_col, rating_col=rating_col, num_factors=num_factors
        )
        hybrid_engine.fit(meta_df, train_df)
        
        # Get sub-recommenders for independent runs
        content_rec = hybrid_engine.content_rec
        collab_rec = hybrid_engine.collab_rec
        
        # 4. Find evaluation users (users who exist in both train and test)
        train_users = set(train_df[user_col].unique())
        test_users = set(test_df[user_col].unique())
        eval_users = list(train_users.intersection(test_users))
        
        if len(eval_users) == 0:
            logger.error("No overlap between train and test users. Evaluation cannot proceed.")
            return None
            
        # Select user sample
        np.random.seed(42)
        if len(eval_users) > sample_size:
            eval_users = np.random.choice(eval_users, size=sample_size, replace=False)
            
        logger.info(f"Evaluating over {len(eval_users)} test users...")
        
        # Initialize metrics accumulator
        models = ['Popularity', 'Content-Based', 'Collaborative (Item-Item)', 'Collaborative (SVD)', 'Hybrid']
        results = {m: {'precision': [], 'recall': [], 'ndcg': []} for m in models}
        
        # 5. Loop over users
        for u_id in eval_users:
            # Get user's relevant test items (rating >= 4.0 is considered "relevant")
            user_test_ratings = test_df[test_df[user_col] == u_id]
            relevant_test_items = set(user_test_ratings[user_test_ratings[rating_col] >= 4.0][id_col].values)
            
            # Skip if user has no relevant items in test set (cannot compute recall/ndcg fairly)
            if not relevant_test_items:
                continue
                
            # Get user's train rating history (for content profiles)
            user_train_ratings = train_df[train_df[user_col] == u_id]
            liked_train_items = user_train_ratings[user_train_ratings[rating_col] >= 4.0][id_col].values
            
            # Build search preferences for Content-Based and Hybrid
            preferences = {'genres': [], 'similar_to': []}
            if len(liked_train_items) > 0:
                liked_meta = meta_df[meta_df[id_col].isin(liked_train_items)]
                # Add top liked genre tags
                all_genres = []
                for g in liked_meta[genre_col].fillna(""):
                    all_genres.extend(str(g).split('|'))
                if all_genres:
                    # Top 3 most frequent genres
                    genre_series = pd.Series(all_genres).value_counts()
                    preferences['genres'] = list(genre_series.head(3).index)
                # Add titles for similarity matching
                preferences['similar_to'] = list(liked_meta[title_col].head(3).values)
                
            # Generate recommendations for each model
            # A. Popularity Baseline
            pop_recs = [r['item_id'] for r in hybrid_engine._recommend_popularity_baseline(top_k=k)]
            
            # B. Content-Based Recommender
            # (If preferences are empty, content returns empty; we evaluate content capability)
            content_recs = [r['item_id'] for r in content_rec.recommend_by_profile(preferences, top_k=k)]
            
            # C. Collaborative Item-Item Recommender
            ii_recs = [r['item_id'] for r in collab_rec.recommend_collaborative(
                user_id=u_id, method='item_item', top_k=k, items_metadata_df=meta_df
            )]
            
            # D. Collaborative SVD Recommender
            svd_recs = [r['item_id'] for r in collab_rec.recommend_collaborative(
                user_id=u_id, method='svd', top_k=k, items_metadata_df=meta_df
            )]
            
            # E. Hybrid Recommender
            hybrid_recs = [r['item_id'] for r in hybrid_engine.recommend_hybrid(
                user_id=u_id, preferences=preferences, method='svd', top_k=k
            )]
            
            # Calculate metrics
            recs_dict = {
                'Popularity': pop_recs,
                'Content-Based': content_recs,
                'Collaborative (Item-Item)': ii_recs,
                'Collaborative (SVD)': svd_recs,
                'Hybrid': hybrid_recs
            }
            
            for m_name, rec_ids in recs_dict.items():
                results[m_name]['precision'].append(precision_at_k(rec_ids, relevant_test_items, k=k))
                results[m_name]['recall'].append(recall_at_k(rec_ids, relevant_test_items, k=k))
                results[m_name]['ndcg'].append(ndcg_at_k(rec_ids, relevant_test_items, k=k))
                
        # 6. Aggregate averages
        report_data = []
        for m_name in models:
            avg_prec = np.mean(results[m_name]['precision']) if results[m_name]['precision'] else 0.0
            avg_rec = np.mean(results[m_name]['recall']) if results[m_name]['recall'] else 0.0
            avg_ndcg = np.mean(results[m_name]['ndcg']) if results[m_name]['ndcg'] else 0.0
            
            report_data.append({
                "Model": m_name,
                f"Precision@{k}": round(avg_prec, 4),
                f"Recall@{k}": round(avg_rec, 4),
                f"NDCG@{k}": round(avg_ndcg, 4)
            })
            
        report_df = pd.DataFrame(report_data)
        
        # 7. Print and return
        print(f"\n=== Offline Evaluation Results for {media_type.upper()}S ===")
        print(report_df.to_string(index=False))
        print("====================================================\n")
        
        return report_df

if __name__ == "__main__":
    evaluator = RecommenderEvaluator()
    # Evaluate movies (fast sample of 50 users)
    movie_results = evaluator.run_evaluation(media_type='movie', sample_size=50)
    # Evaluate books
    book_results = evaluator.run_evaluation(media_type='book', sample_size=50)
