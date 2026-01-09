"""
Cal.com API Wrapper
Handles all interactions with the Cal.com API v2
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import httpx
from dotenv import load_dotenv

load_dotenv()


class CalApiClient:
    """Client for interacting with Cal.com API v2"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("CAL_API_KEY")
        self.base_url = base_url or os.getenv("CAL_API_BASE_URL", "https://api.cal.com/v2")

        if not self.api_key:
            raise ValueError("CAL_API_KEY is required")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def get_event_types(self) -> List[Dict[str, Any]]:
        """Get all event types for the authenticated user"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/event-types",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()

            # Cal.com V2 API returns: {status: "success", data: {eventTypeGroups: [...]}}
            event_types = []
            if "data" in data:
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

        Args:
            event_type_id: The event type ID
            start_time: Start time in ISO format (e.g., "2024-01-15T00:00:00Z")
            end_time: End time in ISO format (e.g., "2024-01-15T23:59:59Z")
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/slots/available",
                headers=self.headers,
                params={
                    "eventTypeId": event_type_id,
                    "startTime": start_time,
                    "endTime": end_time
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("slots", [])

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
        Create a new booking

        Args:
            event_type_id: The event type ID
            start_time: Start time in ISO format
            attendee_email: Email of the attendee
            attendee_name: Name of the attendee
            attendee_timezone: Timezone of the attendee
            metadata: Additional metadata (e.g., meeting reason)
        """
        payload = {
            "eventTypeId": event_type_id,
            "start": start_time,
            "attendee": {
                "email": attendee_email,
                "name": attendee_name,
                "timeZone": attendee_timezone
            },
            "metadata": metadata or {}
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/bookings",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
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

        Args:
            status: Filter by status (upcoming, past, cancelled)
            attendee_email: Filter by attendee email
            after_start: Get bookings after this date (ISO format)
            before_start: Get bookings before this date (ISO format)
        """
        params = {"status": status}

        if attendee_email:
            params["attendeeEmail"] = attendee_email
        if after_start:
            params["afterStart"] = after_start
        if before_start:
            params["beforeStart"] = before_start

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/bookings",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            data = response.json()

            # Cal.com V2 API returns: {status: "success", data: {bookings: [...]}}
            if "data" in data:
                return data["data"].get("bookings", [])
            return []

    async def cancel_booking(self, booking_id: int, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel a booking

        Args:
            booking_id: The booking ID to cancel
            reason: Optional cancellation reason
        """
        payload = {}
        if reason:
            payload["reason"] = reason

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/bookings/{booking_id}/cancel",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", {})

    async def reschedule_booking(
        self,
        booking_id: int,
        new_start_time: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Reschedule a booking

        Args:
            booking_id: The booking ID to reschedule
            new_start_time: New start time in ISO format
            reason: Optional rescheduling reason
        """
        payload = {
            "start": new_start_time
        }
        if reason:
            payload["rescheduledReason"] = reason

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/bookings/{booking_id}",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", {})
