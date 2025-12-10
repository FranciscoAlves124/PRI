#!/bin/bash

# convert qrels to trec format
#./scripts/qrels2trec.py --qrels config/qrels > results/trec_qrels.txt

# Automatically detect all query folders in config/queries/
for query_folder in config/queries/query*; do
    # Extract just the folder name (e.g., query1)
    query_name=$(basename "$query_folder")
    
    echo "Processing $query_name..."
    
    # Create results directory for this query if it doesn't exist
    mkdir -p "results/basic/$query_name"
    
    # Query solr and save results
    python3 scripts/query_solr.py --queries "$query_folder" --uri http://localhost:8983/solr --output-folder "results/basic/$query_name" --collection media_basic
    
    # Convert to TREC format and save to query-specific folder Also add new qrels
    python3 scripts/solr2trec.py --queryName "$query_name" --core basic > "results/basic/$query_name/trec_results.txt"
    
    echo "✓ Completed $query_name"
done

# Automatically detect all query folders in config/queries/
for query_folder in config/queries/query*; do
    # Extract just the folder name (e.g., query1)
    query_name=$(basename "$query_folder")
    
    echo "Processing $query_name..."
    
    # Create results directory for this query if it doesn't exist
    mkdir -p "results/intermediate/$query_name"
    
    # Query solr and save results
    python3 scripts/query_solr.py --queries "$query_folder" --uri http://localhost:8983/solr --output-folder "results/intermediate/$query_name" --collection media_intermediate
    
    # Convert to TREC format and save to query-specific folder Also add new qrels
    python3 scripts/solr2trec.py --queryName "$query_name" --core intermediate > "results/intermediate/$query_name/trec_results.txt"
    
    echo "✓ Completed $query_name"
done

echo "✓ All queries processed successfully"

# Automatically detect all query folders in config/queries/
for query_folder in config/queries/query*; do
    # Extract just the folder name (e.g., query1)
    query_name=$(basename "$query_folder")
    
    echo "Processing $query_name..."
    
    # Create results directory for this query if it doesn't exist
    mkdir -p "results/semantic/$query_name"
    
    # Query solr and save results
    python3 scripts/query_solr.py --queries "$query_folder" --uri http://localhost:8983/solr --output-folder "results/semantic/$query_name" --collection semantic_core
    
    # Convert to TREC format and save to query-specific folder Also add new qrels
    python3 scripts/solr2trec.py --queryName "$query_name" --core semantic > "results/semantic/$query_name/trec_results.txt"
    
    echo "✓ Completed $query_name"
done

echo "✓ All queries processed successfully"