#!/bin/bash

set -e

echo "🚀 Starting AI Product Search Platform..."

if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

python_version=$(python --version 2>&1)
echo "✓ Using $python_version"

echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

echo "🗄️  Initializing database..."
python scripts/init_db.py

echo "🚀 Starting FastAPI server..."
echo "📍 API available at http://localhost:8000"
echo "📖 Docs available at http://localhost:8000/docs"

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
