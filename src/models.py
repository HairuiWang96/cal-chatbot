"""
Pydantic models for request/response validation

This file defines DATA MODELS using Pydantic. Think of models as blueprints or schemas
that define what data should look like.

WHAT IS PYDANTIC?
Pydantic is a Python library for data validation. It:
1. Defines what fields an object should have
2. Validates data types (ensures strings are strings, numbers are numbers, etc.)
3. Converts data automatically (e.g., "123" string to 123 integer)
4. Generates helpful error messages if data is invalid
5. Auto-generates API documentation in FastAPI

WHY USE MODELS?
- Type Safety: Catch errors early (e.g., passing a number where a string is expected)
- Documentation: Models document your API's input/output format
- Validation: Automatically reject invalid requests
- IDE Support: Your code editor can autocomplete fields

EXAMPLE:
Without Pydantic:
  data = request.json()  # What fields does this have? What types?
  message = data["message"]  # Could crash if "message" doesn't exist

With Pydantic:
  request: ChatRequest  # Clear structure, validated automatically
  message = request.message  # Guaranteed to exist and be a string
"""

from pydantic import BaseModel, Field  # Pydantic's base class and Field for metadata
from typing import Optional, List, Dict, Any  # Type hints for complex types
from datetime import datetime  # For date/time fields (imported but not heavily used)


class ChatMessage(BaseModel):
    """
    Chat message model - represents a single message in a conversation

    This is used to represent messages between the user and the chatbot.
    Each message has a role (who sent it) and content (what they said).

    EXAMPLE:
    {
        "role": "user",
        "content": "Book a meeting tomorrow at 2pm"
    }
    or
    {
        "role": "assistant",
        "content": "I'd be happy to help! What's your email?"
    }

    WHY SEPARATE MODEL FOR MESSAGES?
    - Reusable: Used in both ChatRequest and ChatResponse
    - Clear structure: Always has role and content
    - Easy to extend: Can add fields like timestamp, metadata later
    """
    # The role field tells us who sent this message
    # The "..." means this field is REQUIRED (must be provided)
    role: str = Field(..., description="Role of the message sender (user, assistant, system)")

    # The content field is the actual text of the message
    content: str = Field(..., description="Content of the message")


class ChatRequest(BaseModel):
    """
    Request model for chat endpoint - defines what clients send to /chat

    When someone calls our /chat API endpoint, they send JSON data.
    This model defines the structure of that JSON and validates it.

    EXAMPLE REQUEST BODY:
    {
        "message": "What meetings do I have?",
        "conversation_history": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help?"}
        ],
        "user_email": "john@example.com"
    }

    WHY THIS STRUCTURE?
    - message: The user's new message (required)
    - conversation_history: Previous messages for context (optional, defaults to empty)
    - user_email: Needed for booking operations (optional)
    """
    # The new message from the user (required)
    message: str = Field(..., description="User message")

    # Previous conversation for context
    # default_factory=list means if not provided, use empty list []
    # This allows stateless API - client manages conversation history
    conversation_history: List[ChatMessage] = Field(
        default_factory=list,
        description="Previous conversation history"
    )

    # User's email for booking/listing meetings (optional)
    # Optional[str] means this can be a string OR None
    user_email: Optional[str] = Field(None, description="User's email for booking queries")


class ChatResponse(BaseModel):
    """
    Response model for chat endpoint - defines what our API returns

    After processing a chat message, we return this structure.
    FastAPI automatically converts our Python objects to JSON using this model.

    EXAMPLE RESPONSE:
    {
        "response": "You have 2 meetings today: 10am with John, 2pm with Sarah",
        "conversation_history": [
            {"role": "user", "content": "What meetings do I have?"},
            {"role": "assistant", "content": "You have 2 meetings today..."}
        ]
    }

    WHY RETURN CONVERSATION HISTORY?
    - Stateless API: Server doesn't store history, so we return it
    - Client responsibility: Client sends this back in next request for context
    - Flexibility: Client can manage/store history however they want
    """
    # The chatbot's response text
    response: str = Field(..., description="Chatbot response")

    # Updated conversation including the new exchange
    # This includes all previous messages PLUS the new user message and assistant response
    conversation_history: List[ChatMessage] = Field(..., description="Updated conversation history")


class BookingDetails(BaseModel):
    """
    Booking details model - represents a Cal.com meeting/booking

    This model structures the data we get back from Cal.com API about a booking.
    It's useful for type safety and documentation, though not heavily used in
    the current implementation (chatbot returns raw Cal.com data).

    EXAMPLE:
    {
        "id": 12345,
        "event_type_id": 678,
        "title": "30 min meeting",
        "start_time": "2026-01-15T14:00:00Z",
        "end_time": "2026-01-15T14:30:00Z",
        "status": "accepted",
        "attendees": [
            {"name": "John Doe", "email": "john@example.com"}
        ]
    }

    FIELDS EXPLAINED:
    - id: Numeric ID (not used for cancel/reschedule - use UID instead!)
    - event_type_id: What type of meeting (30 min, 1 hour, etc.)
    - title: Meeting title/description
    - start_time: When meeting starts (ISO format)
    - end_time: When meeting ends (ISO format)
    - status: "accepted", "pending", "cancelled", etc.
    - attendees: List of people attending with their info
    """
    id: int  # Numeric booking ID
    event_type_id: int  # Type of meeting
    title: str  # Meeting title
    start_time: str  # Start datetime in ISO format
    end_time: str  # End datetime in ISO format
    status: str  # Booking status
    attendees: List[Dict[str, Any]]  # List of attendee objects


class AvailableSlot(BaseModel):
    """
    Available time slot model - represents a free time slot

    When checking availability, Cal.com returns a list of available times.
    This model structures each time slot.

    EXAMPLE:
    {
        "time": "2026-01-15T14:00:00Z",
        "available": true
    }

    USAGE:
    User asks: "What times are available tomorrow?"
    Cal.com returns list of AvailableSlot objects
    Chatbot shows: "You have 5 available slots: 9am, 10am, 11am, 2pm, 3pm"
    """
    time: str  # ISO format datetime for this slot
    available: bool  # Whether this slot is actually available (usually true in responses)
