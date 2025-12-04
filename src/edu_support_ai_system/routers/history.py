"""Chat history endpoints"""
import math
from fastapi import APIRouter, HTTPException, status, Query

from ..models import HistoryResponse, Message, PaginationMeta
from ..database import session_store, message_store
from .. import config

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=HistoryResponse)
async def get_history(
    session_id: str = Query(..., description="Session ID to retrieve history for"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(
        config.DEFAULT_PAGE_SIZE,
        ge=1,
        le=config.MAX_PAGE_SIZE,
        description="Number of messages per page"
    )
):
    """
    Get paginated chat history for a session
    
    Args:
        session_id: Session identifier
        page: Page number (starts at 1)
        page_size: Number of messages per page
    
    Returns:
        Paginated chat history with metadata
    
    Raises:
        HTTPException: If session doesn't exist
    """
    # Validate session exists
    if not session_store.session_exists(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get total message count
    total_messages = message_store.get_message_count(session_id)
    
    # Calculate pagination
    total_pages = math.ceil(total_messages / page_size) if total_messages > 0 else 1
    skip = (page - 1) * page_size
    
    # Validate page number
    if page > total_pages and total_messages > 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Page {page} not found. Total pages: {total_pages}"
        )
    
    # Get messages for current page
    messages = message_store.get_messages(
        session_id=session_id,
        skip=skip,
        limit=page_size
    )
    
    # Convert to response model
    message_list = [
        Message(
            role=msg.role,
            content=msg.content,
            timestamp=msg.timestamp
        )
        for msg in messages
    ]
    
    # Build pagination metadata
    pagination = PaginationMeta(
        total=total_messages,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
    
    return HistoryResponse(
        messages=message_list,
        pagination=pagination
    )
