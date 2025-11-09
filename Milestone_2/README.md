
# 06-evaluation Simplified

Created queries: 

0001.json (A simple search that looks for “Crime Drama” in the title, genres, or description)

0002.json (Like 0001 but boosts certain fields and filters by type and year, so you only get high-quality TV series)

Created the Qrels in results/trec_qrels.txt

### Commands Used

Install Dependencies:

sudo apt update
sudo apt install -y python3-venv build-essential python3-dev

cd Milestone_2
python3 -m venv .venv
source .venv/bin/activate

sudo apt install -y libfreetype6-dev libpng-dev

python -m pip install --upgrade pip
pip install matplotlib numpy pandas scikit-learn pytrec_eval==0.5

Run created queries with query_solr.py script: 

python scripts/query_solr.py --queries config/queries --uri http://localhost:8983/solr --collection media

Run pipeline 

./scripts/pipeline.sh
