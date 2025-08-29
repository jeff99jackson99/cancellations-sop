#!/bin/bash

# Cancellations SOP Processor Setup Script
# This script sets up the development environment

set -e  # Exit on any error

echo "🚀 Setting up Cancellations SOP Processor..."

# Check if Python 3.9+ is installed
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9 or higher is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "📥 Installing dependencies..."
pip install -e ".[dev]"

# Install pre-commit hooks
echo "🔒 Installing pre-commit hooks..."
pre-commit install

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p processed_reports
mkdir -p logs

# Set up environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cp env.example .env
    echo "📝 Please review and update .env file with your configuration"
fi

# Run initial tests
echo "🧪 Running initial tests..."
python -m pytest tests/ -v

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Review and update .env file if needed"
echo "2. Run 'make dev' to start the application"
echo "3. Open http://localhost:8501 in your browser"
echo ""
echo "Available commands:"
echo "  make dev          - Start development server"
echo "  make test         - Run tests"
echo "  make lint         - Run linting"
echo "  make fmt          - Format code"
echo "  make docker/build - Build Docker image"
echo "  make docker/run   - Run Docker container"
echo ""
