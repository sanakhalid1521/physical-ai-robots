from typing import List, Optional, Dict, Any
from src.services.embedding_service import embedding_service
from src.services.qdrant_service import qdrant_service
from src.services.llm_service import llm_service
from src.services.database_service import database_service
from src.services.cache_service import cache_service
from src.models.chat import ChatRequest, ChatResponse
from src.utils.text_processor import chunk_text
from src.utils.language_detector import get_preferred_language
import logging
from datetime import datetime


logger = logging.getLogger(__name__)


class RAGService:
    """
    Service class that orchestrates RAG (Retrieval-Augmented Generation) functionality
    """
    def __init__(self):
        self.embedding_service = embedding_service
        self.qdrant_service = qdrant_service
        self.llm_service = llm_service
        self.database_service = database_service

    async def process_book_mode_request(self, request: ChatRequest) -> Optional[ChatResponse]:
        """
        Process a request in book mode (retrieve from entire book).

        Args:
            request: ChatRequest with mode 'book'

        Returns:
            ChatResponse with the answer and sources
        """
        try:
            # Generate embedding for the question
            query_embedding = await self.embedding_service.generate_embedding(request.message)
            if not query_embedding:
                logger.error("Failed to generate embedding for query")
                return None

            # Search for similar content in the vector database
            # For book mode, we'll search across all books unless specified otherwise
            similar_chunks = self.qdrant_service.search_similar(
                query_vector=query_embedding,
                book_id=None,  # Search across all books
                limit=5
            )

            if not similar_chunks:
                # No relevant context found
                language = get_preferred_language(request.message, request.language)
                answer = self._get_no_context_response(language)
                sources = []
            else:
                # Build context from similar chunks using the new method
                context = await self.build_context_from_chunks(similar_chunks)

                # Generate response using LLM with context
                language = get_preferred_language(request.message, request.language)
                answer = await self.llm_service.enforce_context_only_response(context, request.message, language)

                # Extract source information
                sources = [chunk["content"][:100] + "..." for chunk in similar_chunks]  # Truncate for response

            # Create ChatResponse
            response = ChatResponse(
                answer=answer,
                sources=sources if sources else None,
                language=language
            )

            # Log the query to database
            await self.database_service.log_query(
                user_id=request.userId,
                message=request.message,
                mode=request.mode,
                selected_text=None,
                response=answer,
                sources=sources,
                language=language
            )

            return response
        except Exception as e:
            logger.error(f"Error processing book mode request: {e}")
            return None

    async def retrieve_relevant_chunks_from_book(self, query: str, book_id: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks from the book based on the query.

        Args:
            query: The query to search for
            book_id: Optional specific book to search in
            limit: Maximum number of chunks to return

        Returns:
            List of relevant chunks with content and metadata
        """
        try:
            # Check cache first for similarity search results
            cached_results = await cache_service.get_cached_similarity_results(
                query_vector=None,  # We'll generate the vector key differently
                book_id=book_id,
                limit=limit
            )

            # Since we can't cache with None vector, let's generate the embedding first
            query_embedding = await self.embedding_service.generate_embedding(query)
            if not query_embedding:
                logger.error("Failed to generate embedding for query")
                return []

            # Generate cache key using the query embedding
            cache_key = await cache_service.get_similarity_cache_key(query_embedding, book_id, limit)
            cached_results = await cache_service.get(cache_key)

            if cached_results is not None:
                logger.debug("Retrieved similarity search results from cache")
                return cached_results

            # Search for similar content in the vector database
            similar_chunks = self.qdrant_service.search_similar(
                query_vector=query_embedding,
                book_id=book_id,
                limit=limit
            )

            # Cache the results
            await cache_service.cache_similarity_results(query_embedding, book_id, limit, similar_chunks)

            logger.info(f"Retrieved {len(similar_chunks)} relevant chunks for query: {query[:50]}...")
            return similar_chunks
        except Exception as e:
            logger.error(f"Error retrieving relevant chunks: {e}")
            return []

    async def build_context_from_chunks(self, chunks: List[Dict[str, Any]], max_context_length: int = 3000) -> str:
        """
        Build a context string from retrieved chunks, respecting the maximum length.

        Args:
            chunks: List of retrieved chunks with content
            max_context_length: Maximum length of the context string

        Returns:
            Context string built from the chunks
        """
        if not chunks:
            return ""

        # Create a cache key based on the chunk IDs and max length
        chunk_ids = [chunk.get("chunkId", str(i)) for i, chunk in enumerate(chunks)]
        cache_key = await cache_service.get_context_cache_key(chunk_ids, max_context_length)

        # Check if context is already cached
        cached_context = await cache_service.get(cache_key)
        if cached_context is not None:
            logger.debug("Retrieved context from cache")
            return cached_context

        # Sort chunks by relevance score (highest first) if available
        sorted_chunks = sorted(chunks, key=lambda x: x.get('score', 0), reverse=True)

        context_parts = []
        current_length = 0

        for chunk in sorted_chunks:
            chunk_content = chunk.get("content", "")
            if not chunk_content.strip():
                continue

            # Check if adding this chunk would exceed the max length
            if current_length + len(chunk_content) > max_context_length:
                # Try to add a truncated version of the chunk
                remaining_length = max_context_length - current_length
                if remaining_length > 0:
                    truncated_chunk = chunk_content[:remaining_length]
                    context_parts.append(truncated_chunk)
                    current_length += len(truncated_chunk)
                break
            else:
                context_parts.append(chunk_content)
                current_length += len(chunk_content)

        # Join the context parts with clear separators
        context = "\n\n".join(context_parts)
        logger.debug(f"Built context with {len(context)} characters from {len(context_parts)} chunks")

        # Cache the built context
        await cache_service.cache_context(chunk_ids, max_context_length, context)

        return context

    async def process_selection_mode_request(self, request: ChatRequest) -> Optional[ChatResponse]:
        """
        Process a request in selection mode (use only provided selected text).

        Args:
            request: ChatRequest with mode 'selection' and selectedText

        Returns:
            ChatResponse with the answer and sources
        """
        try:
            # Validate that selectedText is provided
            if not request.selectedText or not request.selectedText.strip():
                logger.error("Selected text is required for selection mode")
                return None

            # Use the selected text directly as context (skip vector search)
            context = request.selectedText.strip()

            # Generate response using LLM with the selected text as context
            language = get_preferred_language(request.message, request.language)
            answer = await self.llm_service.enforce_context_only_response(context, request.message, language)

            # For selection mode, the source is the selected text itself
            sources = [context[:100] + "..."] if len(context) > 100 else [context]

            # Create ChatResponse
            response = ChatResponse(
                answer=answer,
                sources=sources,
                language=language
            )

            # Log the query to database
            await self.database_service.log_query(
                user_id=request.userId,
                message=request.message,
                mode=request.mode,
                selected_text=request.selectedText,
                response=answer,
                sources=sources,
                language=language
            )

            return response
        except Exception as e:
            logger.error(f"Error processing selection mode request: {e}")
            return None

    async def process_request(self, request: ChatRequest) -> Optional[ChatResponse]:
        """
        Process a chat request based on its mode.

        Args:
            request: ChatRequest to process

        Returns:
            ChatResponse with the answer and sources
        """
        if request.mode == "book":
            return await self.process_book_mode_request(request)
        elif request.mode == "selection":
            return await self.process_selection_mode_request(request)
        else:
            logger.error(f"Invalid mode: {request.mode}")
            return None

    def _get_no_context_response(self, language: str) -> str:
        """
        Get the appropriate response when no context is found.

        Args:
            language: Language for the response

        Returns:
            Appropriate response string
        """
        if language == "ur":
            return "Is sawal ka jawab kitab ke matn mein mojood nahi hai."
        else:
            return "Is sawal ka jawab kitab ke matn mein mojood nahi hai."

    async def index_book_content(self, book_id: str, title: str, content: str) -> bool:
        """
        Index book content by chunking, embedding, and storing in vector database.

        Args:
            book_id: Unique identifier for the book
            title: Title of the book
            content: Full content of the book

        Returns:
            True if indexing was successful, False otherwise
        """
        try:
            # Chunk the content
            chunks = chunk_text(content, max_tokens=500, overlap_tokens=100)

            embeddings_to_store = []

            for i, (chunk_text, start_pos, end_pos) in enumerate(chunks):
                # Create a unique chunk ID
                chunk_id = f"{book_id}_chunk_{i:04d}"

                # Generate embedding for the chunk
                embedding = await self.embedding_service.create_embedding_from_request(
                    type('EmbeddingRequest', (), {
                        'text': chunk_text,
                        'bookId': book_id,
                        'chunkId': chunk_id
                    })()
                )

                if embedding:
                    embeddings_to_store.append(embedding)
                else:
                    logger.warning(f"Failed to generate embedding for chunk {chunk_id}")

            # Store all embeddings in the vector database
            if embeddings_to_store:
                success = self.qdrant_service.store_embeddings_batch(embeddings_to_store)
                if success:
                    logger.info(f"Successfully indexed {len(embeddings_to_store)} chunks for book {book_id}")

                    # Save book metadata to database
                    await self.database_service.save_book_metadata(
                        book_id=book_id,
                        title=title,
                        chunk_count=len(embeddings_to_store)
                    )

                    return True
                else:
                    logger.error(f"Failed to store embeddings in vector database for book {book_id}")
                    return False
            else:
                logger.warning(f"No embeddings generated for book {book_id}")
                return False
        except Exception as e:
            logger.error(f"Error indexing book content for {book_id}: {e}")
            return False

    async def get_relevant_chunks(self, query: str, book_id: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get relevant chunks for a query from the vector database.

        Args:
            query: Query to search for
            book_id: Optional book ID to limit search to specific book
            limit: Maximum number of chunks to return

        Returns:
            List of relevant chunks with content and metadata
        """
        try:
            # Generate embedding for the query
            query_embedding = await self.embedding_service.generate_embedding(query)
            if not query_embedding:
                logger.error("Failed to generate embedding for query")
                return []

            # Search for similar content in the vector database
            similar_chunks = self.qdrant_service.search_similar(
                query_vector=query_embedding,
                book_id=book_id,
                limit=limit
            )

            return similar_chunks
        except Exception as e:
            logger.error(f"Error getting relevant chunks: {e}")
            return []

    async def validate_response_context(self, question: str, response: str, context: str) -> bool:
        """
        Validate that the response is properly grounded in the provided context.

        Args:
            question: Original question
            response: Generated response
            context: Context used to generate the response

        Returns:
            True if response is properly grounded, False otherwise
        """
        try:
            # Use the LLM service to validate context relevance
            is_relevant = await self.llm_service.validate_context_relevance(context, question, response)

            # Also check for hallucinations
            has_hallucination = await self.llm_service.detect_hallucination(context, response)

            is_valid = is_relevant and not has_hallucination
            logger.debug(f"Response validation - Relevant: {is_relevant}, No hallucination: {not has_hallucination}, Valid: {is_valid}")

            return is_valid
        except Exception as e:
            logger.error(f"Error validating response context: {e}")
            return False


# Global instance for use throughout the application
rag_service = RAGService()