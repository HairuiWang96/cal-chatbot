# Quick Setup Guide

Follow these steps to get the chatbot running in under 5 minutes.

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Environment Variables

1. The `.env` file has been created with the provided API keys
2. You need to add two more values:

### Get Your Cal.com Event Type ID

Run the test script:
```bash
python test_api.py
```

This will show you:
- Your Cal.com event types and their IDs
- Available slots (if configured)
- Your current bookings

Copy one of the event type IDs and add it to `.env`:
```env
CAL_EVENT_TYPE_ID=123456
```

### Set Your Email

Update the `.env` file with your Cal.com email:
```env
CAL_USER_EMAIL=your_email@example.com
```

## Step 3: Test the Setup

Run the test script again to verify everything works:
```bash
python test_api.py
```

You should see:
- ✅ Cal.com API client initialized successfully
- ✅ Found X event type(s)
- ✅ Found X available slot(s)
- ✅ Configuration checklist all green

## Step 4: Choose How to Run

### Option A: Web UI (Easiest)

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

### Option B: REST API

```bash
python src/main.py
```

API available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### Option C: Interactive CLI

```bash
python example_usage.py --interactive
```

### Option D: Use the Quick Start Script

```bash
./run.sh
```

This will guide you through testing and running the application.

## Step 5: Try It Out

Example conversations to try:

1. **Book a meeting**:
   - "Help me book a meeting for tomorrow at 2pm"
   - Provide your email, name, and meeting reason when asked

2. **View meetings**:
   - "Show me my scheduled events"

3. **Cancel a meeting** (if you have bookings):
   - "Cancel my meeting at 2pm today"

4. **Reschedule** (if you have bookings):
   - "Reschedule my Monday meeting to Tuesday at 3pm"

## Troubleshooting

### "Event type ID not configured"
- Run `python test_api.py` to see your event types
- Copy an event type ID to `.env` as `CAL_EVENT_TYPE_ID`

### "No event types found"
- Log in to Cal.com
- Go to Event Types
- Create a new event type (e.g., "30 Minute Meeting")
- Set your availability
- Run `python test_api.py` again

### "Failed to get available slots"
- Make sure your event type has availability set
- Check that you're looking at future dates
- Verify the event type is active and public/bookable

### Import errors
- Make sure you installed requirements: `pip install -r requirements.txt`
- Try upgrading pip: `pip install --upgrade pip`

## What's Next?

Once everything is working:

1. **Read** [IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md) to understand:
   - What AI can and cannot do
   - Areas that need manual testing
   - Business logic decisions you need to make

2. **Test thoroughly**:
   - Try all the example conversations
   - Test edge cases (past dates, invalid times, etc.)
   - Verify the Cal.com responses match expectations

3. **Customize**:
   - Adjust the system prompt in [src/chatbot.py](src/chatbot.py#L20)
   - Modify function descriptions in [src/tools.py](src/tools.py)
   - Enhance error handling in [src/cal_api.py](src/cal_api.py)

4. **Package for submission**:
   - Test everything one more time
   - Zip the project directory
   - Submit by the deadline

## Project Structure

```
chatbot/
├── app.py                    # Streamlit UI (run this for web interface)
├── src/
│   ├── main.py              # FastAPI server (run this for REST API)
│   ├── chatbot.py           # Core chatbot logic
│   ├── cal_api.py           # Cal.com API client
│   ├── tools.py             # OpenAI function definitions
│   └── models.py            # Data models
├── test_api.py              # Test Cal.com connectivity
├── example_usage.py         # CLI examples
├── run.sh                   # Quick start script
└── requirements.txt         # Dependencies
```

## Need Help?

- Check [README.md](README.md) for detailed documentation
- Read [IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md) for technical details
- Review the code comments for inline documentation
- Test individual components using the test scripts
