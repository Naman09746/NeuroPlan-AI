#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting NeuroPlan AI Backend Setup..."

# Ensure we are in the backend directory
cd "$(dirname "$0")"

# 1. Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# 2. Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# 3. Update pip and install requirements
echo "📥 Installing/Updating dependencies (this may take a moment)..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Set Python Path to include the current directory
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 5. Run database migrations
echo "🗄️ Running database migrations..."
alembic upgrade head

# 6. Start Ollama Local AI Server (in background)
echo "🧠 Starting Ollama local AI server..."
if ! curl -s http://localhost:11434 >/dev/null ; then
    nohup ollama serve > ollama.log 2>&1 &
    sleep 3
    echo "✅ Ollama started."
else
    echo "✅ Ollama is already running."
fi

# 7. Clear port 8000 if it's in use
echo "🧹 Checking for existing processes on port 8000..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ Port 8000 is busy. Clearing it..."
    kill -9 $(lsof -t -i:8000) || true
    sleep 1
fi

# 8. Start the server
echo "🔥 Starting Uvicorn server on http://localhost:8000..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
