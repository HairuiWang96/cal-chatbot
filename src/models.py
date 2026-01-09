"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="Content of the message")


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User message")
    conversation_history: List[ChatMessage] = Field(default_factory=list, description="Previous conversation history")
    user_email: Optional[str] = Field(None, description="User's email for booking queries")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str = Field(..., description="Chatbot response")
    conversation_history: List[ChatMessage] = Field(..., description="Updated conversation history")


class BookingDetails(BaseModel):
    """Booking details model"""
    id: int
    event_type_id: int
    title: str
    start_time: str
    end_time: str
    status: str
    attendees: List[Dict[str, Any]]


class AvailableSlot(BaseModel):
    """Available time slot model"""
    time: str
    available: bool
