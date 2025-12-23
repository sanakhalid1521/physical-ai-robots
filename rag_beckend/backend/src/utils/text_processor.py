import re
from typing import List, Tuple
from tiktoken import get_encoding
import logging


logger = logging.getLogger(__name__)


def get_token_count(text: str, encoding_name: str = "cl100k_base") -> int:
    """
    Get the number of tokens in a text using the specified encoding.

    Args:
        text: Input text to count tokens for
        encoding_name: Name of the encoding to use (default: cl100k_base for GPT-4)

    Returns:
        Number of tokens in the text
    """
    encoding = get_encoding(encoding_name)
    tokens = encoding.encode(text)
    return len(tokens)


def chunk_text(text: str, max_tokens: int = 500, overlap_tokens: int = 100,
               encoding_name: str = "cl100k_base") -> List[Tuple[str, int, int]]:
    """
    Split text into chunks with specified token limits and overlap.

    Args:
        text: Input text to chunk
        max_tokens: Maximum number of tokens per chunk (default: 500)
        overlap_tokens: Number of overlapping tokens between chunks (default: 100)
        encoding_name: Name of the encoding to use for tokenization

    Returns:
        List of tuples containing (chunk_text, start_position, end_position)
    """
    if not text or not text.strip():
        return []

    encoding = get_encoding(encoding_name)
    tokens = encoding.encode(text)

    if len(tokens) <= max_tokens:
        return [(text, 0, len(text))]

    chunks = []
    start_idx = 0

    while start_idx < len(tokens):
        # Calculate the end index for this chunk
        end_idx = start_idx + max_tokens

        # If this is the last chunk, include all remaining tokens
        if end_idx >= len(tokens):
            end_idx = len(tokens)
        else:
            # If not the last chunk, add overlap
            if end_idx + overlap_tokens < len(tokens):
                end_idx = end_idx + overlap_tokens

        # Decode the token slice back to text
        chunk_tokens = tokens[start_idx:end_idx]
        chunk_text = encoding.decode(chunk_tokens)

        # Find the actual text boundaries to avoid cutting words
        if start_idx > 0:
            # Try to find a sentence or word boundary near the start
            chunk_start = find_sentence_boundary(text, encoding.decode(tokens[start_idx:start_idx+20]))
        else:
            chunk_start = 0

        if end_idx < len(tokens):
            # Try to find a sentence or word boundary near the end
            chunk_end = find_sentence_boundary(text, encoding.decode(tokens[end_idx-20:end_idx]),
                                             forward=False)
        else:
            chunk_end = len(text)

        # Extract the actual chunk with proper boundaries
        actual_chunk = text[chunk_start:chunk_end]

        chunks.append((actual_chunk, chunk_start, chunk_end))

        # Move to the next chunk, accounting for overlap
        if start_idx + max_tokens >= len(tokens):
            # This was the last chunk
            break

        # Move start index to the next non-overlapping position
        start_idx = end_idx - overlap_tokens

        # Ensure we make progress to avoid infinite loops
        if start_idx <= start_idx:
            start_idx += max_tokens

    return chunks


def find_sentence_boundary(text: str, search_token: str, forward: bool = True) -> int:
    """
    Find the nearest sentence or word boundary to avoid cutting words/sentences.

    Args:
        text: Original text
        search_token: Token to search for
        forward: Whether to search forward (True) or backward (False)

    Returns:
        Index of the nearest boundary
    """
    if forward:
        # Find the position of the search token and look for sentence/word boundary after
        pos = text.find(search_token)
        if pos == -1:
            return min(len(text), pos + len(search_token))

        # Look for sentence boundaries (.!? followed by space or end)
        sentence_end = re.search(r'[.!?]+\s', text[pos:])
        if sentence_end:
            return pos + sentence_end.end()

        # Look for word boundary
        word_boundary = re.search(r'\s', text[pos:])
        if word_boundary:
            return pos + word_boundary.end()

        return pos + len(search_token)
    else:
        # Search backward
        pos = text.rfind(search_token)
        if pos <= 0:
            return max(0, pos)

        # Look for sentence boundaries before
        sentence_start = re.search(r'\s[.!?]+', text[:pos])
        if sentence_start:
            return sentence_start.start()

        # Look for word boundary
        word_boundary = re.search(r'\s\S*$', text[:pos])
        if word_boundary:
            return word_boundary.start()

        return pos


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and normalizing.

    Args:
        text: Input text to clean

    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove extra newlines but keep paragraph structure
    text = re.sub(r'\n\s*\n', '\n\n', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences.

    Args:
        text: Input text to split

    Returns:
        List of sentences
    """
    # Split on sentence boundaries
    sentences = re.split(r'[.!?]+\s+', text)
    # Clean up each sentence
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences


def truncate_to_token_limit(text: str, max_tokens: int, encoding_name: str = "cl100k_base") -> str:
    """
    Truncate text to fit within the token limit.

    Args:
        text: Input text to truncate
        max_tokens: Maximum number of tokens allowed
        encoding_name: Name of the encoding to use

    Returns:
        Truncated text that fits within the token limit
    """
    encoding = get_encoding(encoding_name)
    tokens = encoding.encode(text)

    if len(tokens) <= max_tokens:
        return text

    truncated_tokens = tokens[:max_tokens]
    truncated_text = encoding.decode(truncated_tokens)

    # Try to find a sentence boundary to avoid cutting mid-sentence
    last_sentence_end = max(truncated_text.rfind('.'), truncated_text.rfind('!'), truncated_text.rfind('?'))
    if last_sentence_end > 0:
        # Include the sentence ending
        truncated_text = truncated_text[:last_sentence_end + 1]

    return truncated_text