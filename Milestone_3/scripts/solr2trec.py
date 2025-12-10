#!/usr/bin/env python3

import argparse
import json
import sys
import os


def solr_to_trec(solr_response, run_id="run0"):
    """
    Converts Solr search results to TREC format and writes the results to STDOUT.

    Format:
    qid     iter    docno       rank    sim     run_id
    0       Q0      M.EIC028    1       0.80    run0

    Arguments:
    - solr_response: Dictionary containing Solr response with document IDs and scores.
    - run_id: Identifier for the experiment or system (default: run0).

    Output:
    - Writes the converted results to STDOUT.
    """

    for query_id, response in solr_response.items():
        try:
            # Extract the document results from the Solr response
            docs = response["response"]["docs"]

            # Enumerate through the results and write them in TREC format
            for rank, doc in enumerate(docs, start=1):
                # Handle both list and scalar formats for tconst and score
                tconst = doc['tconst'][0] if isinstance(doc['tconst'], list) else doc['tconst']
                
                # Try different score fields
                if 'averageRating' in doc:
                    score = doc['averageRating'][0] if isinstance(doc['averageRating'], list) else doc['averageRating']
                elif 'weightedRating' in doc:
                    score = doc['weightedRating'][0] if isinstance(doc['weightedRating'], list) else doc['weightedRating']
                elif 'score' in doc:
                    score = doc['score']
                else:
                    score = 1.0  # Default score if none found
                    
                print(f"{int(query_id)} Q0 {tconst} {rank} {score} {run_id}")

        except KeyError as e:
            print(f"Error: Invalid Solr response format. Missing key: {e}")
            print(f"Response structure for query {query_id}: {response.keys()}")
            sys.exit(1)


def add_new_qrels(solr_response, output_file):
    
    # Load existing qrels if file exists
    if os.path.exists(output_file):
        with open(output_file, "r") as existing_f:
            existing_tconsts = set()
            for line in existing_f:
                parts = line.strip().split()
                if len(parts) >= 1:
                    existing_tconsts.add(parts[0])
    else:
        existing_tconsts = set()
    
    # Add new qrels to qrels file
    with open(output_file, "a") as f:
        for query_id, response in solr_response.items():
            try:
                docs = response["response"]["docs"]
                for doc in docs:
                    tconst = doc['tconst'][0] if isinstance(doc['tconst'], list) else doc['tconst']
                    # Only write if tconst not already in qrels file
                    if tconst not in existing_tconsts:
                        f.write(f"{tconst} 2\n")
                        existing_tconsts.add(tconst)  # Update set to avoid duplicates in same run
            except KeyError as e:
                print(f"Error: Invalid Solr response format. Missing key: {e}")
                print(f"Response structure for query {query_id}: {response.keys()}")
                sys.exit(1)


if __name__ == "__main__":
    # Set up argument parsing for command-line interface
    parser = argparse.ArgumentParser(description="Convert Solr results to TREC format.")

    # Add argument for optional run ID
    parser.add_argument(
        "--run-id",
        type=str,
        default="run0",
        help="Experiment or system identifier (default: run0).",
    )

    parser.add_argument(
        "--queryName",
        type=str,
        default="results",
        help="Folder to save the qrels file (default: results).",
    )

    parser.add_argument(
        "--core",
        type=str,
        default="basic",
        help="Core name to identify the correct results folder (default: media_basic).",
    )

    # Parse command-line arguments
    args = parser.parse_args()

    input_file = os.path.join("results", args.core, args.queryName, "solr_results.json")
    with open(input_file, "r") as f:
        solr_response = json.load(f)

    # Convert all Solr results to TREC format and write to STDOUT
    solr_to_trec(solr_response, args.run_id)

    # Create qrels file for evaluation
    add_new_qrels(solr_response, os.path.join("config/queries", args.queryName, "qrels.txt"))