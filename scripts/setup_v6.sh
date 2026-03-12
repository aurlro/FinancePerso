#!/bin/bash

# FinancePerso v6.0 Setup Script
# Sets up the development environment

set -e

echo "🚀 FinancePerso v6.0 Setup"
echo "=========================="

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if [ "$(printf '%s\n' "3.11" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.11" ]; then
    echo "❌ Python 3.11+ is required (found $PYTHON_VERSION)"
    exit 1
fi

echo "✅ Prerequisites OK"

# Setup backend
echo ""
echo "🔧 Setting up Backend..."
cd server

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "✅ Backend setup complete"
deactivate
cd ..

# Setup frontend
echo ""
echo "🔧 Setting up Frontend..."
cd client

if command -v pnpm &> /dev/null; then
    echo "Installing with pnpm..."
    pnpm install
elif command -v npm &> /dev/null; then
    echo "Installing with npm..."
    npm install
else
    echo "❌ Neither pnpm nor npm found"
    exit 1
fi

echo "✅ Frontend setup complete"
cd ..

# Setup environment files
echo ""
echo "📝 Setting up environment files..."

if [ ! -f "server/.env" ]; then
    cp server/.env.example server/.env
    echo "✅ Created server/.env"
fi

if [ ! -f "client/.env" ]; then
    cp client/.env.example client/.env
    echo "✅ Created client/.env"
fi

# Create data directory
mkdir -p Data

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo ""
echo "1. Start the backend:"
echo "   cd server && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "2. Start the frontend (in another terminal):"
echo "   cd client && pnpm dev"
echo ""
echo "3. Open http://localhost:5173 in your browser"
echo ""
echo "API documentation available at http://localhost:8000/docs"
