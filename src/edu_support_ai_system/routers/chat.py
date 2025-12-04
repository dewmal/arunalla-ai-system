"""Chat endpoints with SSE and WebSocket support"""
import asyncio
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, WebSocket, WebSocketDisconnect
from sse_starlette.sse import EventSourceResponse

from ..models import ChatRequest, ChatResponse, WebSocketMessage
from ..database import session_store, message_store

router = APIRouter(prefix="/chat", tags=["chat"])


async def generate_ai_response(message: str) -> str:
    """
    Generate AI response (mock implementation)
    
    In production, this would integrate with your AI model/service.
    
    Args:
        message: User's message
    
    Returns:
        AI generated response
    """
    # Simulate processing delay
    await asyncio.sleep(0.5)
    
    # Mock responses based on message content
    message_lower = message.lower()
    
    if "hello" in message_lower or "hi" in message_lower:
        return "Hello! How can I help you with your educational needs today?"
    elif "help" in message_lower:
        return "I'm here to assist you with your learning. You can ask me questions about various topics, request explanations, or seek study guidance."
    elif "?" in message:
        return f"That's a great question! Let me help you understand that better. Regarding '{message}', here's what I can tell you..."
    else:
        return f"I understand you said: '{message}'. How can I assist you further with your studies?"


async def stream_response(message: str) -> str:
    """
    Stream response word by word
    
    Args:
        message: Full response message
    
    Yields:
        Words from the response
    """
    words = message.split()
    for word in words:
        await asyncio.sleep(0.05)  # Simulate streaming delay
        yield word + " "


@router.post("/sse", response_class=EventSourceResponse)
async def chat_sse(request: ChatRequest):
    """
    Chat endpoint using Server-Sent Events for streaming responses
    
    Args:
        request: Chat request with session_id and message
    
    Returns:
        EventSourceResponse: Streaming SSE response
    
    Raises:
        HTTPException: If session doesn't exist
    """
    # Validate session exists
    if not session_store.session_exists(request.session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Store user message
    message_store.add_message(
        session_id=request.session_id,
        role="user",
        content=request.message
    )
    
    async def event_generator():
        """Generate SSE events"""
        try:
            # Generate AI response
            ai_response = await generate_ai_response(request.message)
            
            # Stream response word by word
            full_response = ""
            async for chunk in stream_response(ai_response):
                full_response += chunk
                # Send each chunk as an SSE event
                yield {
                    "event": "message",
                    "data": json.dumps({
                        "role": "assistant",
                        "content": chunk,
                        "timestamp": datetime.now().isoformat()
                    })
                }
            
            # Store complete AI response
            message_store.add_message(
                session_id=request.session_id,
                role="assistant",
                content=ai_response
            )
            
            # Send completion event
            yield {
                "event": "done",
                "data": json.dumps({"status": "complete"})
            }
            
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
    
    return EventSourceResponse(event_generator())


@router.websocket("/ws/{session_id}")
async def chat_websocket(websocket: WebSocket, session_id: str):
    """
    Chat endpoint using WebSocket for bidirectional communication
    
    Args:
        websocket: WebSocket connection
        session_id: Session identifier
    """
    # Validate session exists
    if not session_store.session_exists(session_id):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Session not found")
        return
    
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                # Parse message
                msg_data = json.loads(data)
                ws_message = WebSocketMessage(**msg_data)
                user_message = ws_message.message
                
                # Store user message
                message_store.add_message(
                    session_id=session_id,
                    role="user",
                    content=user_message
                )
                
                # Send acknowledgment
                await websocket.send_json({
                    "type": "user_message_received",
                    "role": "user",
                    "content": user_message,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Generate AI response
                ai_response = await generate_ai_response(user_message)
                
                # Stream response
                full_response = ""
                async for chunk in stream_response(ai_response):
                    full_response += chunk
                    await websocket.send_json({
                        "type": "assistant_message_chunk",
                        "role": "assistant",
                        "content": chunk,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Store AI response
                message_store.add_message(
                    session_id=session_id,
                    role="assistant",
                    content=ai_response
                )
                
                # Send completion
                await websocket.send_json({
                    "type": "message_complete",
                    "status": "complete",
                    "timestamp": datetime.now().isoformat()
                })
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "error": "Invalid JSON format"
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "error": str(e)
                })
    
    except WebSocketDisconnect:
        pass  # Client disconnected
