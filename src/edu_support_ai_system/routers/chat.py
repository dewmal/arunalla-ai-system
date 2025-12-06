"""Chat endpoints with SSE and WebSocket support"""

import asyncio
import json
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, WebSocket, WebSocketDisconnect
from sse_starlette.sse import EventSourceResponse

from ..models import ChatRequest, ChatResponse, WebSocketMessage
from ..database import session_store, message_store

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


async def send_message_via_mesh(message: str, from_agent: str = "chat_api") -> str:
    """
    Send message to coordinator through mesh network.

    This function uses the mesh infrastructure for agent communication,
    providing proper routing and error handling. Falls back to direct
    coordinator access if mesh is unavailable.

    Args:
        message: User's message to send
        from_agent: Identifier of the sending agent (default: "chat_api")

    Returns:
        Response from the coordinator agent

    Raises:
        RuntimeError: If both mesh and direct communication fail
    """
    try:
        # Try mesh-based communication first
        from agent_mesh.mesh import send_message, is_agent_registered, get_agents

        logger.info(f"Registered agents: {get_agents()}")
        if is_agent_registered("Coordinator"):
            logger.info("Coordinator registered in mesh")
            # Use mesh to route message to coordinator
            response = send_message(
                from_agent=from_agent, to_agent="Coordinator", message=message
            )
            return response
        else:
            # Fallback: Coordinator not registered in mesh yet
            # Use direct access as fallback
            from agent_mesh.agents.coordinator import coordinator

            response = await coordinator.send_message_async(message)
            return (
                response
                if response
                else "I'm sorry, I didn't understand that. Can you please rephrase your question?"
            )

    except Exception as e:
        # If mesh communication fails, fallback to direct coordinator access
        try:
            from agent_mesh.agents.coordinator import coordinator

            response = await coordinator.send_message_async(message)
            return (
                response
                if response
                else "I'm sorry, I didn't understand that. Can you please rephrase your question?"
            )
        except Exception as fallback_error:
            raise RuntimeError(
                f"Failed to communicate with coordinator: {e}, Fallback error: {fallback_error}"
            )


async def generate_ai_response(message: str) -> str:
    """
    Generate AI response using mesh-based communication.

    This function routes the user message through the mesh network to the
    coordinator agent, which orchestrates the response using specialized agents.

    Args:
        message: User's message

    Returns:
        AI generated response
    """
    try:
        response = await send_message_via_mesh(message)
        return response
    except RuntimeError as e:
        # Log error and return user-friendly message
        logger.error(f"Error generating AI response: {e}")
        return "I'm experiencing technical difficulties. Please try again later."


async def stream_response(message: str):
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    # Store user message
    message_store.add_message(
        session_id=request.session_id, role="user", content=request.message
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
                    "data": json.dumps(
                        {
                            "role": "assistant",
                            "content": chunk,
                            "timestamp": datetime.now().isoformat(),
                        }
                    ),
                }

            # Store complete AI response
            message_store.add_message(
                session_id=request.session_id, role="assistant", content=ai_response
            )

            # Send completion event
            yield {"event": "done", "data": json.dumps({"status": "complete"})}

        except Exception as e:
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

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
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="Session not found"
        )
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
                    session_id=session_id, role="user", content=user_message
                )

                # Send acknowledgment
                await websocket.send_json(
                    {
                        "type": "user_message_received",
                        "role": "user",
                        "content": user_message,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                # Generate AI response
                ai_response = await generate_ai_response(user_message)

                # Stream response
                full_response = ""
                async for chunk in stream_response(ai_response):
                    full_response += chunk
                    await websocket.send_json(
                        {
                            "type": "assistant_message_chunk",
                            "role": "assistant",
                            "content": chunk,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

                # Store AI response
                message_store.add_message(
                    session_id=session_id, role="assistant", content=ai_response
                )

                # Send completion
                await websocket.send_json(
                    {
                        "type": "message_complete",
                        "status": "complete",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            except json.JSONDecodeError:
                await websocket.send_json(
                    {"type": "error", "error": "Invalid JSON format"}
                )
            except Exception as e:
                await websocket.send_json({"type": "error", "error": str(e)})

    except WebSocketDisconnect:
        pass  # Client disconnected
