"""Mesh networking infrastructure for agent communication

This module provides a centralized mesh for agent discovery and communication.
It uses Ceylon AI's LocalMesh for in-memory, low-latency agent messaging.
"""

import logging
from typing import List, Optional
from ceylonai_next import LocalMesh, Agent

logger = logging.getLogger(__name__)

# Singleton mesh instance
_mesh_instance: Optional[LocalMesh] = None


def get_mesh() -> LocalMesh:
    """
    Get the singleton mesh instance.

    Creates the mesh on first call, subsequent calls return the same instance.

    Returns:
        LocalMesh instance for agent communication
    """
    global _mesh_instance

    if _mesh_instance is None:
        logger.info("Initializing LocalMesh for agent communication")
        _mesh_instance = LocalMesh("agent_mesh")  # LocalMesh requires a name parameter
        logger.info("LocalMesh initialized successfully")

    return _mesh_instance


def register_agent(agent: Agent) -> bool:
    """
    Register an agent with the mesh.

    Args:
        agent: Agent instance to register

    Returns:
        True if registration successful, False otherwise
    """
    try:
        mesh = get_mesh()
        mesh.add_agent(agent)  # Ceylon AI uses add_agent, not register_agent
        # Get agent name - handle both property and method
        try:
            agent_name = agent.name() if callable(agent.name) else agent.name
        except Exception:
            agent_name = str(agent)
        logger.info(f"Registered agent '{agent_name}' with mesh")
        return True
    except Exception as e:
        try:
            agent_name = agent.name() if callable(agent.name) else agent.name
        except Exception:
            agent_name = str(agent)
        logger.error(f"Failed to register agent '{agent_name}' with mesh: {e}")

        return False


def list_agents() -> List[str]:
    """
    List all agents registered with the mesh.

    Returns:
        List of agent names
    """
    try:
        mesh = get_mesh()
        # Ceylon AI uses get_registered_agents() method
        agents = (
            mesh.get_registered_agents()
            if hasattr(mesh, "get_registered_agents")
            else []
        )
        return agents
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        return []


def is_agent_registered(agent_name: str) -> bool:
    """
    Check if an agent is registered with the mesh.

    Args:
        agent_name: Name of the agent to check

    Returns:
        True if agent is registered, False otherwise
    """
    agents = list_agents()
    return agent_name in agents


def send_message(from_agent: str, to_agent: str, message: str) -> str:
    """
    Send a message from one agent to another through the mesh.

    Args:
        from_agent: Name of the sending agent
        to_agent: Name of the receiving agent
        message: Message content

    Returns:
        Response from the receiving agent

    Raises:
        ValueError: If either agent is not registered
        RuntimeError: If message delivery fails
    """
    try:
        mesh = get_mesh()

        # Validate agents are registered
        if not is_agent_registered(to_agent):
            raise ValueError(f"Agent '{to_agent}' is not registered with the mesh")

        logger.debug(f"Routing message from '{from_agent}' to '{to_agent}'")
        # Ceylon AI uses send_to(to_agent, message, from_agent)
        response = mesh.send_to(to_agent, message, from_agent)
        logger.debug(f"Received response from '{to_agent}'")

        return response
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Failed to send message from '{from_agent}' to '{to_agent}': {e}")
        raise RuntimeError(f"Message delivery failed: {e}")


def health_check() -> bool:
    """
    Check if the mesh is healthy and operational.

    Returns:
        True if mesh is operational, False otherwise
    """
    try:
        mesh = get_mesh()
        # Mesh is healthy if it's initialized
        return mesh is not None
    except Exception as e:
        logger.error(f"Mesh health check failed: {e}")
        return False


def get_agents() -> List[str]:
    """
    Get all agents registered with the mesh.

    Returns:
        List of agent names
    """
    try:
        mesh = get_mesh()
        # Ceylon AI uses get_registered_agents() method
        agents = (
            mesh.get_registered_agents()
            if hasattr(mesh, "get_registered_agents")
            else []
        )
        return agents
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        return []
