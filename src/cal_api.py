"""
Cal.com API Wrapper - Handles all interactions with the Cal.com API v2

This file is a WRAPPER around the Cal.com REST API. Think of it as a translator:
- Instead of manually making HTTP requests with complex parameters,
- We provide simple Python methods like create_booking() or cancel_booking()
- This wrapper handles all the HTTP details, authentication, and error handling

WHY USE A WRAPPER?
1. Cleaner code - chatbot.py just calls simple methods, not HTTP details
2. Reusability - if we need Cal.com API elsewhere, we can reuse this client
3. Error handling - centralized place to handle API errors
4. API changes - if Cal.com changes their API, we only update this file

IMPORTANT: This uses Cal.com API V2 which has different endpoints and
response formats than V1. The API version is specified in the headers.
"""

# Import standard Python libraries
import os  # For reading environment variables
from typing import List, Dict, Any, Optional  # Type hints for function parameters and returns
from datetime import datetime, timedelta  # For working with dates (imported but not used much here)
import httpx  # Modern async HTTP client (like requests but supports async/await)
from dotenv import load_dotenv  # For loading .env file

# Load environment variables from .env file
load_dotenv()


class CalApiClient:
    """
    Client for interacting with Cal.com API v2

    This class wraps all Cal.com API operations into easy-to-use Python methods.
    It handles authentication, HTTP requests, and response parsing.

    AUTHENTICATION:
    Cal.com uses Bearer token authentication. We include the API key in the
    Authorization header of every request.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the Cal.com API client

        Args:
            api_key: Cal.com API key (if not provided, reads from environment)
            base_url: Base URL for Cal.com API (if not provided, uses default v2 URL)

        Raises:
            ValueError: If no API key is provided or found in environment
        """
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv("CAL_API_KEY")

        # Get base URL from parameter or environment, default to Cal.com v2 API
        self.base_url = base_url or os.getenv("CAL_API_BASE_URL", "https://api.cal.com/v2")

        # Validate that we have an API key
        if not self.api_key:
            raise ValueError("CAL_API_KEY is required")

        # Prepare headers that will be sent with every API request
        # These headers authenticate us and specify the API version
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",  # Bearer token authentication
            "Content-Type": "application/json",  # We're sending/receiving JSON
            "cal-api-version": "2024-08-13"  # Required for v2 API - tells Cal.com which API version to use
        }

    async def get_event_types(self) -> List[Dict[str, Any]]:
        """
        Get all event types for the authenticated user

        EVENT TYPES are different kinds of meetings you can schedule.
        For example: "30 min meeting", "1 hour consultation", "Team standup"

        Each event type has:
        - A unique ID
        - A duration
        - Availability rules
        - Custom fields

        Returns:
            List of event type dictionaries with details about each type
        """
        # Use httpx AsyncClient for making HTTP requests
        # "async with" ensures the client is properly closed after use
        async with httpx.AsyncClient() as client:
            # Make GET request to fetch event types
            response = await client.get(
                f"{self.base_url}/event-types",  # The API endpoint
                headers=self.headers  # Include auth headers
            )

            # Raise exception if request failed (4xx or 5xx status codes)
            response.raise_for_status()

            # Parse JSON response into Python dictionary
            data = response.json()

            # Cal.com V2 API returns a nested structure:
            # {status: "success", data: {eventTypeGroups: [...]}}
            # We need to flatten this to get a simple list of event types
            event_types = []
            if "data" in data:
                # Event types are grouped (personal, team, etc.)
                # We extract all event types from all groups
                for group in data["data"].get("eventTypeGroups", []):
                    event_types.extend(group.get("eventTypes", []))

            return event_types

    async def get_available_slots(
        self,
        event_type_id: int,
        start_time: str,
        end_time: str
    ) -> List[Dict[str, Any]]:
        """
        Get available time slots for booking

        This checks when someone is available for a meeting by looking at:
        - Their calendar availability
        - The event type's scheduling rules
        - Existing bookings

        EXAMPLE:
        If you query January 15th from 9am-5pm, you might get back:
        [{"time": "2026-01-15T09:00:00Z"}, {"time": "2026-01-15T10:00:00Z"}, ...]

        Args:
            event_type_id: Which type of meeting (e.g., "30 min meeting")
            start_time: Start of time range in ISO format (e.g., "2026-01-15T00:00:00Z")
            end_time: End of time range in ISO format (e.g., "2026-01-15T23:59:59Z")

        Returns:
            List of available time slot dictionaries, each with a "time" field
        """
        async with httpx.AsyncClient() as client:
            # Make GET request with query parameters
            response = await client.get(
                f"{self.base_url}/slots/available",  # The availability endpoint
                headers=self.headers,
                params={
                    # Cal.com uses camelCase for parameter names
                    "eventTypeId": event_type_id,
                    "startTime": start_time,
                    "endTime": end_time
                }
            )
            response.raise_for_status()
            data = response.json()

            # Cal.com V2 API returns slots grouped by date:
            # {data: {slots: {"2026-01-12": [{time: "..."}, ...], "2026-01-13": [...]}}}
            # We need to flatten this into a simple list of all slots
            slots_by_date = data.get("data", {}).get("slots", {})
            all_slots = []

            # Iterate through each date and combine all slots
            for date_key, slots_list in slots_by_date.items():
                all_slots.extend(slots_list)

            return all_slots

    async def create_booking(
        self,
        event_type_id: int,
        start_time: str,
        attendee_email: str,
        attendee_name: str,
        attendee_timezone: str = "UTC",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new booking (schedule a meeting)

        This is the core function for booking meetings. It:
        1. Creates a calendar event
        2. Sends confirmation emails
        3. Blocks off the time slot
        4. Returns booking details including a unique UID

        IMPORTANT: The payload structure must match Cal.com v2 API exactly.
        timeZone and language go INSIDE the attendee object (not at top level).

        Args:
            event_type_id: Which type of meeting to book
            start_time: When the meeting starts (ISO format: "2026-01-15T14:00:00Z")
            attendee_email: Email of person attending (receives confirmation)
            attendee_name: Full name of attendee
            attendee_timezone: Attendee's timezone (e.g., "America/Chicago", "UTC")
            metadata: Extra info like meeting reason, notes, custom fields

        Returns:
            Dictionary with booking details including:
            - id: Numeric booking ID
            - uid: String booking UID (used for cancel/reschedule)
            - status: "accepted", "pending", etc.
            - startTime: When meeting starts
            - attendees: List of attendees

        Raises:
            Exception: If booking fails (time unavailable, invalid params, etc.)
        """
        # Build the request payload according to Cal.com v2 API spec
        # This structure was determined from Cal.com community examples and docs
        payload = {
            "eventTypeId": event_type_id,  # What type of meeting
            "start": start_time,  # When it starts
            "attendee": {
                # Attendee details nested in attendee object
                "name": attendee_name,
                "email": attendee_email,
                "timeZone": attendee_timezone,  # Note: camelCase per Cal.com API
                "language": "en"  # Language for confirmation emails
            }
        }

        # Add optional metadata (meeting reason, custom fields, etc.)
        if metadata:
            payload["metadata"] = metadata

        async with httpx.AsyncClient() as client:
            # Make POST request to create booking
            response = await client.post(
                f"{self.base_url}/bookings",  # Bookings endpoint
                headers=self.headers,
                json=payload  # Send payload as JSON body
            )

            # Enhanced error handling - show actual Cal.com error message
            # This helps debug issues like "time slot unavailable" or "invalid parameters"
            if response.status_code >= 400:
                error_body = response.text
                raise Exception(f"Cal.com booking failed ({response.status_code}): {error_body}")

            response.raise_for_status()

            # Parse response and extract booking data
            data = response.json()
            return data.get("data", {})

    async def get_bookings(
        self,
        status: str = "upcoming",
        attendee_email: Optional[str] = None,
        after_start: Optional[str] = None,
        before_start: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get bookings for the authenticated user

        This retrieves a list of scheduled meetings based on filters.
        Useful for answering questions like:
        - "What meetings do I have?"
        - "Show my meetings this week"
        - "List all cancelled meetings"

        FILTERING:
        You can combine multiple filters to narrow results.
        For example: upcoming meetings for a specific email after a certain date.

        Args:
            status: Filter by booking status:
                - "upcoming": Future meetings (default)
                - "past": Already completed meetings
                - "cancelled": Meetings that were cancelled
            attendee_email: Only show meetings where this person is attending
            after_start: Only show meetings after this datetime (ISO format)
            before_start: Only show meetings before this datetime (ISO format)

        Returns:
            List of booking dictionaries, each containing:
            - id: Numeric ID
            - uid: String UID (for cancel/reschedule)
            - startTime: When meeting starts
            - endTime: When meeting ends
            - status: Current status
            - attendees: List of attendee info
            - eventType: Meeting type details
        """
        # Start with base parameters (status is required)
        params = {"status": status}

        # Add optional filters if provided
        # Cal.com API uses camelCase for parameter names
        if attendee_email:
            params["attendeeEmail"] = attendee_email
        if after_start:
            params["afterStart"] = after_start
        if before_start:
            params["beforeStart"] = before_start

        async with httpx.AsyncClient() as client:
            # Make GET request with query parameters
            response = await client.get(
                f"{self.base_url}/bookings",  # Same endpoint as create, but GET instead of POST
                headers=self.headers,
                params=params  # Filters passed as query parameters
            )
            response.raise_for_status()
            data = response.json()

            # Cal.com V2 API returns: {status: "success", data: [...]}
            # The data field is directly a list of bookings (not nested further)
            if "data" in data:
                # Ensure we return a list (sometimes API might return unexpected format)
                return data["data"] if isinstance(data["data"], list) else []
            return []

    async def cancel_booking(self, booking_uid: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel a booking (delete a scheduled meeting)

        This permanently cancels a meeting:
        1. Sends cancellation emails to all attendees
        2. Frees up the time slot
        3. Updates the booking status to "cancelled"

        IMPORTANT: Use the booking UID (string), not the numeric ID!
        UIDs look like: "abc123xyz"
        IDs look like: 12345

        When you get bookings via get_bookings(), each has both an "id" and a "uid".
        For cancellation, you MUST use the "uid" field.

        Args:
            booking_uid: The unique string identifier (UID) of the booking to cancel
            reason: Why the meeting is being cancelled (shown to attendees)

        Returns:
            Dictionary with cancellation result including:
            - status: "cancelled"
            - Other booking details

        Raises:
            HTTPException: If booking not found or already cancelled
        """
        # Cal.com requires a cancellation reason for the host
        # If not provided, use a default message
        payload = {
            "cancellationReason": reason or "User requested cancellation"
        }

        async with httpx.AsyncClient() as client:
            # Make POST request to cancel endpoint
            # Note: This is a POST, not DELETE - Cal.com API design choice
            response = await client.post(
                f"{self.base_url}/bookings/{booking_uid}/cancel",  # UID in URL path
                headers=self.headers,
                json=payload  # Reason in request body
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", {})

    async def reschedule_booking(
        self,
        booking_uid: str,
        new_start_time: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Reschedule a booking (move a meeting to a new time)

        This moves an existing meeting to a new time:
        1. Cancels the old booking
        2. Creates a new booking at the new time
        3. Sends update emails to attendees
        4. Returns NEW booking with a DIFFERENT UID

        CRITICAL: Rescheduling creates a NEW booking!
        - The old booking gets cancelled
        - A new booking is created with a new UID
        - You cannot use the old UID after rescheduling

        EXAMPLE:
        Old meeting: UID "abc123" at 2pm
        After reschedule to 3pm: UID "xyz789" at 3pm
        (Notice the UID changed!)

        Args:
            booking_uid: The UID of the existing booking to reschedule
            new_start_time: New meeting time in ISO format (e.g., "2026-01-15T15:00:00Z")
            reason: Why the meeting is being rescheduled (optional)

        Returns:
            Dictionary with NEW booking details including:
            - uid: NEW UID (different from the one you passed in!)
            - startTime: New start time
            - status: Usually "accepted"
            - Other booking details

        Raises:
            HTTPException: If booking not found or new time unavailable
        """
        # Build payload with new start time
        payload = {
            "start": new_start_time  # When the meeting should be moved to
        }

        # Add optional reason for rescheduling
        if reason:
            payload["reschedulingReason"] = reason

        async with httpx.AsyncClient() as client:
            # Make POST request to reschedule endpoint
            response = await client.post(
                f"{self.base_url}/bookings/{booking_uid}/reschedule",  # Old UID in URL
                headers=self.headers,
                json=payload  # New time in body
            )
            response.raise_for_status()
            data = response.json()

            # Response contains the NEW booking (with new UID)
            return data.get("data", {})
