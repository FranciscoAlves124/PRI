#### start Solr container (runs standalone Solr on port 8983)
docker pull solr:9
docker run -d -p 8983:8983 --name initial_solr -v "$(pwd):/data" solr:9

#### create schemaless core (basic)
docker exec initial_solr solr create -c media_basic -n data_driven_schema_configs

#### create strict core for intermediate (non-schemaless)
docker exec initial_solr solr create -c media_intermediate -n basic_configs

#### apply intermediate schema (preferred helper)
python3 apply_schema.py --core media_intermediate --file intermediate_schema.json

docker exec initial_solr solr create -c semantic_core -n basic_configs

# Add the schema defined at semantic_schema.json
curl.exe -X POST -H "Content-type:application/json" --data-binary "@./semantic_schema.json" http://localhost:8983/solr/semantic_core/schema

# Ensure 'datasets' is installed
if ! python3 -c "import datasets" 2>/dev/null; then
	echo "Installing required Python package: datasets"
	pip install datasets
fi

# Run add_poster_urls.py
python3 scripts/add_poster_urls.py

# Index the JSON documents.
curl.exe -X POST -H "Content-type:application/json" --data-binary "@./data/movies_series_with_posters.json" "http://localhost:8983/solr/semantic_core/update?commit=true"
curl.exe -X POST -H "Content-type:application/json" --data-binary "@./data/movies_series_with_posters.json" "http://localhost:8983/solr/media_basic/update?commit=true"
curl.exe -X POST -H "Content-type:application/json" --data-binary "@./data/movies_series_with_posters.json" "http://localhost:8983/solr/media_intermediate/update?commit=true"

