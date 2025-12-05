"""Vector database query agent"""

import os
import logging
from ceylonai_next import LlmAgent

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
        """You are a vector database query assistant. Your role is to help users search and retrieve relevant documents from the knowledge base.

When processing queries:
1. Understand the user's search intent
2. Formulate effective search queries
3. Interpret and present search results clearly
4. Provide context and relevance information
5. Suggest follow-up queries when helpful

You have access to a semantic search system that finds documents based on meaning, not just keywords. Always explain the relevance of returned results and help users refine their searches if needed.

Respond in clear, concise text format."""
    )
    vector_db_agent.build()
