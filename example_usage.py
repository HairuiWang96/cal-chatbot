"""
Example usage script demonstrating how to interact with the chatbot via code
"""

import asyncio
from src.chatbot import CalChatbot


async def example_conversation():
    """Example conversation with the chatbot"""
    chatbot = CalChatbot()
    conversation_history = []

    print("=" * 60)
    print("Cal.com Chatbot - Example Conversation")
    print("=" * 60)
    print()

    # Example 1: Booking a meeting
    print("Example 1: Booking a meeting")
    print("-" * 60)

    user_message = "Help me book a meeting"
    print(f"User: {user_message}")

    response, conversation_history = await chatbot.chat(
        user_message=user_message,
        conversation_history=conversation_history,
        user_email="john@example.com"
    )

    print(f"Bot: {response}")
    print()

    # Example 2: Listing meetings
    print("Example 2: Listing scheduled meetings")
    print("-" * 60)

    user_message = "Show me my scheduled events"
    print(f"User: {user_message}")

    response, conversation_history = await chatbot.chat(
        user_message=user_message,
        conversation_history=conversation_history,
        user_email="john@example.com"
    )

    print(f"Bot: {response}")
    print()

    print("=" * 60)
    print("Note: To actually create bookings, make sure:")
    print("1. Your .env file is properly configured")
    print("2. You have valid Cal.com API credentials")
    print("3. You have at least one event type set up")
    print("=" * 60)


async def interactive_mode():
    """Interactive mode for testing"""
    chatbot = CalChatbot()
    conversation_history = []

    print("=" * 60)
    print("Cal.com Chatbot - Interactive Mode")
    print("=" * 60)
    print("Type 'quit' or 'exit' to end the conversation")
    print()

    user_email = input("Enter your email: ").strip()

    while True:
        user_message = input("\nYou: ").strip()

        if user_message.lower() in ["quit", "exit"]:
            print("Goodbye!")
            break

        if not user_message:
            continue

        try:
            response, conversation_history = await chatbot.chat(
                user_message=user_message,
                conversation_history=conversation_history,
                user_email=user_email
            )

            print(f"\nBot: {response}")
        except Exception as e:
            print(f"\nError: {str(e)}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        asyncio.run(interactive_mode())
    else:
        asyncio.run(example_conversation())
        print("\nTip: Run with --interactive flag for interactive mode")
        print("Example: python example_usage.py --interactive")
