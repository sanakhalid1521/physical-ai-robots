import asyncio
import json
import time
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
from src.utils.config import get_settings
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """
    Service class for managing caching of embeddings and other data to improve performance
    """
    def __init__(self):
        self.settings = get_settings()
        self.cache = {}
        self.cache_expiry = {}  # Track when each cache item expires
        self.default_ttl = 3600  # Default TTL in seconds (1 hour)

    def _generate_cache_key(self, prefix: str, *args) -> str:
        """Generate a cache key from prefix and arguments"""
        key_parts = [prefix] + [str(arg) for arg in args]
        return ":".join(key_parts)

    def _is_expired(self, key: str) -> bool:
        """Check if a cache key has expired"""
        if key not in self.cache_expiry:
            return True
        return time.time() > self.cache_expiry[key]

    def _cleanup_expired(self):
        """Remove expired cache entries"""
        expired_keys = [key for key, expiry in self.cache_expiry.items()
                       if time.time() > expiry]
        for key in expired_keys:
            self.cache.pop(key, None)
            self.cache_expiry.pop(key, None)

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        try:
            self._cleanup_expired()

            if key not in self.cache:
                return None

            if self._is_expired(key):
                del self.cache[key]
                del self.cache_expiry[key]
                return None

            value = self.cache[key]
            logger.debug(f"Cache HIT for key: {key}")
            return value
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache with optional TTL"""
        try:
            if ttl is None:
                ttl = self.default_ttl

            self.cache[key] = value
            self.cache_expiry[key] = time.time() + ttl
            logger.debug(f"Cache SET for key: {key} with TTL: {ttl}")
            return True
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete a value from cache"""
        try:
            self.cache.pop(key, None)
            self.cache_expiry.pop(key, None)
            logger.debug(f"Cache DELETE for key: {key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False

    async def clear(self) -> bool:
        """Clear all cache entries"""
        try:
            self.cache.clear()
            self.cache_expiry.clear()
            logger.debug("Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

    # Embedding-specific cache methods
    async def get_embedding_cache_key(self, text: str, model: str = "openai-ada-002") -> str:
        """Generate cache key for embedding"""
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return self._generate_cache_key("embedding", model, text_hash)

    async def get_cached_embedding(self, text: str, model: str = "openai-ada-002") -> Optional[List[float]]:
        """Get cached embedding for text"""
        key = await self.get_embedding_cache_key(text, model)
        return await self.get(key)

    async def cache_embedding(self, text: str, embedding: List[float], model: str = "openai-ada-002", ttl: int = 86400) -> bool:
        """Cache embedding for text"""
        key = await self.get_embedding_cache_key(text, model)
        return await self.set(key, embedding, ttl)

    # Similarity search result caching
    async def get_similarity_cache_key(self, query_vector: List[float], book_id: Optional[str], limit: int) -> str:
        """Generate cache key for similarity search results"""
        import hashlib
        vector_str = str(query_vector)
        vector_hash = hashlib.md5(vector_str.encode()).hexdigest()
        book_str = book_id or "all"
        return self._generate_cache_key("similarity", vector_hash, book_str, str(limit))

    async def get_cached_similarity_results(self, query_vector: List[float], book_id: Optional[str], limit: int) -> Optional[List[Dict[str, Any]]]:
        """Get cached similarity search results"""
        key = await self.get_similarity_cache_key(query_vector, book_id, limit)
        return await self.get(key)

    async def cache_similarity_results(self, query_vector: List[float], book_id: Optional[str], limit: int,
                                     results: List[Dict[str, Any]], ttl: int = 1800) -> bool:
        """Cache similarity search results"""
        key = await self.get_similarity_cache_key(query_vector, book_id, limit)
        return await self.set(key, results, ttl)

    # Context building caching
    async def get_context_cache_key(self, chunk_ids: List[str], max_length: int) -> str:
        """Generate cache key for built context"""
        import hashlib
        chunks_str = "-".join(sorted(chunk_ids))
        chunks_hash = hashlib.md5(chunks_str.encode()).hexdigest()
        return self._generate_cache_key("context", chunks_hash, str(max_length))

    async def get_cached_context(self, chunk_ids: List[str], max_length: int) -> Optional[str]:
        """Get cached built context"""
        key = await self.get_context_cache_key(chunk_ids, max_length)
        return await self.get(key)

    async def cache_context(self, chunk_ids: List[str], max_length: int, context: str, ttl: int = 3600) -> bool:
        """Cache built context"""
        key = await self.get_context_cache_key(chunk_ids, max_length)
        return await self.set(key, context, ttl)

# Global instance for use throughout the application
cache_service = CacheService()