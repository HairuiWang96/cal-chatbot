#!/bin/bash

# Cal.com Chatbot - Quick Start Script

echo "=================================================="
echo "Cal.com Chatbot - Quick Start"
echo "=================================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Copying .env.example to .env..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "📝 Please edit .env and add your API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - CAL_API_KEY"
    echo "   - CAL_USER_EMAIL"
    echo "   - CAL_EVENT_TYPE_ID"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Ask user what to run
echo "What would you like to run?"
echo ""
echo "1) Test Cal.com API connection"
echo "2) Start FastAPI server (REST API)"
echo "3) Start Streamlit UI (Web Interface)"
echo "4) Interactive CLI mode"
echo "5) Exit"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🧪 Testing Cal.com API..."
        echo ""
        python test_api.py
        ;;
    2)
        echo ""
        echo "🚀 Starting FastAPI server..."
        echo "📍 Server will be available at: http://localhost:8000"
        echo "📖 API docs at: http://localhost:8000/docs"
        echo ""
        python src/main.py
        ;;
    3)
        echo ""
        echo "🚀 Starting Streamlit UI..."
        echo "📍 UI will open in your browser automatically"
        echo ""
        streamlit run app.py
        ;;
    4)
        echo ""
        echo "💬 Starting interactive CLI mode..."
        echo ""
        python example_usage.py --interactive
        ;;
    5)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
