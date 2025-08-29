#!/bin/bash

# Cancellations SOP Processor Run Script
# This script runs the application with proper environment setup

set -e  # Exit on any error

echo "🚀 Starting Cancellations SOP Processor..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from example..."
    cp env.example .env
    echo "📝 Please review and update .env file with your configuration"
fi

# Validate configuration
echo "✅ Validating configuration..."
python -c "
from src.app.config import config
errors = config.validate_config()
if errors:
    print('Configuration errors found:')
    for error in errors:
        print(f'  - {error}')
    exit(1)
print('Configuration validation passed')
"

# Run the application
echo "🌐 Starting Streamlit application..."
echo "📱 Open http://localhost:8501 in your browser"
echo "🛑 Press Ctrl+C to stop the application"
echo ""

streamlit run src/app/main.py --server.port=8501 --server.address=0.0.0.0
