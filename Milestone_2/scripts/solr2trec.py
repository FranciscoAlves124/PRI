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
                print(f"{int(query_id)} Q0 {doc['tconst'][0]} {rank} {doc['averageRating'][0]} {run_id}")

        except KeyError:
            print("Error: Invalid Solr response format. 'docs' key not found.")
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
                    f.write(f"{int(query_id)} 0 {doc['tconst'][0]} 1\n")
            except KeyError:
                print("Error: Invalid Solr response format. 'docs' key not found.")
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

    # Parse command-line arguments
    args = parser.parse_args()

    input_file = os.path.join("results", "solr_results.json")
    with open(input_file, "r") as f:
        solr_response = json.load(f)

    # Convert all Solr results to TREC format and write to STDOUT
    solr_to_trec(solr_response, args.run_id)

    # Create qrels file for evaluation
    #create_qrels(solr_response, "results/trec_qrels.txt")
