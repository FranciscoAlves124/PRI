import json
from datasets import load_dataset

# Load HuggingFace dataset and build a mapping from tconst to poster_url
source_ds = load_dataset("Pablinho/movies-dataset", split="train")
tconst_to_poster = {row["Title"]: row.get("Poster_Url") for row in source_ds if row.get("Title")}

input_path = "data/movies_series_mpnet.json"
output_path = "data/movies_series_with_posters.json"

# Read your dataset
with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Add poster_url from HuggingFace dataset if available
for entry in data:
    primary_title = entry.get("primaryTitle")
    original_title = entry.get("originalTitle")
    if primary_title and primary_title in tconst_to_poster:
        entry["poster_url"] = tconst_to_poster[primary_title]
        print(f"Added poster URL for {primary_title}")
    elif original_title and original_title in tconst_to_poster:
        entry["poster_url"] = tconst_to_poster[original_title]
        print(f"Added poster URL for {original_title}")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Saved with poster URLs to {output_path}")