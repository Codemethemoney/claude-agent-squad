#!/bin/bash
# Start Jump Codes CLI for Claude Agent Squad

echo "🚀 Starting Claude Agent Squad Jump Codes System..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

# Navigate to the correct directory
cd python_agent_squad || exit 1

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Check if requirements are installed
if ! python -c "import yaml" &> /dev/null; then
    echo "📥 Installing requirements..."
    pip install -r requirements.txt
fi

# Start the CLI
echo ""
echo "✨ Starting Jump Code CLI..."
echo ""
python jump_code_cli.py
