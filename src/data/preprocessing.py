import os
import re
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class DataPreprocessor:
    """Preprocesses raw movie and book datasets into structured, normalized features."""
    
    def __init__(self, data_dir="data"):
        self.data_dir = os.path.abspath(data_dir)
        self.processed_dir = os.path.join(self.data_dir, "processed")
        os.makedirs(self.processed_dir, exist_ok=True)

    def clean_text(self, text):
        """Standard text cleaning: lowercase, remove punctuation, strip whitespaces."""
        if pd.isna(text) or not isinstance(text, str):
            return ""
        # Lowercase
        text = text.lower()
        # Remove special characters/punctuation except letters and numbers
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def preprocess_movies(self, movies_df, tags_df):
        """
        Preprocesses movie metadata.
        Aggregates movie tags from tags_df and appends them to genres to create 'combined_text'.
        """
        logger.info("Preprocessing movie dataset...")
        movies = movies_df.copy()
        
        # 1. Handle missing values
        movies['title'] = movies['title'].fillna("Unknown Movie")
        movies['genres'] = movies['genres'].fillna("None")
        
        # 2. Extract tags for each movie
        tags = tags_df.copy()
        tags['tag'] = tags['tag'].astype(str).apply(self.clean_text)
        
        # Group tags by movieId and join with spaces
        grouped_tags = tags.groupby('movieId')['tag'].apply(lambda x: ' '.join(set(x))).reset_index()
        grouped_tags.rename(columns={'tag': 'user_tags'}, inplace=True)
        
        # Merge tags into movies
        movies = pd.merge(movies, grouped_tags, on='movieId', how='left')
        movies['user_tags'] = movies['user_tags'].fillna("")
        
        # 3. Create cleaned genre features
        movies['cleaned_genres'] = movies['genres'].apply(lambda x: x.replace('|', ' ').lower())
        
        # 4. Generate combined text column for TF-IDF Vectorization
        # Combined text structure: Title + cleaned genres + tags
        movies['combined_text'] = (
            movies['title'].apply(self.clean_text) + " " +
            movies['cleaned_genres'] + " " +
            movies['user_tags']
        )
        
        # Remove double spaces
        movies['combined_text'] = movies['combined_text'].apply(lambda x: re.sub(r'\s+', ' ', x).strip())
        
        # Save processed movie metadata
        processed_path = os.path.join(self.processed_dir, "movies_processed.csv")
        movies.to_csv(processed_path, index=False)
        logger.info(f"Processed movies saved to {processed_path}. Shape: {movies.shape}")
        
        return movies

    def preprocess_books(self, books_df):
        """
        Preprocesses book metadata.
        Combines title, authors, and genres into 'combined_text'.
        """
        logger.info("Preprocessing book dataset...")
        books = books_df.copy()
        
        # 1. Clean fields
        books['title'] = books['title'].fillna("Unknown Book")
        books['authors'] = books['authors'].fillna("Unknown Author")
        books['genres'] = books['genres'].fillna("Fiction")
        
        # 2. Format genres (space-separated and lower)
        books['cleaned_genres'] = books['genres'].apply(lambda x: x.replace('|', ' ').lower())
        books['cleaned_authors'] = books['authors'].apply(self.clean_text)
        
        # 3. Generate combined text column for TF-IDF Vectorization
        # Combined text structure: Title + Authors + Genres
        books['combined_text'] = (
            books['title'].apply(self.clean_text) + " " +
            books['cleaned_authors'] + " " +
            books['cleaned_genres']
        )
        books['combined_text'] = books['combined_text'].apply(lambda x: re.sub(r'\s+', ' ', x).strip())
        
        # Save processed book metadata
        processed_path = os.path.join(self.processed_dir, "books_processed.csv")
        books.to_csv(processed_path, index=False)
        logger.info(f"Processed books saved to {processed_path}. Shape: {books.shape}")
        
        return books

    def split_ratings_user_aware(self, ratings_df, split_ratio=0.8, is_temporal=True):
        """
        Splits ratings dataset into train (earlier) and test (later) subsets per user.
        If 'timestamp' is not present, splits randomly per user (retaining user awareness).
        """
        logger.info(f"Splitting ratings (user-aware, temporal={is_temporal})...")
        df = ratings_df.copy()
        
        # Detect column names (userId/user_id, movieId/book_id)
        user_col = 'userId' if 'userId' in df.columns else 'user_id'
        item_col = 'movieId' if 'movieId' in df.columns else 'book_id'
        time_col = 'timestamp' if 'timestamp' in df.columns else None
        
        train_records = []
        test_records = []
        
        # Group by user to ensure every user has representation in train and test if possible
        for uid, user_data in df.groupby(user_col):
            n_ratings = len(user_data)
            
            # If user has only 1 rating, put it in train
            if n_ratings <= 1:
                train_records.append(user_data)
                continue
            
            # Determine split index
            split_idx = int(np.ceil(n_ratings * split_ratio))
            # Edge case protection
            if split_idx == n_ratings:
                split_idx = n_ratings - 1
                
            # Sort data
            if is_temporal and time_col is not None:
                # Temporal split: sort by timestamp
                user_data_sorted = user_data.sort_values(by=time_col)
            else:
                # Random split (shuffle with seed to ensure reproducibility)
                user_data_sorted = user_data.sample(frac=1, random_state=42)
                
            train_records.append(user_data_sorted.iloc[:split_idx])
            test_records.append(user_data_sorted.iloc[split_idx:])
            
        train_df = pd.concat(train_records, ignore_index=True)
        test_df = pd.concat(test_records, ignore_index=True)
        
        logger.info(f"Split complete. Train shape: {train_df.shape}, Test shape: {test_df.shape}")
        return train_df, test_df

if __name__ == "__main__":
    from src.data.dataset import DatasetManager
    
    # Initialize Preprocessor
    preprocessor = DataPreprocessor()
    manager = DatasetManager()
    
    # Check if files exist or build them
    try:
        manager.prepare_movielens()
        movies_df, ratings_df, tags_df = manager.get_raw_movie_data()
    except Exception:
        manager.generate_fallback_data()
        movies_df, ratings_df, tags_df = manager.get_raw_movie_data()
        
    try:
        manager.prepare_goodbooks()
        books_df, book_ratings_df = manager.create_book_subset(user_limit=2000)
    except Exception:
        books_df, book_ratings_df = manager.get_raw_book_data()
        
    # Process movies
    processed_movies = preprocessor.preprocess_movies(movies_df, tags_df)
    movie_train, movie_test = preprocessor.split_ratings_user_aware(ratings_df, is_temporal=True)
    
    movie_train.to_csv(os.path.join(preprocessor.processed_dir, "movie_ratings_train.csv"), index=False)
    movie_test.to_csv(os.path.join(preprocessor.processed_dir, "movie_ratings_test.csv"), index=False)
    
    # Process books
    processed_books = preprocessor.preprocess_books(books_df)
    book_train, book_test = preprocessor.split_ratings_user_aware(book_ratings_df, is_temporal=False)
    
    book_train.to_csv(os.path.join(preprocessor.processed_dir, "book_ratings_train.csv"), index=False)
    book_test.to_csv(os.path.join(preprocessor.processed_dir, "book_ratings_test.csv"), index=False)
    
    print("Preprocessing successfully run and saved.")
