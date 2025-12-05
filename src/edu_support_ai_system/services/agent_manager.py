"""Agent management service for dynamic agent configuration"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from sqlalchemy.exc import IntegrityError

from ..database_pg import get_db_session
from ..database_models import (
    AgentConfigModel,
    AgentPromptHistoryModel,
    AgentConfig,
    AgentPromptHistory,
)

logger = logging.getLogger(__name__)


class AgentManager:
    """Service for managing agent configurations"""

    def __init__(self):
        """Initialize agent manager"""
        self._agent_cache: Dict[str, Any] = {}  # Cache for agent instances

    def get_agent_config(self, agent_name: str) -> Optional[AgentConfig]:
        """
        Get agent configuration by name

        Args:
            agent_name: Name of the agent

        Returns:
            AgentConfig or None if not found
        """
        try:
            with get_db_session() as db:
                config = (
                    db.query(AgentConfigModel)
                    .filter(AgentConfigModel.name == agent_name)
                    .first()
                )

                if not config:
                    return None

                return AgentConfig(
                    name=config.name,
                    model=config.model,
                    system_prompt=config.system_prompt,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    enabled=config.enabled,
                    config_metadata=config.config_metadata,
                    created_at=config.created_at,
                    updated_at=config.updated_at,
                    updated_by=config.updated_by,
                )
        except Exception as e:
            logger.error(f"Error getting agent config for {agent_name}: {e}")
            return None

    def list_agent_configs(self, enabled_only: bool = False) -> List[AgentConfig]:
        """
        List all agent configurations

        Args:
            enabled_only: If True, only return enabled agents

        Returns:
            List of AgentConfig objects
        """
        try:
            with get_db_session() as db:
                query = db.query(AgentConfigModel)
                if enabled_only:
                    query = query.filter(AgentConfigModel.enabled)

                configs = query.all()

                return [
                    AgentConfig(
                        name=c.name,
                        model=c.model,
                        system_prompt=c.system_prompt,
                        temperature=c.temperature,
                        max_tokens=c.max_tokens,
                        enabled=c.enabled,
                        config_metadata=c.config_metadata,
                        created_at=c.created_at,
                        updated_at=c.updated_at,
                        updated_by=c.updated_by,
                    )
                    for c in configs
                ]
        except Exception as e:
            logger.error(f"Error listing agent configs: {e}")
            return []

    def create_agent_config(
        self,
        name: str,
        model: str,
        system_prompt: str,
        temperature: Optional[float] = 0.7,
        max_tokens: Optional[int] = 2048,
        enabled: bool = True,
        config_metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None,
    ) -> Optional[AgentConfig]:
        """
        Create a new agent configuration

        Args:
            name: Agent name
            model: Model identifier
            system_prompt: System prompt
            temperature: Model temperature
            max_tokens: Max tokens
            enabled: Whether agent is enabled
            config_metadata: Additional metadata
            created_by: Who created this config

        Returns:
            Created AgentConfig or None on error
        """
        try:
            with get_db_session() as db:
                config = AgentConfigModel(
                    name=name,
                    model=model,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    enabled=enabled,
                    config_metadata=config_metadata,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    updated_by=created_by,
                )
                db.add(config)
                db.commit()
                db.refresh(config)

                # Record in history
                history = AgentPromptHistoryModel(
                    agent_name=name,
                    old_prompt=None,
                    new_prompt=system_prompt,
                    changed_at=datetime.now(),
                    changed_by=created_by,
                    change_reason="Initial configuration",
                )
                db.add(history)
                db.commit()

                return self.get_agent_config(name)
        except IntegrityError:
            logger.error(f"Agent config with name {name} already exists")
            return None
        except Exception as e:
            logger.error(f"Error creating agent config: {e}")
            return None

    def update_agent_config(
        self,
        name: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        enabled: Optional[bool] = None,
        config_metadata: Optional[Dict[str, Any]] = None,
        updated_by: Optional[str] = None,
        change_reason: Optional[str] = None,
    ) -> Optional[AgentConfig]:
        """
        Update an existing agent configuration

        Args:
            name: Agent name
            model: New model identifier (optional)
            system_prompt: New system prompt (optional)
            temperature: New temperature (optional)
            max_tokens: New max tokens (optional)
            enabled: New enabled status (optional)
            config_metadata: New metadata (optional)
            updated_by: Who updated this config
            change_reason: Reason for the change

        Returns:
            Updated AgentConfig or None on error
        """
        try:
            with get_db_session() as db:
                config = (
                    db.query(AgentConfigModel)
                    .filter(AgentConfigModel.name == name)
                    .first()
                )

                if not config:
                    logger.error(f"Agent config {name} not found")
                    return None

                old_prompt = config.system_prompt

                # Update fields if provided
                if model is not None:
                    config.model = model
                if system_prompt is not None:
                    config.system_prompt = system_prompt
                if temperature is not None:
                    config.temperature = temperature
                if max_tokens is not None:
                    config.max_tokens = max_tokens
                if enabled is not None:
                    config.enabled = enabled
                if config_metadata is not None:
                    config.config_metadata = config_metadata

                config.updated_at = datetime.now()
                config.updated_by = updated_by

                db.commit()

                # Record prompt change in history if prompt was updated
                if system_prompt is not None and system_prompt != old_prompt:
                    history = AgentPromptHistoryModel(
                        agent_name=name,
                        old_prompt=old_prompt,
                        new_prompt=system_prompt,
                        changed_at=datetime.now(),
                        changed_by=updated_by,
                        change_reason=change_reason,
                    )
                    db.add(history)
                    db.commit()

                # Clear cache for this agent
                if name in self._agent_cache:
                    del self._agent_cache[name]

                return self.get_agent_config(name)
        except Exception as e:
            logger.error(f"Error updating agent config: {e}")
            return None

    def delete_agent_config(self, name: str) -> bool:
        """
        Delete an agent configuration

        Args:
            name: Agent name

        Returns:
            True if deleted, False otherwise
        """
        try:
            with get_db_session() as db:
                result = (
                    db.query(AgentConfigModel)
                    .filter(AgentConfigModel.name == name)
                    .delete()
                )
                db.commit()

                # Clear cache
                if name in self._agent_cache:
                    del self._agent_cache[name]

                return result > 0
        except Exception as e:
            logger.error(f"Error deleting agent config: {e}")
            return False

    def get_prompt_history(
        self, agent_name: str, limit: int = 50
    ) -> List[AgentPromptHistory]:
        """
        Get prompt change history for an agent

        Args:
            agent_name: Agent name
            limit: Maximum number of history entries to return

        Returns:
            List of AgentPromptHistory objects
        """
        try:
            with get_db_session() as db:
                history = (
                    db.query(AgentPromptHistoryModel)
                    .filter(AgentPromptHistoryModel.agent_name == agent_name)
                    .order_by(AgentPromptHistoryModel.changed_at.desc())
                    .limit(limit)
                    .all()
                )

                return [
                    AgentPromptHistory(
                        id=h.id,
                        agent_name=h.agent_name,
                        old_prompt=h.old_prompt,
                        new_prompt=h.new_prompt,
                        changed_at=h.changed_at,
                        changed_by=h.changed_by,
                        change_reason=h.change_reason,
                    )
                    for h in history
                ]
        except Exception as e:
            logger.error(f"Error getting prompt history: {e}")
            return []

    def initialize_default_configs(self):
        """Initialize default agent configurations if they don't exist"""
        try:
            # Check if coordinator exists
            if not self.get_agent_config("coordinator"):
                logger.info("Creating default coordinator agent configuration")
                self.create_agent_config(
                    name="coordinator",
                    model="google::gemini-2.5-flash",
                    system_prompt="You are a helpful coordinator. and we need output as a simple text",
                    temperature=0.7,
                    max_tokens=2048,
                    enabled=True,
                    created_by="system",
                )

            # Check if vector_db_agent exists
            if not self.get_agent_config("vector_db_agent"):
                logger.info("Creating default vector_db_agent configuration")
                self.create_agent_config(
                    name="vector_db_agent",
                    model="google::gemini-2.5-flash",
                    system_prompt="""You are a vector database query assistant. Your role is to help users search and retrieve relevant documents from the knowledge base.

When processing queries:
1. Understand the user's search intent
2. Formulate effective search queries
3. Interpret and present search results clearly
4. Provide context and relevance information
5. Suggest follow-up queries when helpful

You have access to a semantic search system that finds documents based on meaning, not just keywords. Always explain the relevance of returned results and help users refine their searches if needed.

Respond in clear, concise text format.""",
                    temperature=0.7,
                    max_tokens=2048,
                    enabled=True,
                    created_by="system",
                )
        except Exception as e:
            logger.error(f"Error initializing default configs: {e}")


# Global agent manager instance
agent_manager = AgentManager()
