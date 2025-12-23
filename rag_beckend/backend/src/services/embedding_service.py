from typing import List, Optional
from openai import AsyncOpenAI
from src.models.embedding import Embedding, EmbeddingRequest, EmbeddingResponse
from src.utils.config import get_settings
from src.services.cache_service import cache_service
import logging
import asyncio
from datetime import datetime


logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service class for generating and managing embeddings using OpenAI
    """
    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "text-embedding-ada-002"  # Default OpenAI embedding model
        self.dimension = 1536  # Dimension for ada-002

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to generate embedding for

        Returns:
            List of embedding values or None if failed
        """
        try:
            # Check cache first
            cached_embedding = await cache_service.get_cached_embedding(text, self.model)
            if cached_embedding:
                logger.debug("Retrieved embedding from cache")
                return cached_embedding

            # Truncate text if it's too long (OpenAI has a limit)
            if len(text) > 8192:  # Conservative limit
                text = text[:8192]
                logger.warning("Text truncated for embedding generation due to length")

            response = await self.client.embeddings.create(
                input=text,
                model=self.model
            )

            embedding_values = response.data[0].embedding
            logger.debug(f"Generated embedding with {len(embedding_values)} dimensions")

            # Cache the result
            await cache_service.cache_embedding(text, embedding_values, self.model)

            return embedding_values
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    async def generate_embeddings_batch(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        Generate embeddings for multiple texts in a batch.

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            List of embedding lists or None if failed
        """
        try:
            # Check cache for each text and identify which ones need to be generated
            results = []
            texts_to_generate = []
            text_indices_map = {}  # Maps index in texts_to_generate to index in original list

            for i, text in enumerate(texts):
                if text and len(text.strip()) > 0:
                    if len(text) > 8192:
                        text = text[:8192]
                        logger.warning("Text truncated for embedding generation due to length")

                    # Check if embedding is already cached
                    cached_embedding = await cache_service.get_cached_embedding(text, self.model)
                    if cached_embedding:
                        # Pad results list to match the original position
                        while len(results) <= i:
                            results.append(None)
                        results[i] = cached_embedding
                        logger.debug(f"Retrieved embedding from cache for text {i}")
                    else:
                        texts_to_generate.append(text)
                        text_indices_map[len(texts_to_generate) - 1] = i

            # Generate embeddings for texts not in cache
            if texts_to_generate:
                response = await self.client.embeddings.create(
                    input=texts_to_generate,
                    model=self.model
                )

                new_embeddings = [data.embedding for data in response.data]

                # Add to results and cache
                for j, embedding in enumerate(new_embeddings):
                    original_index = text_indices_map[j]
                    while len(results) <= original_index:
                        results.append(None)
                    results[original_index] = embedding

                    # Cache the new embedding
                    await cache_service.cache_embedding(texts[original_index], embedding, self.model)

            logger.info(f"Processed {len(texts)} texts, {len(texts_to_generate)} generated fresh")
            return results
        except Exception as e:
            logger.error(f"Error generating embeddings batch: {e}")
            return None

    async def create_embedding_from_request(self, request: EmbeddingRequest) -> Optional[Embedding]:
        """
        Create an Embedding object from an EmbeddingRequest.

        Args:
            request: EmbeddingRequest containing text and metadata

        Returns:
            Embedding object or None if failed
        """
        embedding_values = await self.generate_embedding(request.text)
        if embedding_values is None:
            return None

        return Embedding(
            chunkId=request.chunkId,
            vector=embedding_values,
            content=request.text,
            bookId=request.bookId,
            createdAt=datetime.utcnow()
        )

    async def create_embeddings_from_requests(self, requests: List[EmbeddingRequest]) -> List[Embedding]:
        """
        Create multiple Embedding objects from a list of EmbeddingRequests.

        Args:
            requests: List of EmbeddingRequests

        Returns:
            List of Embedding objects that were successfully created
        """
        # Extract texts for batch processing
        texts = [req.text for req in requests]
        embeddings_data = await self.generate_embeddings_batch(texts)

        if embeddings_data is None:
            return []

        # Create Embedding objects
        embeddings = []
        for i, request in enumerate(requests):
            if i < len(embeddings_data):
                embedding = Embedding(
                    chunkId=request.chunkId,
                    vector=embeddings_data[i],
                    content=request.text,
                    bookId=request.bookId,
                    createdAt=datetime.utcnow()
                )
                embeddings.append(embedding)

        return embeddings

    def validate_embedding(self, embedding: Embedding) -> bool:
        """
        Validate that an embedding has the correct format and dimensions.

        Args:
            embedding: Embedding object to validate

        Returns:
            True if valid, False otherwise
        """
        if not embedding.chunkId or not embedding.vector or not embedding.content:
            return False

        if len(embedding.vector) != self.dimension:
            logger.warning(f"Embedding vector has {len(embedding.vector)} dimensions, expected {self.dimension}")
            return False

        return True

    def calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two embedding vectors.

        Args:
            vec1: First embedding vector
            vec2: Second embedding vector

        Returns:
            Cosine similarity value between -1 and 1
        """
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same length")

        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))

        # Calculate magnitudes
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        # Calculate cosine similarity
        similarity = dot_product / (magnitude1 * magnitude2)
        return similarity


# Global instance for use throughout the application
embedding_service = EmbeddingService()