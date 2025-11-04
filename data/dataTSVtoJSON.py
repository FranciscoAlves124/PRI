import csv
import json
import ast

def tsv_to_json(tsv_file_path, json_file_path):
    """
    Converts a TSV file (tab-separated) with movie/series data
    into a JSON array of structured objects.
    """

    data = []
    with open(tsv_file_path, mode='r', encoding='utf-8', newline='') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        for row in reader:
            cleaned_row = {}
            for key, value in row.items():
                value = value.strip() if isinstance(value, str) else value

                # Handle null or placeholder values
                if value in ('\\N', '', None):
                    cleaned_row[key] = None
                    continue

                # Attempt to convert numeric fields automatically
                if key in ('startYear', 'endYear', 'runtimeMinutes', 'numVotes'):
                    try:
                        cleaned_row[key] = int(value)
                    except ValueError:
                        cleaned_row[key] = None
                elif key in ('averageRating', 'weightedRating'):
                    try:
                        cleaned_row[key] = float(value)
                    except ValueError:
                        cleaned_row[key] = None
                elif key == 'top_3_cast':
                    # Safely evaluate stringified list of tuples
                    try:
                        cleaned_row[key] = ast.literal_eval(value)
                    except (ValueError, SyntaxError):
                        cleaned_row[key] = value
                elif key == 'genres':
                    # Split genres by comma into a list
                    cleaned_row[key] = [g.strip() for g in value.split(',') if g.strip()]
                else:
                    cleaned_row[key] = value

            data.append(cleaned_row)

    with open(json_file_path, mode='w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4, ensure_ascii=False)

    print(f"✅ JSON file created successfully: {json_file_path}")


if __name__ == "__main__":
    # Example usage
    tsv_input = "FinalData.tsv"   # Replace with your TSV file path
    json_output = "FinalData.json"
    tsv_to_json(tsv_input, json_output)
