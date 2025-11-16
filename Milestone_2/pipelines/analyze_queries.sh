
# Automatically detect all query folders in config/queries/
for query_folder in config/queries/query*; do
    # Extract just the folder name (e.g., query1)
    query_name=$(basename "$query_folder")
    
    echo "Processing $query_name..."
    
    # Create results directory for this query if it doesn't exist
    mkdir -p "results/basic/$query_name"
    
    ./trec_eval/trec_eval \
    -q -m all_trec \
    results/basic/$query_name/trec_qrels.txt results/basic/$query_name/trec_results.txt | ./scripts/plot_pr.py --output-folder "results/basic/$query_name"
    
    echo "✓ Completed $query_name"
done

# Automatically detect all query folders in config/queries/
for query_folder in config/queries/query*; do
    # Extract just the folder name (e.g., query1)
    query_name=$(basename "$query_folder")
    
    echo "Processing $query_name..."
    
    # Create results directory for this query if it doesn't exist
    mkdir -p "results/intermediate/$query_name"
    
    ./trec_eval/trec_eval \
    -q -m all_trec \
    results/intermediate/$query_name/trec_qrels.txt results/intermediate/$query_name/trec_results.txt | ./scripts/plot_pr.py --output-folder "results/intermediate/$query_name"
    
    echo "✓ Completed $query_name"
done