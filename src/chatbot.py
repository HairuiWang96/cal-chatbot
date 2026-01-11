"""
Core chatbot logic with OpenAI function calling

This is the BRAIN of the chatbot - it connects OpenAI's GPT model with Cal.com's API.

KEY CONCEPT - OpenAI Function Calling:
Imagine you're talking to a smart assistant. When you say "book a meeting tomorrow at 2pm",
the assistant needs to:
1. Understand what you want (natural language processing)
2. Call the right API function (create_booking)
3. Fill in the parameters (date, time, email, etc.)
4. Return a natural response to you

OpenAI's GPT doesn't directly call APIs - instead, it tells US which function to call
and what parameters to use. We then execute it and give the result back to GPT,
which formats a nice response for the user.

This is called "function calling" or "tool use" - the AI acts as the decision-maker,
and we handle the actual API calls.
"""

# Import standard Python libraries
import os  # For reading environment variables
import json  # For parsing JSON data from function calls
from typing import List, Dict, Any, Optional  # Type hints for better code clarity
from datetime import datetime, timedelta  # For working with dates and times
from dateutil import parser  # Advanced date parsing library
import pytz  # Timezone support

# Import OpenAI library for talking to GPT
from openai import OpenAI

# Import dotenv to load environment variables from .env file
from dotenv import load_dotenv

# Import our custom modules
from src.cal_api import CalApiClient  # Our wrapper for Cal.com API
from src.tools import TOOLS  # Function definitions that GPT can "see" and choose to call

# Load environment variables from .env file (API keys, etc.)
load_dotenv()


class CalChatbot:
    """
    Chatbot that integrates Cal.com with OpenAI function calling

    This class is the orchestrator - it:
    1. Manages conversations with OpenAI's GPT
    2. Decides when to call Cal.com API functions
    3. Handles the back-and-forth between user, GPT, and Cal.com
    """

    def __init__(self):
        """
        Initialize the chatbot with OpenAI and Cal.com clients

        This constructor runs once when we create a CalChatbot instance.
        It sets up connections to both OpenAI and Cal.com APIs.
        """
        # Create OpenAI client for talking to GPT
        # The API key is loaded from the .env file
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Create Cal.com API client for booking operations
        self.cal_client = CalApiClient()

        # Get the default event type ID from environment
        # This tells Cal.com what type of meeting we're booking
        self.default_event_type_id = os.getenv("CAL_EVENT_TYPE_ID")

        # Create the system message that defines GPT's behavior
        # This is like giving GPT its job description and instructions
        # Import datetime here to get current date (we already imported it at top, but used here)
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")  # Get today's date in YYYY-MM-DD format

        # The system message is a special instruction that tells GPT:
        # 1. What role it should play (meeting scheduling assistant)
        # 2. What capabilities it has (the functions it can call)
        # 3. How it should behave (polite, ask for missing info, etc.)
        self.system_message = {
            "role": "system",  # Special role that sets the AI's behavior
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

        This is the MAIN METHOD where all the magic happens!

        THE CONVERSATION FLOW:
        1. User sends a message ("Book a meeting tomorrow at 2pm")
        2. We send it to GPT along with conversation history
        3. GPT decides if it needs to call a function (like create_booking)
        4. If yes, we execute the function and give results back to GPT
        5. GPT uses those results to create a natural language response
        6. We return that response to the user

        Args:
            user_message: The user's current message (e.g., "What meetings do I have?")
            conversation_history: All previous messages in this conversation
                                This gives GPT context about what was discussed before
            user_email: The user's email address (needed for booking/listing meetings)

        Returns:
            A tuple containing:
            1. The chatbot's response text (what to show the user)
            2. Updated conversation history (including this exchange)
        """
        # Build the complete message list to send to OpenAI
        # We always include: system message + history + new user message
        messages = [self.system_message]  # Start with system instructions
        messages.extend(conversation_history)  # Add all previous messages
        messages.append({"role": "user", "content": user_message})  # Add the new message

        # Store user email in a context dictionary
        # We pass this to functions that need it (like listing bookings)
        context = {"user_email": user_email}

        # Make the initial request to OpenAI's GPT model
        # This is where we ask GPT: "What should I do with this message?"
        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",  # The specific GPT model to use
            messages=messages,  # All the conversation messages
            tools=TOOLS,  # The list of functions GPT can choose to call (from tools.py)
            tool_choice="auto"  # Let GPT decide if it needs to call a function or just respond
        )

        # Extract GPT's response from the API result
        # GPT might either:
        # 1. Return a text response (e.g., "What time would you like?")
        # 2. Request a function call (e.g., call create_booking with specific parameters)
        assistant_message = response.choices[0].message

        # THE FUNCTION CALLING LOOP
        # This loop handles the case where GPT wants to call one or more functions
        # It keeps running as long as GPT is requesting function calls
        #
        # EXAMPLE FLOW:
        # 1. User: "Book a meeting tomorrow at 2pm with john@example.com"
        # 2. GPT: "I need to call create_booking with these parameters..."
        # 3. We execute create_booking and get the result
        # 4. We send the result back to GPT
        # 5. GPT: "Great! I've booked your meeting for tomorrow at 2pm"
        while assistant_message.tool_calls:
            # Add GPT's function call request to the message history
            # This is important so GPT knows what it asked for
            messages.append(assistant_message)

            # Execute each function that GPT requested
            # GPT can request multiple functions at once (e.g., check availability then book)
            for tool_call in assistant_message.tool_calls:
                # Extract the function name and arguments from GPT's request
                function_name = tool_call.function.name  # e.g., "create_booking"
                function_args = json.loads(tool_call.function.arguments)  # e.g., {"start_time": "...", "attendee_email": "..."}

                # Log what we're about to do (helpful for debugging)
                print(f"Calling function: {function_name} with args: {function_args}")

                # Execute the actual function (calls Cal.com API)
                try:
                    # Call our internal method that routes to the right function
                    result = await self._execute_function(
                        function_name,  # Which function to call
                        function_args,  # The parameters GPT provided
                        context  # Additional context like user email
                    )
                    # Convert result to JSON string for GPT to read
                    function_response = json.dumps(result)
                except Exception as e:
                    # If something goes wrong, return the error to GPT
                    # GPT will then tell the user about the error in natural language
                    function_response = json.dumps({"error": str(e)})

                # Add the function's result to the conversation
                # This tells GPT: "Here's what happened when I called that function"
                messages.append({
                    "role": "tool",  # Special role for function results
                    "tool_call_id": tool_call.id,  # Links this result to the function call
                    "name": function_name,  # Which function this result is from
                    "content": function_response  # The actual result data
                })

            # Now that we've executed all functions, ask GPT again
            # GPT will read the function results and either:
            # 1. Call more functions if needed
            # 2. Generate a final response for the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,  # Now includes function results
                tools=TOOLS,
                tool_choice="auto"
            )
            assistant_message = response.choices[0].message

        # If we're here, GPT is done calling functions and has a final text response
        # Extract the natural language response to show the user
        final_response = assistant_message.content

        # Update the conversation history with this exchange
        # This is important so future messages have context
        conversation_history.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "assistant", "content": final_response})

        # Return both the response and updated history
        return final_response, conversation_history

    async def _execute_function(
        self,
        function_name: str,
        arguments: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a function call by routing to the appropriate handler

        This is a ROUTER function - it looks at the function name and calls
        the right internal method. Think of it like a switchboard operator
        connecting the call to the right department.

        WHY USE A ROUTER?
        - Keeps code organized (each function has its own method)
        - Easy to add new functions (just add a new elif block)
        - Centralized error handling

        Args:
            function_name: Name of the function GPT wants to call (e.g., "create_booking")
            arguments: The parameters GPT provided for the function
            context: Additional data like user email

        Returns:
            Dictionary with either success data or an error message
        """

        # Route to the appropriate function handler
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
            # If GPT requests a function we don't recognize, return an error
            return {"error": f"Unknown function: {function_name}"}

    async def _get_available_slots(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get available time slots for a specific date

        When a user asks "What times are available tomorrow?", GPT calls this function.
        We then query Cal.com to see which time slots are free.

        EXAMPLE:
        User: "What times are available on January 15th?"
        GPT calls: get_available_slots(date="2026-01-15")
        We query Cal.com and return: ["10:00 AM", "2:00 PM", "4:00 PM"]
        GPT responds: "You have three available slots: 10am, 2pm, and 4pm"

        Args:
            args: Dictionary containing:
                - date: Date in YYYY-MM-DD format (e.g., "2026-01-15")
                - event_type_id: (optional) Which type of meeting

        Returns:
            Dictionary with success status and list of available time slots
        """
        date_str = args["date"]  # Extract the date from arguments
        # Use event_type_id from args if provided, otherwise use default
        event_type_id = args.get("event_type_id") or self.default_event_type_id

        if not event_type_id:
            return {"error": "Event type ID not configured"}

        # Parse the date string and create time range for the entire day
        try:
            # Convert string "2026-01-15" to datetime object
            date = datetime.strptime(date_str, "%Y-%m-%d")

            # Create start of day (midnight) in ISO format with UTC timezone
            # Example: "2026-01-15T00:00:00Z"
            start_time = date.replace(hour=0, minute=0, second=0).isoformat() + "Z"

            # Create end of day (11:59:59 PM) in ISO format
            # Example: "2026-01-15T23:59:59Z"
            end_time = date.replace(hour=23, minute=59, second=59).isoformat() + "Z"

            # Call Cal.com API to get available slots for this day
            slots = await self.cal_client.get_available_slots(
                event_type_id=int(event_type_id),
                start_time=start_time,
                end_time=end_time
            )

            # Return success response with the slots
            return {
                "success": True,
                "date": date_str,
                "slots": slots  # List of available time slots
            }
        except Exception as e:
            # If anything goes wrong (invalid date, API error, etc.), return error
            return {"error": f"Failed to get available slots: {str(e)}"}

    async def _create_booking(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new meeting booking

        This is the core function for booking meetings. When a user says
        "Book a meeting tomorrow at 2pm", GPT extracts all the necessary details
        and calls this function.

        EXAMPLE:
        User: "I want to book a meeting on January 15th at 2pm with john@example.com"
        GPT calls: create_booking(
            start_time="2026-01-15T14:00:00Z",
            attendee_email="john@example.com",
            attendee_name="John",
            reason="Discussion"
        )
        Cal.com creates the booking and returns confirmation
        GPT responds: "I've booked your meeting for January 15th at 2pm with John!"

        Args:
            args: Dictionary containing:
                - start_time: ISO format datetime (e.g., "2026-01-15T14:00:00Z")
                - attendee_email: Email of the person attending
                - attendee_name: Name of the attendee
                - timezone: (optional) Timezone, defaults to UTC
                - reason: (optional) Purpose of the meeting

        Returns:
            Dictionary with success status and booking details
        """
        # Get event type ID (what type of meeting this is)
        event_type_id = args.get("event_type_id") or self.default_event_type_id

        if not event_type_id:
            return {"error": "Event type ID not configured"}

        try:
            # Call Cal.com API to create the booking
            booking = await self.cal_client.create_booking(
                event_type_id=int(event_type_id),
                start_time=args["start_time"],  # When the meeting starts
                attendee_email=args["attendee_email"],  # Who's attending
                attendee_name=args["attendee_name"],  # Their name
                attendee_timezone=args.get("timezone", "UTC"),  # Their timezone
                metadata={"reason": args.get("reason", "")}  # Additional info
            )

            # Return success with the booking details
            return {
                "success": True,
                "booking": booking  # Contains ID, UID, time, attendee info, etc.
            }
        except Exception as e:
            # Common errors: time slot already taken, invalid time, etc.
            return {"error": f"Failed to create booking: {str(e)}"}

    async def _get_user_bookings(self, args: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a list of meetings for a user

        When a user asks "What meetings do I have?" or "Show my upcoming meetings",
        this function queries Cal.com to get their bookings.

        EXAMPLE:
        User: "What meetings do I have this week?"
        GPT calls: get_user_bookings(status="upcoming", after_date="2026-01-10")
        Cal.com returns list of meetings
        GPT responds: "You have 3 meetings this week: Monday at 2pm with John..."

        Args:
            args: Dictionary containing:
                - status: "upcoming", "past", or "cancelled" (default: "upcoming")
                - after_date: (optional) Only show meetings after this date
                - before_date: (optional) Only show meetings before this date
                - user_email: (optional) User's email (can also come from context)
            context: Additional context including user_email

        Returns:
            Dictionary with success status, list of bookings, and count
        """
        try:
            # Get filter parameters with defaults
            status = args.get("status", "upcoming")  # Default to upcoming meetings
            after_date = args.get("after_date")  # Optional date filter
            before_date = args.get("before_date")  # Optional date filter

            # Get user email - try args first, then context
            # Context email comes from the FastAPI request
            user_email = args.get("user_email") or context.get("user_email")
            if not user_email:
                return {"error": "User email is required but not provided"}

            # Convert date strings to ISO format if provided
            # Cal.com API expects ISO format timestamps
            after_start = None
            before_start = None

            if after_date:
                # Convert "2026-01-15" to "2026-01-15T00:00:00Z"
                after_start = datetime.strptime(after_date, "%Y-%m-%d").isoformat() + "Z"
            if before_date:
                before_start = datetime.strptime(before_date, "%Y-%m-%d").isoformat() + "Z"

            # Query Cal.com API for bookings
            bookings = await self.cal_client.get_bookings(
                status=status,  # Filter by status
                attendee_email=user_email,  # Filter by who's attending
                after_start=after_start,  # Optional date range start
                before_start=before_start  # Optional date range end
            )

            # Return the list of bookings
            return {
                "success": True,
                "bookings": bookings,  # List of meeting objects
                "count": len(bookings)  # How many meetings found
            }
        except Exception as e:
            return {"error": f"Failed to get bookings: {str(e)}"}

    async def _cancel_booking(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cancel an existing booking

        When a user says "Cancel my meeting on Monday", GPT first calls
        get_user_bookings to find the meeting, then calls this function
        to cancel it.

        EXAMPLE:
        User: "Cancel my 2pm meeting"
        GPT calls: get_user_bookings() to find the meeting
        GPT finds meeting with UID "abc123"
        GPT calls: cancel_booking(booking_uid="abc123", reason="User requested")
        Cal.com cancels the meeting
        GPT responds: "I've cancelled your 2pm meeting"

        IMPORTANT: Cal.com uses UIDs (strings like "abc123"), not numeric IDs

        Args:
            args: Dictionary containing:
                - booking_uid: The unique identifier for the booking (string)
                - booking_id: Alternative ID (will be converted to string)
                - reason: (optional) Why the meeting is being cancelled

        Returns:
            Dictionary with success status and cancellation result
        """
        try:
            # Cal.com API requires booking UID (string), not numeric ID
            # Try to get UID first, otherwise convert ID to string
            booking_uid = args.get("booking_uid") or str(args.get("booking_id", ""))

            # Call Cal.com API to cancel the booking
            result = await self.cal_client.cancel_booking(
                booking_uid=booking_uid,  # The meeting to cancel
                reason=args.get("reason")  # Optional cancellation reason
            )

            # Return success with cancellation details
            return {
                "success": True,
                "result": result  # Contains status: "cancelled"
            }
        except Exception as e:
            # Common errors: booking not found, already cancelled, etc.
            return {"error": f"Failed to cancel booking: {str(e)}"}

    async def _reschedule_booking(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reschedule an existing booking to a new time

        When a user says "Move my Monday meeting to Tuesday", GPT identifies
        the meeting and calls this function with the new time.

        EXAMPLE:
        User: "Move my 2pm meeting to 3pm"
        GPT calls: get_user_bookings() to find the 2pm meeting
        GPT finds meeting with UID "abc123" at "2026-01-15T14:00:00Z"
        GPT calls: reschedule_booking(
            booking_uid="abc123",
            new_start_time="2026-01-15T15:00:00Z",
            reason="User requested time change"
        )
        Cal.com moves the meeting to 3pm
        GPT responds: "I've moved your meeting from 2pm to 3pm"

        NOTE: Rescheduling creates a NEW booking with a different UID
        and cancels the old one. This is how Cal.com handles rescheduling.

        Args:
            args: Dictionary containing:
                - booking_uid: The unique identifier for the booking to reschedule
                - booking_id: Alternative ID (will be converted to string)
                - new_start_time: New time in ISO format (e.g., "2026-01-15T15:00:00Z")
                - reason: (optional) Why the meeting is being rescheduled

        Returns:
            Dictionary with success status and new booking details
        """
        try:
            # Get the booking UID (Cal.com requires string UIDs)
            booking_uid = args.get("booking_uid") or str(args.get("booking_id", ""))

            # Call Cal.com API to reschedule the booking
            result = await self.cal_client.reschedule_booking(
                booking_uid=booking_uid,  # Which meeting to reschedule
                new_start_time=args["new_start_time"],  # New time for the meeting
                reason=args.get("reason")  # Optional reason for rescheduling
            )

            # Return success with new booking details
            # The result contains the NEW booking with a different UID
            return {
                "success": True,
                "result": result  # Contains new booking info with new UID
            }
        except Exception as e:
            # Common errors: new time not available, booking not found, etc.
            return {"error": f"Failed to reschedule booking: {str(e)}"}
