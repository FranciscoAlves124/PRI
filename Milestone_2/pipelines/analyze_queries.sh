# run evaluation pipeline
./trec_eval/trec_eval \
    -q -m all_trec \
   results/trec_qrels.txt results/trec_results.txt | ./scripts/plot_pr.py