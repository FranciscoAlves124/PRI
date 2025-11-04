import csv
import json

def csv_to_json(csv_file_path, json_file_path):
    """
    Converts a CSV file with fields: title, quote, author, tconst
    into a JSON array of objects.
    """

    data = []
    with open(csv_file_path, mode='r', encoding='utf-8', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Clean up extra whitespace
            cleaned_row = {key: value.strip() for key, value in row.items()}
            data.append(cleaned_row)

    with open(json_file_path, mode='w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4, ensure_ascii=False)

    print(f"✅ JSON file created successfully: {json_file_path}")


if __name__ == "__main__":
    # Example usage
    csv_input = "filtered_reviews2.csv"   # Replace with your CSV file path
    json_output = "filtered_reviews2.json"
    csv_to_json(csv_input, json_output)
