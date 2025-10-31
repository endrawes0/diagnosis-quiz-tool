#!/bin/bash
# Start the Diagnosis Quiz Tool API server

# Load environment variables
export $(cat .env | xargs)

# Activate virtual environment
source venv/bin/activate

# Set Flask environment
export FLASK_APP=src.app:create_app
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start server
echo "Starting Diagnosis Quiz Tool API Server..."
echo "Server will be available at http://localhost:${FLASK_PORT:-5000}"
echo "Press Ctrl+C to stop"
echo ""

python3 -m flask run --host=${FLASK_HOST:-0.0.0.0} --port=${FLASK_PORT:-5000}
