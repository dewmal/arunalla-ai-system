import os
import logging
from ceylonai_next import LlmAgent

from ..mesh import register_agent, list_agents

logger = logging.getLogger(__name__)

# Ensure GOOGLE_API_KEY is set from environment
# This is required for google::gemini-* models
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError(
        "GOOGLE_API_KEY environment variable is not set. "
        "Please set it in your .env file or environment. "
        "Get your API key from: https://makersuite.google.com/app/apikey"
    )

# Try to load coordinator from database configuration
# Falls back to static configuration if database is not available
coordinator = None

try:
    from .agent_factory import agent_factory

    coordinator = agent_factory.get_agent("coordinator")
except Exception as e:
    logger.warning(f"Could not load coordinator from database: {e}")

# Fallback to static configuration if dynamic loading failed
if coordinator is None:
    logger.info("Using static coordinator configuration")
    coordinator = LlmAgent("Coordinator", "google::gemini-2.5-flash")

coordinator.with_system_prompt(
    """You are a helpful coordinator agent that helps users by orchestrating different specialized agents through a mesh network.

Your primary responsibility is to:
1. Understand user queries and determine what information or help they need
2. Delegate to specialized agents when appropriate using the mesh network
3. Synthesize information from multiple sources into coherent, helpful responses
4. Provide clear, concise answers in simple text format

You have access to the following specialized agents through the mesh:
- VectorDBAgent: Use this agent when you need to search for information in the knowledge base. This agent can perform semantic searches to find relevant documents and information.

When to use VectorDBAgent:
- User asks questions that require knowledge from stored documents
- User wants to find information on a specific topic
- User needs factual information that might be in the knowledge base

How to use agents:
- You can communicate with other agents through the mesh network
- To use VectorDBAgent, you would request a search for relevant information
- The VectorDBAgent will search the knowledge base and return relevant information
- Always synthesize the results from agents into a clear, helpful response for the user

Note: You are part of a mesh network where agents can discover and communicate with each other.
Available agents can be found through agent discovery in the mesh.

Remember: Always provide output as simple, clear text. Be helpful and concise."""
)

coordinator.build()

# Register coordinator with the mesh
register_agent(coordinator)
logger.info(f"Coordinator registered with mesh. Available agents: {list_agents()}")
