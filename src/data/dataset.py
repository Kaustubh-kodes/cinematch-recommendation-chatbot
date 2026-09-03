import os
import zipfile
import urllib.request
import logging
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
MOVIELENS_URL = "http://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
GOODBOOKS_BOOKS_URL = "https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/books.csv"
GOODBOOKS_RATINGS_URL = "https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/ratings.csv"
GOODBOOKS_BOOK_TAGS_URL = "https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/book_tags.csv"
GOODBOOKS_TAGS_URL = "https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/tags.csv"

class DatasetManager:
    """Manages downloading, extracting, caching, and loading MovieLens and Goodbooks-10k datasets."""
    
    def __init__(self, data_dir="data"):
        self.data_dir = os.path.abspath(data_dir)
        self.raw_dir = os.path.join(self.data_dir, "raw")
        self.processed_dir = os.path.join(self.data_dir, "processed")
        
        # Ensure directories exist
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)

    def _download_file(self, url, dest_path):
        """Downloads a file with basic progress logging."""
        if os.path.exists(dest_path):
            logger.info(f"File already exists: {dest_path}. Skipping download.")
            return True
        
        logger.info(f"Downloading {url} to {dest_path}...")
        try:
            # Set a user-agent to avoid HTTP blocks
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req) as response, open(dest_path, 'wb') as out_file:
                # Copy network stream in chunks
                chunk_size = 1024 * 1024  # 1MB
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    out_file.write(chunk)
            logger.info(f"Successfully downloaded to {dest_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return False

    def prepare_movielens(self):
        """Downloads and extracts MovieLens dataset."""
        zip_path = os.path.join(self.raw_dir, "ml-latest-small.zip")
        extract_dir = os.path.join(self.raw_dir, "ml-latest-small")
        
        # Download
        success = self._download_file(MOVIELENS_URL, zip_path)
        if not success:
            logger.warning("MovieLens download failed. Attempting to load existing file if available.")
            
        # Extract
        if os.path.exists(zip_path) and not os.path.exists(extract_dir):
            logger.info(f"Extracting {zip_path}...")
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.raw_dir)
                logger.info("Extraction complete.")
            except Exception as e:
                logger.error(f"Failed to extract zip file: {e}")
        
        # Check files
        expected_files = ["movies.csv", "ratings.csv", "tags.csv"]
        src_path = os.path.join(self.raw_dir, "ml-latest-small")
        
        for file in expected_files:
            file_path = os.path.join(src_path, file)
            if not os.path.exists(file_path):
                logger.error(f"Expected MovieLens file missing: {file_path}")
                return False
        
        logger.info("MovieLens dataset is ready in raw folder.")
        return True

    def prepare_goodbooks(self):
        """Downloads and prepares a subset of the Goodbooks-10k dataset."""
        books_path = os.path.join(self.raw_dir, "books.csv")
        ratings_path = os.path.join(self.raw_dir, "book_ratings_raw.csv")
        book_tags_path = os.path.join(self.raw_dir, "book_tags.csv")
        tags_path = os.path.join(self.raw_dir, "tags.csv")

        # Download files
        success_books = self._download_file(GOODBOOKS_BOOKS_URL, books_path)
        success_ratings = self._download_file(GOODBOOKS_RATINGS_URL, ratings_path)
        success_book_tags = self._download_file(GOODBOOKS_BOOK_TAGS_URL, book_tags_path)
        success_tags = self._download_file(GOODBOOKS_TAGS_URL, tags_path)

        if not (success_books and success_ratings):
            logger.warning("Core Goodbooks files download failed. Checking if fallbacks exist.")
            if not (os.path.exists(books_path) and os.path.exists(ratings_path)):
                return False

        logger.info("Goodbooks dataset files are ready in raw folder.")
        return True

    def get_raw_movie_data(self):
        """Loads and returns the raw MovieLens datasets."""
        ml_dir = os.path.join(self.raw_dir, "ml-latest-small")
        movies_df = pd.read_csv(os.path.join(ml_dir, "movies.csv"))
        ratings_df = pd.read_csv(os.path.join(ml_dir, "ratings.csv"))
        tags_df = pd.read_csv(os.path.join(ml_dir, "tags.csv"))
        
        return movies_df, ratings_df, tags_df

    def get_raw_book_data(self):
        """Loads and returns raw Goodreads datasets, mapping tags to extract genres."""
        books_df = pd.read_csv(os.path.join(self.raw_dir, "books.csv"))
        ratings_df = pd.read_csv(os.path.join(self.raw_dir, "book_ratings_raw.csv"))
        
        # Optionally load tags to build book genres
        book_tags_file = os.path.join(self.raw_dir, "book_tags.csv")
        tags_file = os.path.join(self.raw_dir, "tags.csv")
        
        genres_mapped = {}
        if os.path.exists(book_tags_file) and os.path.exists(tags_file):
            try:
                logger.info("Extracting genres from Goodreads tags...")
                book_tags = pd.read_csv(book_tags_file)
                tags = pd.read_csv(tags_file)
                
                # List of target genres
                target_genres = ['fantasy', 'science-fiction', 'sci-fi', 'romance', 'mystery', 
                                 'thriller', 'horror', 'historical-fiction', 'history', 'biography', 
                                 'non-fiction', 'nonfiction', 'classics', 'poetry', 'drama']
                
                # Filter tags that match target genres
                tags['tag_name_lower'] = tags['tag_name'].str.lower()
                genre_tags = tags[tags['tag_name_lower'].isin(target_genres)].copy()
                
                # Rename standard sci-fi names
                genre_tags['normalized_genre'] = genre_tags['tag_name_lower'].replace({
                    'science-fiction': 'Sci-Fi',
                    'sci-fi': 'Sci-Fi',
                    'nonfiction': 'Non-Fiction',
                    'non-fiction': 'Non-Fiction',
                    'historical-fiction': 'Historical Fiction',
                    'fantasy': 'Fantasy',
                    'romance': 'Romance',
                    'mystery': 'Mystery',
                    'thriller': 'Thriller',
                    'horror': 'Horror',
                    'history': 'History',
                    'biography': 'Biography',
                    'classics': 'Classics',
                    'poetry': 'Poetry',
                    'drama': 'Drama'
                })
                
                # Merge tags with book_tags to find book-genre associations
                merged_tags = pd.merge(book_tags, genre_tags, on='tag_id')
                
                # Keep top tag for each book
                merged_tags = merged_tags.sort_values(by=['goodreads_book_id', 'count'], ascending=[True, False])
                
                # Group by book_id and collect unique genres
                book_genres = merged_tags.groupby('goodreads_book_id')['normalized_genre'].apply(lambda x: list(set(x))).to_dict()
                genres_mapped = book_genres
            except Exception as e:
                logger.error(f"Error mapping book tags: {e}")

        # Inject genres or default to 'Fiction'
        def get_genres(book_row):
            b_id = book_row['book_id']
            if b_id in genres_mapped and genres_mapped[b_id]:
                return "|".join(genres_mapped[b_id])
            return "Fiction"

        books_df['genres'] = books_df.apply(get_genres, axis=1)
        return books_df, ratings_df

    def create_book_subset(self, user_limit=2000):
        """Creates a manageable slice of Goodreads ratings for faster local performance."""
        logger.info(f"Slicing Goodreads dataset to keep user IDs <= {user_limit}...")
        
        books_df, ratings_df = self.get_raw_book_data()
        
        # Filter ratings for users with ID <= user_limit
        ratings_subset = ratings_df[ratings_df['user_id'] <= user_limit].copy()
        
        # Also clean ratings data to only include books that actually exist in books_df
        existing_book_ids = set(books_df['book_id'].unique())
        ratings_subset = ratings_subset[ratings_subset['book_id'].isin(existing_book_ids)]
        
        # Save subsets to processed
        books_df.to_csv(os.path.join(self.processed_dir, "books.csv"), index=False)
        ratings_subset.to_csv(os.path.join(self.processed_dir, "book_ratings.csv"), index=False)
        
        logger.info(f"Created books subset. Ratings shape: {ratings_subset.shape}")
        return books_df, ratings_subset

    def generate_fallback_data(self):
        """Generates high-quality synthetic backup data in case of failed downloads."""
        logger.warning("Generating fallback dataset for movies and books...")
        
        # Fallback Movies
        movies = []
        genres_list = ["Action", "Adventure", "Sci-Fi", "Comedy", "Drama", "Thriller", "Romance", "Mystery"]
        for i in range(1, 201):
            title = f"Fallback Movie {i}"
            genres = "|".join(np.random.choice(genres_list, size=np.random.randint(1, 3), replace=False))
            movies.append({"movieId": i, "title": title, "genres": genres})
        movies_df = pd.DataFrame(movies)
        
        # Fallback Movie Ratings
        ratings = []
        for user_id in range(1, 51):
            # Each user rates a random set of movies
            rated_movies = np.random.choice(range(1, 201), size=np.random.randint(5, 30), replace=False)
            for m_id in rated_movies:
                rating = float(np.random.choice([1.0, 2.0, 3.0, 4.0, 5.0], p=[0.05, 0.1, 0.2, 0.4, 0.25]))
                timestamp = 1600000000 + np.random.randint(0, 10000000)
                ratings.append({"userId": user_id, "movieId": m_id, "rating": rating, "timestamp": timestamp})
        ratings_df = pd.DataFrame(ratings)
        
        # Save
        ml_dir = os.path.join(self.raw_dir, "ml-latest-small")
        os.makedirs(ml_dir, exist_ok=True)
        movies_df.to_csv(os.path.join(ml_dir, "movies.csv"), index=False)
        ratings_df.to_csv(os.path.join(ml_dir, "ratings.csv"), index=False)
        
        # Create dummy tags.csv
        pd.DataFrame(columns=["userId", "movieId", "tag", "timestamp"]).to_csv(os.path.join(ml_dir, "tags.csv"), index=False)
        
        # Fallback Books
        books = []
        book_genres = ["Fantasy", "Sci-Fi", "Mystery", "Romance", "Classics", "Non-Fiction", "Drama"]
        for i in range(1, 101):
            title = f"Fallback Book {i}"
            authors = f"Author {np.random.randint(1, 20)}"
            genres = "|".join(np.random.choice(book_genres, size=np.random.randint(1, 3), replace=False))
            books.append({
                "book_id": i, "title": title, "authors": authors, 
                "genres": genres, "average_rating": np.random.uniform(3.5, 4.8)
            })
        books_df = pd.DataFrame(books)
        
        # Fallback Book Ratings
        book_ratings = []
        for user_id in range(1, 31):
            rated_books = np.random.choice(range(1, 101), size=np.random.randint(3, 15), replace=False)
            for b_id in rated_books:
                rating = int(np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.05, 0.2, 0.4, 0.3]))
                book_ratings.append({"user_id": user_id, "book_id": b_id, "rating": rating})
        book_ratings_df = pd.DataFrame(book_ratings)
        
        # Save Goodbooks fallbacks
        books_df.to_csv(os.path.join(self.raw_dir, "books.csv"), index=False)
        book_ratings_df.to_csv(os.path.join(self.raw_dir, "book_ratings_raw.csv"), index=False)
        
        # Create processed subsets
        books_df.to_csv(os.path.join(self.processed_dir, "books.csv"), index=False)
        book_ratings_df.to_csv(os.path.join(self.processed_dir, "book_ratings.csv"), index=False)
        
        logger.info("Fallback datasets generated successfully.")

if __name__ == "__main__":
    manager = DatasetManager()
    logger.info("Initializing dataset preparation...")
    
    # Attempt MovieLens
    try:
        if not manager.prepare_movielens():
            logger.warning("MovieLens download failed, using fallbacks.")
            manager.generate_fallback_data()
    except Exception as e:
        logger.error(f"Error preparing MovieLens: {e}")
        manager.generate_fallback_data()
        
    # Attempt Goodbooks
    try:
        if manager.prepare_goodbooks():
            manager.create_book_subset(user_limit=2000)
        else:
            logger.warning("Goodbooks preparation failed, using fallbacks.")
            manager.generate_fallback_data()
    except Exception as e:
        logger.error(f"Error preparing Goodbooks: {e}")
        manager.generate_fallback_data()
