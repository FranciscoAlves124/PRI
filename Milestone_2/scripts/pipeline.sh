#!/bin/bash

# convert qrels to trec format
#./scripts/qrels2trec.py --qrels config/qrels > results/trec_qrels.txt

# query solr and convert results to trec format
python scripts/query_solr.py --queries config/queries --uri http://localhost:8983/solr --collection media
./scripts/solr2trec.py > results/trec_results.txt

# run evaluation pipeline
./trec_eval/trec_eval \
    -q -m all_trec \
    results/trec_qrels.txt results/trec_results.txt | ./scripts/plot_pr.py

# cleanup
#rm results/trec_qrels.txt
rm results/trec_results.txt
