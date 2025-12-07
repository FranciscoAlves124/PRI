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


def create_qrels(solr_response, output_file="results/trec_qrels.txt"):
    """
    Creates a qrels file from the Solr response for evaluation purposes.

    Arguments:
    - solr_response: Dictionary containing Solr response with document IDs and scores.
    - output_file: Path to the output qrels file (default: results/qrels.txt).
    """

    with open(output_file, "w") as f:
        for query_id, response in solr_response.items():
            try:
                docs = response["response"]["docs"]
                for doc in docs:
                    # Handle both list and scalar formats for tconst
                    tconst = doc['tconst'][0] if isinstance(doc['tconst'], list) else doc['tconst']
                    f.write(f"{int(query_id)} 0 {tconst} 1\n")
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
        "--output-folder",
        type=str,
        default="results",
        help="Folder to save the qrels file (default: results).",
    )

    # Parse command-line arguments
    args = parser.parse_args()

    input_file = os.path.join(args.output_folder, "solr_results.json")
    with open(input_file, "r") as f:
        solr_response = json.load(f)

    # Convert all Solr results to TREC format and write to STDOUT
    solr_to_trec(solr_response, args.run_id)

    # Create qrels file for evaluation
    create_qrels(solr_response, args.output_folder + "/trec_qrels.txt")
