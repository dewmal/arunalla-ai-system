"""Vector search tool for semantic search in knowledge base"""

import logging
from typing import Optional

from ..services.vector_db_service import vector_db_service

logger = logging.getLogger(__name__)


def vector_search_tool(
    query: str, limit: int = 5, score_threshold: Optional[float] = None
) -> str:
    """
    Search the knowledge base for relevant documents using semantic search.

    This tool performs semantic search to find documents that are most relevant
    to the given query. Results are ranked by similarity score.

    Args:
        query: The search query text to find relevant documents
        limit: Maximum number of results to return (default: 5)
        score_threshold: Minimum similarity score (0-1). Only return results
                        with scores above this threshold (optional)

    Returns:
        A formatted string containing the search results with:
        - Document text
        - Similarity score
        - Metadata (if available)

    Example:
        results = vector_search_tool("What is machine learning?", limit=3)
    """
    try:
        # Perform the search
        results = vector_db_service.search(
            query=query, limit=limit, score_threshold=score_threshold
        )

        if not results:
            return "No relevant documents found in the knowledge base."

        # Format the results
        formatted_results = []
        formatted_results.append(f"Found {len(results)} relevant document(s):\n")

        for idx, result in enumerate(results, 1):
            formatted_results.append(
                f"\n--- Result {idx} (Score: {result['score']:.4f}) ---"
            )
            formatted_results.append(f"Text: {result['text']}")

            # Include metadata if available
            if result.get("metadata"):
                metadata_str = ", ".join(
                    [f"{k}: {v}" for k, v in result["metadata"].items()]
                )
                formatted_results.append(f"Metadata: {metadata_str}")

        return "\n".join(formatted_results)

    except Exception as e:
        logger.error(f"Error in vector search tool: {e}")
        return f"Error performing search: {str(e)}"
