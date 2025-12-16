# filepath: Milestone_3/api/server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
import requests
import sys
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Solr configuration
SOLR_BASE_URL = 'http://localhost:8983/solr'

# Load the SentenceTransformer model
model = SentenceTransformer('all-mpnet-base-v2')

@app.route('/api/solr/<core>/select', methods=['POST', 'GET'])
def proxy_solr(core):
    """
    Proxy requests to Solr to avoid CORS issues.
    
    Supports both GET and POST requests.
    For large queries (like semantic search with vectors), uses POST to Solr.
    """
    try:
        solr_url = f'{SOLR_BASE_URL}/{core}/select'
        
        if request.method == 'POST':
            # Get JSON body
            json_data = request.get_json()
            print(f"Received query params: {json_data}", file=sys.stderr)
            
            # Check if this is a large query (e.g., has vector field)
            # If query string contains vector or is very long, use POST to Solr
            query_str = json_data.get('q', '')
            use_post_to_solr = len(str(json_data)) > 2000 or '{!' in query_str
            
            if use_post_to_solr:
                print("Using POST to Solr (large query)", file=sys.stderr)
                # Send as POST to Solr with form data
                response = requests.post(
                    solr_url,
                    data=json_data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
            else:
                # Convert to Solr params format for GET request
                # Handle arrays (like fq) by creating tuples for requests
                params = []
                for key, value in json_data.items():
                    if isinstance(value, list):
                        # Multiple values for same parameter (e.g., fq)
                        for v in value:
                            params.append((key, v))
                    else:
                        params.append((key, value))
                
                print(f"Solr params: {params}", file=sys.stderr)
                
                # Forward as GET with query parameters
                response = requests.get(
                    solr_url,
                    params=params
                )
        else:
            # Forward GET request with query parameters
            response = requests.get(
                solr_url,
                params=request.args
            )
        
        print(f"Solr response status: {response.status_code}", file=sys.stderr)
        
        # Return Solr response
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            error_text = response.text
            print(f"Solr error: {error_text}", file=sys.stderr)
            return jsonify({'error': error_text}), response.status_code
    
    except requests.exceptions.RequestException as e:
        print(f"Solr request error: {e}", file=sys.stderr)
        return jsonify({'error': f'Solr connection failed: {str(e)}'}), 500
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/embed', methods=['POST'])
def get_embedding():
    """
    Generate embedding for given text.
    
    Expected JSON payload:
    {
        "text": "search query here"
    }
    
    Returns:
    {
        "embedding": [0.1, 0.2, ...]
    }
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Generate embedding
        embedding = model.encode(text, convert_to_tensor=False).tolist()
        
        return jsonify({'embedding': embedding})
    
    except Exception as e:
        print(f"Error generating embedding: {e}", file=sys.stderr)
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'model': 'all-mpnet-base-v2'})

if __name__ == '__main__':
    print("Starting Flask API server...")
    print("Model loaded: all-mpnet-base-v2")
    app.run(host='0.0.0.0', port=5000, debug=True)