import json
import os

notebook_content = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# CineMatch — Stage 2: Content-Based Recommender\n",
    "\n",
    "In this stage, we implement the **Content-Based Filtering** recommendation model. \n",
    "\n",
    "### Core Concepts:\n",
    "1. **TF-IDF (Term Frequency-Inverse Document Frequency)**: A statistical measure used to evaluate how important a word is to a document in a collection or corpus. In our case, the document is a combination of title, genres, and user tags, and the corpus is the collection of all movies or books.\n",
    "2. **Cosine Similarity**: Measures the cosine of the angle between two vectors projected in a multi-dimensional space. The closer the cosine is to 1, the more similar the items.\n",
    "3. **Sparse Representation**: Rather than storing a massive $N \\times N$ dense similarity matrix in memory, we compute similarity vectors **on-the-fly** by calculating the dot product of a sparse target vector against our sparse TF-IDF matrix. This avoids scaling bottlenecks.\n",
    "\n",
    "Let's import libraries and load our preprocessed data."
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
    "from src.recommendation.content_based import ContentBasedRecommender\n",
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
    "We load `movies_processed.csv` and `books_processed.csv` from the `data/processed` folder."
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
    "movies_df = pd.read_csv(os.path.join(data_dir, \"movies_processed.csv\"))\n",
    "books_df = pd.read_csv(os.path.join(data_dir, \"books_processed.csv\"))\n",
    "\n",
    "print(f\"Loaded {len(movies_df)} movies and {len(books_df)} books.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Movies: Fit Recommender and Generate Recommendations\n",
    "\n",
    "We fit the recommender on movies and fetch similar movies to a specific input target. Let's inspect the movies dataset to find a good target."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Print a few popular movies to select an ID\n",
    "print(movies_df[['movieId', 'title', 'genres']].head(10))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 2.1 Fit Movie Recommender\n",
    "We initialize and train our recommender using the movies dataset."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "movie_recommender = ContentBasedRecommender(id_col='movieId', title_col='title', genre_col='genres')\n",
    "movie_recommender.fit(movies_df)\n",
    "\n",
    "# Check vocabulary size\n",
    "vocab_size = len(movie_recommender.vectorizer.vocabulary_)\n",
    "print(f\"TF-IDF Vocabulary size: {vocab_size} words.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 2.2 Recommend Similar Movies\n",
    "Let's select **Toy Story (1995)**, which typically has `movieId = 1`, and recommend 10 similar items. We'll examine the structured evidence."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "target_id = 1  # Toy Story\n",
    "recs = movie_recommender.recommend_by_item(item_id=target_id, top_k=10)\n",
    "\n",
    "print(f\"=== RECOMMENDATIONS FOR TOY STORY ===\\n\")\n",
    "for r in recs:\n",
    "    print(f\"Title: {r['title']}\")\n",
    "    print(f\"Genres: {r['genres']}\")\n",
    "    print(f\"Score: {r['score']:.4f}\")\n",
    "    print(f\"Evidence: {r['evidence']}\")\n",
    "    print(\"-\" * 50)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 2.3 User Profile Search\n",
    "Let's query the movie recommendation engine using explicit structured user preferences."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "user_prefs = {\n",
    "    \"genres\": [\"Sci-Fi\", \"Action\"],\n",
    "    \"similar_to\": [\"Toy Story\"],\n",
    "    \"keywords\": [\"space\", \"adventure\"]\n",
    "}\n",
    "\n",
    "recs_profile = movie_recommender.recommend_by_profile(user_prefs, top_k=10)\n",
    "\n",
    "print(f\"=== PROFILE-BASED RECOMMENDATIONS ===\\n\")\n",
    "for r in recs_profile:\n",
    "    print(f\"Title: {r['title']}\")\n",
    "    print(f\"Genres: {r['genres']}\")\n",
    "    print(f\"Score: {r['score']:.4f}\")\n",
    "    print(f\"Evidence: {r['evidence']}\")\n",
    "    print(\"-\" * 50)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Books: Fit Recommender and Generate Recommendations\n",
    "\n",
    "Now we apply the exact same architecture to books, showing its media-agnostic design."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Print a few popular books\n",
    "print(books_df[['book_id', 'title', 'authors', 'genres']].head(5))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 3.1 Fit Book Recommender"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "book_recommender = ContentBasedRecommender(id_col='book_id', title_col='title', genre_col='genres')\n",
    "book_recommender.fit(books_df)\n",
    "print(f\"TF-IDF Vocabulary size (books): {len(book_recommender.vectorizer.vocabulary_)} words.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 3.2 Recommend Similar Books\n",
    "Let's select the first book in the dataset and recommend 5 similar items."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "target_book_id = books_df.iloc[0]['book_id']\n",
    "target_title = books_df.iloc[0]['title']\n",
    "recs_books = book_recommender.recommend_by_item(item_id=target_book_id, top_k=5)\n",
    "\n",
    "print(f\"=== RECOMMENDATIONS FOR: '{target_title}' ===\\n\")\n",
    "for r in recs_books:\n",
    "    print(f\"Title: {r['title']}\")\n",
    "    print(f\"Genres: {r['genres']}\")\n",
    "    print(f\"Score: {r['score']:.4f}\")\n",
    "    print(f\"Evidence: {r['evidence']}\")\n",
    "    print(\"-\" * 50)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 3.3 User Profile Search (Books)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "book_prefs = {\n",
    "    \"genres\": [\"Fantasy\"],\n",
    "    \"similar_to\": [target_title],\n",
    "    \"keywords\": [\"magic\", \"wizard\"]\n",
    "}\n",
    "\n",
    "recs_book_profile = book_recommender.recommend_by_profile(book_prefs, top_k=5)\n",
    "\n",
    "print(f\"=== PROFILE-BASED BOOK RECOMMENDATIONS ===\\n\")\n",
    "for r in recs_book_profile:\n",
    "    print(f\"Title: {r['title']}\")\n",
    "    print(f\"Genres: {r['genres']}\")\n",
    "    print(f\"Score: {r['score']:.4f}\")\n",
    "    print(f\"Evidence: {r['evidence']}\")\n",
    "    print(\"-\" * 50)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Stage 2 Content-Based Recommendation is fully complete! We have built a sparse representation TF-IDF recommender that works on-the-fly and supports both movies and books natively, producing rich structured evidence. We are ready to proceed to Stage 3: Collaborative Filtering!"
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
notebook_path = "C:/Users/ASUS/.gemini/antigravity/scratch/cinematch/notebooks/02_content_based.ipynb"
with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(notebook_content, f, indent=1)

print("Content-based Notebook successfully generated.")
