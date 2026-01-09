#!/usr/bin/env python3
"""
Simple CLI client for testing the chatbot REST API
Usage: python cli_client.py
"""

import requests
import json
import sys

API_URL = "http://localhost:8000"


def chat(message, conversation_history, user_email):
    """Send a chat message to the API"""
    response = requests.post(
        f"{API_URL}/chat",
        json={
            "message": message,
            "conversation_history": conversation_history,
            "user_email": user_email
        }
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def main():
    """Main CLI loop"""
    print("=" * 60)
    print("Cal.com Chatbot - CLI Client")
    print("=" * 60)
    print("This client connects to the FastAPI server")
    print(f"Make sure the server is running at {API_URL}")
    print("Type 'quit' or 'exit' to end the conversation")
    print("=" * 60)
    print()

    # Check if server is running
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code != 200:
            print(f"⚠️  Server health check failed: {response.status_code}")
            print("Make sure the FastAPI server is running:")
            print("  python src/main.py")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server!")
        print("Make sure the FastAPI server is running:")
        print("  python src/main.py")
        sys.exit(1)

    print("✅ Connected to server")
    print()

    # Get user email
    user_email = input("Enter your email (for booking queries): ").strip()
    print()

    conversation_history = []

    while True:
        user_message = input("You: ").strip()

        if user_message.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        if not user_message:
            continue

        # Send message to API
        result = chat(user_message, conversation_history, user_email)

        if result:
            bot_response = result["response"]
            conversation_history = result["conversation_history"]

            print(f"\nBot: {bot_response}\n")
        else:
            print("Failed to get response from server\n")


if __name__ == "__main__":
    main()
