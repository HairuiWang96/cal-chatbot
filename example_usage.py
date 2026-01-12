"""
Example usage script demonstrating how to interact with the chatbot via code

This file shows TWO WAYS to use the chatbot:
1. SCRIPTED MODE: Predefined example conversation (default)
2. INTERACTIVE MODE: Live terminal chat session (use --interactive flag)

WHY THIS FILE?
- Shows developers how to integrate the chatbot into their own code
- Provides a quick way to test the chatbot from the command line
- Demonstrates the chatbot.chat() method and conversation history management
- Useful for debugging without running the full web UI

HOW TO RUN:
Scripted mode (default):
  python example_usage.py

Interactive mode (live chat in terminal):
  python example_usage.py --interactive

WHAT YOU'LL LEARN:
- How to create a chatbot instance
- How to maintain conversation history across multiple messages
- How to pass user email for booking operations
- How async/await works with the chatbot
- How to handle errors from the chatbot
"""

# Import required libraries
import asyncio  # For running async functions
from src.chatbot import CalChatbot  # Our chatbot class


async def example_conversation():
    """
    SCRIPTED MODE: Run predefined example conversations

    This function demonstrates how to use the chatbot in your code.
    It shows two example interactions:
    1. Starting to book a meeting
    2. Listing scheduled meetings

    KEY CONCEPTS DEMONSTRATED:
    - Creating a chatbot instance
    - Maintaining conversation_history across multiple messages
    - Passing user_email for booking operations
    - Using async/await to call the chatbot

    This is the DEFAULT mode when you run: python example_usage.py
    """
    # Step 1: Create a chatbot instance
    # This initializes the OpenAI client and loads Cal.com API configuration
    chatbot = CalChatbot()

    # Step 2: Initialize empty conversation history
    # The history is a list of message dictionaries: [{"role": "user", "content": "..."}]
    # We start with an empty list and build it as we chat
    conversation_history = []

    # Print header
    print("=" * 60)
    print("Cal.com Chatbot - Example Conversation")
    print("=" * 60)
    print()

    # ========================================================================
    # EXAMPLE 1: Starting to book a meeting
    # ========================================================================
    # This shows the beginning of a booking flow
    # The bot will likely ask for more details (date, time, name, etc.)
    print("Example 1: Booking a meeting")
    print("-" * 60)

    # Define the user's message
    user_message = "Help me book a meeting"
    print(f"User: {user_message}")

    # Call the chatbot with:
    # - user_message: The new message to process
    # - conversation_history: Previous messages (empty for first message)
    # - user_email: The user's email (needed for booking operations)
    #
    # The chatbot returns:
    # - response: The bot's reply text
    # - conversation_history: Updated history including this exchange
    #
    # IMPORTANT: We update conversation_history with the returned value
    # This maintains context for the next message
    response, conversation_history = await chatbot.chat(
        user_message=user_message,
        conversation_history=conversation_history,
        user_email="john@example.com"
    )

    # Display the bot's response
    print(f"Bot: {response}")
    print()

    # ========================================================================
    # EXAMPLE 2: Listing scheduled meetings
    # ========================================================================
    # This shows how to query for existing bookings
    # The bot will call get_user_bookings and format the results
    print("Example 2: Listing scheduled meetings")
    print("-" * 60)

    user_message = "Show me my scheduled events"
    print(f"User: {user_message}")

    # Call the chatbot again
    # Notice we're passing the conversation_history from the previous exchange
    # This gives the bot context from Example 1 (though it's not needed for this query)
    response, conversation_history = await chatbot.chat(
        user_message=user_message,
        conversation_history=conversation_history,
        user_email="john@example.com"
    )

    print(f"Bot: {response}")
    print()

    # Print setup reminder
    # These notes help users understand why the examples might not work
    print("=" * 60)
    print("Note: To actually create bookings, make sure:")
    print("1. Your .env file is properly configured")
    print("2. You have valid Cal.com API credentials")
    print("3. You have at least one event type set up")
    print("=" * 60)


async def interactive_mode():
    """
    INTERACTIVE MODE: Live terminal chat session

    This function creates a REPL (Read-Eval-Print Loop) where you can chat
    with the bot in real-time from the terminal.

    HOW IT WORKS:
    1. Prompts for your email once at the start
    2. Enters a loop where you can type messages
    3. Each message is sent to the chatbot
    4. The bot's response is displayed
    5. Conversation history is maintained across all messages
    6. Type 'quit' or 'exit' to end

    WHY THIS IS USEFUL:
    - Quick testing without running the full web UI
    - Debug chatbot responses in real-time
    - Great for development and testing new features

    HOW TO USE:
    python example_usage.py --interactive
    """
    # Create chatbot instance
    chatbot = CalChatbot()

    # Initialize empty conversation history
    # This will grow as we chat, maintaining context across messages
    conversation_history = []

    # Print header and instructions
    print("=" * 60)
    print("Cal.com Chatbot - Interactive Mode")
    print("=" * 60)
    print("Type 'quit' or 'exit' to end the conversation")
    print()

    # Get user's email once at the start
    # .strip() removes leading/trailing whitespace
    # This email will be used for all booking operations in this session
    user_email = input("Enter your email: ").strip()

    # Main chat loop - runs forever until user types quit/exit
    while True:
        # Get user's message
        # input() waits for user to type and press Enter
        user_message = input("\nYou: ").strip()

        # Check if user wants to quit
        # .lower() converts to lowercase so "Quit", "QUIT", "quit" all work
        if user_message.lower() in ["quit", "exit"]:
            print("Goodbye!")
            break  # Exit the loop, ending the program

        # Skip empty messages (user just pressed Enter)
        if not user_message:
            continue  # Go back to top of loop, ask for input again

        # Try to send message to chatbot
        # Using try/except to catch and display any errors gracefully
        try:
            # Call chatbot with user's message
            # Pass conversation_history so bot has context from previous messages
            response, conversation_history = await chatbot.chat(
                user_message=user_message,
                conversation_history=conversation_history,
                user_email=user_email
            )

            # Display bot's response
            print(f"\nBot: {response}")

        except Exception as e:
            # If anything goes wrong (API error, network issue, etc.), display error
            # This prevents the program from crashing and lets user continue chatting
            print(f"\nError: {str(e)}")


# MAIN EXECUTION BLOCK
# This runs when you execute this file directly (not when importing it)
if __name__ == "__main__":
    # Import sys to access command line arguments
    # sys.argv is a list: [script_name, arg1, arg2, ...]
    # Example: "python example_usage.py --interactive" gives:
    #   sys.argv = ["example_usage.py", "--interactive"]
    import sys

    # Check if user passed the --interactive flag
    # len(sys.argv) > 1 means there's at least one argument
    # sys.argv[1] is the first argument after the script name
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        # Run interactive mode (live terminal chat)
        asyncio.run(interactive_mode())
    else:
        # Run scripted mode (predefined examples) - this is the default
        asyncio.run(example_conversation())

        # Print helpful tip about interactive mode
        print("\nTip: Run with --interactive flag for interactive mode")
        print("Example: python example_usage.py --interactive")
