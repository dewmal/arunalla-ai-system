"""Vector database service for Qdrant integration"""

import os
import logging
from typing import List, Dict, Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.http.exceptions import UnexpectedResponse
import google.generativeai as genai

logger = logging.getLogger(__name__)


class VectorDBService:
    """Service for managing Qdrant vector database operations"""

    def __init__(self):
        """Initialize the vector database service"""
        self.host = os.getenv("QDRANT_HOST", "localhost")
        self.port = int(os.getenv("QDRANT_PORT", "6333"))
        self.collection_name = os.getenv("QDRANT_COLLECTION_NAME", "documents")
        self.vector_dimension = int(os.getenv("VECTOR_DIMENSION", "768"))

        # Initialize Google AI for embeddings
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY is required for embeddings")

        genai.configure(api_key=google_api_key)
        self._client: Optional[QdrantClient] = None

    @property
    def client(self) -> QdrantClient:
        """Get or create Qdrant client"""
        if self._client is None:
            self._client = QdrantClient(host=self.host, port=self.port)
            logger.info(f"Connected to Qdrant at {self.host}:{self.port}")
        return self._client

    def get_embedding(
        self, text: str, model: str = "models/embedding-001"
    ) -> List[float]:
        """
        Generate embedding vector for text using Google AI

        Args:
            text: Text to embed
            model: Embedding model to use

        Returns:
            List of floats representing the embedding vector
        """
        try:
            result = genai.embed_content(
                model=model, content=text, task_type="retrieval_document"
            )
            return result["embedding"]
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def create_collection(
        self,
        collection_name: Optional[str] = None,
        vector_size: Optional[int] = None,
        distance: Distance = Distance.COSINE,
    ) -> bool:
        """
        Create a new collection in Qdrant

        Args:
            collection_name: Name of the collection (defaults to configured name)
            vector_size: Size of vectors (defaults to configured dimension)
            distance: Distance metric to use

        Returns:
            True if created successfully, False otherwise
        """
        collection_name = collection_name or self.collection_name
        vector_size = vector_size or self.vector_dimension

        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            if any(c.name == collection_name for c in collections):
                logger.info(f"Collection {collection_name} already exists")
                return True

            # Create collection
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=distance),
            )
            logger.info(f"Created collection {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            return False

    def add_documents(
        self,
        documents: List[str],
        collection_name: Optional[str] = None,
        metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Add documents to the vector database

        Args:
            documents: List of document texts
            collection_name: Collection to add to (defaults to configured name)
            metadata: Optional metadata for each document

        Returns:
            True if added successfully, False otherwise
        """
        collection_name = collection_name or self.collection_name

        try:
            # Ensure collection exists
            self.create_collection(collection_name)

            # Generate embeddings
            points = []
            for idx, doc in enumerate(documents):
                embedding = self.get_embedding(doc)

                payload = {"text": doc}
                if metadata and idx < len(metadata):
                    payload.update(metadata[idx])

                points.append(PointStruct(id=idx, vector=embedding, payload=payload))

            # Upload to Qdrant
            self.client.upsert(collection_name=collection_name, points=points)
            logger.info(f"Added {len(documents)} documents to {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False

    def search(
        self,
        query: str,
        collection_name: Optional[str] = None,
        limit: int = 5,
        score_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using semantic search

        Args:
            query: Search query text
            collection_name: Collection to search (defaults to configured name)
            limit: Maximum number of results
            score_threshold: Minimum similarity score (0-1)

        Returns:
            List of search results with text, metadata, and scores
        """
        collection_name = collection_name or self.collection_name

        try:
            # Generate query embedding
            query_embedding = self.get_embedding(query)

            # Search in Qdrant
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
            )

            # Format results
            results = []
            for hit in search_result:
                results.append(
                    {
                        "text": hit.payload.get("text", ""),
                        "score": hit.score,
                        "metadata": {
                            k: v for k, v in hit.payload.items() if k != "text"
                        },
                    }
                )

            logger.info(f"Found {len(results)} results for query in {collection_name}")
            return results
        except UnexpectedResponse as e:
            if "Not found: Collection" in str(e):
                logger.warning(f"Collection {collection_name} does not exist")
                return []
            logger.error(f"Error searching: {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []

    def delete_collection(self, collection_name: Optional[str] = None) -> bool:
        """
        Delete a collection

        Args:
            collection_name: Collection to delete (defaults to configured name)

        Returns:
            True if deleted successfully, False otherwise
        """
        collection_name = collection_name or self.collection_name

        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Deleted collection {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            return False

    def get_collection_info(
        self, collection_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get information about a collection

        Args:
            collection_name: Collection name (defaults to configured name)

        Returns:
            Dictionary with collection information or None
        """
        collection_name = collection_name or self.collection_name

        try:
            info = self.client.get_collection(collection_name=collection_name)
            return {
                "name": collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status,
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return None

    def health_check(self) -> bool:
        """
        Check if Qdrant is healthy and accessible

        Returns:
            True if healthy, False otherwise
        """
        try:
            collections = self.client.get_collections()
            logger.info(
                f"Qdrant health check passed. Found {len(collections.collections)} collections"
            )
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False


# Global vector DB service instance
vector_db_service = VectorDBService()
