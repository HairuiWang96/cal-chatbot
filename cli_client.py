#!/usr/bin/env python3
"""
Simple CLI client for testing the chatbot REST API

This is a COMMAND LINE CLIENT that talks to the FastAPI server (main.py).
Think of it as a terminal-based alternative to the Streamlit web UI.

THE ARCHITECTURE:
┌─────────────┐    HTTP/REST    ┌──────────────┐    Function    ┌──────────┐
│ cli_client  │  ───────────>   │ main.py      │    Calls   ───>│ chatbot  │
│   (this)    │ <───────────    │ (FastAPI)    │ <──────────    │   .py    │
└─────────────┘    JSON         └──────────────┘                └──────────┘

WHY THIS FILE?
- Test the REST API directly without a web browser
- Useful for development and debugging
- Shows how external clients can integrate with the API
- Demonstrates proper API request/response handling

!WHEN TO USE THIS vs EXAMPLE_USAGE.PY?
- example_usage.py: Imports chatbot directly (no server needed)
- cli_client.py: Calls the API over HTTP (server must be running)

HOW TO USE:
1. Start the FastAPI server: python src/main.py
2. In another terminal, run: python cli_client.py
3. Enter your email and start chatting!

REQUIREMENTS:
- FastAPI server must be running (src/main.py)
- Server must be accessible at http://localhost:8000
"""

# Import required libraries
import requests  # HTTP library for making API calls
import json  # For JSON serialization/deserialization (imported but not used directly)
import sys  # For sys.exit() to exit the program with error codes

# API base URL - where the FastAPI server is running
# This assumes the server is running locally on port 8000 (default for FastAPI)
API_URL = "http://localhost:8000"


def chat(message, conversation_history, user_email):
    """
    Send a chat message to the API server

    This function makes an HTTP POST request to the /chat endpoint.
    It sends the user's message along with conversation history and email.

    WHAT HAPPENS:
    1. Package the message, history, and email into JSON
    2. Send POST request to http://localhost:8000/chat
    3. Wait for the server to process and respond
    4. Parse the JSON response and return it

    Args:
        message: The user's new message (string)
        conversation_history: List of previous messages (list of dicts)
        user_email: User's email for booking operations (string)

    Returns:
        Dictionary with "response" and "conversation_history" fields
        Or None if the request failed

    HTTP STATUS CODES:
    - 200: Success - request worked
    - 4xx: Client error - bad request, invalid data, etc.
    - 5xx: Server error - server crashed, internal error, etc.
    """
    # Make POST request to /chat endpoint
    # requests.post() sends an HTTP POST with JSON body
    #! The json= parameter automatically:
    # 1. Converts the dict to JSON string
    # 2. Sets Content-Type header to application/json
    response = requests.post(
        f"{API_URL}/chat",  # Full URL: http://localhost:8000/chat
        json={
            # This dictionary matches the ChatRequest model in models.py
            "message": message,
            "conversation_history": conversation_history,
            "user_email": user_email,
        },
    )

    # Check if request succeeded
    # Status code 200 means OK (successful)
    if response.status_code == 200:
        # Parse JSON response into Python dictionary
        # response.json() converts the JSON string to a dict
        # This dict matches the ChatResponse model in models.py
        return response.json()
    else:
        # Request failed - print error details
        print(f"Error: {response.status_code}")
        print(response.text)  # Raw error message from server
        return None  # Signal failure to caller


def main():
    """
    Main CLI loop - the interactive chat interface

    This function:
    1. Checks if the server is running
    2. Gets user's email
    3. Enters a loop where user can chat with the bot
    4. Maintains conversation history across all messages
    5. Handles errors gracefully

    CONTROL FLOW:
    1. Health check server
    2. Get email from user
    3. Loop: get message -> send to API -> display response
    4. Exit when user types quit/exit/q
    """
    # Print welcome header
    print("=" * 60)
    print("Cal.com Chatbot - CLI Client")
    print("=" * 60)
    print("This client connects to the FastAPI server")
    print(f"Make sure the server is running at {API_URL}")
    print("Type 'quit' or 'exit' to end the conversation")
    print("=" * 60)
    print()

    # ========================================================================
    # HEALTH CHECK: Verify server is running before starting
    # ========================================================================
    # This prevents confusing errors if user forgot to start the server
    try:
        # Make GET request to /health endpoint
        # This is a simple endpoint that just returns {"status": "ok"}
        response = requests.get(f"{API_URL}/health")

        # Check if health check succeeded
        if response.status_code != 200:
            # Server responded but with an error status
            print(f"⚠️  Server health check failed: {response.status_code}")
            print("Make sure the FastAPI server is running:")
            print("  python src/main.py")
            sys.exit(1)  # Exit with error code 1 (non-zero = error)

    except requests.exceptions.ConnectionError:
        # Server is not running or not reachable
        # ConnectionError = cannot connect to the server at all
        print("❌ Cannot connect to server!")
        print("Make sure the FastAPI server is running:")
        print("  python src/main.py")
        sys.exit(1)  # Exit with error code

    # If we get here, server is running and healthy!
    print("✅ Connected to server")
    print()

    # ========================================================================
    # GET USER EMAIL
    # ========================================================================
    # Get user's email once at the start (used for all booking operations)
    user_email = input("Enter your email (for booking queries): ").strip()
    print()

    # Initialize empty conversation history
    # This will grow as we chat, maintaining context
    conversation_history = []

    # ========================================================================
    # MAIN CHAT LOOP
    # ========================================================================
    # This loop runs forever until user types quit/exit
    while True:
        # Get user's message
        user_message = input("You: ").strip()

        # Check if user wants to quit
        # Supports "quit", "exit", or "q" (all case-insensitive)
        if user_message.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break  # Exit the loop, ending the program

        # Skip empty messages (user just pressed Enter)
        if not user_message:
            continue  # Go back to top of loop

        # Send message to API server
        # The chat() function handles the HTTP request
        result = chat(user_message, conversation_history, user_email)

        # Check if request succeeded
        if result:
            # Extract response text from the result
            # result is a dict like: {"response": "...", "conversation_history": [...]}
            bot_response = result["response"]

            # Update our conversation history with the server's version
            # The server adds both our message and the bot's response
            # IMPORTANT: We must use the server's history (not build our own)
            # because the server's history includes the exact format needed
            conversation_history = result["conversation_history"]

            # Display bot's response
            print(f"\nBot: {bot_response}\n")
        else:
            # Request failed (chat() returned None)
            # Error details were already printed by chat()
            print("Failed to get response from server\n")


# MAIN EXECUTION BLOCK
# This runs when you execute this file directly: python cli_client.py
if __name__ == "__main__":
    main()  # Start the CLI chat interface
