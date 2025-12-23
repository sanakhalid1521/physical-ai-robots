from typing import Optional, List, Dict, Any
import asyncpg
from src.utils.config import get_settings
import logging
from datetime import datetime
import json


logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Service class for managing database operations with Neon Postgres
    """
    def __init__(self):
        self.settings = get_settings()
        self.pool = None

    async def initialize(self):
        """
        Initialize the database connection pool
        """
        try:
            self.pool = await asyncpg.create_pool(
                dsn=self.settings.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60,
                statement_cache_size=100
            )
            logger.info("Database connection pool initialized")

            # Create required tables if they don't exist
            await self._create_tables()
        except Exception as e:
            logger.error(f"Error initializing database connection pool: {e}")
            raise

    async def _create_tables(self):
        """
        Create required tables if they don't exist
        """
        async with self.pool.acquire() as connection:
            # Create queries table for storing query logs
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS queries (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255),
                    message TEXT NOT NULL,
                    mode VARCHAR(20) NOT NULL,
                    selected_text TEXT,
                    response TEXT NOT NULL,
                    sources TEXT,
                    language VARCHAR(10),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create books table for storing book metadata
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id SERIAL PRIMARY KEY,
                    book_id VARCHAR(255) UNIQUE NOT NULL,
                    title VARCHAR(500) NOT NULL,
                    author VARCHAR(255),
                    description TEXT,
                    source_path VARCHAR(1000),
                    chunk_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create sessions table for storing user sessions
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) UNIQUE NOT NULL,
                    preferences JSONB,
                    history JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            logger.info("Database tables created/verified")

    async def log_query(self, user_id: Optional[str], message: str, mode: str,
                       selected_text: Optional[str], response: str,
                       sources: Optional[List[str]], language: str):
        """
        Log a query and its response to the database.

        Args:
            user_id: ID of the user making the query
            message: The user's question
            mode: The chat mode used ('book' or 'selection')
            selected_text: The selected text (if in selection mode)
            response: The chatbot's response
            sources: List of sources used in the response
            language: The language of the query/response
        """
        try:
            sources_json = json.dumps(sources) if sources else None

            async with self.pool.acquire() as connection:
                await connection.execute("""
                    INSERT INTO queries (user_id, message, mode, selected_text, response, sources, language)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, user_id, message, mode, selected_text, response, sources_json, language)

            logger.debug(f"Logged query from user {user_id}")
        except Exception as e:
            logger.error(f"Error logging query: {e}")

    async def get_query_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get query history for a specific user.

        Args:
            user_id: ID of the user
            limit: Maximum number of records to return

        Returns:
            List of query records
        """
        try:
            async with self.pool.acquire() as connection:
                rows = await connection.fetch("""
                    SELECT message, response, language, created_at
                    FROM queries
                    WHERE user_id = $1
                    ORDER BY created_at DESC
                    LIMIT $2
                """, user_id, limit)

                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting query history for user {user_id}: {e}")
            return []

    async def save_book_metadata(self, book_id: str, title: str, author: Optional[str] = None,
                                description: Optional[str] = None, source_path: Optional[str] = None,
                                chunk_count: int = 0):
        """
        Save or update book metadata in the database.

        Args:
            book_id: Unique identifier for the book
            title: Title of the book
            author: Author of the book
            description: Description of the book
            source_path: Path to the original book files
            chunk_count: Number of chunks in the book
        """
        try:
            async with self.pool.acquire() as connection:
                await connection.execute("""
                    INSERT INTO books (book_id, title, author, description, source_path, chunk_count)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (book_id)
                    DO UPDATE SET
                        title = EXCLUDED.title,
                        author = EXCLUDED.author,
                        description = EXCLUDED.description,
                        source_path = EXCLUDED.source_path,
                        chunk_count = EXCLUDED.chunk_count,
                        updated_at = CURRENT_TIMESTAMP
                """, book_id, title, author, description, source_path, chunk_count)

            logger.info(f"Saved metadata for book {book_id}")
        except Exception as e:
            logger.error(f"Error saving book metadata for {book_id}: {e}")

    async def get_book_metadata(self, book_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific book.

        Args:
            book_id: Unique identifier for the book

        Returns:
            Dictionary containing book metadata or None if not found
        """
        try:
            async with self.pool.acquire() as connection:
                row = await connection.fetchrow("""
                    SELECT book_id, title, author, description, source_path, chunk_count, created_at, updated_at
                    FROM books
                    WHERE book_id = $1
                """, book_id)

                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting metadata for book {book_id}: {e}")
            return None

    async def get_all_books(self) -> List[Dict[str, Any]]:
        """
        Get metadata for all books in the database.

        Returns:
            List of book metadata dictionaries
        """
        try:
            async with self.pool.acquire() as connection:
                rows = await connection.fetch("""
                    SELECT book_id, title, author, description, source_path, chunk_count, created_at, updated_at
                    FROM books
                    ORDER BY created_at DESC
                """)

                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting all books: {e}")
            return []

    async def save_session(self, session_id: str, preferences: Optional[Dict] = None,
                          history: Optional[List[Dict]] = None):
        """
        Save or update user session data.

        Args:
            session_id: Unique identifier for the session
            preferences: User preferences
            history: Chat history
        """
        try:
            preferences_json = json.dumps(preferences) if preferences else None
            history_json = json.dumps(history) if history else None

            async with self.pool.acquire() as connection:
                await connection.execute("""
                    INSERT INTO sessions (session_id, preferences, history)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (session_id)
                    DO UPDATE SET
                        preferences = COALESCE(EXCLUDED.preferences, sessions.preferences),
                        history = COALESCE(EXCLUDED.history, sessions.history),
                        last_active = CURRENT_TIMESTAMP
                """, session_id, preferences_json, history_json)

            logger.debug(f"Saved session {session_id}")
        except Exception as e:
            logger.error(f"Error saving session {session_id}: {e}")

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data for a specific session ID.

        Args:
            session_id: Unique identifier for the session

        Returns:
            Dictionary containing session data or None if not found
        """
        try:
            async with self.pool.acquire() as connection:
                row = await connection.fetchrow("""
                    SELECT session_id, preferences, history, created_at, last_active
                    FROM sessions
                    WHERE session_id = $1
                """, session_id)

                if row:
                    result = dict(row)
                    # Parse JSON fields
                    if result['preferences']:
                        result['preferences'] = json.loads(result['preferences'])
                    if result['history']:
                        result['history'] = json.loads(result['history'])
                    return result
                return None
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            return None

    async def get_book_by_id(self, book_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific book by its ID.

        Args:
            book_id: Unique identifier for the book

        Returns:
            Dictionary containing book metadata or None if not found
        """
        try:
            async with self.pool.acquire() as connection:
                row = await connection.fetchrow("""
                    SELECT book_id, title, author, description, source_path, chunk_count, created_at, updated_at
                    FROM books
                    WHERE book_id = $1
                """, book_id)

                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting book {book_id}: {e}")
            return None

    async def delete_book(self, book_id: str) -> bool:
        """
        Delete a book from the database.

        Args:
            book_id: Unique identifier for the book to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            async with self.pool.acquire() as connection:
                result = await connection.execute("""
                    DELETE FROM books WHERE book_id = $1
                """, book_id)

                # Check if any rows were affected
                if result and "DELETE 0" not in result:
                    logger.info(f"Deleted book {book_id} from database")
                    return True
                else:
                    logger.warning(f"No book found with ID {book_id} to delete")
                    return False
        except Exception as e:
            logger.error(f"Error deleting book {book_id}: {e}")
            return False

    async def update_book_metadata(self, book_id: str, title: Optional[str] = None,
                                  description: Optional[str] = None) -> bool:
        """
        Update metadata for a specific book.

        Args:
            book_id: Unique identifier for the book
            title: New title for the book (optional)
            description: New description for the book (optional)

        Returns:
            True if update was successful, False otherwise
        """
        try:
            # First, get the current metadata to preserve other fields
            current_book = await self.get_book_by_id(book_id)
            if not current_book:
                logger.warning(f"Book {book_id} not found for update")
                return False

            # Use provided values or keep existing ones
            new_title = title if title is not None else current_book['title']
            new_description = description if description is not None else current_book['description']

            async with self.pool.acquire() as connection:
                await connection.execute("""
                    UPDATE books
                    SET title = $2, description = $3, updated_at = CURRENT_TIMESTAMP
                    WHERE book_id = $1
                """, book_id, new_title, new_description)

            logger.info(f"Updated metadata for book {book_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating book {book_id} metadata: {e}")
            return False

    async def search_books(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for books by title or description.

        Args:
            query: Search query string

        Returns:
            List of matching book metadata dictionaries
        """
        try:
            async with self.pool.acquire() as connection:
                rows = await connection.fetch("""
                    SELECT book_id, title, author, description, source_path, chunk_count, created_at, updated_at
                    FROM books
                    WHERE title ILIKE $1 OR description ILIKE $1
                    ORDER BY created_at DESC
                """, f"%{query}%")

                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error searching books for query '{query}': {e}")
            return []

    async def get_book_statistics(self, book_id: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a specific book.

        Args:
            book_id: Unique identifier for the book

        Returns:
            Dictionary with book statistics or None if not found
        """
        try:
            book_metadata = await self.get_book_by_id(book_id)
            if not book_metadata:
                return None

            # Return the metadata as statistics (can be extended with more stats)
            return {
                'book_id': book_metadata['book_id'],
                'title': book_metadata['title'],
                'author': book_metadata['author'],
                'description': book_metadata['description'],
                'chunk_count': book_metadata['chunk_count'],
                'created_at': book_metadata['created_at'],
                'updated_at': book_metadata['updated_at']
            }
        except Exception as e:
            logger.error(f"Error getting statistics for book {book_id}: {e}")
            return None

    async def close(self):
        """
        Close the database connection pool
        """
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")


# Global instance for use throughout the application
database_service = DatabaseService()