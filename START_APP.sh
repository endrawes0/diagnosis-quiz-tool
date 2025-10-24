#!/bin/bash
# Easy startup script for Diagnosis Quiz Tool
# For Mac/Linux users

echo "🚀 Starting Diagnosis Quiz Tool..."
echo ""
echo "📍 The app will open at: http://localhost:3000"
echo "   (Your browser will open automatically in a few seconds)"
echo ""
echo "⚠️  Keep this window open while using the app!"
echo "   Press Ctrl+C when you're done to stop everything"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if in correct directory
if [ ! -d "venv" ]; then
    echo "❌ Error: Can't find 'venv' folder"
    echo "   Make sure you're in the diagnosis-quiz-tool directory"
    echo "   and have run the setup first (see EASY_INSTALL.md)"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export FLASK_APP=src.app:create_app
export PYTHONPATH=$(pwd):$PYTHONPATH

# Start backend in background
echo "🔧 Starting backend server..."
python3 -m flask run --host=0.0.0.0 --port=5000 > logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 4

# Check if backend started
if ! ps -p $BACKEND_PID > /dev/null; then
    echo "❌ Backend failed to start. Check logs/backend.log for details"
    exit 1
fi

echo "✅ Backend ready!"
echo ""

# Start frontend
echo "🎨 Starting frontend..."
echo "   (This will open your browser automatically)"
echo ""
cd frontend

# Start frontend (this will block and open browser)
npm start

# Cleanup when frontend stops
echo ""
echo "🛑 Stopping backend server..."
kill $BACKEND_PID 2>/dev/null

echo ""
echo "✅ App stopped. Thanks for using Diagnosis Quiz Tool!"
