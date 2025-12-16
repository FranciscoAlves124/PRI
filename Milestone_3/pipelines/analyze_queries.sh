
# Automatically detect all query folders in config/queries/
for query_folder in config/queries/query*; do
    # Extract just the folder name (e.g., query1)
    query_name=$(basename "$query_folder")
    
    echo "Processing $query_name..."
    
    # Create results directory for this query if it doesn't exist
    mkdir -p "results/basic/$query_name"

    python3 scripts/qrels2trec.py --trec-results "results/basic/$query_name/trec_results.txt" --queries-dir "config/queries/$query_name" > results/basic/$query_name/trec_qrels.txt
    
    # trec eval 
    echo "=== Precision@20 for $query_name ==="
    ./trec_eval/trec_eval -q -m P.20 \
    results/basic/$query_name/trec_qrels.txt results/basic/$query_name/trec_results.txt
    
    echo ""
    echo "=== Full metrics for $query_name ==="
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

    python3 scripts/qrels2trec.py --trec-results "results/intermediate/$query_name/trec_results.txt" --queries-dir "config/queries/$query_name" > results/intermediate/$query_name/trec_qrels.txt
    
    echo "=== Precision@20 for $query_name ==="
    ./trec_eval/trec_eval -q -m P.20 \
    results/intermediate/$query_name/trec_qrels.txt results/intermediate/$query_name/trec_results.txt
    
    echo ""
    echo "=== Full metrics for $query_name ==="
    ./trec_eval/trec_eval \
    -q -m all_trec \
    results/intermediate/$query_name/trec_qrels.txt results/intermediate/$query_name/trec_results.txt | ./scripts/plot_pr.py --output-folder "results/intermediate/$query_name"
    
    echo "✓ Completed $query_name"
done

# Automatically detect all query folders in config/queries/
for query_folder in config/queries/query*; do
    # Extract just the folder name (e.g., query1)
    query_name=$(basename "$query_folder")
    
    echo "Processing $query_name..."
    
    # Create results directory for this query if it doesn't exist
    mkdir -p "results/semantic/$query_name"

    python3 scripts/qrels2trec.py --trec-results "results/semantic/$query_name/trec_results.txt" --queries-dir "config/queries/$query_name" > results/semantic/$query_name/trec_qrels.txt
    
    echo "=== Precision@20 for $query_name ==="
    ./trec_eval/trec_eval -q -m P.20 \
    results/semantic/$query_name/trec_qrels.txt results/semantic/$query_name/trec_results.txt
    
    echo ""
    echo "=== Full metrics for $query_name ==="
    ./trec_eval/trec_eval \
    -q -m all_trec \
    results/semantic/$query_name/trec_qrels.txt results/semantic/$query_name/trec_results.txt | ./scripts/plot_pr.py --output-folder "results/semantic/$query_name"
    
    echo "✓ Completed $query_name"
done