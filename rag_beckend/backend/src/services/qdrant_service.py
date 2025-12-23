from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct, Distance, VectorParams
from typing import List, Dict, Any, Optional
from src.models.embedding import Embedding
from src.utils.config import get_settings
import logging
import uuid


logger = logging.getLogger(__name__)


class QdrantService:
    """
    Service class for managing vector operations with Qdrant
    """
    def __init__(self):
        settings = get_settings()
        if settings.qdrant_url and settings.qdrant_api_key:
            self.client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
                timeout=10
            )
        else:
            # For local development
            self.client = QdrantClient(host="localhost", port=6333)

        self.default_collection_name = "book_embeddings"
        self.vector_size = 1536  # Default for OpenAI ada-002 embeddings

    def create_collection(self, collection_name: str = None, vector_size: int = None) -> bool:
        """
        Create a collection in Qdrant for storing embeddings.

        Args:
            collection_name: Name of the collection to create
            vector_size: Size of the embedding vectors

        Returns:
            True if collection was created successfully, False otherwise
        """
        if collection_name is None:
            collection_name = self.default_collection_name

        if vector_size is None:
            vector_size = self.vector_size

        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            existing_collection_names = [c.name for c in collections.collections]

            if collection_name not in existing_collection_names:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
                )
                logger.info(f"Created Qdrant collection: {collection_name}")
                return True
            else:
                logger.info(f"Collection {collection_name} already exists")
                return True
        except Exception as e:
            logger.error(f"Error creating collection {collection_name}: {e}")
            return False

    def store_embedding(self, embedding: Embedding, collection_name: str = None) -> bool:
        """
        Store a single embedding in Qdrant.

        Args:
            embedding: Embedding object to store
            collection_name: Name of the collection to store in

        Returns:
            True if stored successfully, False otherwise
        """
        if collection_name is None:
            collection_name = self.default_collection_name

        try:
            points = [
                PointStruct(
                    id=embedding.chunkId,
                    vector=embedding.vector,
                    payload={
                        "content": embedding.content,
                        "bookId": embedding.bookId,
                        "chunkId": embedding.chunkId,
                        "created_at": embedding.createdAt.isoformat()
                    }
                )
            ]

            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            logger.debug(f"Stored embedding for chunk {embedding.chunkId}")
            return True
        except Exception as e:
            logger.error(f"Error storing embedding for chunk {embedding.chunkId}: {e}")
            return False

    def store_embeddings_batch(self, embeddings: List[Embedding], collection_name: str = None) -> bool:
        """
        Store multiple embeddings in Qdrant in a batch operation.

        Args:
            embeddings: List of Embedding objects to store
            collection_name: Name of the collection to store in

        Returns:
            True if all embeddings were stored successfully, False otherwise
        """
        if collection_name is None:
            collection_name = self.default_collection_name

        try:
            points = []
            for embedding in embeddings:
                point = PointStruct(
                    id=embedding.chunkId,
                    vector=embedding.vector,
                    payload={
                        "content": embedding.content,
                        "bookId": embedding.bookId,
                        "chunkId": embedding.chunkId,
                        "created_at": embedding.createdAt.isoformat()
                    }
                )
                points.append(point)

            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            logger.info(f"Stored {len(embeddings)} embeddings in batch")
            return True
        except Exception as e:
            logger.error(f"Error storing embeddings batch: {e}")
            return False

    def search_similar(self, query_vector: List[float], book_id: str = None,
                      collection_name: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings to the query vector.

        Args:
            query_vector: Vector to search for similar items
            book_id: Optional filter to only search within a specific book
            collection_name: Name of the collection to search in
            limit: Maximum number of results to return

        Returns:
            List of similar items with content and metadata
        """
        if collection_name is None:
            collection_name = self.default_collection_name

        try:
            # Build filters
            filters = models.Filter()
            if book_id:
                filters.must.append(
                    models.FieldCondition(
                        key="bookId",
                        match=models.MatchValue(value=book_id)
                    )
                )

            search_results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                query_filter=filters,
                limit=limit,
                with_payload=True,
                score_threshold=0.3  # Minimum similarity score
            )

            results = []
            for hit in search_results:
                results.append({
                    "chunkId": hit.id,
                    "content": hit.payload.get("content", ""),
                    "bookId": hit.payload.get("bookId", ""),
                    "score": hit.score,
                    "metadata": {k: v for k, v in hit.payload.items() if k not in ["content", "bookId", "chunkId"]}
                })

            logger.debug(f"Found {len(results)} similar items for query")
            return results
        except Exception as e:
            logger.error(f"Error searching for similar embeddings: {e}")
            return []

    def get_embedding_by_id(self, chunk_id: str, collection_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific embedding by its ID.

        Args:
            chunk_id: ID of the chunk to retrieve
            collection_name: Name of the collection to search in

        Returns:
            Dictionary containing the embedding data or None if not found
        """
        if collection_name is None:
            collection_name = self.default_collection_name

        try:
            records = self.client.retrieve(
                collection_name=collection_name,
                ids=[chunk_id],
                with_payload=True,
                with_vectors=True
            )

            if records:
                record = records[0]
                return {
                    "chunkId": record.id,
                    "vector": record.vector,
                    "content": record.payload.get("content", ""),
                    "bookId": record.payload.get("bookId", ""),
                    "metadata": {k: v for k, v in record.payload.items()
                               if k not in ["content", "bookId", "chunkId"]}
                }
            return None
        except Exception as e:
            logger.error(f"Error retrieving embedding {chunk_id}: {e}")
            return None

    def delete_embedding(self, chunk_id: str, collection_name: str = None) -> bool:
        """
        Delete a specific embedding by its ID.

        Args:
            chunk_id: ID of the chunk to delete
            collection_name: Name of the collection to delete from

        Returns:
            True if deleted successfully, False otherwise
        """
        if collection_name is None:
            collection_name = self.default_collection_name

        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(points=[chunk_id])
            )
            logger.info(f"Deleted embedding with ID: {chunk_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting embedding {chunk_id}: {e}")
            return False

    def delete_collection(self, collection_name: str = None) -> bool:
        """
        Delete an entire collection.

        Args:
            collection_name: Name of the collection to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        if collection_name is None:
            collection_name = self.default_collection_name

        try:
            self.client.delete_collection(collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection {collection_name}: {e}")
            return False

    def count_embeddings(self, book_id: str = None, collection_name: str = None) -> int:
        """
        Count the number of embeddings in the collection.

        Args:
            book_id: Optional filter to count only embeddings from a specific book
            collection_name: Name of the collection to count in

        Returns:
            Number of embeddings in the collection
        """
        if collection_name is None:
            collection_name = self.default_collection_name

        try:
            filters = models.Filter()
            if book_id:
                filters.must.append(
                    models.FieldCondition(
                        key="bookId",
                        match=models.MatchValue(value=book_id)
                    )
                )

            count = self.client.count(
                collection_name=collection_name,
                count_filter=filters
            )
            return count.count
        except Exception as e:
            logger.error(f"Error counting embeddings: {e}")
            return 0

    def delete_book_embeddings(self, book_id: str, collection_name: str = None) -> bool:
        """
        Delete all embeddings associated with a specific book.

        Args:
            book_id: ID of the book whose embeddings should be deleted
            collection_name: Name of the collection to delete from

        Returns:
            True if deletion was successful, False otherwise
        """
        if collection_name is None:
            collection_name = self.default_collection_name

        try:
            # Create a filter to match all points with the given bookId
            book_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="bookId",
                        match=models.MatchValue(value=book_id)
                    )
                ]
            )

            # Delete all points matching the filter
            self.client.delete(
                collection_name=collection_name,
                points_selector=book_filter
            )

            logger.info(f"Deleted all embeddings for book {book_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting embeddings for book {book_id}: {e}")
            return False

    def get_book_vector_count(self, book_id: str, collection_name: str = None) -> int:
        """
        Get the count of vectors for a specific book.

        Args:
            book_id: ID of the book
            collection_name: Name of the collection to count in

        Returns:
            Number of vectors for the book
        """
        if collection_name is None:
            collection_name = self.default_collection_name

        try:
            # Create a filter to match points with the given bookId
            book_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="bookId",
                        match=models.MatchValue(value=book_id)
                    )
                ]
            )

            count = self.client.count(
                collection_name=collection_name,
                count_filter=book_filter
            )

            return count.count
        except Exception as e:
            logger.error(f"Error counting vectors for book {book_id}: {e}")
            return 0


# Global instance for use throughout the application
qdrant_service = QdrantService()