"""
FastAPI server for Cal.com chatbot
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from src.models import ChatRequest, ChatResponse, ChatMessage
from src.chatbot import CalChatbot

# Global chatbot instance
chatbot = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup chatbot"""
    global chatbot
    chatbot = CalChatbot()
    print("Chatbot initialized")
    yield
    print("Shutting down")


# Create FastAPI app
app = FastAPI(
    title="Cal.com Chatbot API",
    description="Interactive chatbot for booking meetings via Cal.com",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
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
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for interacting with the chatbot

    Send a message and get a response. The chatbot can:
    - Book new meetings
    - List scheduled meetings
    - Cancel meetings
    - Reschedule meetings
    """
    try:
        # Convert Pydantic models to dicts for chatbot
        history = [{"role": msg.role, "content": msg.content} for msg in request.conversation_history]

        # Get response from chatbot
        response, updated_history = await chatbot.chat(
            user_message=request.message,
            conversation_history=history,
            user_email=request.user_email
        )

        # Convert back to Pydantic models
        history_models = [ChatMessage(role=msg["role"], content=msg["content"]) for msg in updated_history]

        return ChatResponse(
            response=response,
            conversation_history=history_models
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.post("/reset")
async def reset_conversation():
    """Reset the conversation history"""
    return {"message": "To reset conversation, simply stop sending conversation_history in your requests"}


def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the FastAPI server"""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
