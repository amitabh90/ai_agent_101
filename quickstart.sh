#!/bin/bash

echo "🚀 AI PR Agent - Quick Start Setup"
echo "=================================="
echo ""

if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your GitHub token and other credentials"
    echo ""
fi

echo "📊 Using existing PostgreSQL container..."
echo "   Make sure your PostgreSQL is running and accessible"
echo ""

if command -v docker-compose &> /dev/null; then
    read -p "Do you want to start pgAdmin for database management? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🐳 Starting pgAdmin with Docker Compose..."
        docker-compose up -d
        echo "✓ pgAdmin started on port 5050 (admin@admin.com / admin)"
        echo ""
    fi
fi

if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

echo "📦 Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "🗄️  Initializing database..."
python -m src.cli.commands init

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your GitHub token"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python -m src.cli.commands check-repo"
echo ""
echo "For help: python -m src.cli.commands --help"
