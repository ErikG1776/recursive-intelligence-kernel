#!/bin/bash
# RIK Demo Launcher Script

echo "🤖 Starting Recursive Intelligence Kernel Demo..."
echo ""

# Check if streamlit is installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing demo dependencies..."
    pip3 install -r requirements-demo.txt -q
fi

# Initialize memory database if needed
if [ ! -f "data/memory.db" ]; then
    echo "🗄️  Initializing memory database..."
    python3 -c "import memory; memory.init_memory_db()"
fi

echo ""
echo "✅ Setup complete! Launching demo..."
echo ""
echo "🌐 Demo will open in your browser at http://localhost:8501"
echo "Press Ctrl+C to stop the demo"
echo ""

# Run streamlit
streamlit run demo_app.py
