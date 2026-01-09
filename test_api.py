"""
Test script to verify Cal.com API connectivity and endpoints
Run this to test your Cal.com API integration before using the chatbot
"""

import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from src.cal_api import CalApiClient

load_dotenv()


async def test_cal_api():
    """Test Cal.com API endpoints"""
    print("=" * 60)
    print("Testing Cal.com API Integration")
    print("=" * 60)

    try:
        client = CalApiClient()
        print("✅ Cal.com API client initialized successfully")
        print(f"   Base URL: {client.base_url}")
        print()

        # Test 1: Get event types
        print("Test 1: Getting event types...")
        try:
            event_types = await client.get_event_types()
            print(f"   Raw response type: {type(event_types)}")
            print(f"   Raw response: {event_types}")
            print()
            print(f"✅ Found {len(event_types)} event type(s)")
            if event_types:
                for et in event_types:
                    print(f"   - ID: {et.get('id')}, Title: {et.get('title')}, Slug: {et.get('slug')}")
                print(f"\n💡 Tip: Use one of these IDs in your .env file as CAL_EVENT_TYPE_ID")
            else:
                print("⚠️  No event types found. Please create an event type in Cal.com")
            print()
        except Exception as e:
            import traceback
            print(f"❌ Failed to get event types: {str(e)}")
            traceback.print_exc()
            print()

        # Test 2: Get available slots (if event type ID is configured)
        event_type_id = os.getenv("CAL_EVENT_TYPE_ID")
        if event_type_id:
            print("Test 2: Getting available slots...")
            try:
                tomorrow = datetime.now() + timedelta(days=1)
                start_time = tomorrow.replace(hour=0, minute=0, second=0).isoformat() + "Z"
                end_time = tomorrow.replace(hour=23, minute=59, second=59).isoformat() + "Z"

                slots = await client.get_available_slots(
                    event_type_id=int(event_type_id),
                    start_time=start_time,
                    end_time=end_time
                )
                print(f"✅ Found {len(slots)} available slot(s) for tomorrow")
                if slots:
                    for slot in slots[:5]:  # Show first 5 slots
                        print(f"   - {slot.get('time')}")
                print()
            except Exception as e:
                print(f"❌ Failed to get available slots: {str(e)}")
                print()
        else:
            print("Test 2: Skipped (CAL_EVENT_TYPE_ID not configured)")
            print()

        # Test 3: Get bookings
        print("Test 3: Getting bookings...")
        user_email = os.getenv("CAL_USER_EMAIL")
        if user_email:
            try:
                bookings = await client.get_bookings(
                    status="upcoming",
                    attendee_email=user_email
                )
                print(f"✅ Found {len(bookings)} upcoming booking(s)")
                if bookings:
                    for booking in bookings[:3]:  # Show first 3 bookings
                        print(f"   - ID: {booking.get('id')}, Start: {booking.get('startTime')}")
                print()
            except Exception as e:
                print(f"❌ Failed to get bookings: {str(e)}")
                print()
        else:
            print("⚠️  CAL_USER_EMAIL not configured in .env")
            print()

        print("=" * 60)
        print("Configuration Checklist:")
        print("=" * 60)
        print(f"{'✅' if os.getenv('CAL_API_KEY') else '❌'} CAL_API_KEY")
        print(f"{'✅' if os.getenv('OPENAI_API_KEY') else '❌'} OPENAI_API_KEY")
        print(f"{'✅' if event_type_id else '❌'} CAL_EVENT_TYPE_ID")
        print(f"{'✅' if user_email else '❌'} CAL_USER_EMAIL")
        print()

        if not event_type_id or not user_email:
            print("⚠️  Please update your .env file with the missing configuration")

    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_cal_api())
