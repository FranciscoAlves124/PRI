def generate_qrels_query1(query_id, results):
    """
    Generates qrels for a query.

    Parameters:
    - query_id: int or str, the identifier of the query.
    - results: list of dicts, each dict must have at least:
        - 'tconst': the series/movie ID
        - 'description': list containing description(s)

    Returns:
    - List of strings formatted as "query_id iter tconst relevance"
    """
    qrels = []
    for i, doc in enumerate(results):
        tconst = doc.get("tconst", [""])[0]
        description_list = doc.get("description", [])
        description_text = " ".join(description_list).lower()
        relevance = 1 if "sitcom" in description_text else 0
        qrels.append(f"{query_id} 0 {tconst} {relevance}")
    return qrels

def generate_qrels(query_id, results):
    """
    Generate qrels for a query based on top_3_cast and genres.

    Args:
        query_id (str or int): ID of the query.
        results (list of dict): List of documents returned by Solr/Elasticsearch.
            Each document should have at least 'tconst', 'top_3_cast', and 'genres'.

    Returns:
        list of str: Qrels in format "QueryID Iter tconst Relevance".
    """
    qrels = []
    for i, doc in enumerate(results):
        tconst = doc.get("tconst", [""])[0] if isinstance(doc.get("tconst"), list) else doc.get("tconst", "")
        top_3_cast_raw = doc.get("top_3_cast", [])
        top_3_cast = [actor.lower() for actor in top_3_cast_raw]
        
        genres_raw = doc.get("genres", [])
        # Genres might be ["Crime,Drama"] or ["Crime", "Drama"]
        if genres_raw and isinstance(genres_raw, list):
            genres_flat = ",".join(genres_raw).lower()
        else:
            genres_flat = ""

        # Check relevance: either actor in cast AND "crime" and "drama" in genres
        has_actor = any("robert de niro" in actor or "al pacino" in actor for actor in top_3_cast)
        has_crime_drama = "crime" in genres_flat and "drama" in genres_flat
        
        relevance = 1 if (has_actor and has_crime_drama) else 0

        qrels.append(f"{query_id} 0 {tconst} {relevance}")

    return qrels

if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path
    import glob

    solr_resultsBasicQ1 = "results/basic/query1/solr_results.json"
    solr_resultsBasicQ2 = "results/basic/query2/solr_results.json"

    solr_resultsIntermediateQ1 = "results/intermediate/query1/solr_results.json"
    solr_resultsIntermediateQ2 = "results/intermediate/query2/solr_results.json"

    qrels_outputBasicQ1 = "results/basic/query1/trec_qrels.txt"
    qrels_outputBasicQ2 = "results/basic/query2/trec_qrels.txt"

    qrels_outputIntermediateQ1 = "results/intermediate/query1/trec_qrels.txt"
    qrels_outputIntermediateQ2 = "results/intermediate/query2/trec_qrels.txt"

    # Generate QRELs for Basic Query 1
    with open(solr_resultsBasicQ1, "r") as f:
        solr_data = json.load(f)
    qrels_q1_v1 = generate_qrels_query1(1, solr_data["1"]["response"]["docs"])
    qrels_q1_v2 = generate_qrels_query1(2, solr_data["2"]["response"]["docs"])
    with open(qrels_outputBasicQ1, "w") as f:
        f.write("\n".join(qrels_q1_v1) + "\n")
        f.write("\n".join(qrels_q1_v2) + "\n")

    # Generate QRELs for Basic Query 2
    with open(solr_resultsBasicQ2, "r") as f:
        solr_data = json.load(f)
    qrels_q2_v1 = generate_qrels(1, solr_data["1"]["response"]["docs"])
    qrels_q2_v2 = generate_qrels(2, solr_data["2"]["response"]["docs"])
    with open(qrels_outputBasicQ2, "w") as f:
        f.write("\n".join(qrels_q2_v1) + "\n")
        f.write("\n".join(qrels_q2_v2) + "\n")

    # Generate QRELs for Intermediate Query 1
    with open(solr_resultsIntermediateQ1, "r") as f:
        solr_data = json.load(f)
    qrels_q1_v1_int = generate_qrels_query1(1, solr_data["1"]["response"]["docs"])
    qrels_q1_v2_int = generate_qrels_query1(2, solr_data["2"]["response"]["docs"])
    with open(qrels_outputIntermediateQ1, "w") as f:
        f.write("\n".join(qrels_q1_v1_int) + "\n")
        f.write("\n".join(qrels_q1_v2_int) + "\n")

    # Generate QRELs for Intermediate Query 2
    with open(solr_resultsIntermediateQ2, "r") as f:
        solr_data = json.load(f)
    qrels_q2_v1_int = generate_qrels(1, solr_data["1"]["response"]["docs"])
    qrels_q2_v2_int = generate_qrels(2, solr_data["2"]["response"]["docs"])
    with open(qrels_outputIntermediateQ2, "w") as f:
        f.write("\n".join(qrels_q2_v1_int) + "\n")
        f.write("\n".join(qrels_q2_v2_int) + "\n")
