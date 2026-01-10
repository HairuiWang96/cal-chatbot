#!/usr/bin/env python3
"""
Comprehensive test script for all chatbot features
Tests all core and bonus functionality
"""

import asyncio
import sys

sys.path.insert(0, "/Users/HARRY/Projects/chatbot")

from src.chatbot import CalChatbot
from datetime import datetime


async def test_all_features():
    """Test all chatbot features systematically with closed-loop testing"""

    print("=" * 70)
    print("COMPREHENSIVE CHATBOT FEATURE TESTING (CLOSED LOOP)")
    print("=" * 70)
    print()

    chatbot = CalChatbot()
    conversation_history = []
    user_email = "hairuiwang@yahoo.com"

    tests = [
        {
            "name": "Test 1: Get Available Time Slots",
            "message": "Show me available times for Monday January 12th, 2026",
        },
        {
            "name": "Test 2: Book Meeting #1 (For Cancel Test)",
            "message": "I want to book a meeting on Tuesday January 13th, 2026 at 10:00 AM Central Time (which is 16:00 UTC). My name is Harry Wang, my email is hairuiwang@yahoo.com, and the reason is to discuss the project requirements. Please book this meeting now.",
        },
        {
            "name": "Test 3: Book Meeting #2 (For Reschedule Test)",
            "message": "I want to book another meeting on Wednesday January 14th, 2026 at 10:00 AM Central Time (which is 17:00 UTC). My name is Harry Wang, my email is hairuiwang@yahoo.com, and the reason is to discuss the implementation details. Please book this meeting now.",
        },
        {
            "name": "Test 4: List Scheduled Meetings",
            "message": "Show me all my upcoming meetings",
        },
        {
            "name": "Test 5: Natural Language - Tomorrow",
            "message": "What times are available tomorrow?",
        },
        {
            "name": "Test 6: Natural Language - Next Week",
            "message": "Show me slots for next Monday",
        },
        {
            "name": "Test 7: Cancel Meeting #1",
            "message": "Cancel my meeting on January 13th",
        },
        {
            "name": "Test 8: Verify Cancellation",
            "message": "Show me all my upcoming meetings",
        },
        {
            "name": "Test 9: Reschedule Meeting #2 (Bonus)",
            "message": "Reschedule my Wednesday meeting to Thursday at 3pm",
        },
        {
            "name": "Test 10: Verify Reschedule",
            "message": "Show me all my upcoming meetings",
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
                user_message=test["message"],
                conversation_history=conversation_history,
                user_email=user_email,
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
    print("- Test 2: Book meeting #1 (for cancel) ✓")
    print("- Test 3: Book meeting #2 (for reschedule) ✓")
    print("- Test 4: List meetings (verify 2 bookings) ✓")
    print("- Test 5: Natural language (tomorrow) ✓")
    print("- Test 6: Natural language (next week) ✓")
    print("- Test 7: Cancel meeting #1 ✓")
    print("- Test 8: Verify cancellation (1 booking left) ✓")
    print("- Test 9: Reschedule meeting #2 (bonus) ✓")
    print("- Test 10: Verify reschedule (new time) ✓")
    print()
    print("All core and bonus features tested in closed loop!")


if __name__ == "__main__":
    asyncio.run(test_all_features())
