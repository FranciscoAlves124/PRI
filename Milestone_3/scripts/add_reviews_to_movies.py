#!/usr/bin/env python3
"""
Script to merge reviews into movies_series_with_embeddings.json.
Matches reviews to movies using tconst and adds them as nested documents.
"""

import json
import os
from collections import defaultdict

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')

MOVIES_FILE = os.path.join(DATA_DIR, 'movies_series_with_embeddings.json')
REVIEWS_FILE = os.path.join(DATA_DIR, 'reviews.json')
OUTPUT_FILE = os.path.join(DATA_DIR, 'movies_series_with_reviews.json')


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
            # Create review without ID and tconst
            review_data = {
                'review_content': review.get('review_content', ''),
                'review_author': review.get('review_author', '')
            }
            reviews_by_tconst[tconst].append(review_data)
    
    return reviews_by_tconst


def merge_reviews_into_movies(movies, reviews_by_tconst):
    """Add reviews to each movie as nested documents."""
    movies_with_reviews = 0
    total_reviews_added = 0
    
    for movie in movies:
        tconst = movie.get('tconst')
        if tconst and tconst in reviews_by_tconst:
            movie['reviews'] = reviews_by_tconst[tconst]
            movies_with_reviews += 1
            total_reviews_added += len(reviews_by_tconst[tconst])
        else:
            movie['reviews'] = []
    
    print(f"Added reviews to {movies_with_reviews} movies/series.")
    print(f"Total reviews added: {total_reviews_added}")
    
    return movies


def main():
    # Load data
    movies = load_json(MOVIES_FILE)
    reviews = load_json(REVIEWS_FILE)
    
    print(f"Loaded {len(movies)} movies/series.")
    print(f"Loaded {len(reviews)} reviews.")
    
    # Group reviews by tconst
    reviews_by_tconst = group_reviews_by_tconst(reviews)
    print(f"Found reviews for {len(reviews_by_tconst)} unique titles.")
    
    # Merge reviews into movies
    movies_with_reviews = merge_reviews_into_movies(movies, reviews_by_tconst)
    
    # Save output
    save_json(movies_with_reviews, OUTPUT_FILE)
    
    # Print sample
    print("\nSample output (first movie with reviews):")
    for movie in movies_with_reviews[:10]:
        if movie.get('reviews'):
            print(f"  Title: {movie.get('primaryTitle')}")
            print(f"  Number of reviews: {len(movie.get('reviews', []))}")
            if movie.get('reviews'):
                print(f"  First review author: {movie['reviews'][0].get('review_author')}")
            break


if __name__ == '__main__':
    main()
