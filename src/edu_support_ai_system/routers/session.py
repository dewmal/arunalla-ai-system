"""Session management endpoints"""
from fastapi import APIRouter, HTTPException, status

from ..models import InitSessionRequest, InitSessionResponse
from ..database import session_store
from ..auth import require_valid_api_key

router = APIRouter(prefix="", tags=["session"])


@router.post("/init-session", response_model=InitSessionResponse, status_code=status.HTTP_201_CREATED)
async def init_session(request: InitSessionRequest):
    """
    Initialize a new chat session
    
    Args:
        request: Session initialization request with API key, username, and optional metadata
    
    Returns:
        Session details including session_id and metadata
    
    Raises:
        HTTPException: If API key is invalid
    """
    # Validate API key
    require_valid_api_key(request.api_key)
    
    # Create new session with metadata
    session = session_store.create_session(
        username=request.username,
        api_key=request.api_key,
        metadata=request.metadata
    )
    
    return InitSessionResponse(
        session_id=session.session_id,
        username=session.username,
        created_at=session.created_at,
        metadata=session.metadata
    )
