@echo off
REM RIK Demo Launcher Script for Windows

echo 🤖 Starting Recursive Intelligence Kernel Demo...
echo.

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo 📦 Installing demo dependencies...
    pip install -r requirements-demo.txt -q
)

REM Initialize memory database if needed
if not exist "data\memory.db" (
    echo 🗄️  Initializing memory database...
    python -c "import memory; memory.init_memory_db()"
)

echo.
echo ✅ Setup complete! Launching demo...
echo.
echo 🌐 Demo will open in your browser at http://localhost:8501
echo Press Ctrl+C to stop the demo
echo.

REM Run streamlit
streamlit run demo_app.py

pause
