import sys
import json
from sentence_transformers import SentenceTransformer

# Load the SentenceTransformer model
model = SentenceTransformer('all-mpnet-base-v2')

def get_embedding(text):
    # The model.encode() method already returns a list of floats
    return model.encode(text, convert_to_tensor=False).tolist()

if __name__ == "__main__":
    # Check if input/output files are provided as arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        # Fallback to stdin
        data = json.load(sys.stdin)

    # Update each document in the JSON data
    total = len(data)
    print(f"Generating embeddings for {total} documents...", file=sys.stderr)
    
    for i, document in enumerate(data):
        if (i + 1) % 100 == 0:
            print(f"Processing document {i + 1}/{total}...", file=sys.stderr)

        # Extract fields relevant for movies
        title = document.get("primaryTitle", "")
        description = document.get("description", "")
        # Optional: include genres or cast if you want them in the vector
        
        combined_text = title + " " + description
        document["vector"] = get_embedding(combined_text)
    
    print("Embedding generation complete.", file=sys.stderr)

    # Output updated JSON
    if len(sys.argv) > 2 and output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    else:
        json.dump(data, sys.stdout, indent=4, ensure_ascii=False)
