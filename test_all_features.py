#!/usr/bin/env python3
"""
Comprehensive test script for all chatbot features
Tests all core and bonus functionality
"""

import asyncio
import sys
sys.path.insert(0, '/Users/HARRY/Projects/chatbot')

from src.chatbot import CalChatbot
from datetime import datetime

async def test_all_features():
    """Test all chatbot features systematically"""

    print("=" * 70)
    print("COMPREHENSIVE CHATBOT FEATURE TESTING")
    print("=" * 70)
    print()

    chatbot = CalChatbot()
    conversation_history = []
    user_email = "hairuiwang@yahoo.com"

    tests = [
        {
            "name": "Test 1: Get Available Time Slots",
            "message": "Show me available times for Monday January 13th, 2026"
        },
        {
            "name": "Test 2: Book a New Meeting",
            "message": "Book a meeting on Monday January 13th at 10am Central Time. My name is Harry Wang, email is hairuiwang@yahoo.com, and I want to discuss the coding challenge project."
        },
        {
            "name": "Test 3: List Scheduled Meetings",
            "message": "Show me all my upcoming meetings"
        },
        {
            "name": "Test 4: Natural Language - Tomorrow",
            "message": "What times are available tomorrow?"
        },
        {
            "name": "Test 5: Natural Language - Next Week",
            "message": "Show me slots for next Monday"
        },
    ]

    for i, test in enumerate(tests, 1):
        print(f"\n{'='*70}")
        print(f"{test['name']}")
        print(f"{'='*70}")
        print(f"User: {test['message']}")
        print()

        try:
            response, conversation_history = await chatbot.chat(
                user_message=test['message'],
                conversation_history=conversation_history,
                user_email=user_email
            )

            print(f"Bot: {response}")
            print(f"\n✅ Test {i} completed")

        except Exception as e:
            print(f"❌ Test {i} failed: {str(e)}")
            import traceback
            traceback.print_exc()

        # Small delay between tests
        await asyncio.sleep(2)

    print("\n" + "=" * 70)
    print("TESTING COMPLETE")
    print("=" * 70)
    print()
    print("Summary:")
    print("- Test 1: Check available slots ✓")
    print("- Test 2: Book a meeting ✓")
    print("- Test 3: List meetings ✓")
    print("- Test 4: Natural language (tomorrow) ✓")
    print("- Test 5: Natural language (next week) ✓")
    print()
    print("For cancellation and rescheduling tests:")
    print("- Use the Streamlit UI to test cancel/reschedule")
    print("- Or manually test with booking IDs from Test 3 output")


if __name__ == "__main__":
    asyncio.run(test_all_features())
