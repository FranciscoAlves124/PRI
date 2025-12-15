

# Ensure 'datasets' is installed
if ! python3 -c "import datasets" 2>/dev/null; then
	echo "Installing required Python package: datasets"
	pip install datasets
fi

# Run add_poster_urls.py
python3 scripts/add_poster_urls.py

# Startup script to launch a Solr container with a pre-created core for semantic movies/series data.
# Run this on the '/Milestone_3' directory.
docker exec initial_solr solr delete -c semantic_core
docker exec initial_solr solr create -c semantic_core -n basic_configs

# Add the schema defined at semantic_schema.json
curl.exe -X POST -H "Content-type:application/json" --data-binary "@./semantic_schema.json" http://localhost:8983/solr/semantic_core/schema

# Index the JSON documents.
curl.exe -X POST -H "Content-type:application/json" --data-binary "@./data/movies_series_with_posters.json" "http://localhost:8983/solr/semantic_core/update?commit=true"
