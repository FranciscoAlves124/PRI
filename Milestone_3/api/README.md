# Movie & Series Search Frontend

## Overview
This is the frontend interface for the PRI Movie & Series Search System (Milestone 3).

## Features
- **Basic Search**: Simple keyword-based search
- **Intermediate Search**: Advanced search with synonyms, stopwords, and custom analyzers
- **Semantic Search**: Natural language search using vector embeddings
- **Advanced Filters**: Filter by type, genre, year, rating
- **Responsive Design**: Works on desktop and mobile devices

## Setup

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Python 3.7+ (for the embedding API)
- Running Solr instances:
  - `media_basic` (port 8983)
  - `media_intermediate` (port 8983)
  - `semantic_core` (port 8983)

### Installation

1. **Install Python dependencies for the API:**
```bash
cd api
pip install flask flask-cors sentence-transformers
```

2. **Start the embedding API server:**
```bash
cd api
python server.py
```

The API will run on `http://localhost:5000`

3. **Serve the frontend:**

You can use any static file server. For example:

```bash
# Using Python's built-in server
cd frontend
python -m http.server 8000
```

Or use VS Code's Live Server extension.

4. **Access the application:**
Open your browser and navigate to:
```
http://localhost:8000
```

## Usage

### Basic Search
1. Click "Basic Search" in the navigation
2. Enter your search query
3. Click "Search" or press Enter

### Intermediate Search
1. Click "Intermediate Search"
2. Enter your query
3. Optionally, click "Toggle Filters" for advanced options
4. Click "Search"

### Semantic Search
1. Click "Semantic Search"
2. Enter a natural language query (e.g., "movies about time travel")
3. Click "Search"

### Viewing Details
Click on any result card to see full details including cast, description, and metadata.

## File Structure
```
frontend/
├── index.html          # Main HTML page
├── css/
│   ├── style.css       # Main styles
│   └── components.css  # Component styles
├── js/
│   ├── app.js          # Main application logic
│   ├── api.js          # Solr API client
│   ├── search.js       # Search manager
│   └── utils.js        # Utility functions
└── assets/             # Images and icons
```

## API Endpoints

### Embedding API (`http://localhost:5000`)
- `POST /api/embed` - Get embedding for text
- `GET /api/health` - Health check

### Solr (`http://localhost:8983/solr`)
- `POST /media_basic/select` - Basic search
- `POST /media_intermediate/select` - Intermediate search
- `POST /semantic_core/select` - Semantic search

## Troubleshooting

### CORS Errors
If you see CORS errors in the browser console:
1. Ensure the Flask API is running with CORS enabled
2. Check that Solr is configured to allow cross-origin requests

### No Results
1. Verify Solr cores are running and contain data
2. Check browser console for errors
3. Test Solr directly: `http://localhost:8983/solr/media_basic/select?q=*:*`

### Embedding API Not Working
1. Ensure Flask server is running: `python api/server.py`
2. Check the model is downloaded (first run may take time)
3. Test the endpoint: `curl http://localhost:5000/api/health`

## Development

### Adding New Features
1. Update HTML in `index.html`
2. Add styles in `css/style.css` or `css/components.css`
3. Implement logic in appropriate JS module

### Customization
- Modify color scheme in `:root` CSS variables
- Adjust results per page in `app.js` (`resultsPerPage`)
- Change Solr cores in `api.js` constructor

## License
Part of PRI Milestone 3 project.