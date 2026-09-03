import json
import os

notebook_content = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# CineMatch — Stage 3: Collaborative Filtering\n",
    "\n",
    "In this stage, we implement **Collaborative Filtering** recommendation models. Unlike content-based filtering which relies on item descriptions, collaborative filtering recommends items based on the history of user ratings and user-item interactions.\n",
    "\n",
    "### Core Concepts:\n",
    "1. **User-Item Interaction Matrix**: A matrix where rows are users, columns are items, and cells contain user ratings. It is typically sparse because most users rate only a fraction of available items.\n",
    "2. **Item-Item Collaborative Filtering (Neighborhood-based)**: Computes similarities between items based on their ratings vectors. A user's rating for an item is predicted as a similarity-weighted average of the user's ratings on similar items.\n",
    "3. **Matrix Factorization (SVD)**: Decomposes the ratings matrix into low-rank matrices representing user and item latent features. Predicted ratings are computed by the dot product of these latent feature vectors.\n",
    "\n",
    "Let's import libraries and load our train ratings and processed items."
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
    "\n",
    "# Ensure our src files are in the python path\n",
    "sys.path.append(os.path.abspath(\"..\"))\n",
    "\n",
    "from src.recommendation.collaborative import CollaborativeRecommender\n",
    "\n",
    "print(\"Recommender class successfully imported!\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Load Preprocessed Data\n",
    "\n",
    "We load `movie_ratings_train.csv` and `book_ratings_train.csv` (the training splits), along with processed metadata files `movies_processed.csv` and `books_processed.csv` from the `data/processed` folder."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "data_dir = \"../data/processed\"\n",
    "\n",
    "# Movies\n",
    "movie_train_df = pd.read_csv(os.path.join(data_dir, \"movie_ratings_train.csv\"))\n",
    "movies_metadata = pd.read_csv(os.path.join(data_dir, \"movies_processed.csv\"))\n",
    "\n",
    "# Books\n",
    "book_train_df = pd.read_csv(os.path.join(data_dir, \"book_ratings_train.csv\"))\n",
    "books_metadata = pd.read_csv(os.path.join(data_dir, \"books_processed.csv\"))\n",
    "\n",
    "print(f\"Loaded {len(movie_train_df)} movie ratings (train) and {len(book_train_df)} book ratings (train).\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Movies: Fit Recommender and Compare Approaches\n",
    "\n",
    "We train the collaborative models on movie training ratings."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "movie_cf = CollaborativeRecommender(user_col='userId', item_col='movieId', rating_col='rating', num_factors=30)\n",
    "movie_cf.fit(movie_train_df)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 2.1 Predict Ratings\n",
    "Let's predict ratings for a specific user and movie (e.g. user 1 on movie 31, which is *Dangerous Minds* if present, or other movies) and compare our models."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "sample_user = movie_train_df.iloc[0]['userId']\n",
    "sample_movie = movie_train_df.iloc[0]['movieId']\n",
    "actual_rating = movie_train_df.iloc[0]['rating']\n",
    "\n",
    "pred_ii = movie_cf.predict_rating_item_item(sample_user, sample_movie)\n",
    "pred_svd = movie_cf.predict_rating_svd(sample_user, sample_movie)\n",
    "\n",
    "print(f\"Predicting for User {sample_user} on Movie {sample_movie}:\")\n",
    "print(f\"Actual rating in training set: {actual_rating}\")\n",
    "print(f\"Item-Item CF Prediction: {pred_ii:.2f}\")\n",
    "print(f\"SVD Matrix Factorization Prediction: {pred_svd:.2f}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 2.2 Recommendation Generation\n",
    "Let's recommend unrated movies for a specific user (e.g., user 10) using both SVD and Item-Item models."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "test_user_id = 10\n",
    "\n",
    "recs_svd = movie_cf.recommend_collaborative(\n",
    "    user_id=test_user_id, method='svd', top_k=5, \n",
    "    items_metadata_df=movies_metadata, title_col='title', genre_col='genres'\n",
    ")\n",
    "\n",
    "recs_ii = movie_cf.recommend_collaborative(\n",
    "    user_id=test_user_id, method='item_item', top_k=5, \n",
    "    items_metadata_df=movies_metadata, title_col='title', genre_col='genres'\n",
    ")\n",
    "\n",
    "print(f\"=== SVD RECOMMENDATIONS FOR USER {test_user_id} ===\")\n",
    "for r in recs_svd:\n",
    "    print(f\"Title: {r['title']} | Score: {r['score']:.4f} (Raw: {r['raw_rating']})\")\n",
    "print(\"\\n\")\n",
    "\n",
    "print(f\"=== ITEM-ITEM RECOMMENDATIONS FOR USER {test_user_id} ===\")\n",
    "for r in recs_ii:\n",
    "    print(f\"Title: {r['title']} | Score: {r['score']:.4f} (Raw: {r['raw_rating']})\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Books: Fit Recommender and Compare Approaches\n",
    "\n",
    "Let's run the collaborative recommendation logic on books."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "book_cf = CollaborativeRecommender(user_col='user_id', item_col='book_id', rating_col='rating', num_factors=30)\n",
    "book_cf.fit(book_train_df)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 3.1 Predict Book Ratings"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "sample_user_b = book_train_df.iloc[0]['user_id']\n",
    "sample_book_b = book_train_df.iloc[0]['book_id']\n",
    "actual_rating_b = book_train_df.iloc[0]['rating']\n",
    "\n",
    "pred_ii_b = book_cf.predict_rating_item_item(sample_user_b, sample_book_b)\n",
    "pred_svd_b = book_cf.predict_rating_svd(sample_user_b, sample_book_b)\n",
    "\n",
    "print(f\"Predicting for User {sample_user_b} on Book {sample_book_b}:\")\n",
    "print(f\"Actual rating in training set: {actual_rating_b}\")\n",
    "print(f\"Item-Item CF Prediction: {pred_ii_b:.2f}\")\n",
    "print(f\"SVD Matrix Factorization Prediction: {pred_svd_b:.2f}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 3.2 Book Recommendations"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "test_user_id_b = 5\n",
    "\n",
    "recs_svd_b = book_cf.recommend_collaborative(\n",
    "    user_id=test_user_id_b, method='svd', top_k=5, \n",
    "    items_metadata_df=books_metadata, title_col='title', genre_col='genres'\n",
    ")\n",
    "\n",
    "print(f\"=== SVD BOOK RECOMMENDATIONS FOR USER {test_user_id_b} ===\")\n",
    "for r in recs_svd_b:\n",
    "    print(f\"Title: {r['title']} | Score: {r['score']:.4f} (Raw: {r['raw_rating']}) | Genres: {r['genres']}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Stage 3 Collaborative Filtering is fully complete! We have implemented Item-Item and SVD models that can predict ratings on a 1-5 scale and generate unrated recommendations for users. We are ready to proceed to Stage 4: Hybrid Recommender!"
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
notebook_path = "C:/Users/ASUS/.gemini/antigravity/scratch/cinematch/notebooks/03_collaborative_filtering.ipynb"
with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(notebook_content, f, indent=1)

print("Collaborative Notebook successfully generated.")
