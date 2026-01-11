"""
FastAPI server for Cal.com chatbot

This file creates a REST API server that allows clients to interact with the Cal.com chatbot.
FastAPI is a modern Python web framework for building APIs - it's fast, easy to use, and
automatically generates API documentation.
"""

# Import statements - bringing in external libraries and modules we need
from fastapi import FastAPI, HTTPException  # FastAPI: main framework, HTTPException: for error responses
from fastapi.middleware.cors import CORSMiddleware  # CORS: allows web browsers to call our API
from contextlib import asynccontextmanager  # Python's context manager for setup/cleanup
import uvicorn  # ASGI server that actually runs our FastAPI application

# Import our custom classes from other files in the project
from src.models import ChatRequest, ChatResponse, ChatMessage  # Data models (what our API sends/receives)
from src.chatbot import CalChatbot  # The actual chatbot logic

# Global variable to store our chatbot instance
# "Global" means this variable is accessible throughout the entire file
# We initialize it as None and set it up later in the lifespan function
chatbot = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager - handles startup and shutdown events

    This is a special FastAPI feature that runs code when:
    1. The server STARTS (before the "yield" line)
    2. The server STOPS (after the "yield" line)

    Think of it like:
    - Setup code (before yield) runs when you start the server
    - Cleanup code (after yield) runs when you stop the server (Ctrl+C)

    Why use this? To create resources once (like database connections or our chatbot)
    instead of creating them for every single request.
    """
    global chatbot  # Access the global chatbot variable defined above
    chatbot = CalChatbot()  # Create a single chatbot instance that will handle all requests
    print("Chatbot initialized")  # Log message when server starts
    yield  # This line separates startup code (above) from shutdown code (below)
    print("Shutting down")  # Log message when server stops


# Create the main FastAPI application instance
# This is the core object that will handle all incoming HTTP requests
app = FastAPI(
    title="Cal.com Chatbot API",  # Shows up in auto-generated documentation
    description="Interactive chatbot for booking meetings via Cal.com",  # API description
    version="1.0.0",  # API version number
    lifespan=lifespan  # Connect our lifespan function to handle startup/shutdown
)

# Add CORS middleware to the application
# CORS (Cross-Origin Resource Sharing) allows web browsers to call our API
# Without this, browsers would block requests from web pages to our API
app.add_middleware(
    CORSMiddleware,  # The middleware class we're adding
    allow_origins=["*"],  # Allow requests from ANY domain (use specific domains in production)
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers in requests
)


@app.get("/")
async def root():
    """
    Root endpoint - the homepage of our API

    What is an endpoint? It's like a specific URL path on a website.
    When someone visits http://localhost:8000/ they hit this endpoint.

    The @app.get("/") is a "decorator" - it tells FastAPI:
    - This function handles GET requests (reading data, not changing anything)
    - For the "/" path (the root/home page)

    The "async def" means this is an asynchronous function - it can handle
    multiple requests at the same time without blocking.
    """
    return {
        "message": "Cal.com Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """
    Health check endpoint

    This is a simple endpoint that other services can call to check if our
    API is running properly. Common in production environments for monitoring.

    Example: http://localhost:8000/health returns {"status": "healthy"}
    """
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - this is where the magic happens!

    The @app.post decorator means:
    - This handles POST requests (sending data to create/modify something)
    - At the "/chat" path

    The "response_model=ChatResponse" tells FastAPI:
    - Validate that our return value matches the ChatResponse structure
    - Auto-generate documentation showing what this endpoint returns

    Parameters:
    - request: ChatRequest - A validated object containing the user's message
      and conversation history. FastAPI automatically converts the JSON from
      the HTTP request into this Python object and validates it.

    The chatbot can:
    - Book new meetings ("Book a meeting tomorrow at 2pm")
    - List scheduled meetings ("What meetings do I have?")
    - Cancel meetings ("Cancel my meeting on Monday")
    - Reschedule meetings ("Move my 2pm meeting to 3pm")
    """
    try:
        # Convert Pydantic models to plain Python dictionaries
        # Why? Our chatbot.chat() function expects simple dicts, not Pydantic objects
        # This is a list comprehension - a compact way to transform a list in Python
        # It takes each message object and converts it to a dict with "role" and "content" keys
        history = [{"role": msg.role, "content": msg.content} for msg in request.conversation_history]

        # Call the chatbot with the user's message and conversation history
        # The "await" keyword means "wait for this async operation to complete"
        # This returns two things (tuple unpacking):
        # 1. response: the chatbot's text response to the user
        # 2. updated_history: the full conversation including the new exchange
        response, updated_history = await chatbot.chat(
            user_message=request.message,
            conversation_history=history,
            user_email=request.user_email
        )

        # Convert the plain dicts back into Pydantic models for the API response
        # Why? FastAPI uses Pydantic models to validate and document the response format
        # Again using list comprehension to transform the data
        history_models = [ChatMessage(role=msg["role"], content=msg["content"]) for msg in updated_history]

        # Return a ChatResponse object (FastAPI converts this to JSON automatically)
        return ChatResponse(
            response=response,
            conversation_history=history_models
        )
    except Exception as e:
        # If anything goes wrong, raise an HTTP 500 error with details
        # HTTPException is FastAPI's way of returning error responses
        # Status code 500 = "Internal Server Error"
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.post("/reset")
async def reset_conversation():
    """
    Reset conversation endpoint

    This endpoint doesn't actually do anything except return instructions.
    Why? Because our API is stateless - we don't store conversation history
    on the server. The client (Streamlit UI or whoever calls our API) is
    responsible for managing and sending the conversation history with each request.

    To "reset" a conversation, the client just stops sending the old history.
    """
    return {"message": "To reset conversation, simply stop sending conversation_history in your requests"}


def start_server(host: str = "0.0.0.0", port: int = 8000):
    """
    Helper function to start the FastAPI server

    Parameters:
    - host: The IP address to bind to
      "0.0.0.0" means "listen on all available network interfaces"
      This allows connections from localhost AND from other machines on the network
    - port: The port number to listen on (default 8000)

    uvicorn is the actual web server that runs our FastAPI app
    It handles the low-level HTTP protocol stuff so we don't have to
    """
    uvicorn.run(app, host=host, port=port)


# This is Python's way of saying "only run this code if this file is executed directly"
# If someone imports this file as a module, this block won't run
# When you run "python src/main.py", this condition is True
if __name__ == "__main__":
    start_server()  # Start the server on default host and port
