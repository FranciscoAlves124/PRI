#!/bin/bash

# This script expects a container started with the following command.
docker run -p 8983:8983 --name initial_solr -v ${PWD}:/data -d solr:9 solr-precreate media

# Populate collection using mapped path inside container.
docker exec initial_solr solr post -c media /data/final_data_solr/movies_series.json