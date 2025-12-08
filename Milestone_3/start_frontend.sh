# NOT WORKING YET

#!/bin/bash
# Start script for Movie & Series Search System
# This script starts both the Flask API server and the frontend HTTP server

echo -e "\033[0;32mStarting Movie & Series Search System...\033[0m"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check for virtual environment, create if needed
VENV_DIR="$SCRIPT_DIR/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "\033[0;33mCreating virtual environment...\033[0m"
    python3 -m venv "$VENV_DIR"
    
    echo -e "\033[0;33mInstalling dependencies...\033[0m"
    "$VENV_DIR/bin/pip" install flask flask-cors sentence-transformers
    echo -e "\033[0;32mDependencies installed!\033[0m"
fi

# Use virtual environment Python
PYTHON="$VENV_DIR/bin/python"

# Start Flask API server in background
echo -e "\n\033[0;36mStarting Flask API server on port 5000...\033[0m"
cd "$SCRIPT_DIR/api"
"$PYTHON" server.py &
API_PID=$!

# Wait a moment for API to initialize
sleep 2

# Start frontend HTTP server in background
echo -e "\033[0;36mStarting frontend server on port 8000...\033[0m"
cd "$SCRIPT_DIR/frontend"
python3 -m http.server 8000 &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 2

echo -e "\n\033[0;32m==================================================\033[0m"
echo -e "\033[0;32mSystem started successfully!\033[0m"
echo -e "\033[0;32m==================================================\033[0m"
echo -e "\n\033[0;33mAPI Server:      http://localhost:5000\033[0m"
echo -e "\033[0;33mFrontend:        http://localhost:8000\033[0m"
echo -e "\n\033[0;37mAPI PID:         $API_PID\033[0m"
echo -e "\033[0;37mFrontend PID:    $FRONTEND_PID\033[0m"
echo -e "\n\033[0;90mPress Ctrl+C to stop both servers.\033[0m"
echo -e "\033[0;90mOr run: kill $API_PID $FRONTEND_PID\033[0m"
echo -e "\033[0;32m==================================================\033[0m\n"

# Function to cleanup on exit
cleanup() {
    echo -e "\n\033[0;31mStopping servers...\033[0m"
    kill $API_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "\033[0;32mServers stopped.\033[0m"
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup INT

# Keep script running
wait
