#!/bin/bash
# Startup script for Enterprise Knowledge Assistant

set -e

echo "🚀 Starting Enterprise Knowledge Assistant..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Load environment variables
export $(cat .env | xargs)

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [[ "$python_version" < "$required_version" ]]; then
    echo "❌ Python $required_version or higher is required (found $python_version)"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d venv ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate || . venv/Scripts/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Initialize database
echo "🗄️  Initializing database..."
python -m alembic upgrade head 2>/dev/null || echo "Skipping Alembic (not configured)"

# Start the application
echo "🎉 Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
