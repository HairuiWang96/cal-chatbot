# Cal.com Meeting Assistant Chatbot

An interactive chatbot that integrates Cal.com with OpenAI's function calling capabilities to help users book, view, cancel, and reschedule meetings through natural language conversations.

## Features

### Core Features
- **Book Meetings**: Ask the chatbot to book a meeting and it will guide you through the process
- **List Meetings**: View your scheduled meetings by simply asking
- **Natural Language Processing**: Use conversational language for dates and times (e.g., "tomorrow at 3pm", "next Monday")

### Bonus Features
- **Cancel Meetings**: Cancel specific meetings by describing them
- **Reschedule Meetings**: Move meetings to new times
- **Interactive Web UI**: Beautiful Streamlit-based web interface for easy interaction
- **REST API**: Programmatic access via FastAPI endpoints

## Project Structure

```
chatbot/
├── .env                          # Environment variables (not committed)
├── .env.example                  # Example environment configuration
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── test_api.py                   # Cal.com API test script
├── app.py                        # Streamlit web UI
├── src/
│   ├── __init__.py
│   ├── main.py                   # FastAPI server
│   ├── chatbot.py                # Core chatbot logic with OpenAI
│   ├── cal_api.py                # Cal.com API wrapper
│   ├── tools.py                  # OpenAI function definitions
│   └── models.py                 # Pydantic models
└── tests/
    └── (test files)
```

## Setup Instructions

### 1. Prerequisites

- Python 3.9 or higher
- Cal.com account with API access
- OpenAI API key

### 2. Cal.com Account Setup

1. Create a Cal.com account at [cal.com](https://cal.com)
2. Create at least one event type (e.g., "30 Minute Meeting")
3. Get your API key:
   - Go to Settings > Developer > API Keys
   - Create a new API key
   - Copy the key (starts with `cal_live_`)

### 3. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### 4. Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and fill in your credentials:
```env
# OpenAI API Key (provided in challenge)
OPENAI_API_KEY=your_openai_key_here

# Cal.com API Key (from your Cal.com account)
CAL_API_KEY=your_cal_api_key_here

# Your Cal.com user email
CAL_USER_EMAIL=your_email@example.com

# Event Type ID (get this by running test_api.py)
CAL_EVENT_TYPE_ID=your_event_type_id
```

### 5. Test Your Setup

Run the test script to verify your Cal.com API configuration:

```bash
python test_api.py
```

This will:
- List your event types and their IDs
- Test available slots endpoint
- Test bookings endpoint
- Verify your configuration

Copy one of the event type IDs and add it to your `.env` file as `CAL_EVENT_TYPE_ID`.

## Usage

### Option 1: Web UI (Recommended)

Start the Streamlit web interface:

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

**Features:**
- Beautiful chat interface
- Real-time responses
- Email configuration in sidebar
- Chat history management

**Example conversations:**
- "Help me book a meeting for tomorrow at 2pm"
- "Show me my scheduled events"
- "Cancel my meeting at 3pm today"
- "Reschedule my Monday meeting to Tuesday"

### Option 2: REST API

Start the FastAPI server:

```bash
python -m uvicorn src.main:app --reload
```

Or:

```bash
python src/main.py
```

The API will be available at `http://localhost:8000`

**API Documentation:** Visit `http://localhost:8000/docs` for interactive API documentation

**Example API Request:**

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me book a meeting",
    "conversation_history": [],
    "user_email": "your_email@example.com"
  }'
```

**Response:**
```json
{
  "response": "I'd be happy to help you book a meeting! Could you please provide me with the following details:\n1. What date would you like?\n2. What time works for you?\n3. What is the meeting about?",
  "conversation_history": [
    {"role": "user", "content": "Help me book a meeting"},
    {"role": "assistant", "content": "I'd be happy to help..."}
  ]
}
```

## How It Works

### Architecture

1. **User Input**: User sends a natural language message
2. **OpenAI Processing**: GPT-4 processes the message and determines if function calls are needed
3. **Function Calling**: If needed, the chatbot calls Cal.com API functions:
   - `get_available_slots`: Check availability
   - `create_booking`: Create a new meeting
   - `get_user_bookings`: List meetings
   - `cancel_booking`: Cancel a meeting
   - `reschedule_booking`: Reschedule a meeting
4. **Response Generation**: OpenAI generates a natural language response based on API results
5. **User Response**: Response is sent back to the user

### Key Components

- **OpenAI Function Calling**: Enables the LLM to call external functions with proper parameters
- **Cal.com API v2**: REST API for managing bookings and availability
- **FastAPI**: Modern Python web framework for REST endpoints
- **Streamlit**: Interactive web UI framework
- **Async/Await**: Asynchronous programming for better performance

## Example Conversations

### Booking a Meeting

```
User: Help me book a meeting
Bot: I'd be happy to help you book a meeting! Could you please provide me with:
     1. Your preferred date and time
     2. Your email address
     3. Your name
     4. The reason for the meeting

User: Tomorrow at 2pm, john@example.com, John Doe, discuss project proposal
Bot: Let me check availability for tomorrow at 2pm...
     Great! I've successfully booked your meeting for tomorrow at 2:00 PM.
     Meeting details:
     - Time: 2024-01-16 14:00 UTC
     - Attendee: John Doe (john@example.com)
     - Reason: discuss project proposal
```

### Viewing Meetings

```
User: Show me my scheduled events
Bot: Let me fetch your upcoming meetings...
     You have 2 upcoming meetings:

     1. Meeting on Jan 16, 2024 at 2:00 PM
        With: John Doe
        Reason: discuss project proposal

     2. Meeting on Jan 18, 2024 at 10:00 AM
        With: Jane Smith
        Reason: quarterly review
```

### Canceling a Meeting

```
User: Cancel my 2pm meeting today
Bot: Let me find your 2pm meeting today...
     I found your meeting at 2:00 PM today. Would you like me to cancel it?

User: Yes, please cancel it
Bot: Your meeting at 2:00 PM has been successfully cancelled.
```

## API Endpoints

### POST /chat
Main chat endpoint for interacting with the chatbot.

**Request Body:**
```json
{
  "message": "string",
  "conversation_history": [
    {"role": "user", "content": "string"},
    {"role": "assistant", "content": "string"}
  ],
  "user_email": "string (optional)"
}
```

**Response:**
```json
{
  "response": "string",
  "conversation_history": [...]
}
```

### GET /health
Health check endpoint.

### GET /
API information and available endpoints.

## Development

### Running Tests

```bash
pytest tests/
```

### Code Structure

- **cal_api.py**: Handles all Cal.com API interactions with proper error handling
- **tools.py**: Defines OpenAI function schemas for function calling
- **chatbot.py**: Core chatbot logic that orchestrates OpenAI and Cal.com API
- **main.py**: FastAPI server with REST endpoints
- **app.py**: Streamlit web UI
- **models.py**: Pydantic models for request/response validation

## What AI Can vs Cannot Do

### What AI CAN Do (Demonstrated in this project):
- Generate boilerplate code and project structure
- Create API integration patterns
- Design function calling schemas
- Build web UI scaffolding
- Write documentation

### What AI CANNOT Do (Requires Human Judgment):
- Test with real credentials and verify actual API responses
- Make business logic decisions (e.g., how to handle booking conflicts)
- Configure production deployment and scaling
- Understand Cal.com's specific response formats without testing
- Handle edge cases that require domain knowledge
- Make security and API key management decisions

## Troubleshooting

### "Event type ID not configured"
- Run `python test_api.py` to see your event types
- Copy an event type ID to your `.env` file

### "Failed to get available slots"
- Verify your event type has availability configured in Cal.com
- Check that your event type is active and bookable

### "Failed to create booking"
- Ensure the time slot is actually available
- Verify all required fields are provided
- Check Cal.com booking settings

### OpenAI API errors
- Verify your OpenAI API key is correct
- Check you have sufficient credits
- Ensure you're using a supported model

## Security Notes

- Never commit `.env` file or API keys to version control
- The provided OpenAI key is for this project only
- Rotate API keys regularly in production
- Use environment variables for all sensitive data

## Future Enhancements

- Add timezone detection and conversion
- Support for recurring meetings
- Integration with Google Calendar/Outlook
- Multi-user support with authentication
- Email notifications for bookings
- Meeting reminders
- Video conferencing link generation

## License

This project is created for the Cal.com coding challenge.

## Support

For issues with:
- Cal.com API: Check [Cal.com API docs](https://cal.com/docs/api-reference)
- OpenAI: Check [OpenAI documentation](https://platform.openai.com/docs)
- This project: Review code comments and test scripts
