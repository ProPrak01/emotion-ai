#!/bin/bash

# Emotion Music Generator - Run Script

echo "🎵 Starting Emotion Music Generator..."
echo "=================================="

# Check if running with Docker
if [ "$1" == "docker" ]; then
    echo "Running with Docker..."
    cd docker
    docker-compose up --build
    exit 0
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
cd backend
pip install -r requirements.txt

# Create necessary directories
mkdir -p models logs ../frontend/assets/music/{happy,sad,angry,surprise,neutral,fear,disgust}

# Start the application
echo ""
echo "Starting FastAPI server..."
echo "=================================="
echo "🌐 Open http://localhost:8000 in your browser"
echo "📸 Make sure to allow camera access when prompted"
echo "🎵 Enjoy the emotion-driven music experience!"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="

python app.py