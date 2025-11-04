#!/bin/bash

# This script expects a container started with the following command.
docker run -p 8983:8983 --name initial_solr -v ${PWD}:/data -d solr:9 solr-precreate media

# Schema definition via API
curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./initial_schema.json" \
    http://localhost:8983/solr/media/schema

# Populate collection using mapped path inside container.
docker exec -it initial_solr solr post -c media /final_data_solr/movies_series.json