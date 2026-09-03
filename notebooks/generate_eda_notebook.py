import json
import os

notebook_content = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# CineMatch — Stage 1: Data Exploration and Preprocessing\n",
    "\n",
    "Welcome to the first stage of **CineMatch**! In this notebook, we will set up the data pipeline, download the datasets (MovieLens for movies and a slice of Goodbooks-10k for books), clean them, perform Exploratory Data Analysis (EDA), and establish our user-aware temporal/random split evaluation strategy.\n",
    "\n",
    "Let's import our libraries and configure the environment."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "import sys\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "\n",
    "# Ensure our src files are in the python path\n",
    "sys.path.append(os.path.abspath(\"..\"))\n",
    "\n",
    "from src.data.dataset import DatasetManager\n",
    "from src.data.preprocessing import DataPreprocessor\n",
    "\n",
    "%matplotlib inline\n",
    "plt.style.use('ggplot')\n",
    "print(\"Libraries successfully imported!\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Download and Prepare Datasets\n",
    "\n",
    "We use `DatasetManager` to fetch:\n",
    "1. **MovieLens latest small dataset** (~100k ratings, 9k movies).\n",
    "2. **Goodbooks-10k dataset** (sliced to users <= 2000 for local efficiency, resulting in ~100k ratings, 10k books)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Initialize managers (using '../data' as relative data directory)\n",
    "manager = DatasetManager(data_dir=\"../data\")\n",
    "preprocessor = DataPreprocessor(data_dir=\"../data\")\n",
    "\n",
    "print(\"Preparing MovieLens dataset...\")\n",
    "try:\n",
    "    if not manager.prepare_movielens():\n",
    "        print(\"MovieLens download failed, generating fallback data.\")\n",
    "        manager.generate_fallback_data()\n",
    "except Exception as e:\n",
    "    print(f\"Error preparing MovieLens: {e}. Generating fallback data.\")\n",
    "    manager.generate_fallback_data()\n",
    "\n",
    "print(\"Preparing Goodreads dataset...\")\n",
    "try:\n",
    "    if manager.prepare_goodbooks():\n",
    "        manager.create_book_subset(user_limit=2000)\n",
    "    else:\n",
    "        print(\"Goodreads download failed, generating fallback data.\")\n",
    "        manager.generate_fallback_data()\n",
    "except Exception as e:\n",
    "    print(f\"Error preparing Goodreads: {e}. Generating fallback data.\")\n",
    "    manager.generate_fallback_data()\n",
    "\n",
    "print(\"All datasets downloaded and cached.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Load the Raw Data\n",
    "\n",
    "Let's load the dataframes into memory so we can perform EDA."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Load Movies\n",
    "movies_df, movie_ratings_df, movie_tags_df = manager.get_raw_movie_data()\n",
    "print(f\"Movies Metadata Shape: {movies_df.shape}\")\n",
    "print(f\"Movie Ratings Shape: {movie_ratings_df.shape}\")\n",
    "print(f\"Movie Tags Shape: {movie_tags_df.shape}\")\n",
    "\n",
    "# Load Books\n",
    "books_df, book_ratings_df = manager.get_raw_book_data()\n",
    "# Slice the ratings just like the pipeline does\n",
    "book_ratings_df = book_ratings_df[book_ratings_df['user_id'] <= 2000]\n",
    "print(f\"Books Metadata Shape: {books_df.shape}\")\n",
    "print(f\"Book Ratings Shape: {book_ratings_df.shape}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Exploratory Data Analysis (EDA) — Movies\n",
    "\n",
    "Let's run basic statistics and visualize distributions for the MovieLens dataset."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Count of users, movies, and ratings\n",
    "n_users_m = movie_ratings_df['userId'].nunique()\n",
    "n_movies_m = movies_df['movieId'].nunique()\n",
    "n_ratings_m = len(movie_ratings_df)\n",
    "density_m = (n_ratings_m / (n_users_m * n_movies_m)) * 100\n",
    "\n",
    "print(\"=== MOVIELENS STATISTICS ===\")\n",
    "print(f\"Number of Users: {n_users_m}\")\n",
    "print(f\"Number of Movies: {n_movies_m}\")\n",
    "print(f\"Number of Ratings: {n_ratings_m}\")\n",
    "print(f\"Interaction Matrix Density: {density_m:.4f}%\")\n",
    "print(f\"Average ratings per user: {movie_ratings_df.groupby('userId').size().mean():.1f}\")\n",
    "print(f\"Average ratings per movie: {movie_ratings_df.groupby('movieId').size().mean():.1f}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 3.1 Rating Distribution (Movies)\n",
    "Let's see what scores users give most frequently."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "plt.figure(figsize=(8, 5))\n",
    "movie_ratings_df['rating'].value_counts().sort_index().plot(kind='bar', color='skyblue', edgecolor='black')\n",
    "plt.title('MovieLens Rating Distribution')\n",
    "plt.xlabel('Rating')\n",
    "plt.ylabel('Count')\n",
    "plt.grid(axis='y', linestyle='--', alpha=0.7)\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 3.2 Most-Rated Movies\n",
    "Let's see which movies have the highest rating volume."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "movie_counts = movie_ratings_df.groupby('movieId').size().reset_index(name='count')\n",
    "top_movies = pd.merge(movie_counts, movies_df, on='movieId')\n",
    "top_movies = top_movies.sort_values(by='count', ascending=False).head(10)\n",
    "\n",
    "print(\"Top 10 Most-Rated Movies:\")\n",
    "print(top_movies[['title', 'count', 'genres']].to_string(index=False))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 3.3 Genre Distribution (Movies)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Split genres and count frequencies\n",
    "movie_genres_split = movies_df['genres'].str.split('|').explode()\n",
    "genre_counts = movie_genres_split.value_counts()\n",
    "\n",
    "plt.figure(figsize=(10, 6))\n",
    "genre_counts.plot(kind='barh', color='coral', edgecolor='black')\n",
    "plt.title('Movie Genre Frequencies')\n",
    "plt.xlabel('Count')\n",
    "plt.gca().invert_yaxis()  # Put most popular on top\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Exploratory Data Analysis (EDA) — Books\n",
    "\n",
    "Let's perform the same analysis for our Goodreads book rating subset."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "n_users_b = book_ratings_df['user_id'].nunique()\n",
    "n_books_b = books_df['book_id'].nunique()\n",
    "n_ratings_b = len(book_ratings_df)\n",
    "density_b = (n_ratings_b / (n_users_b * n_books_b)) * 100\n",
    "\n",
    "print(\"=== GOODREADS STATISTICS ===\")\n",
    "print(f\"Number of Users: {n_users_b}\")\n",
    "print(f\"Number of Books: {n_books_b}\")\n",
    "print(f\"Number of Ratings: {n_ratings_b}\")\n",
    "print(f\"Interaction Matrix Density: {density_b:.4f}%\")\n",
    "print(f\"Average ratings per user: {book_ratings_df.groupby('user_id').size().mean():.1f}\")\n",
    "print(f\"Average ratings per book: {book_ratings_df.groupby('book_id').size().mean():.1f}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 4.1 Rating Distribution (Books)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "plt.figure(figsize=(8, 5))\n",
    "book_ratings_df['rating'].value_counts().sort_index().plot(kind='bar', color='lightgreen', edgecolor='black')\n",
    "plt.title('Goodreads Book Rating Distribution')\n",
    "plt.xlabel('Rating')\n",
    "plt.ylabel('Count')\n",
    "plt.grid(axis='y', linestyle='--', alpha=0.7)\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 4.2 Most-Rated Books"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "book_counts = book_ratings_df.groupby('book_id').size().reset_index(name='count')\n",
    "top_books = pd.merge(book_counts, books_df, on='book_id')\n",
    "top_books = top_books.sort_values(by='count', ascending=False).head(10)\n",
    "\n",
    "print(\"Top 10 Most-Rated Books:\")\n",
    "print(top_books[['title', 'authors', 'count', 'genres']].to_string(index=False))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 4.3 Genre Distribution (Books)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "book_genres_split = books_df['genres'].str.split('|').explode()\n",
    "book_genre_counts = book_genres_split.value_counts()\n",
    "\n",
    "plt.figure(figsize=(10, 6))\n",
    "book_genre_counts.plot(kind='barh', color='plum', edgecolor='black')\n",
    "plt.title('Book Genre Frequencies')\n",
    "plt.xlabel('Count')\n",
    "plt.gca().invert_yaxis()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 5. Preprocess Data and Apply Split Strategies\n",
    "\n",
    "Now we run the preprocessing script to clean text, build our `combined_text` features for content search, and create the user-aware split datasets."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Preprocess items\n",
    "print(\"Preprocessing movies and books metadata...\")\n",
    "processed_movies = preprocessor.preprocess_movies(movies_df, movie_tags_df)\n",
    "processed_books = preprocessor.preprocess_books(books_df)\n",
    "\n",
    "# Perform splits\n",
    "print(\"Performing user-aware splits...\")\n",
    "movie_train, movie_test = preprocessor.split_ratings_user_aware(movie_ratings_df, is_temporal=True)\n",
    "book_train, book_test = preprocessor.split_ratings_user_aware(book_ratings_df, is_temporal=False)\n",
    "\n",
    "# Save splits\n",
    "movie_train.to_csv(\"../data/processed/movie_ratings_train.csv\", index=False)\n",
    "movie_test.to_csv(\"../data/processed/movie_ratings_test.csv\", index=False)\n",
    "book_train.to_csv(\"../data/processed/book_ratings_train.csv\", index=False)\n",
    "book_test.to_csv(\"../data/processed/book_ratings_test.csv\", index=False)\n",
    "\n",
    "print(\"Train/Test splits successfully saved to data/processed/\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 5.1 Content Feature Inspect\n",
    "Let's print a sample of the text representations generated for our TF-IDF model."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "print(\"=== MOVIE COMBINED TEXT SAMPLE ===\")\n",
    "for i, row in processed_movies.head(3).iterrows():\n",
    "    print(f\"Title: {row['title']}\")\n",
    "    print(f\"Combined Feature: {row['combined_text']}\\n\")\n",
    "    \n",
    "print(\"=== BOOK COMBINED TEXT SAMPLE ===\")\n",
    "for i, row in processed_books.head(3).iterrows():\n",
    "    print(f\"Title: {row['title']}\")\n",
    "    print(f\"Combined Feature: {row['combined_text']}\\n\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 5.2 Verification of Split Properties\n",
    "For collaborative filtering models (like Item-Item or Matrix Factorization), it is vital to check if test users exist in the training set (to avoid the absolute cold-start user problem during model evaluation, which is treated separately)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "train_users = set(movie_train['userId'])\n",
    "test_users = set(movie_test['userId'])\n",
    "unseen_users = test_users - train_users\n",
    "\n",
    "print(f\"Total training users: {len(train_users)}\")\n",
    "print(f\"Total test users: {len(test_users)}\")\n",
    "print(f\"Test users missing from training set: {len(unseen_users)}\")\n",
    "\n",
    "# Check item coverage in train vs test\n",
    "train_items = set(movie_train['movieId'])\n",
    "test_items = set(movie_test['movieId'])\n",
    "unseen_items = test_items - train_items\n",
    "print(f\"Total training items: {len(train_items)}\")\n",
    "print(f\"Total test items: {len(test_items)}\")\n",
    "print(f\"Test items missing from training set (cold items): {len(unseen_items)}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Excellent! Stage 1 is fully complete. We have loaded, analyzed, preprocessed, and saved train/test partitions using a user-aware temporal/random split. We are ready to proceed to Stage 2: Content-Based Recommender!"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbformat_minor": 2,
   "pygments_lexer": "ipython3",
   "version": "3.13.1"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

# Write notebook file
notebook_path = "C:/Users/ASUS/.gemini/antigravity/scratch/cinematch/notebooks/01_data_exploration.ipynb"
with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(notebook_content, f, indent=1)

print("EDA Notebook successfully generated.")
