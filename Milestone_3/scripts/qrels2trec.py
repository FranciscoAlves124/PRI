#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path
import os


def qrels_to_trec(trec_results_file: Path, queries_dir: Path) -> None:
    """
    Reads trec_results.txt, extracts query IDs, fetches corresponding qrels 
    from config/queries/queryX/qrels.txt, and converts to TREC format.

    Arguments:
    - trec_results_file: Path to trec_results.txt file containing query results
    - queries_dir: Path to directory containing query folders (e.g., config/queries/)
    
    Output format: query_id iteration doc_id relevance
    Example: 1 0 tt0068646 1
    """
    
    # Read trec_results.txt to get unique query IDs
    if not trec_results_file.exists():
        print(f"Error: {trec_results_file} not found")
        return
    
    # Read trec_results.txt to get document IDs for each query
    query_docs = {}
    with open(trec_results_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 3:
                query_id = parts[0]
                doc_id = parts[2]  # Document ID is in 3rd column
                if query_id not in query_docs:
                    query_docs[query_id] = set()
                query_docs[query_id].add(doc_id)
    
    # For each query ID, read corresponding qrels file and output TREC format
    for query_id in sorted(query_docs.keys(), key=int):
        qrels_file = queries_dir / "qrels.txt"
        
        if not qrels_file.exists():
            print(f"Warning: {qrels_file} not found, skipping query {query_id}", file=os.sys.stderr)
            continue
        
        # Read qrels and output only for documents in trec_results
        with open(qrels_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    doc_id = parts[0]
                    relevance = parts[1]
                    # Only output if this doc_id appears in trec_results for this query
                    if doc_id in query_docs[query_id]:
                        # TREC format: qid iter docno rel
                        print(f"{query_id} 0 {doc_id} {relevance}")


if __name__ == "__main__":
    """
    Read trec_results.txt, fetch qrels for each query, and output in TREC format.
    """
    parser = ArgumentParser(description="Convert QRELs to TREC format by reading trec_results.txt")

    parser.add_argument(
        "--trec-results",
        type=Path,
        default="trec_results.txt",
        help="Path to trec_results.txt file (default: trec_results.txt)",
    )
    
    parser.add_argument(
        "--queries-dir",
        type=Path,
        default="config/queries",
        help="Path to queries directory containing queryX folders (default: config/queries)",
    )

    args = parser.parse_args()

    qrels_to_trec(args.trec_results, args.queries_dir)

