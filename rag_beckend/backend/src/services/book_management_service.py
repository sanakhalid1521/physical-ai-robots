from typing import List, Optional, Dict, Any
from src.services.database_service import database_service
from src.services.qdrant_service import qdrant_service
from src.utils.config import get_settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BookManagementService:
    """
    Service class for managing multiple books in the system
    """
    def __init__(self):
        self.database_service = database_service
        self.qdrant_service = qdrant_service
        self.settings = get_settings()

    async def list_books(self) -> List[Dict[str, Any]]:
        """
        List all books in the system with their metadata.

        Returns:
            List of book metadata dictionaries
        """
        try:
            books = await self.database_service.get_all_books()
            return books
        except Exception as e:
            logger.error(f"Error listing books: {e}")
            return []

    async def get_book_by_id(self, book_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific book by its ID.

        Args:
            book_id: Unique identifier for the book

        Returns:
            Book metadata dictionary or None if not found
        """
        try:
            book = await self.database_service.get_book_by_id(book_id)
            return book
        except Exception as e:
            logger.error(f"Error getting book {book_id}: {e}")
            return None

    async def delete_book(self, book_id: str) -> bool:
        """
        Delete a book and all its associated embeddings and data.

        Args:
            book_id: Unique identifier for the book to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # First, delete embeddings from Qdrant
            success = self.qdrant_service.delete_book_embeddings(book_id)
            if not success:
                logger.error(f"Failed to delete embeddings for book {book_id} from Qdrant")
                return False

            # Then, delete book metadata from database
            success = await self.database_service.delete_book(book_id)
            if not success:
                logger.error(f"Failed to delete book {book_id} from database")
                # Rollback: we deleted from Qdrant but not from DB, so try to restore in Qdrant
                return False

            logger.info(f"Successfully deleted book {book_id}")
            return True
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
            success = await self.database_service.update_book_metadata(
                book_id=book_id,
                title=title,
                description=description
            )
            if success:
                logger.info(f"Updated metadata for book {book_id}")
            else:
                logger.error(f"Failed to update metadata for book {book_id}")

            return success
        except Exception as e:
            logger.error(f"Error updating book {book_id} metadata: {e}")
            return False

    async def search_books(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for books by title or content.

        Args:
            query: Search query string

        Returns:
            List of matching book metadata dictionaries
        """
        try:
            # Search in database by title and metadata
            books = await self.database_service.search_books(query)
            return books
        except Exception as e:
            logger.error(f"Error searching books: {e}")
            return []

    async def get_book_statistics(self, book_id: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a specific book (chunk count, last updated, etc.).

        Args:
            book_id: Unique identifier for the book

        Returns:
            Dictionary with book statistics or None if not found
        """
        try:
            book_stats = await self.database_service.get_book_statistics(book_id)
            if book_stats:
                # Add vector count from Qdrant
                vector_count = self.qdrant_service.get_book_vector_count(book_id)
                book_stats['vector_count'] = vector_count
            return book_stats
        except Exception as e:
            logger.error(f"Error getting statistics for book {book_id}: {e}")
            return None

    async def get_all_books_statistics(self) -> List[Dict[str, Any]]:
        """
        Get statistics for all books in the system.

        Returns:
            List of dictionaries with book statistics
        """
        try:
            books = await self.list_books()
            stats_list = []

            for book in books:
                book_id = book.get('book_id')
                if book_id:
                    stats = await self.get_book_statistics(book_id)
                    if stats:
                        stats_list.append(stats)

            return stats_list
        except Exception as e:
            logger.error(f"Error getting all books statistics: {e}")
            return []

    async def validate_book_exists(self, book_id: str) -> bool:
        """
        Check if a book exists in the system.

        Args:
            book_id: Unique identifier for the book

        Returns:
            True if book exists, False otherwise
        """
        try:
            book = await self.get_book_by_id(book_id)
            return book is not None
        except Exception as e:
            logger.error(f"Error validating book existence {book_id}: {e}")
            return False


# Global instance for use throughout the application
book_management_service = BookManagementService()