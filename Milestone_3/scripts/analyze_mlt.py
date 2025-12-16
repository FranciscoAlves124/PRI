#!/usr/bin/env python3
"""
Analyze More Like This (MLT) results and generate visualizations.
This script queries MLT for sample movies and analyzes the similarity patterns.

RUN: python scripts/analyze_mlt.py --samples 30 --output results/mlt_analysis
"""

import argparse
import json
import os
import requests
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter, defaultdict

# Solr configuration
SOLR_URL = "http://localhost:8983/solr"
CORE = "media_intermediate"

def query_mlt(tconst, core=CORE):
    """Query More Like This for a given movie/series."""
    params = {
        'q': f'tconst:{tconst}',
        'mlt': 'true',
        'mlt.fl': 'description,genres,top_3_cast',
        'mlt.mindf': 1,
        'mlt.mintf': 1,
        'mlt.count': 20,
        'fl': 'tconst,primaryTitle,genres,titleType,startYear,averageRating,top_3_cast,score',
        'rows': 1,
        'wt': 'json'
    }
    
    response = requests.get(f'{SOLR_URL}/{core}/select', params=params)
    if response.status_code == 200:
        return response.json()
    return None

def get_source_document(tconst, core=CORE):
    """Get the source document details."""
    params = {
        'q': f'tconst:{tconst}',
        'fl': 'tconst,primaryTitle,genres,titleType,startYear,averageRating,top_3_cast,description',
        'rows': 1,
        'wt': 'json'
    }
    
    response = requests.get(f'{SOLR_URL}/{core}/select', params=params)
    if response.status_code == 200:
        data = response.json()
        if data['response']['docs']:
            return data['response']['docs'][0]
    return None

def get_sample_movies(core=CORE, num_samples=10):
    """Get a diverse sample of movies for MLT analysis."""
    params = {
        'q': '*:*',
        'fq': 'titleType:movie',
        'fl': 'tconst,primaryTitle,genres,averageRating',
        'rows': 100,
        'sort': 'averageRating desc',
        'wt': 'json'
    }
    
    response = requests.get(f'{SOLR_URL}/{core}/select', params=params)
    if response.status_code == 200:
        docs = response.json()['response']['docs']
        # Sample diverse movies (every nth to get variety)
        step = len(docs) // num_samples
        return [docs[i * step] for i in range(min(num_samples, len(docs)))]
    return []

def parse_genres(genres_field):
    """Parse genres from various formats."""
    if isinstance(genres_field, list):
        return [g.strip() for g in genres_field]
    elif isinstance(genres_field, str):
        return [g.strip() for g in genres_field.split(',')]
    return []

def calculate_genre_overlap(source_genres, mlt_genres):
    """Calculate Jaccard similarity for genres."""
    source_set = set(source_genres)
    mlt_set = set(mlt_genres)
    if not source_set or not mlt_set:
        return 0.0
    intersection = len(source_set & mlt_set)
    union = len(source_set | mlt_set)
    return intersection / union if union > 0 else 0.0

def calculate_cast_overlap(source_cast, mlt_cast):
    """Calculate cast overlap (number of shared actors)."""
    if not source_cast or not mlt_cast:
        return 0
    # Extract actor names (before the " - " character name part)
    source_actors = set(c.split(' - ')[0].strip().lower() for c in source_cast if c)
    mlt_actors = set(c.split(' - ')[0].strip().lower() for c in mlt_cast if c)
    return len(source_actors & mlt_actors)

def analyze_mlt_results(sample_movies, output_folder):
    """Analyze MLT results and generate statistics."""
    
    all_genre_overlaps = []
    all_cast_overlaps = []
    all_year_diffs = []
    all_rating_diffs = []
    all_type_matches = []
    genre_recommendation_counts = Counter()
    mlt_per_source = []
    
    results_data = []
    
    print(f"Analyzing MLT for {len(sample_movies)} sample movies...")
    
    for movie in sample_movies:
        tconst = movie.get('tconst', movie.get('id'))
        if not tconst:
            continue
            
        source = get_source_document(tconst)
        if not source:
            continue
            
        mlt_response = query_mlt(tconst)
        if not mlt_response or 'moreLikeThis' not in mlt_response:
            continue
        
        # Get MLT results
        mlt_data = mlt_response.get('moreLikeThis', {})
        mlt_docs = []
        for key, value in mlt_data.items():
            if isinstance(value, dict) and 'docs' in value:
                mlt_docs = value['docs']
                break
        
        if not mlt_docs:
            continue
        
        source_genres = parse_genres(source.get('genres', []))
        source_cast = source.get('top_3_cast', [])
        source_year = source.get('startYear', 0)
        source_rating = source.get('averageRating', 0)
        source_type = source.get('titleType', '')
        
        movie_result = {
            'source': source.get('primaryTitle', tconst),
            'source_genres': source_genres,
            'mlt_count': len(mlt_docs),
            'recommendations': []
        }
        
        for mlt_doc in mlt_docs:
            mlt_genres = parse_genres(mlt_doc.get('genres', []))
            mlt_cast = mlt_doc.get('top_3_cast', [])
            mlt_year = mlt_doc.get('startYear', 0)
            mlt_rating = mlt_doc.get('averageRating', 0)
            mlt_type = mlt_doc.get('titleType', '')
            
            # Calculate overlaps
            genre_overlap = calculate_genre_overlap(source_genres, mlt_genres)
            cast_overlap = calculate_cast_overlap(source_cast, mlt_cast)
            
            all_genre_overlaps.append(genre_overlap)
            all_cast_overlaps.append(cast_overlap)
            
            if source_year and mlt_year:
                all_year_diffs.append(abs(source_year - mlt_year))
            
            if source_rating and mlt_rating:
                all_rating_diffs.append(abs(source_rating - mlt_rating))
            
            all_type_matches.append(1 if source_type == mlt_type else 0)
            
            for g in mlt_genres:
                genre_recommendation_counts[g] += 1
            
            movie_result['recommendations'].append({
                'title': mlt_doc.get('primaryTitle', ''),
                'genre_overlap': genre_overlap,
                'cast_overlap': cast_overlap
            })
        
        mlt_per_source.append(len(mlt_docs))
        results_data.append(movie_result)
    
    return {
        'genre_overlaps': all_genre_overlaps,
        'cast_overlaps': all_cast_overlaps,
        'year_diffs': all_year_diffs,
        'rating_diffs': all_rating_diffs,
        'type_matches': all_type_matches,
        'genre_counts': genre_recommendation_counts,
        'mlt_per_source': mlt_per_source,
        'results_data': results_data
    }

def plot_genre_overlap_distribution(genre_overlaps, output_folder):
    """Plot distribution of genre overlap (Jaccard similarity)."""
    plt.figure(figsize=(10, 6))
    
    plt.hist(genre_overlaps, bins=20, edgecolor='black', alpha=0.7, color='#667eea')
    
    mean_overlap = np.mean(genre_overlaps)
    plt.axvline(mean_overlap, color='red', linestyle='--', linewidth=2, 
                label=f'Mean: {mean_overlap:.3f}')
    
    plt.title('Genre Overlap Distribution in MLT Recommendations', fontsize=14, fontweight='bold')
    plt.xlabel('Jaccard Similarity (Genre Overlap)', fontsize=11, style='italic')
    plt.ylabel('Frequency', fontsize=11, style='italic')
    plt.legend(loc='upper right', fontsize=10)
    plt.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
    plt.tight_layout()
    
    out_path = os.path.join(output_folder, 'mlt_genre_overlap.png')
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Genre overlap plot saved to {out_path}")

def plot_cast_overlap_distribution(cast_overlaps, output_folder):
    """Plot distribution of cast overlap."""
    plt.figure(figsize=(10, 6))
    
    max_overlap = max(cast_overlaps) if cast_overlaps else 3
    bins = range(0, int(max_overlap) + 2)
    
    plt.hist(cast_overlaps, bins=bins, edgecolor='black', alpha=0.7, color='#764ba2', 
             align='left', rwidth=0.8)
    
    mean_overlap = np.mean(cast_overlaps)
    plt.axvline(mean_overlap, color='red', linestyle='--', linewidth=2,
                label=f'Mean: {mean_overlap:.2f}')
    
    plt.title('Cast Overlap Distribution in MLT Recommendations', fontsize=14, fontweight='bold')
    plt.xlabel('Number of Shared Cast Members', fontsize=11, style='italic')
    plt.ylabel('Frequency', fontsize=11, style='italic')
    plt.xticks(range(0, int(max_overlap) + 1))
    plt.legend(loc='upper right', fontsize=10)
    plt.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
    plt.tight_layout()
    
    out_path = os.path.join(output_folder, 'mlt_cast_overlap.png')
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Cast overlap plot saved to {out_path}")

def plot_year_difference_distribution(year_diffs, output_folder):
    """Plot distribution of year differences between source and recommendations."""
    plt.figure(figsize=(10, 6))
    
    plt.hist(year_diffs, bins=25, edgecolor='black', alpha=0.7, color='#059669')
    
    mean_diff = np.mean(year_diffs)
    median_diff = np.median(year_diffs)
    plt.axvline(mean_diff, color='red', linestyle='--', linewidth=2,
                label=f'Mean: {mean_diff:.1f} years')
    plt.axvline(median_diff, color='orange', linestyle=':', linewidth=2,
                label=f'Median: {median_diff:.1f} years')
    
    plt.title('Temporal Distance in MLT Recommendations', fontsize=14, fontweight='bold')
    plt.xlabel('Year Difference (Source vs Recommendation)', fontsize=11, style='italic')
    plt.ylabel('Frequency', fontsize=11, style='italic')
    plt.legend(loc='upper right', fontsize=10)
    plt.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
    plt.tight_layout()
    
    out_path = os.path.join(output_folder, 'mlt_year_difference.png')
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Year difference plot saved to {out_path}")

def plot_similarity_metrics_comparison(stats, output_folder):
    """Plot comparison of different similarity metrics."""
    plt.figure(figsize=(10, 6))
    
    metrics = ['Genre Overlap\n(Jaccard)', 'Type Match\nRate', 'Cast Overlap\n(Normalized)']
    
    # Calculate normalized values
    genre_mean = np.mean(stats['genre_overlaps']) if stats['genre_overlaps'] else 0
    type_rate = np.mean(stats['type_matches']) if stats['type_matches'] else 0
    
    # Normalize cast overlap (assume max 3 shared actors is perfect)
    cast_mean = np.mean(stats['cast_overlaps']) / 3.0 if stats['cast_overlaps'] else 0
    
    values = [genre_mean, type_rate, cast_mean]
    colors = ['#667eea', '#764ba2', '#059669']
    
    bars = plt.bar(metrics, values, color=colors, edgecolor='black', alpha=0.8)
    
    # Add value labels on bars
    for bar, val in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.2%}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.title('MLT Similarity Metrics Comparison', fontsize=14, fontweight='bold')
    plt.ylabel('Score (0-1 normalized)', fontsize=11, style='italic')
    plt.ylim(0, 1.1)
    plt.grid(True, axis='y', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.tight_layout()
    
    out_path = os.path.join(output_folder, 'mlt_metrics_comparison.png')
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Metrics comparison plot saved to {out_path}")

def plot_top_recommended_genres(genre_counts, output_folder, top_n=10):
    """Plot most frequently recommended genres."""
    plt.figure(figsize=(12, 6))
    
    top_genres = genre_counts.most_common(top_n)
    genres = [g[0] for g in top_genres]
    counts = [g[1] for g in top_genres]
    
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(genres)))
    
    bars = plt.barh(genres[::-1], counts[::-1], color=colors[::-1], edgecolor='black', alpha=0.8)
    
    plt.title('Most Frequently Recommended Genres via MLT', fontsize=14, fontweight='bold')
    plt.xlabel('Recommendation Count', fontsize=11, style='italic')
    plt.ylabel('Genre', fontsize=11, style='italic')
    plt.grid(True, axis='x', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.tight_layout()
    
    out_path = os.path.join(output_folder, 'mlt_top_genres.png')
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Top genres plot saved to {out_path}")

def generate_summary_table(stats):
    """Generate a summary table for LaTeX."""
    print("\n" + "="*60)
    print("MLT ANALYSIS SUMMARY")
    print("="*60)
    
    n_samples = len(stats['mlt_per_source'])
    total_recs = sum(stats['mlt_per_source'])
    
    print(f"Source Documents Analyzed: {n_samples}")
    print(f"Total Recommendations Generated: {total_recs}")
    print(f"Average Recommendations per Source: {np.mean(stats['mlt_per_source']):.1f}")
    print()
    
    print("SIMILARITY METRICS:")
    print(f"  Genre Overlap (Jaccard): {np.mean(stats['genre_overlaps']):.3f} ± {np.std(stats['genre_overlaps']):.3f}")
    print(f"  Cast Overlap (avg shared): {np.mean(stats['cast_overlaps']):.2f} ± {np.std(stats['cast_overlaps']):.2f}")
    print(f"  Type Match Rate: {np.mean(stats['type_matches']):.1%}")
    print(f"  Year Difference (avg): {np.mean(stats['year_diffs']):.1f} ± {np.std(stats['year_diffs']):.1f} years")
    print(f"  Rating Difference (avg): {np.mean(stats['rating_diffs']):.2f} ± {np.std(stats['rating_diffs']):.2f}")
    print()
    
    print("LaTeX Table:")
    print("\\begin{table}[H]")
    print("\\caption{More Like This Similarity Analysis}")
    print("\\label{tab:mlt_analysis}")
    print("\\begin{tabular}{lcc}")
    print("\\toprule")
    print("Metric & Mean & Std. Dev. \\\\")
    print("\\midrule")
    print(f"Genre Overlap (Jaccard) & {np.mean(stats['genre_overlaps']):.3f} & {np.std(stats['genre_overlaps']):.3f} \\\\")
    print(f"Cast Overlap (shared actors) & {np.mean(stats['cast_overlaps']):.2f} & {np.std(stats['cast_overlaps']):.2f} \\\\")
    print(f"Type Match Rate & {np.mean(stats['type_matches']):.1%} & - \\\\")
    print(f"Year Difference & {np.mean(stats['year_diffs']):.1f} & {np.std(stats['year_diffs']):.1f} \\\\")
    print(f"Rating Difference & {np.mean(stats['rating_diffs']):.2f} & {np.std(stats['rating_diffs']):.2f} \\\\")
    print("\\bottomrule")
    print("\\end{tabular}")
    print("\\end{table}")

def main():
    parser = argparse.ArgumentParser(description='Analyze More Like This results')
    parser.add_argument('--output', '-o', default='../results/mlt_analysis',
                        help='Output folder for plots')
    parser.add_argument('--samples', '-n', type=int, default=20,
                        help='Number of sample movies to analyze')
    parser.add_argument('--core', '-c', default='media_intermediate',
                        help='Solr core to use')
    args = parser.parse_args()
    
    global CORE
    CORE = args.core
    
    os.makedirs(args.output, exist_ok=True)
    
    print(f"Fetching sample movies from {CORE}...")
    sample_movies = get_sample_movies(num_samples=args.samples)
    
    if not sample_movies:
        print("Error: Could not fetch sample movies. Is Solr running?")
        return 1
    
    print(f"Found {len(sample_movies)} sample movies")
    
    stats = analyze_mlt_results(sample_movies, args.output)
    
    if not stats['genre_overlaps']:
        print("Error: No MLT results obtained. Check Solr configuration.")
        return 1
    
    # Generate plots
    print("\nGenerating visualizations...")
    plot_genre_overlap_distribution(stats['genre_overlaps'], args.output)
    plot_cast_overlap_distribution(stats['cast_overlaps'], args.output)
    plot_year_difference_distribution(stats['year_diffs'], args.output)
    plot_similarity_metrics_comparison(stats, args.output)
    plot_top_recommended_genres(stats['genre_counts'], args.output)
    
    # Print summary
    generate_summary_table(stats)
    
    # Save raw data
    with open(os.path.join(args.output, 'mlt_analysis_data.json'), 'w') as f:
        json.dump({
            'summary': {
                'n_sources': len(stats['mlt_per_source']),
                'total_recommendations': sum(stats['mlt_per_source']),
                'avg_genre_overlap': float(np.mean(stats['genre_overlaps'])),
                'avg_cast_overlap': float(np.mean(stats['cast_overlaps'])),
                'type_match_rate': float(np.mean(stats['type_matches'])),
                'avg_year_diff': float(np.mean(stats['year_diffs'])),
                'avg_rating_diff': float(np.mean(stats['rating_diffs']))
            },
            'results': stats['results_data']
        }, f, indent=2)
    
    print(f"\nAll outputs saved to {args.output}/")
    return 0

if __name__ == '__main__':
    exit(main())
