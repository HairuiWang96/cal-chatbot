"""
Core chatbot logic with OpenAI function calling
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dateutil import parser
import pytz
from openai import OpenAI
from dotenv import load_dotenv

from src.cal_api import CalApiClient
from src.tools import TOOLS

load_dotenv()


class CalChatbot:
    """Chatbot that integrates Cal.com with OpenAI function calling"""

    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.cal_client = CalApiClient()
        self.default_event_type_id = os.getenv("CAL_EVENT_TYPE_ID")

        # Include current date in system message for better date parsing
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")

        self.system_message = {
            "role": "system",
            "content": f"""You are a helpful meeting scheduling assistant that helps users book, view, cancel, and reschedule meetings using Cal.com.

Today's date is {today}.

Your capabilities:
1. Book new meetings - Ask for date, time, attendee email, attendee name, and reason
2. List scheduled meetings - Show user's upcoming meetings
3. Cancel meetings - Help users cancel existing meetings
4. Reschedule meetings - Help users move meetings to new times

Important guidelines:
- Always be polite and conversational
- When booking, confirm all details before creating the booking
- Parse natural language dates/times (e.g., "tomorrow at 3pm", "next Monday at 10am")
- If information is missing, ask the user for it
- After completing an action, confirm the result to the user
- For date/time parsing, assume the user is in UTC unless they specify otherwise
- CRITICAL: When checking available slots, ONLY show times that are returned by the get_available_slots function. If the function returns an empty list or no slots, tell the user there are NO available times for that day. NEVER make up or suggest times that weren't in the API response.
- CRITICAL: When any function returns an "error" field, the operation FAILED. You MUST tell the user about the error and that the operation was NOT successful. NEVER claim success when there's an error in the function response.
- When listing meetings, format them in a readable way with date, time, and details
"""
        }

    async def chat(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        user_email: Optional[str] = None
    ) -> tuple[str, List[Dict[str, str]]]:
        """
        Process a user message and return the chatbot's response

        Args:
            user_message: The user's message
            conversation_history: Previous conversation messages
            user_email: Optional user email for booking queries

        Returns:
            Tuple of (response message, updated conversation history)
        """
        # Build messages for OpenAI
        messages = [self.system_message]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        # Store user email in context if provided
        context = {"user_email": user_email}

        # Make initial request to OpenAI
        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        # Handle function calls
        while assistant_message.tool_calls:
            messages.append(assistant_message)

            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                print(f"Calling function: {function_name} with args: {function_args}")

                # Execute the function
                try:
                    result = await self._execute_function(
                        function_name,
                        function_args,
                        context
                    )
                    function_response = json.dumps(result)
                except Exception as e:
                    function_response = json.dumps({"error": str(e)})

                # Add function response to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": function_response
                })

            # Get next response from OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto"
            )
            assistant_message = response.choices[0].message

        # Extract final response
        final_response = assistant_message.content

        # Update conversation history
        conversation_history.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "assistant", "content": final_response})

        return final_response, conversation_history

    async def _execute_function(
        self,
        function_name: str,
        arguments: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a function call"""

        if function_name == "get_available_slots":
            return await self._get_available_slots(arguments)

        elif function_name == "create_booking":
            return await self._create_booking(arguments)

        elif function_name == "get_user_bookings":
            return await self._get_user_bookings(arguments, context)

        elif function_name == "cancel_booking":
            return await self._cancel_booking(arguments)

        elif function_name == "reschedule_booking":
            return await self._reschedule_booking(arguments)

        else:
            return {"error": f"Unknown function: {function_name}"}

    async def _get_available_slots(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get available time slots for a date"""
        date_str = args["date"]
        event_type_id = args.get("event_type_id") or self.default_event_type_id

        if not event_type_id:
            return {"error": "Event type ID not configured"}

        # Parse date and create time range for the day
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            start_time = date.replace(hour=0, minute=0, second=0).isoformat() + "Z"
            end_time = date.replace(hour=23, minute=59, second=59).isoformat() + "Z"

            slots = await self.cal_client.get_available_slots(
                event_type_id=int(event_type_id),
                start_time=start_time,
                end_time=end_time
            )

            return {
                "success": True,
                "date": date_str,
                "slots": slots
            }
        except Exception as e:
            return {"error": f"Failed to get available slots: {str(e)}"}

    async def _create_booking(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new booking"""
        event_type_id = args.get("event_type_id") or self.default_event_type_id

        if not event_type_id:
            return {"error": "Event type ID not configured"}

        try:
            booking = await self.cal_client.create_booking(
                event_type_id=int(event_type_id),
                start_time=args["start_time"],
                attendee_email=args["attendee_email"],
                attendee_name=args["attendee_name"],
                attendee_timezone=args.get("timezone", "UTC"),
                metadata={"reason": args.get("reason", "")}
            )

            return {
                "success": True,
                "booking": booking
            }
        except Exception as e:
            return {"error": f"Failed to create booking: {str(e)}"}

    async def _get_user_bookings(self, args: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Get bookings for a user"""
        try:
            status = args.get("status", "upcoming")
            after_date = args.get("after_date")
            before_date = args.get("before_date")

            # Use email from args if provided, otherwise use from context
            user_email = args.get("user_email") or context.get("user_email")
            if not user_email:
                return {"error": "User email is required but not provided"}

            # Convert dates to ISO format if provided
            after_start = None
            before_start = None

            if after_date:
                after_start = datetime.strptime(after_date, "%Y-%m-%d").isoformat() + "Z"
            if before_date:
                before_start = datetime.strptime(before_date, "%Y-%m-%d").isoformat() + "Z"

            bookings = await self.cal_client.get_bookings(
                status=status,
                attendee_email=user_email,
                after_start=after_start,
                before_start=before_start
            )

            return {
                "success": True,
                "bookings": bookings,
                "count": len(bookings)
            }
        except Exception as e:
            return {"error": f"Failed to get bookings: {str(e)}"}

    async def _cancel_booking(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel a booking"""
        try:
            # Cal.com API requires booking UID (string), not numeric ID
            booking_uid = args.get("booking_uid") or str(args.get("booking_id", ""))

            result = await self.cal_client.cancel_booking(
                booking_uid=booking_uid,
                reason=args.get("reason")
            )

            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {"error": f"Failed to cancel booking: {str(e)}"}

    async def _reschedule_booking(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Reschedule a booking"""
        try:
            # Use UID if provided, otherwise try to convert ID to string
            booking_uid = args.get("booking_uid") or str(args.get("booking_id", ""))

            result = await self.cal_client.reschedule_booking(
                booking_uid=booking_uid,
                new_start_time=args["new_start_time"],
                reason=args.get("reason")
            )

            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {"error": f"Failed to reschedule booking: {str(e)}"}
