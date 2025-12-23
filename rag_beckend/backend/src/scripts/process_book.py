#!/usr/bin/env python3
"""
Script to load book markdown files and process them into chunks for embedding.
This script handles the ingestion pipeline for the RAG system.
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import List, Tuple
import logging

# Add the backend/src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.rag_service import rag_service
from src.utils.markdown_loader import load_markdown_file
from src.utils.text_processor import chunk_text
from src.utils.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_single_book(book_path: str, book_id: str, title: str = None) -> bool:
    """
    Process a single book file by loading, chunking, and indexing it.

    Args:
        book_path: Path to the markdown file
        book_id: Unique identifier for the book
        title: Title of the book (optional, will use filename if not provided)

    Returns:
        True if processing was successful, False otherwise
    """
    try:
        if not title:
            title = Path(book_path).stem

        logger.info(f"Processing book: {title} (ID: {book_id}) from {book_path}")

        # Load the markdown file
        content = load_markdown_file(book_path)
        if not content:
            logger.error(f"Failed to load content from {book_path}")
            return False

        logger.info(f"Loaded content with {len(content)} characters")

        # Process the content using the RAG service
        success = await rag_service.index_book_content(
            book_id=book_id,
            title=title,
            content=content
        )

        if success:
            logger.info(f"Successfully processed and indexed book: {title}")
        else:
            logger.error(f"Failed to index book: {title}")

        return success

    except Exception as e:
        logger.error(f"Error processing book {book_path}: {e}")
        return False


async def process_directory(directory_path: str, recursive: bool = True) -> bool:
    """
    Process all markdown files in a directory.

    Args:
        directory_path: Path to the directory containing markdown files
        recursive: Whether to process subdirectories recursively

    Returns:
        True if all files were processed successfully, False otherwise
    """
    try:
        directory = Path(directory_path)
        if not directory.exists():
            logger.error(f"Directory does not exist: {directory_path}")
            return False

        # Find all markdown files
        if recursive:
            markdown_files = list(directory.rglob("*.md"))
        else:
            markdown_files = list(directory.glob("*.md"))

        if not markdown_files:
            logger.warning(f"No markdown files found in {directory_path}")
            return False

        logger.info(f"Found {len(markdown_files)} markdown files to process")

        success_count = 0
        for file_path in markdown_files:
            # Generate a unique book ID based on the filename
            book_id = f"book_{file_path.stem}_{hash(str(file_path)) % 10000:04d}"
            title = file_path.stem

            success = await process_single_book(str(file_path), book_id, title)
            if success:
                success_count += 1

        logger.info(f"Processed {success_count} out of {len(markdown_files)} files successfully")
        return success_count == len(markdown_files)

    except Exception as e:
        logger.error(f"Error processing directory {directory_path}: {e}")
        return False


async def main():
    """
    Main function to process books based on command line arguments.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Process book markdown files for RAG system")
    parser.add_argument("input", help="Path to markdown file or directory")
    parser.add_argument("--book-id", help="Unique book ID (required for single file)")
    parser.add_argument("--title", help="Book title (optional, defaults to filename)")
    parser.add_argument("--recursive", action="store_true", help="Process directories recursively")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed without doing it")

    args = parser.parse_args()

    # Validate input path
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input path does not exist: {args.input}")
        return 1

    # Check if input is a file or directory
    if input_path.is_file():
        if input_path.suffix.lower() != '.md':
            logger.error(f"Input file is not a markdown file: {args.input}")
            return 1

        if not args.book_id:
            logger.error("--book-id is required when processing a single file")
            return 1

        if args.dry_run:
            logger.info(f"Would process file: {args.input} with ID: {args.book_id}")
            return 0

        success = await process_single_book(str(input_path), args.book_id, args.title)
        return 0 if success else 1

    elif input_path.is_dir():
        if args.dry_run:
            logger.info(f"Would process directory: {args.input}")
            # Show files that would be processed
            if args.recursive:
                files = list(input_path.rglob("*.md"))
            else:
                files = list(input_path.glob("*.md"))
            logger.info(f"Would process {len(files)} markdown files")
            return 0

        success = await process_directory(str(input_path), args.recursive)
        return 0 if success else 1

    else:
        logger.error(f"Input path is neither a file nor a directory: {args.input}")
        return 1


if __name__ == "__main__":
    # Check if required environment variables are set
    settings = get_settings()

    if not settings.openai_api_key:
        logger.error("OPENAI_API_KEY environment variable is not set")
        sys.exit(1)

    if not settings.qdrant_url:
        logger.error("QDRANT_URL environment variable is not set")
        sys.exit(1)

    # Run the main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)