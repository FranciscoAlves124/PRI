#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path
import glob
import os
import requests
import re

# Global variable for lazy-loaded model
_model = None

def get_embedding_model():
    """Lazy load the SentenceTransformer model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            print("Loading SentenceTransformer model 'all-mpnet-base-v2'...", file=sys.stderr)
            _model = SentenceTransformer('all-mpnet-base-v2')
            print("Model loaded successfully.", file=sys.stderr)
        except ImportError:
            print("Error: sentence-transformers package not found. Install it with: pip install sentence-transformers", file=sys.stderr)
            sys.exit(1)
    return _model

def convert_text_to_embedding(text):
    """Convert text to embedding vector and return as formatted string."""
    model = get_embedding_model()
    embedding = model.encode(text).tolist()
    # Use json.dumps to format as proper JSON array
    return json.dumps(embedding)


def fetch_solr_results(query_file, solr_uri, collection):
    """
    Fetch search results from a Solr instance based on the query parameters.

    Arguments:
    - query_file: Path to the JSON file containing Solr query parameters.
    - solr_uri: URI of the Solr instance (e.g., http://localhost:8983/solr).
    - collection: Solr collection name from which results will be fetched.

    Output:
    - Prints the JSON search results to STDOUT.
    """

    # Load the query parameters from the JSON file
    try:
        query_params = json.load(open(query_file))
    except FileNotFoundError:
        print(f"Error: Query file {query_file} not found.")
        sys.exit(1)

    # Check if this is a semantic search (collection contains "semantic")
    is_semantic = "semantic" in collection.lower()
    
    # Pattern to match {!knn f=vector topK=N}text_query
    knn_pattern = re.compile(r'\{!knn\s+f=vector\s+topK=(\d+)\}(.+)')
    
    # Process knn query in ANY param (e.g. q, bq, fq)
    if "params" in query_params:
        for key, value in query_params["params"].items():
            if isinstance(value, str):
                match = knn_pattern.match(value)
                if match:
                    if is_semantic:
                        # Convert text to embedding for semantic collections
                        topK = match.group(1)
                        query_text = match.group(2).strip()
                        
                        print(f"Converting text to embedding for param '{key}': '{query_text}'", file=sys.stderr)
                        embedding_vector = convert_text_to_embedding(query_text)
                        
                        # Replace the text with the embedding vector
                        query_params["params"][key] = f"{{!knn f=vector topK={topK}}}{embedding_vector}"
                        print(f"Converted to vector query (first 100 chars): {query_params['params'][key][:100]}...", file=sys.stderr)
                    else:
                        # Skip knn queries for non-semantic collections - use empty query
                        print(f"Skipping knn query in '{key}' for non-semantic collection: {collection}", file=sys.stderr)
                        query_params["params"][key] = "*:*"

    # Construct the Solr request URL
    uri = f"{solr_uri}/{collection}/select"

    # Only send the params to Solr, not the top-level query/fields
    solr_request = query_params.get("params", {}).copy()
    
    # Add the query text if not already present in params
    if "q" not in solr_request and "query" in query_params:
        solr_request["q"] = query_params["query"]
    
    # Add field list if specified at top level
    if "fields" in query_params and "fl" not in solr_request:
        solr_request["fl"] = ",".join(query_params["fields"])
    
    # Check if this is a knn query
    has_knn = "q" in solr_request and "{!knn" in str(solr_request.get("q", ""))
    
    if not has_knn:
        # For non-knn queries, convert arrays to space-separated strings for edismax params
        if "qf" in solr_request and isinstance(solr_request["qf"], list):
            solr_request["qf"] = " ".join(solr_request["qf"])
        if "pf" in solr_request and isinstance(solr_request["pf"], list):
            solr_request["pf"] = " ".join(solr_request["pf"])

    try:
        # Send request to Solr
        print(f"Sending to Solr: {uri}", file=sys.stderr)
        print(f"Params: {list(solr_request.keys())}", file=sys.stderr)
        
        if has_knn:
            # Use POST with JSON body for knn queries (vector too long for URL)
            # For knn, we only need q, fl, sort, start, rows - no defType etc
            # Wrap in "params" like test_knn.py
            knn_request = {
                "params": {
                    "q": solr_request["q"],
                    "fl": solr_request.get("fl", "*,score"),
                    "sort": solr_request.get("sort", "score desc"),
                    "start": solr_request.get("start", 0),
                    "rows": solr_request.get("rows", 20)
                }
            }
            # Add fq if present
            if "fq" in solr_request:
                knn_request["params"]["fq"] = solr_request["fq"]
            
            print("Using POST for knn query", file=sys.stderr)
            response = requests.post(uri, json=knn_request)
        else:
            # Use GET for regular queries
            response = requests.get(uri, params=solr_request)
        
        if response.status_code != 200:
            error_json = response.json()
            if "error" in error_json:
                print(f"Solr error message: {error_json['error'].get('msg', 'Unknown error')}", file=sys.stderr)
            print(f"Solr full error: {json.dumps(error_json, indent=2)}", file=sys.stderr)
            
        response.raise_for_status()  # Raise error if the request failed
    except requests.RequestException as e:
        print(f"Error querying Solr: {e}")
        sys.exit(1)

    # Fetch and print the results as JSON
    return response.json()


def main(query_folder: Path, solr_uri, output_folder, collection):

    results = {}

    for query_file in glob.glob(query_folder.joinpath("*.json").as_posix()):
        # filename contains query number
        filename = Path(query_file).stem

        if(((filename == "0001" or filename == "0002") and (not "semantic" in collection.lower()))
           or ((filename == "0003" or filename == "0004") and ("semantic" in collection.lower()))):
            results[int(filename)] = fetch_solr_results(
                query_file, solr_uri, collection
            )

    print(json.dumps(results, indent=2))

    # Save results to a JSON file
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / "solr_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(results, indent=2))
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    # Set up argument parsing for the command-line interface
    parser = argparse.ArgumentParser(
        description="Fetch search results from Solr and output them in JSON format."
    )

    # Add arguments for query file, Solr URI, and collection name
    parser.add_argument(
        "--queries",
        type=Path,
        required=True,
        help="Path to the directory containing JSON files with Solr query parameters",
    )
    parser.add_argument(
        "--uri",
        type=str,
        default="http://localhost:8983/solr",
        help="The URI of the Solr instance (default: http://localhost:8983/solr).",
    )
    parser.add_argument(
        "--output-folder",
        type=str,
        default="results",
        help="Folder to save the solr results file (default: results).",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default="courses",
        help="Name of the Solr collection to query (default: 'courses').",
    )

    # Parse command-line arguments
    args = parser.parse_args()

    # Call the function with parsed arguments
    main(args.queries, args.uri, args.output_folder, args.collection)
