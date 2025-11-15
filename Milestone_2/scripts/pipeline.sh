#!/bin/bash

# convert qrels to trec format
#./scripts/qrels2trec.py --qrels config/qrels > results/trec_qrels.txt

# Automatically detect all query folders in config/queries/
for query_folder in config/queries/query*; do
    # Extract just the folder name (e.g., query1)
    query_name=$(basename "$query_folder")
    
    echo "Processing $query_name..."
    
    # Create results directory for this query if it doesn't exist
    mkdir -p "results/$query_name"
    
    # Query solr and save results
    python scripts/query_solr.py --queries "$query_folder" --uri http://localhost:8983/solr --collection media
    
    # Move solr_results.json to the query-specific folder
    mv results/solr_results.json "results/$query_name/solr_results.json"
    
    # Convert to TREC format and save to query-specific folder
    ./scripts/solr2trec.py "results/$query_name/solr_results.json" > "results/$query_name/trec_results.txt"
    
    echo "✓ Completed $query_name"
done

echo "✓ All queries processed successfully"

# run evaluation pipeline
#./trec_eval/trec_eval \
#    -q -m all_trec \
#    results/trec_qrels.txt results/trec_results.txt | ./scripts/plot_pr.py

# cleanup
#rm results/trec_qrels.txt
#rm results/trec_results.txt
