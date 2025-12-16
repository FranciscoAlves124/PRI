#!/usr/bin/env python3
"""
Script to merge reviews into movies_series_with_embeddings.json and generate
embeddings for the combined reviews text.

Creates a 'reviews_vector' field containing the embedding of all concatenated reviews.
"""

import json
import os
from collections import defaultdict
from sentence_transformers import SentenceTransformer

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')

MOVIES_FILE = os.path.join(DATA_DIR, 'movies_series_mpnet.json')
REVIEWS_FILE = os.path.join(DATA_DIR, 'reviews.json')
OUTPUT_FILE = os.path.join(DATA_DIR, 'movies_series_with_reviews.json')

# Maximum number of reviews to use for embedding (to avoid very long texts)
MAX_REVIEWS_FOR_EMBEDDING = 20
# Maximum characters for combined reviews text
MAX_CHARS_FOR_EMBEDDING = 5000


def load_json(filepath):
    """Load JSON file."""
    print(f"Loading {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data, filepath):
    """Save data to JSON file."""
    print(f"Saving to {filepath}...")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} records.")


def group_reviews_by_tconst(reviews):
    """Group reviews by their tconst (movie ID)."""
    reviews_by_tconst = defaultdict(list)
    
    for review in reviews:
        tconst = review.get('review_tconst')
        if tconst:
            review_data = {
                'review_content': review.get('review_content', ''),
                'review_author': review.get('review_author', '')
            }
            reviews_by_tconst[tconst].append(review_data)
    
    return reviews_by_tconst


def get_combined_reviews_text(reviews):
    """
    Combine review texts for embedding generation.
    Limits to MAX_REVIEWS_FOR_EMBEDDING reviews and MAX_CHARS_FOR_EMBEDDING characters.
    """
    if not reviews:
        return ""
    
    # Take up to MAX_REVIEWS_FOR_EMBEDDING reviews
    selected_reviews = reviews[:MAX_REVIEWS_FOR_EMBEDDING]
    
    # Combine review content
    combined = " ".join(
        review.get('review_content', '') 
        for review in selected_reviews 
        if review.get('review_content')
    )
    
    # Truncate if too long
    if len(combined) > MAX_CHARS_FOR_EMBEDDING:
        combined = combined[:MAX_CHARS_FOR_EMBEDDING]
    
    return combined


def main():
    # Load the embedding model
    print("Loading SentenceTransformer model...")
    model = SentenceTransformer('all-mpnet-base-v2')
    print("Model loaded.")
    
    # Load data
    movies = load_json(MOVIES_FILE)
    reviews = load_json(REVIEWS_FILE)
    
    print(f"Loaded {len(movies)} movies/series.")
    print(f"Loaded {len(reviews)} reviews.")
    
    # Group reviews by tconst
    reviews_by_tconst = group_reviews_by_tconst(reviews)
    print(f"Found reviews for {len(reviews_by_tconst)} unique titles.")
    
    # Process each movie
    movies_with_reviews = 0
    movies_with_review_embeddings = 0
    total_reviews_added = 0
    
    print("\nProcessing movies and generating review embeddings...")
    
    for i, movie in enumerate(movies):
        tconst = movie.get('tconst')
        
        if tconst and tconst in reviews_by_tconst:
            movie_reviews = reviews_by_tconst[tconst]
            movie['reviews'] = movie_reviews
            movies_with_reviews += 1
            total_reviews_added += len(movie_reviews)
            
            # Generate embedding for combined reviews
            combined_text = get_combined_reviews_text(movie_reviews)
            if combined_text:
                embedding = model.encode(combined_text, convert_to_tensor=False).tolist()
                movie['reviews_vector'] = embedding
                movies_with_review_embeddings += 1
            else:
                movie['reviews_vector'] = None
        else:
            movie['reviews'] = []
            movie['reviews_vector'] = None
        
        # Progress indicator
        if (i + 1) % 500 == 0:
            print(f"  Processed {i + 1}/{len(movies)} movies...")
    
    print(f"\nAdded reviews to {movies_with_reviews} movies/series.")
    print(f"Generated review embeddings for {movies_with_review_embeddings} movies/series.")
    print(f"Total reviews added: {total_reviews_added}")
    
    # Save output
    save_json(movies, OUTPUT_FILE)
    
    # Print sample
    print("\nSample output (first movie with reviews):")
    for movie in movies[:10]:
        if movie.get('reviews'):
            print(f"  Title: {movie.get('primaryTitle')}")
            print(f"  Number of reviews: {len(movie.get('reviews', []))}")
            print(f"  Has reviews_vector: {movie.get('reviews_vector') is not None}")
            if movie.get('reviews_vector'):
                print(f"  Reviews vector dimensions: {len(movie.get('reviews_vector'))}")
            break


if __name__ == '__main__':
    main()
