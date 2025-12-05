"""Agent factory for creating and managing agent instances dynamically"""

import os
from typing import Optional, Dict, Any
import logging

from ceylonai_next import LlmAgent

from edu_support_ai_system.services.agent_manager import agent_manager

logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory for creating and managing agent instances"""

    def __init__(self):
        """Initialize agent factory"""
        self._agent_cache: Dict[str, LlmAgent] = {}

    def get_agent(self, agent_name: str) -> Optional[LlmAgent]:
        """
        Get or create an agent instance

        Args:
            agent_name: Name of the agent

        Returns:
            LlmAgent instance or None if config not found
        """
        # Check cache first
        if agent_name in self._agent_cache:
            return self._agent_cache[agent_name]

        # Load configuration from database
        config = agent_manager.get_agent_config(agent_name)

        if not config:
            logger.warning(f"Agent configuration not found for: {agent_name}")
            return None

        if not config.enabled:
            logger.warning(f"Agent is disabled: {agent_name}")
            return None

        # Create agent instance
        try:
            agent = self._create_agent(config)
            self._agent_cache[agent_name] = agent
            return agent
        except Exception as e:
            logger.error(f"Failed to create agent {agent_name}: {e}")
            return None

    def _create_agent(self, config) -> LlmAgent:
        """
        Create an agent instance from configuration

        Args:
            config: AgentConfig object

        Returns:
            LlmAgent instance
        """
        # Ensure GOOGLE_API_KEY is set
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError(
                "GOOGLE_API_KEY environment variable is not set. "
                "Please set it in your .env file or environment. "
                "Get your API key from: https://makersuite.google.com/app/apikey"
            )

        # Create agent
        agent = LlmAgent(config.name, config.model)
        agent.with_system_prompt(config.system_prompt)

        # Apply additional configuration if available
        if config.config_metadata:
            # You can extend this to apply more configuration options
            pass

        agent.build()

        logger.info(f"Created agent: {config.name} with model: {config.model}")
        return agent

    def reload_agent(self, agent_name: str) -> Optional[LlmAgent]:
        """
        Reload an agent with fresh configuration

        Args:
            agent_name: Name of the agent

        Returns:
            Reloaded LlmAgent instance or None
        """
        # Clear from cache
        if agent_name in self._agent_cache:
            del self._agent_cache[agent_name]

        # Get fresh instance
        return self.get_agent(agent_name)

    def clear_cache(self):
        """Clear all cached agents"""
        self._agent_cache.clear()


# Global agent factory instance
agent_factory = AgentFactory()
