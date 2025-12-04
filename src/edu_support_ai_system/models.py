"""Pydantic models for API requests and responses"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# Session Models
class InitSessionRequest(BaseModel):
    """Request model for initializing a new session"""
    api_key: str = Field(..., description="API key for authentication")
    username: str = Field(..., min_length=1, max_length=100, description="Username for the session")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata for the session")


class InitSessionResponse(BaseModel):
    """Response model for session initialization"""
    session_id: str = Field(..., description="Unique session identifier")
    username: str = Field(..., description="Username associated with the session")
    created_at: datetime = Field(..., description="Session creation timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Session metadata")


# Chat Models
class ChatRequest(BaseModel):
    """Request model for chat messages"""
    session_id: str = Field(..., description="Session identifier")
    message: str = Field(..., min_length=1, description="User message content")


class ChatResponse(BaseModel):
    """Response model for chat messages"""
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp")


# WebSocket Message Model
class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    message: str = Field(..., min_length=1, description="Message content")


# History Models
class Message(BaseModel):
    """Individual message in chat history"""
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp")


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    total: int = Field(..., description="Total number of messages")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class HistoryResponse(BaseModel):
    """Response model for chat history"""
    messages: List[Message] = Field(..., description="List of messages for current page")
    pagination: PaginationMeta = Field(..., description="Pagination information")


# Error Response
class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str = Field(..., description="Error message")
