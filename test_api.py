"""
Test script to verify Cal.com API connectivity and endpoints

This script tests your Cal.com API integration BEFORE you use the chatbot.
Think of it as a diagnostic tool - it checks if everything is configured correctly.

WHY THIS FILE?
- Verify Cal.com API key works
- Check if event types are set up
- Test availability and booking endpoints
- Identify configuration issues early
- Provide helpful error messages and tips

WHEN TO RUN THIS:
- First time setting up the project
- After changing Cal.com API credentials
- When troubleshooting API connection issues
- Before running the full chatbot

WHAT IT TESTS:
1. API client initialization (checks API key validity)
2. Getting event types (lists your Cal.com event types)
3. Getting available slots (checks availability API)
4. Getting bookings (tests booking retrieval)
5. Configuration checklist (verifies .env file)

HOW TO RUN:
python test_api.py

EXPECTED OUTPUT:
- Green checkmarks (✅) for successful tests
- Red X marks (❌) for failures with error details
- Yellow warnings (⚠️) for missing configuration
- Helpful tips for fixing issues
"""

# Import required libraries
import asyncio  # For running async functions
import os  # For reading environment variables
from datetime import datetime, timedelta  # For date calculations (tomorrow's date)
from dotenv import load_dotenv  # For loading .env file
from src.cal_api import CalApiClient  # Our Cal.com API wrapper

# Load environment variables from .env file
# This loads CAL_API_KEY, OPENAI_API_KEY, CAL_EVENT_TYPE_ID, etc.
load_dotenv()


async def test_cal_api():
    """
    Test Cal.com API endpoints systematically

    This function runs multiple tests in sequence:
    1. Initialize API client (validates API key)
    2. Get event types (lists available meeting types)
    3. Get available slots (checks scheduling API)
    4. Get bookings (tests booking retrieval)
    5. Show configuration checklist

    Each test is wrapped in try/except to catch and display errors gracefully.
    Tests continue even if earlier tests fail, giving full diagnostic picture.
    """
    # Print header
    print("=" * 60)
    print("Testing Cal.com API Integration")
    print("=" * 60)

    # Outer try/except catches catastrophic failures (like missing API key)
    try:
        # ====================================================================
        # INITIALIZE API CLIENT
        # ====================================================================
        # This validates the API key and sets up the HTTP client
        # If API key is missing or invalid, this will raise an error
        client = CalApiClient()
        print("✅ Cal.com API client initialized successfully")
        print(f"   Base URL: {client.base_url}")
        print()

        # ====================================================================
        # TEST 1: GET EVENT TYPES
        # ====================================================================
        # Event types are the different kinds of meetings you can schedule
        # (e.g., "30 min meeting", "1 hour consultation")
        # This test verifies we can fetch them from Cal.com
        print("Test 1: Getting event types...")
        try:
            # Call the API to get event types
            event_types = await client.get_event_types()

            # Debug output - shows the raw response structure
            # Useful for understanding what Cal.com returns
            print(f"   Raw response type: {type(event_types)}")
            print(f"   Raw response: {event_types}")
            print()

            # Display results
            print(f"✅ Found {len(event_types)} event type(s)")

            # List each event type with details
            if event_types:
                for et in event_types:
                    # Extract key fields from each event type
                    # .get() is safe - returns None if field doesn't exist
                    print(f"   - ID: {et.get('id')}, Title: {et.get('title')}, Slug: {et.get('slug')}")

                # Helpful tip: Users need to configure one of these IDs
                print(f"\n💡 Tip: Use one of these IDs in your .env file as CAL_EVENT_TYPE_ID")
            else:
                # No event types found - user needs to create one in Cal.com
                print("⚠️  No event types found. Please create an event type in Cal.com")
            print()

        except Exception as e:
            # If this test fails, show the error but continue with other tests
            import traceback
            print(f"❌ Failed to get event types: {str(e)}")
            traceback.print_exc()  # Show full stack trace for debugging
            print()

        # ====================================================================
        # TEST 2: GET AVAILABLE SLOTS
        # ====================================================================
        # This tests the availability checking API - can we see free time slots?
        # Only runs if CAL_EVENT_TYPE_ID is configured in .env
        event_type_id = os.getenv("CAL_EVENT_TYPE_ID")

        if event_type_id:
            print("Test 2: Getting available slots...")
            try:
                # Calculate tomorrow's date
                # We check tomorrow instead of today to avoid timezone issues
                tomorrow = datetime.now() + timedelta(days=1)

                # Convert to ISO format with Z suffix (UTC timezone)
                # Start of day: 00:00:00
                # End of day: 23:59:59
                # .isoformat() converts datetime to string like "2026-01-15T00:00:00"
                # We add "Z" to indicate UTC timezone
                start_time = tomorrow.replace(hour=0, minute=0, second=0).isoformat() + "Z"
                end_time = tomorrow.replace(hour=23, minute=59, second=59).isoformat() + "Z"

                # Call API to get available slots for tomorrow
                # event_type_id must be an integer, so we convert the string from .env
                slots = await client.get_available_slots(
                    event_type_id=int(event_type_id),
                    start_time=start_time,
                    end_time=end_time
                )

                # Display results
                print(f"✅ Found {len(slots)} available slot(s) for tomorrow")

                # Show first 5 slots as examples (avoid cluttering output)
                if slots:
                    for slot in slots[:5]:  # [:5] gets first 5 items
                        print(f"   - {slot.get('time')}")
                print()

            except Exception as e:
                # Availability check failed - could be invalid event type ID,
                # calendar access issue, or API error
                print(f"❌ Failed to get available slots: {str(e)}")
                print()
        else:
            # Skip this test if event type ID is not configured
            # Not a failure - just means user hasn't set it up yet
            print("Test 2: Skipped (CAL_EVENT_TYPE_ID not configured)")
            print()

        # ====================================================================
        # TEST 3: GET BOOKINGS
        # ====================================================================
        # This tests the booking retrieval API - can we list scheduled meetings?
        # Only runs if CAL_USER_EMAIL is configured in .env
        print("Test 3: Getting bookings...")
        user_email = os.getenv("CAL_USER_EMAIL")

        if user_email:
            try:
                # Call API to get bookings for this user
                # status="upcoming" means future meetings (not past or cancelled)
                # attendee_email filters to only this user's meetings
                bookings = await client.get_bookings(
                    status="upcoming",
                    attendee_email=user_email
                )

                # Display results
                print(f"✅ Found {len(bookings)} upcoming booking(s)")

                # Show first 3 bookings as examples
                if bookings:
                    for booking in bookings[:3]:  # [:3] gets first 3 items
                        # Extract and display key booking details
                        print(f"   - ID: {booking.get('id')}, Start: {booking.get('startTime')}")
                print()

            except Exception as e:
                # Booking retrieval failed - could be invalid email,
                # API permissions issue, or network error
                print(f"❌ Failed to get bookings: {str(e)}")
                print()
        else:
            # Skip this test if user email is not configured
            print("⚠️  CAL_USER_EMAIL not configured in .env")
            print()

        # ====================================================================
        # CONFIGURATION CHECKLIST
        # ====================================================================
        # Display a summary of what's configured and what's missing
        # This helps users quickly identify what needs to be set up
        print("=" * 60)
        print("Configuration Checklist:")
        print("=" * 60)

        # Check each required environment variable
        # Uses ternary operator: "✅ if condition else ❌"
        # os.getenv() returns None if variable is not set
        print(f"{'✅' if os.getenv('CAL_API_KEY') else '❌'} CAL_API_KEY")
        print(f"{'✅' if os.getenv('OPENAI_API_KEY') else '❌'} OPENAI_API_KEY")
        print(f"{'✅' if event_type_id else '❌'} CAL_EVENT_TYPE_ID")
        print(f"{'✅' if user_email else '❌'} CAL_USER_EMAIL")
        print()

        # Show warning if any configuration is missing
        # event_type_id and user_email are optional but recommended
        if not event_type_id or not user_email:
            print("⚠️  Please update your .env file with the missing configuration")

    except Exception as e:
        # Catch any fatal errors (like missing API key during client initialization)
        # This prevents the entire script from crashing without any useful output
        print(f"❌ Fatal error: {str(e)}")


# MAIN EXECUTION BLOCK
# This runs when you execute this file directly: python test_api.py
if __name__ == "__main__":
    # Run the test function using asyncio
    # asyncio.run() creates an event loop and executes the async function
    asyncio.run(test_cal_api())
