#!/bin/bash
# The shebang line above tells the system to use bash to run this script

# ============================================================================
# Cal.com Chatbot - Quick Start Script
# ============================================================================
#
#! This is a BASH SCRIPT that automates the setup and running of the chatbot.
# Think of it as a "one-click" launcher for the project.
#
#! WHAT IS A BASH SCRIPT?
# A bash script is a text file containing commands that would normally be typed
# into the terminal. Instead of typing them one by one, you can run them all
# at once by executing this script.
#
# WHY THIS SCRIPT?
# - Automates setup: Creates virtual environment, installs dependencies
# - Checks configuration: Verifies .env file exists
# - Provides menu: Lets you choose what to run (API, UI, CLI, tests)
# - Saves time: No need to remember complex commands
# - Beginner-friendly: Handles common setup issues automatically
#
# HOW TO RUN:
# From terminal in project directory:
#   chmod +x run.sh    (first time only - makes script executable)
#   ./run.sh           (runs the script)
#
# Or:
#   bash run.sh        (runs script with bash explicitly)
#
# WHAT IT DOES:
# 1. Checks if .env file exists (creates from template if missing)
# 2. Creates Python virtual environment if needed
# 3. Installs/updates dependencies
# 4. Shows menu of options (API server, web UI, CLI, tests)
# 5. Runs your choice
#
# ============================================================================

# Print welcome header
# "echo" prints text to the terminal
echo "=================================================="
echo "Cal.com Chatbot - Quick Start"
echo "=================================================="
echo ""  #! Empty line for spacing

# ============================================================================
# STEP 1: CHECK IF .env FILE EXISTS
# ============================================================================
# The .env file contains API keys and configuration (not committed to git)
# We need this file to run the chatbot successfully

# Check if .env file exists
# [ ! -f .env ] means "if .env file does NOT exist"
# -f checks if file exists and is a regular file
# ! means "not" (negation)
if [ ! -f .env ]; then
    # If .env doesn't exist, create it from the template
    echo "⚠️  .env file not found!"
    echo "Copying .env.example to .env..."

    # cp copies .env.example to .env
    # .env.example is the template with placeholder values
    cp .env.example .env

    echo "✅ Created .env file"
    echo ""

    # Remind user to add their actual API keys
    # These are placeholders in .env.example that need real values
    echo "📝 Please edit .env and add your API keys:"
    echo "   - OPENAI_API_KEY      (from OpenAI dashboard)"
    echo "   - CAL_API_KEY         (from Cal.com settings)"
    echo "   - CAL_USER_EMAIL      (your email address)"
    echo "   - CAL_EVENT_TYPE_ID   (from Cal.com event types)"
    echo ""
    echo "Then run this script again."

    #! Exit with error code 1 (non-zero means error)
    # This stops the script so user can add their keys
    exit 1
fi

# ============================================================================
# STEP 2: CREATE VIRTUAL ENVIRONMENT IF NEEDED
# ============================================================================
# A virtual environment is an isolated Python environment for this project
# It prevents conflicts with other Python projects on your system

# Check if venv directory exists
# [ ! -d "venv" ] means "if venv directory does NOT exist"
#! -d checks if it's a directory
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."

    # python3 -m venv venv creates a virtual environment
    # -m venv runs the venv module
    # The last "venv" is the directory name where it's created
    python3 -m venv venv

    echo "✅ Virtual environment created"
    echo ""
fi

# ============================================================================
# STEP 3: ACTIVATE VIRTUAL ENVIRONMENT
# ============================================================================
#! Activating makes this terminal session use the virtual environment's Python
#! All pip installs and python commands will use this isolated environment

echo "🔧 Activating virtual environment..."

#! source runs the activate script which modifies the shell environment
#! venv/bin/activate sets up PATH and other variables
# After this, "python" and "pip" will use the virtual environment
source venv/bin/activate

# ============================================================================
# STEP 4: INSTALL/UPDATE DEPENDENCIES
# ============================================================================
# Install all Python packages needed by the project

echo "📥 Installing dependencies..."

# Upgrade pip to latest version (pip is Python's package installer)
#! -q means "quiet" (less output)
# --upgrade means replace with newer version if available
pip install -q --upgrade pip

# Install all packages listed in requirements.txt
# requirements.txt contains: fastapi, openai, streamlit, etc.
# -q means quiet mode
#! -r means "read from requirements file"
pip install -q -r requirements.txt

echo "✅ Dependencies installed"
echo ""

# ============================================================================
# STEP 5: SHOW MENU AND GET USER CHOICE
# ============================================================================
# Present options to the user and read their selection

# Ask user what to run
echo "What would you like to run?"
echo ""

# Display menu options
# Each option runs a different part of the chatbot system
echo "1) Test Cal.com API connection"    # Diagnostic tool - verify API setup
echo "2) Start FastAPI server (REST API)"  # Backend server for API clients
echo "3) Start Streamlit UI (Web Interface)"  # Web-based chat UI
echo "4) Interactive CLI mode"           # Terminal-based chat
echo "5) Exit"                           # Quit the script
echo ""

# read prompts user for input
#! -p displays a prompt message
# The user's input is stored in the variable "choice"
read -p "Enter your choice (1-5): " choice

# ============================================================================
# STEP 6: EXECUTE USER'S CHOICE
# ============================================================================
# Use a case statement to handle different menu options
# Similar to switch/case in other languages

# case $choice in means "check the value of $choice against these patterns"
case $choice in
    # ========================================================================
    # OPTION 1: Test Cal.com API Connection
    # ========================================================================
    # Runs the diagnostic script to verify API keys and configuration
    1)
        echo ""
        echo "🧪 Testing Cal.com API..."
        echo ""

        # Run the API test script
        # This checks: API key validity, event types, availability, bookings
        python test_api.py

        # ;; ends this case branch (like "break" in other languages)
        ;;

    # ========================================================================
    # OPTION 2: Start FastAPI Server
    # ========================================================================
    # Launches the REST API server for API clients to connect to
    2)
        echo ""
        echo "🚀 Starting FastAPI server..."
        echo "📍 Server will be available at: http://localhost:8000"
        echo "📖 API docs at: http://localhost:8000/docs"
        echo ""

        # Run the FastAPI server (main.py)
        # This starts a web server that listens on port 8000
        # The server handles POST /chat requests from API clients
        # Press Ctrl+C to stop the server
        python src/main.py
        ;;

    # ========================================================================
    # OPTION 3: Start Streamlit Web UI
    # ========================================================================
    # Launches the web-based chat interface
    3)
        echo ""
        echo "🚀 Starting Streamlit UI..."
        echo "📍 UI will open in your browser automatically"
        echo ""

        # Run Streamlit web app (app.py)
        # streamlit run starts a web server on port 8501
        # It automatically opens your browser to http://localhost:8501
        # You'll see a chat interface where you can talk to the bot
        # Press Ctrl+C to stop the server
        streamlit run app.py
        ;;

    # ========================================================================
    # OPTION 4: Interactive CLI Mode
    # ========================================================================
    # Runs the chatbot in terminal with live chat interaction
    4)
        echo ""
        echo "💬 Starting interactive CLI mode..."
        echo ""

        # Run example_usage.py in interactive mode
        # This lets you chat with the bot directly in the terminal
        # No web browser needed - just type your messages
        # Type "quit" or "exit" to end the session
        python example_usage.py --interactive
        ;;

    # ========================================================================
    # OPTION 5: Exit
    # ========================================================================
    # User chose to quit
    5)
        echo "Goodbye!"

        #! exit 0 means successful exit (no error)
        # Exit code 0 indicates everything went well
        exit 0
        ;;

    # ========================================================================
    # DEFAULT: Invalid Choice
    # ========================================================================
    # User entered something other than 1-5
    # * matches any value not matched above
    *)
        echo "Invalid choice"

        # exit 1 means error exit
        # Non-zero exit codes indicate something went wrong
        exit 1
        ;;

# esac ends the case statement (it's "case" spelled backwards!)
esac
