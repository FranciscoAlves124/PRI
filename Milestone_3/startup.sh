# Startup script to launch a Solr container with a pre-created core for semantic movies/series data.
# Run this on the '/Milestone_3' directory.
docker pull solr:9 
docker run -d -p 8983:8983 --name semantic_solr -v "$(pwd):/data" solr:9
docker exec semantic_solr solr create -c semantic_core -n basic_configs

# Add the schema defined at semantic_schema.json
curl -X POST -H 'Content-type:application/json' \
--data-binary "@./semantic_schema.json" \
http://localhost:8983/solr/semantic_core/schema

# Index the JSON documents.
curl -X POST -H 'Content-type:application/json' \
--data-binary "@./data/movies_series_mpnet.json" \
http://localhost:8983/solr/semantic_core/update?commit=true
