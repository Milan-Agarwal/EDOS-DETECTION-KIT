#!/bin/bash

# EDoS Security Dashboard Backend Startup Script

echo "🚀 Starting EDoS Security Dashboard Backend"
echo "==========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Start the FastAPI server
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📚 API Documentation available at http://localhost:8000/api/docs"
echo ""
echo "Press Ctrl+C to stop the server"

# Run the application
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
