
## 4.3

Created queries: 

0001.json (A simple search that looks for “Crime Drama” in the title, genres, or description)

0002.json (Like 0001 but boosts certain fields and filters by type and year, so you only get high-quality TV series)

### Commands Used

Run created queries with query_solr.py script: 

python scripts/query_solr.py --queries config/queries --uri http://localhost:8983/solr --collection media