"""In-memory database for sessions and messages"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class Session:
    """Session data structure"""
    session_id: str
    username: str
    api_key: str
    created_at: datetime
    last_activity: datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ChatMessage:
    """Chat message data structure"""
    session_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime


class SessionStore:
    """Thread-safe in-memory session storage"""
    
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self._lock = Lock()
    
    def create_session(self, username: str, api_key: str, metadata: Optional[Dict[str, Any]] = None) -> Session:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session = Session(
            session_id=session_id,
            username=username,
            api_key=api_key,
            created_at=now,
            last_activity=now,
            metadata=metadata
        )
        
        with self._lock:
            self._sessions[session_id] = session
        
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID"""
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.last_activity = datetime.now()
            return session
    
    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists"""
        with self._lock:
            return session_id in self._sessions
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False
    
    def get_all_sessions(self) -> List[Session]:
        """Get all sessions"""
        with self._lock:
            return list(self._sessions.values())


class MessageStore:
    """Thread-safe in-memory message storage"""
    
    def __init__(self):
        self._messages: Dict[str, List[ChatMessage]] = {}
        self._lock = Lock()
    
    def add_message(self, session_id: str, role: str, content: str) -> ChatMessage:
        """Add a message to a session's history"""
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            timestamp=datetime.now()
        )
        
        with self._lock:
            if session_id not in self._messages:
                self._messages[session_id] = []
            self._messages[session_id].append(message)
        
        return message
    
    def get_messages(
        self, 
        session_id: str, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[ChatMessage]:
        """Get paginated messages for a session"""
        with self._lock:
            messages = self._messages.get(session_id, [])
            return messages[skip:skip + limit]
    
    def get_message_count(self, session_id: str) -> int:
        """Get total message count for a session"""
        with self._lock:
            return len(self._messages.get(session_id, []))
    
    def clear_messages(self, session_id: str) -> bool:
        """Clear all messages for a session"""
        with self._lock:
            if session_id in self._messages:
                del self._messages[session_id]
                return True
            return False


# Global instances
# Choose between PostgreSQL and in-memory storage based on configuration
from .config import settings

if settings.DATABASE_URL:
    # Use PostgreSQL backend
    try:
        from .database_pg import (
            SessionStore as PgSessionStore,
            MessageStore as PgMessageStore,
            init_db
        )
        
        # Initialize database
        init_db(settings.DATABASE_URL)
        
        # Create instances
        session_store = PgSessionStore()
        message_store = PgMessageStore()
        
        print(f"✓ Using PostgreSQL database backend")
    except Exception as e:
        print(f"⚠ Failed to initialize PostgreSQL backend: {e}")
        print("⚠ Falling back to in-memory storage")
        session_store = SessionStore()
        message_store = MessageStore()
else:
    # Use in-memory backend
    session_store = SessionStore()
    message_store = MessageStore()
    print(f"✓ Using in-memory database backend")
