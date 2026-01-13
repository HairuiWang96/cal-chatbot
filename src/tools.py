"""
OpenAI function calling tool definitions for Cal.com integration

This file defines the "tools" (functions) that GPT can call.

WHAT ARE TOOL DEFINITIONS?
Think of this as a menu that you show to GPT. Each tool definition tells GPT:
1. What the function is called
2. What it does (description)
3. What parameters it needs
4. Which parameters are required vs optional

GPT reads these definitions and decides:
- "Should I call a function for this user message?"
- "If yes, which function should I call?"
- "What values should I pass for the parameters?"

THE STRUCTURE:
Each tool follows OpenAI's function calling schema:
{
  "type": "function",
  "function": {
    "name": "function_name",
    "description": "What it does",
    "parameters": {
      "type": "object",
      "properties": {
        "param1": {"type": "string", "description": "What this param is"},
        ...
      },
      "required": ["param1", ...]
    }
  }
}

WHY IS THIS IMPORTANT?
- Good descriptions help GPT choose the right function
- Clear parameter descriptions help GPT extract the right values from user messages
- Marking parameters as "required" ensures GPT asks for missing info
"""

from typing import List, Dict, Any

# Tool definitions for OpenAI function calling
#! This list is imported by chatbot.py and passed to OpenAI
TOOLS: List[Dict[str, Any]] = [
    # TOOL 1: Get Available Slots
    # This function checks when someone is available for a meeting
    {
        "type": "function",  #! Must be "function" for OpenAI function calling
        "function": {
            "name": "get_available_slots",  # The function name (must match chatbot.py)
            # Description is CRITICAL - it tells GPT when to use this function
            # Good descriptions = GPT calls the right function at the right time
            "description": "Get available time slots for booking a meeting. Use this when the user wants to book a meeting and you need to check availability.",
            # Parameters define what GPT needs to provide when calling this function
            "parameters": {
                "type": "object",  # Parameters are passed as an object (dictionary)
                "properties": {
                    # Each property is a parameter GPT can provide
                    "date": {
                        "type": "string",  # Data type of the parameter
                        # Description helps GPT understand what format to use
                        "description": "The date to check availability for, in YYYY-MM-DD format (e.g., '2026-01-15')",
                    },
                    "event_type_id": {
                        "type": "integer",
                        "description": "The event type ID to check availability for. If not provided, use the default from environment.",
                    },
                },
                # Required parameters - GPT must provide these or ask the user
                "required": ["date"],
            },
        },
    },
    # TOOL 2: Create Booking
    # This function actually books/schedules a meeting
    {
        "type": "function",
        "function": {
            "name": "create_booking",
            # Note: Description mentions "after confirming" - this guides GPT to
            # check availability first before booking
            "description": "Create a new booking/meeting. Use this after confirming the time slot is available and you have all necessary details (date, time, attendee info, reason).",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        # ISO 8601 format is CRITICAL - it's the standard datetime format
                        # Example: "2026-01-15T14:00:00Z" = Jan 15, 2026 at 2pm UTC
                        "description": "The start time of the meeting in ISO 8601 format (e.g., '2026-01-15T14:00:00Z')",
                    },
                    "attendee_email": {
                        "type": "string",
                        "description": "Email address of the attendee booking the meeting",
                    },
                    "attendee_name": {
                        "type": "string",
                        "description": "Full name of the attendee",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason or description for the meeting",
                    },
                    "event_type_id": {
                        "type": "integer",
                        "description": "The event type ID. If not provided, use the default from environment.",
                    },
                    "timezone": {
                        "type": "string",
                        "description": "Timezone of the attendee (e.g., 'America/New_York', 'UTC'). Defaults to UTC.",
                    },
                },
                # All these are required - GPT must get them from the user before booking
                "required": ["start_time", "attendee_email", "attendee_name", "reason"],
            },
        },
    },
    # TOOL 3: Get User Bookings
    # This function retrieves a list of scheduled meetings
    {
        "type": "function",
        "function": {
            "name": "get_user_bookings",
            # Note: Mentions "email will be automatically used from context"
            # This tells GPT it doesn't need to ask for email - we already have it
            "description": "Get a list of scheduled bookings/meetings for a user. Use this when the user asks to see their scheduled events or meetings. The user's email will be automatically used from context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_email": {
                        "type": "string",
                        # This is optional because chatbot.py passes email in context
                        "description": "Email address of the user to get bookings for (optional, will use user's email from context if not provided)",
                    },
                    "status": {
                        "type": "string",
                        # The "enum" field restricts values to these options only
                        # GPT can only choose from: "upcoming", "past", or "cancelled"
                        "enum": ["upcoming", "past", "cancelled"],
                        "description": "Filter bookings by status. Defaults to 'upcoming'.",
                    },
                    "after_date": {
                        "type": "string",
                        # Date filters let users say "show meetings this week" or "after Monday"
                        "description": "Only get bookings after this date in YYYY-MM-DD format",
                    },
                    "before_date": {
                        "type": "string",
                        "description": "Only get bookings before this date in YYYY-MM-DD format",
                    },
                },
                # No required parameters! User can just say "show my meetings"
                # and GPT will use defaults (upcoming status, no date filters)
                "required": [],
            },
        },
    },
    # TOOL 4: Cancel Booking
    # This function cancels/deletes a scheduled meeting
    {
        "type": "function",
        "function": {
            "name": "cancel_booking",
            # IMPORTANT: Description guides GPT to use a two-step process:
            # 1. First call get_user_bookings to find the meeting
            # 2. Then call cancel_booking with the UID
            # Also emphasizes UID vs ID distinction (common source of bugs!)
            "description": "Cancel a scheduled booking/meeting. First use get_user_bookings to find the booking UID, then cancel it. The booking UID is a string like 'eTHSdCB89qzCiazPWHV15x', not the numeric ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_uid": {
                        "type": "string",
                        # Emphasize again: UID (string), not ID (number)
                        # This is critical because Cal.com API only accepts UIDs for cancel/reschedule
                        "description": "The UID of the booking to cancel (string, not numeric ID). Get this from get_user_bookings.",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for cancellation",
                    },
                },
                # Only booking_uid is required; reason is optional
                "required": ["booking_uid"],
            },
        },
    },
    # TOOL 5: Reschedule Booking
    # This function moves a meeting to a new time
    {
        "type": "function",
        "function": {
            "name": "reschedule_booking",
            # Similar to cancel - guides GPT through the two-step process
            # Also emphasizes the UID vs ID distinction
            "description": "Reschedule an existing booking to a new time. Use this when the user wants to change the time of an existing meeting. First use get_user_bookings to find the booking UID, then reschedule it. The booking UID is a string like 'hN13LiTrTAsWbuP8dmhLzG', not the numeric ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_uid": {
                        "type": "string",
                        # Again, emphasize UID (string) not ID (number)
                        "description": "The UID of the booking to reschedule (string, not numeric ID). Get this from get_user_bookings.",
                    },
                    "new_start_time": {
                        "type": "string",
                        # New time must be in ISO 8601 format like create_booking
                        "description": "The new start time in ISO 8601 format (e.g., '2024-01-15T14:00:00Z')",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Optional reason for rescheduling",
                    },
                },
                # Both UID and new time are required; reason is optional
                "required": ["booking_uid", "new_start_time"],
            },
        },
    },
]

# HOW GPT USES THESE TOOLS:
# 1. User: "Book a meeting tomorrow at 2pm"
# 2. GPT reads the tool definitions above
# 3. GPT thinks: "I need to call create_booking"
# 4. GPT extracts: start_time="2026-01-16T14:00:00Z", attendee_email=?, attendee_name=?, reason=?
# 5. GPT realizes it's missing info and asks: "What's your email and name?"
# 6. User provides missing info
# 7. GPT calls create_booking with all required parameters
# 8. chatbot.py executes the function and returns result
# 9. GPT formats a friendly response: "Great! I've booked your meeting for tomorrow at 2pm"
