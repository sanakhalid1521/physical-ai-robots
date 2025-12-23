from fastapi import APIRouter, HTTPException, Depends
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from typing import Optional
import logging
from src.models.chat import ChatRequest, ChatResponse
from src.services.rag_service import rag_service
from src.utils.config import get_settings


logger = logging.getLogger(__name__)
router = APIRouter()


# Initialize rate limiter for this router
limiter = Limiter(key_func=get_remote_address)

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def chat_endpoint(chat_request: ChatRequest):
    """
    Main chat endpoint that handles both book mode and selection mode requests.

    Args:
        chat_request: ChatRequest containing the user's message and mode

    Returns:
        ChatResponse with the answer and sources
    """
    try:
        # Validate the request based on mode
        if chat_request.mode == "selection":
            chat_request.validate_for_selection_mode()
        elif chat_request.mode == "book":
            # Additional validation for book mode if needed
            if not chat_request.message or len(chat_request.message.strip()) == 0:
                raise ValueError("Message is required for book mode")
        else:
            raise ValueError(f"Invalid mode: {chat_request.mode}. Must be 'book' or 'selection'")

        # Process the request using the RAG service
        response = await rag_service.process_request(chat_request)

        if response is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to process the request. Please try again."
            )

        return response
    except ValueError as ve:
        logger.error(f"Validation error in chat endpoint: {ve}")
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while processing the request."
        )


@router.post("/chat/book", response_model=ChatResponse)
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def chat_book_mode_endpoint(chat_request: ChatRequest):
    """
    Chat endpoint specifically for book mode (retrieving relevant chunks from entire book).

    Args:
        chat_request: ChatRequest containing the user's message (mode should be 'book')

    Returns:
        ChatResponse with the answer and sources
    """
    try:
        # Ensure the mode is book mode
        if chat_request.mode != "book":
            chat_request.mode = "book"

        # Process the request using the RAG service
        response = await rag_service.process_request(chat_request)

        if response is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to process the book mode request. Please try again."
            )

        return response
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in book mode chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while processing the book mode request."
        )


@router.get("/health")
async def chat_health():
    """
    Health check endpoint for the chat service.
    """
    settings = get_settings()

    # Check if required configurations are available
    if not settings.openai_api_key:
        logger.warning("OpenAI API key not configured")

    if not settings.qdrant_url:
        logger.warning("Qdrant URL not configured")

    return {
        "status": "healthy",
        "openai_configured": bool(settings.openai_api_key),
        "qdrant_configured": bool(settings.qdrant_url)
    }


# Additional utility endpoints can be added here