"""
OpenAI function calling tool definitions for Cal.com integration
"""

from typing import List, Dict, Any

# Tool definitions for OpenAI function calling
TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_available_slots",
            "description": "Get available time slots for booking a meeting. Use this when the user wants to book a meeting and you need to check availability.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "The date to check availability for, in YYYY-MM-DD format (e.g., '2024-01-15')"
                    },
                    "event_type_id": {
                        "type": "integer",
                        "description": "The event type ID to check availability for. If not provided, use the default from environment."
                    }
                },
                "required": ["date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_booking",
            "description": "Create a new booking/meeting. Use this after confirming the time slot is available and you have all necessary details (date, time, attendee info, reason).",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "description": "The start time of the meeting in ISO 8601 format (e.g., '2024-01-15T14:00:00Z')"
                    },
                    "attendee_email": {
                        "type": "string",
                        "description": "Email address of the attendee booking the meeting"
                    },
                    "attendee_name": {
                        "type": "string",
                        "description": "Full name of the attendee"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason or description for the meeting"
                    },
                    "event_type_id": {
                        "type": "integer",
                        "description": "The event type ID. If not provided, use the default from environment."
                    },
                    "timezone": {
                        "type": "string",
                        "description": "Timezone of the attendee (e.g., 'America/New_York', 'UTC'). Defaults to UTC."
                    }
                },
                "required": ["start_time", "attendee_email", "attendee_name", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_bookings",
            "description": "Get a list of scheduled bookings/meetings for a user. Use this when the user asks to see their scheduled events or meetings. The user's email will be automatically used from context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_email": {
                        "type": "string",
                        "description": "Email address of the user to get bookings for (optional, will use user's email from context if not provided)"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["upcoming", "past", "cancelled"],
                        "description": "Filter bookings by status. Defaults to 'upcoming'."
                    },
                    "after_date": {
                        "type": "string",
                        "description": "Only get bookings after this date in YYYY-MM-DD format"
                    },
                    "before_date": {
                        "type": "string",
                        "description": "Only get bookings before this date in YYYY-MM-DD format"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_booking",
            "description": "Cancel a scheduled booking/meeting. First use get_user_bookings to find the booking UID, then cancel it. The booking UID is a string like 'eTHSdCB89qzCiazPWHV15x', not the numeric ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_uid": {
                        "type": "string",
                        "description": "The UID of the booking to cancel (string, not numeric ID). Get this from get_user_bookings."
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for cancellation"
                    }
                },
                "required": ["booking_uid"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reschedule_booking",
            "description": "Reschedule an existing booking to a new time. Use this when the user wants to change the time of an existing meeting. First use get_user_bookings to find the booking UID, then reschedule it. The booking UID is a string like 'hN13LiTrTAsWbuP8dmhLzG', not the numeric ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_uid": {
                        "type": "string",
                        "description": "The UID of the booking to reschedule (string, not numeric ID). Get this from get_user_bookings."
                    },
                    "new_start_time": {
                        "type": "string",
                        "description": "The new start time in ISO 8601 format (e.g., '2024-01-15T14:00:00Z')"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Optional reason for rescheduling"
                    }
                },
                "required": ["booking_uid", "new_start_time"]
            }
        }
    }
]
