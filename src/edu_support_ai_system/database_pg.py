"""PostgreSQL database implementation using SQLAlchemy"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, String, DateTime, JSON, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session as DBSession
from sqlalchemy.pool import QueuePool

from .config import settings

# SQLAlchemy Base
Base = declarative_base()


class SessionModel(Base):
    """SQLAlchemy model for sessions"""

    __tablename__ = "sessions"

    session_id = Column(String(36), primary_key=True)
    username = Column(String(255), nullable=False, index=True)
    api_key = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    last_activity = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )
    # Renamed from 'metadata' because it's a reserved SQLAlchemy name
    session_metadata = Column(JSON, nullable=True)


class ChatMessageModel(Base):
    """SQLAlchemy model for chat messages"""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)


# Database engine and session factory
engine = None
SessionLocal = None


def init_db(database_url: str):
    """Initialize database connection and create tables"""
    global engine, SessionLocal

    engine = create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=getattr(settings, "DB_POOL_SIZE", 5),
        max_overflow=getattr(settings, "DB_MAX_OVERFLOW", 10),
        pool_timeout=getattr(settings, "DB_POOL_TIMEOUT", 30),
        pool_recycle=getattr(settings, "DB_POOL_RECYCLE", 3600),
        echo=False,  # Set to True for SQL debugging
    )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Import agent models to ensure they're registered with Base
    from . import database_models  # noqa: F401

    # Create all tables
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db_session():
    """Context manager for database sessions"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Data classes for compatibility with existing interface
from dataclasses import dataclass


@dataclass
class Session:
    """Session data structure (compatible with in-memory version)"""

    session_id: str
    username: str
    api_key: str
    created_at: datetime
    last_activity: datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ChatMessage:
    """Chat message data structure (compatible with in-memory version)"""

    session_id: str
    role: str
    content: str
    timestamp: datetime


class SessionStore:
    """PostgreSQL-backed session storage"""

    def create_session(
        self, username: str, api_key: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Session:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        now = datetime.now()

        with get_db_session() as db:
            db_session = SessionModel(
                session_id=session_id,
                username=username,
                api_key=api_key,
                created_at=now,
                last_activity=now,
                session_metadata=metadata,
            )
            db.add(db_session)
            db.commit()
            db.refresh(db_session)

            return Session(
                session_id=db_session.session_id,
                username=db_session.username,
                api_key=db_session.api_key,
                created_at=db_session.created_at,
                last_activity=db_session.last_activity,
                metadata=db_session.session_metadata,
            )

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID"""
        with get_db_session() as db:
            db_session = (
                db.query(SessionModel)
                .filter(SessionModel.session_id == session_id)
                .first()
            )

            if not db_session:
                return None

            # Update last activity
            db_session.last_activity = datetime.now()
            db.commit()

            return Session(
                session_id=db_session.session_id,
                username=db_session.username,
                api_key=db_session.api_key,
                created_at=db_session.created_at,
                last_activity=db_session.last_activity,
                metadata=db_session.session_metadata,
            )

    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists"""
        with get_db_session() as db:
            count = (
                db.query(SessionModel)
                .filter(SessionModel.session_id == session_id)
                .count()
            )
            return count > 0

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        with get_db_session() as db:
            result = (
                db.query(SessionModel)
                .filter(SessionModel.session_id == session_id)
                .delete()
            )
            db.commit()
            return result > 0

    def get_all_sessions(self) -> List[Session]:
        """Get all sessions"""
        with get_db_session() as db:
            db_sessions = db.query(SessionModel).all()
            return [
                Session(
                    session_id=s.session_id,
                    username=s.username,
                    api_key=s.api_key,
                    created_at=s.created_at,
                    last_activity=s.last_activity,
                    metadata=s.session_metadata,
                )
                for s in db_sessions
            ]


class MessageStore:
    """PostgreSQL-backed message storage"""

    def add_message(self, session_id: str, role: str, content: str) -> ChatMessage:
        """Add a message to a session's history"""
        now = datetime.now()

        with get_db_session() as db:
            db_message = ChatMessageModel(
                session_id=session_id, role=role, content=content, timestamp=now
            )
            db.add(db_message)
            db.commit()

            return ChatMessage(
                session_id=session_id, role=role, content=content, timestamp=now
            )

    def get_messages(
        self, session_id: str, skip: int = 0, limit: int = 20
    ) -> List[ChatMessage]:
        """Get paginated messages for a session"""
        with get_db_session() as db:
            db_messages = (
                db.query(ChatMessageModel)
                .filter(ChatMessageModel.session_id == session_id)
                .order_by(ChatMessageModel.timestamp.asc())
                .offset(skip)
                .limit(limit)
                .all()
            )

            return [
                ChatMessage(
                    session_id=m.session_id,
                    role=m.role,
                    content=m.content,
                    timestamp=m.timestamp,
                )
                for m in db_messages
            ]

    def get_message_count(self, session_id: str) -> int:
        """Get total message count for a session"""
        with get_db_session() as db:
            return (
                db.query(ChatMessageModel)
                .filter(ChatMessageModel.session_id == session_id)
                .count()
            )

    def clear_messages(self, session_id: str) -> bool:
        """Clear all messages for a session"""
        with get_db_session() as db:
            result = (
                db.query(ChatMessageModel)
                .filter(ChatMessageModel.session_id == session_id)
                .delete()
            )
            db.commit()
            return result > 0
