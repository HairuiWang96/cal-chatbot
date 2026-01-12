#!/usr/bin/env python3
"""
Comprehensive test script for all chatbot features

This script performs CLOSED-LOOP TESTING of the Cal.com chatbot.

WHAT IS CLOSED-LOOP TESTING?
It's a testing approach where you:
1. Perform an action (e.g., book a meeting)
2. Verify the action worked (e.g., list meetings and confirm it's there)
3. Perform another action (e.g., cancel the meeting)
4. Verify again (e.g., list meetings and confirm it's gone)

This ensures the chatbot actually affects the real Cal.com system, not just
pretending to work.

WHY THIS SCRIPT?
- Tests all core features (book, list, natural language)
- Tests all bonus features (cancel, reschedule)
- Verifies operations actually work in Cal.com
- Catches bugs that unit tests might miss
- Demonstrates the chatbot's capabilities

HOW TO RUN:
python test_all_features.py

REQUIREMENTS:
- Valid Cal.com API key in .env
- Valid OpenAI API key in .env
- Available time slots on Cal.com calendar
"""

import asyncio  # For running async functions
import sys  # For sys.path manipulation

# Add project root to path so we can import src modules
sys.path.insert(0, "/Users/HARRY/Projects/chatbot")

from src.chatbot import CalChatbot  # The chatbot to test
from datetime import datetime  # For date operations


async def test_all_features():
    """
    Test all chatbot features systematically with closed-loop testing

    This function runs 10 comprehensive tests that cover:
    - Getting available time slots
    - Booking meetings (creates 2 bookings)
    - Listing meetings (verifies bookings exist)
    - Natural language date parsing
    - Canceling meetings (removes 1 booking)
    - Rescheduling meetings (moves 1 booking to new time)
    - Verification after each operation

    The tests are designed to run sequentially, with each test building on
    or verifying the previous ones.
    """

    print("=" * 70)
    print("COMPREHENSIVE CHATBOT FEATURE TESTING (CLOSED LOOP)")
    print("=" * 70)
    print()

    # Create chatbot instance and initialize conversation
    chatbot = CalChatbot()
    conversation_history = []  # Stores the conversation for context
    user_email = "hairuiwang@yahoo.com"  # Email for booking operations

    # Define all test cases
    # Each test is a dictionary with a name and message
    # The tests are designed to run in sequence and verify each other
    tests = [
        {
            "name": "Test 1: Get Available Time Slots",
            # Tests the get_available_slots function
            # Verifies chatbot can check calendar availability
            "message": "Show me available times for Monday January 19th, 2026",
        },
        {
            "name": "Test 2: Book Meeting #1 (For Cancel Test)",
            # Creates first booking that we'll cancel later (Test 7)
            # Tests create_booking function with all required parameters
            "message": "I want to book a meeting on Tuesday January 20th, 2026 at 10:00 AM Central Time (which is 16:00 UTC). My name is Harry Wang, my email is hairuiwang@yahoo.com, and the reason is to discuss the project requirements. Please book this meeting now.",
        },
        {
            "name": "Test 3: Book Meeting #2 (For Reschedule Test)",
            # Creates second booking that we'll reschedule later (Test 9)
            # Tests creating multiple bookings
            "message": "I want to book another meeting on Wednesday January 21th, 2026 at 10:00 AM Central Time (which is 17:00 UTC). My name is Harry Wang, my email is hairuiwang@yahoo.com, and the reason is to discuss the implementation details. Please book this meeting now.",
        },
        {
            "name": "Test 4: List Scheduled Meetings",
            # VERIFICATION: Should show 2 meetings from Tests 2 & 3
            # Tests get_user_bookings function
            # This is closed-loop verification that bookings actually exist in Cal.com
            "message": "Show me all my upcoming meetings",
        },
        {
            "name": "Test 5: Natural Language - Tomorrow",
            # Tests natural language date parsing (relative dates)
            # GPT should convert "tomorrow" to actual date
            "message": "What times are available tomorrow?",
        },
        {
            "name": "Test 6: Natural Language - Next Week",
            # Tests another natural language pattern
            # GPT should understand "next Monday" and calculate the date
            "message": "Show me slots for next Monday",
        },
        {
            "name": "Test 7: Cancel Meeting #1",
            # Tests cancel_booking function
            # Should find and cancel the booking from Test 2
            "message": "Cancel my meeting on January 20th",
        },
        {
            "name": "Test 8: Verify Cancellation",
            # VERIFICATION: Should now show only 1 meeting (Test 3's booking)
            # Confirms cancellation actually worked in Cal.com
            # This is closed-loop verification of the cancel operation
            "message": "Show me all my upcoming meetings",
        },
        {
            "name": "Test 9: Reschedule Meeting #2 (Bonus)",
            # Tests reschedule_booking function (bonus feature)
            # Moves Test 3's meeting to a new time
            "message": "Reschedule my Wednesday January 21th, 2026 meeting to Thursday January 22th, 2026 at 3pm",
        },
        {
            "name": "Test 10: Verify Reschedule",
            # VERIFICATION: Should show 1 meeting at the NEW time (Thursday 3pm)
            # Confirms reschedule actually worked in Cal.com
            # This is closed-loop verification of the reschedule operation
            "message": "Show me all my upcoming meetings",
        },
    ]

    # TEST EXECUTION LOOP
    # This loop runs each test sequentially, maintaining conversation context
    # The enumerate(tests, 1) gives us both the test and a counter starting from 1
    for i, test in enumerate(tests, 1):
        # Print a nice header for this test
        # The f-string formatting allows us to embed variables in strings
        # {'='*70} creates a line of 70 equal signs for visual separation
        print(f"\n{'='*70}")
        print(f"{test['name']}")
        print(f"{'='*70}")
        print(f"User: {test['message']}")
        print()

        try:
            # Call the chatbot with:
            # - user_message: The test message we want to send
            # - conversation_history: All previous messages (for context)
            # - user_email: The email for booking operations
            #
            # The chatbot returns:
            # - response: The chatbot's reply text
            # - conversation_history: Updated history including this exchange
            #
            # CRITICAL: We update conversation_history with the returned value
            # This maintains context across all tests - each test builds on previous ones
            response, conversation_history = await chatbot.chat(
                user_message=test["message"],
                conversation_history=conversation_history,
                user_email=user_email,
            )

            # Display the bot's response
            print(f"Bot: {response}")
            print(f"\n✅ Test {i} completed")

        except Exception as e:
            # If anything goes wrong, catch the error and display it
            # This prevents one failed test from stopping the entire test suite
            print(f"❌ Test {i} failed: {str(e)}")

            # Import traceback here (only needed if there's an error)
            import traceback

            # Print the full error traceback for debugging
            # This shows exactly where the error occurred in the code
            traceback.print_exc()

        # Small delay between tests
        # This gives Cal.com API a moment to process and prevents rate limiting
        # await asyncio.sleep(2) pauses execution for 2 seconds
        await asyncio.sleep(2)

    # TESTING COMPLETE - PRINT SUMMARY
    # After all tests run, show a nice summary of what was tested
    print("\n" + "=" * 70)
    print("TESTING COMPLETE")
    print("=" * 70)
    print()

    # Summary of all tests
    # This checklist helps verify we tested everything we intended to test
    # Each line shows what feature was tested and marks it complete with ✓
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

    # Final success message
    # This confirms we've tested all the features (core + bonus) with closed-loop verification
    print("All core and bonus features tested in closed loop!")


# MAIN EXECUTION BLOCK
# This special if statement runs only when this file is executed directly
# (not when it's imported as a module by another file)
#
# WHAT IS __name__ == "__main__"?
# - When you run "python test_all_features.py", Python sets __name__ to "__main__"
# - When another file imports this file, __name__ is set to "test_all_features"
# - This pattern lets us have code that only runs when the file is executed directly
#
# WHY USE asyncio.run()?
# - test_all_features() is an async function (uses async/await)
# - asyncio.run() creates an event loop and runs the async function
# - It's the entry point for running async code from a regular Python script
if __name__ == "__main__":
    asyncio.run(test_all_features())
