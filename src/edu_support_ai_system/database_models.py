"""Database models for agent configuration and management"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass

from sqlalchemy import Column, String, DateTime, JSON, Text, Float, Integer, Boolean

# Import Base from database_pg to ensure all models use the same base
from .database_pg import Base


class AgentConfigModel(Base):
    """SQLAlchemy model for agent configurations"""

    __tablename__ = "agent_configs"

    name = Column(String(255), primary_key=True)  # Agent name (e.g., "coordinator")
    model = Column(
        String(255), nullable=False
    )  # Model identifier (e.g., "google::gemini-2.5-flash")
    system_prompt = Column(Text, nullable=False)  # System prompt for the agent
    temperature = Column(Float, nullable=True, default=0.7)  # Model temperature
    max_tokens = Column(Integer, nullable=True, default=2048)  # Max tokens
    enabled = Column(Boolean, nullable=False, default=True)  # Whether agent is enabled
    config_metadata = Column(JSON, nullable=True)  # Additional configuration as JSON
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )
    updated_by = Column(String(255), nullable=True)  # Who last updated this config


class AgentPromptHistoryModel(Base):
    """SQLAlchemy model for tracking agent prompt changes"""

    __tablename__ = "agent_prompt_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_name = Column(String(255), nullable=False, index=True)
    old_prompt = Column(Text, nullable=True)  # Previous prompt (null for first entry)
    new_prompt = Column(Text, nullable=False)  # New prompt
    changed_at = Column(DateTime, nullable=False, default=datetime.now)
    changed_by = Column(String(255), nullable=True)  # Who made the change
    change_reason = Column(Text, nullable=True)  # Optional reason for the change


# Data classes for compatibility with application layer
@dataclass
class AgentConfig:
    """Agent configuration data structure"""

    name: str
    model: str
    system_prompt: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048
    enabled: bool = True
    config_metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


@dataclass
class AgentPromptHistory:
    """Agent prompt history data structure"""

    id: int
    agent_name: str
    old_prompt: Optional[str]
    new_prompt: str
    changed_at: datetime
    changed_by: Optional[str] = None
    change_reason: Optional[str] = None
