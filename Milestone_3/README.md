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

Run Trec Files pipeline 

./pipelines/get_trec_files.sh

Run Analize Querys pipeline

./scripts/pipeline.sh

## Running Solr and creating cores (Bash and PowerShell commands)

Notes:
- The startup script now applies the intermediate schema before indexing (it prefers `apply_schema.py` if present).
- If you want to force core recreation, run the startup script with `--recreate` (e.g. `./startup.sh intermediate --recreate`).

### Common prerequisites
- Docker installed and running
- Python 3 available (for apply_schema.py helper)

---

### Bash (Linux / macOS / WSL)

#### start Solr container (runs standalone Solr on port 8983)
docker pull solr:9
docker run -d -p 8983:8983 --name initial_solr -v "$(pwd):/data" solr:9

#### create schemaless core (basic)
docker exec initial_solr solr create -c media_basic -n data_driven_schema_configs

#### create strict core for intermediate (non-schemaless)
docker exec initial_solr solr create -c media_intermediate -n basic_configs

#### apply intermediate schema (preferred helper)
python3 apply_schema.py --core media_intermediate --file intermediate_schema.json

#### verify schema applied
curl 'http://localhost:8983/solr/media_intermediate/schema/fields?wt=json' | sed -n '1,200p'

#### index **(fixed cast)** documents (only after schema applied)
docker exec initial_solr solr post -c media_basic /data/final_data_solr/movies_series_fixed.json
docker exec initial_solr solr post -c media_intermediate /data/final_data_solr/movies_series_fixed.json
docker cp ./synonyms.txt initial_solr:/var/solr/data/media_intermediate/conf/synonyms.txt


# optional: run the bash startup helper (will apply schema first if apply_schema.py is present)
bash startup.sh intermediate --recreate

---

### PowerShell (Windows)

#### start Solr container (PowerShell; mounts current dir, **current directory (cd) should be on /Milestone_2**)
docker pull solr:9
docker run -d -p 8983:8983 --name initial_solr -v ${PWD}:/data solr:9

#### create schemaless core (basic)
docker exec initial_solr solr create -c media_basic -n data_driven_schema_configs

#### create strict core for intermediate (non-schemaless)
docker exec initial_solr solr create -c media_intermediate -n basic_configs

#### apply intermediate schema (preferred helper)
python .\apply_schema.py --core media_intermediate --file .\intermediate_schema.json

#### verify schema applied (PowerShell)
Invoke-RestMethod -Uri 'http://localhost:8983/solr/media_intermediate/schema/fields?wt=json' -Method Get

#### index **(fixed)** documents Basic (only after schema applied)
docker exec initial_solr solr post -c media_basic /data/final_data_solr/movies_series_fixed.json

#### index **(fixed)** documents Intermediate (only after schema applied)
docker exec initial_solr solr post -c media_intermediate /data/final_data_solr/movies_series_fixed.json

#### optional: run the startup script from WSL/Git-Bash, or run in PowerShell via WSL:
wsl bash ./startup.sh intermediate --recreate

---

### Synonyms

File-based (SynonymGraphFilterFactory)
- Place synonyms at `Milestone_2/synonyms.txt`.
- Copy into the core conf and reload:
  - docker cp ./Milestone_2/synonyms.txt initial_solr:/var/solr/data/media_intermediate/conf/synonyms.txt
  - curl "http://localhost:8983/solr/admin/cores?action=RELOAD&core=media_intermediate"


---

### Troubleshooting notes
- If schema apply fails with HTTP 400 about "docValues" or missing types:
  - Use the helper `apply_schema.py` (it will add missing types/fields instead of blindly replacing).
  - TextField types do not support `docValues=true`; use a StrField (string) or add a copy-field to a StrField for docValues usage.
- If startup reports "core present but conf dir missing", run `docker exec initial_solr bash -lc 'rm -rf /var/solr/data/media_intermediate || true'` and recreate the core.

### Qrels Commands

python scripts/make_qrels.py