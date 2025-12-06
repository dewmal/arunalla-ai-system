"""Vector database query agent"""

import os
import logging
from ceylonai_next import LlmAgent

from ..tools.vector_search_tool import vector_search_tool
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

# Try to load vector_db_agent from database configuration
# Falls back to static configuration if database is not available
vector_db_agent = None

try:
    from .agent_factory import agent_factory

    vector_db_agent = agent_factory.get_agent("vector_db_agent")
except Exception as e:
    logger.warning(f"Could not load vector_db_agent from database: {e}")

# Fallback to static configuration if dynamic loading failed
if vector_db_agent is None:
    logger.info("Using static vector_db_agent configuration")
    vector_db_agent = LlmAgent("VectorDBAgent", "google::gemini-2.5-flash")
    vector_db_agent.with_system_prompt(
        """You are a vector database query assistant connected to a mesh network. Your role is to help users search and retrieve relevant documents from the knowledge base using semantic search.

When processing queries:
1. Understand the user's search intent and extract the key concepts
2. Use the vector_search tool to find relevant documents
3. Interpret the search results and explain their relevance
4. Present the information clearly and concisely
5. Suggest follow-up queries when helpful

You have access to a powerful semantic search system that finds documents based on meaning, not just keywords. The vector_search tool accepts:
- query: The search query text
- limit: Maximum number of results (default 5)
- score_threshold: Minimum similarity score (optional, 0-1 range)

Always explain the relevance of returned results and help users refine their searches if needed. If no results are found, suggest alternative search terms or approaches.

Note: You are part of a mesh network where agents can discover and communicate with each other.
You can be contacted by other agents through the mesh for knowledge base searches.

Respond in clear, concise text format."""
    )

    # Register the vector search tool using the recommended pattern
    @vector_db_agent.action(
        description="Search the knowledge base for relevant documents using semantic search"
    )
    def vector_search(query: str, limit: int = 5, score_threshold: float = None) -> str:
        """
        Search the knowledge base for relevant documents.

        Args:
            query: The search query text to find relevant documents
            limit: Maximum number of results to return (default: 5)
            score_threshold: Minimum similarity score (0-1), only return results above this threshold

        Returns:
            Formatted string with search results including document text, scores, and metadata
        """
        return vector_search_tool(query, limit, score_threshold)

    vector_db_agent.build()

# Register vector_db_agent with the mesh
register_agent(vector_db_agent)
logger.info(f"VectorDBAgent registered with mesh. Available agents: {list_agents()}")
