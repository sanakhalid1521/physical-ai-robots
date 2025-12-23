from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
import logging
import secure
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import logging service
from src.services.logging_service import logging_service

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for application startup and shutdown
    """
    logger.info("Application starting up...")
    # Startup logic can go here
    yield
    # Shutdown logic can go here
    logger.info("Application shutting down...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="RAG Chatbot API",
    description="API for the Retrieval-Augmented Generation Chatbot",
    version="1.0.0",
    lifespan=lifespan
)

# Add security headers using the secure library
secure_headers = secure.Secure(
    secure.CrossOriginOpenerPolicy("same-origin"),
    secure.CrossOriginResourcePolicy("same-origin"),
    secure.ReferrerPolicy("no-referrer"),
    secure.XContentTypeOptions("nosniff"),
    secure.XFrameOptions("DENY"),
    secure.StrictTransportSecurity(
        max_age=31536000,
        include_subdomains=True,
        preload=True
    ),
    secure.PermissionsPolicy({
        "accelerometer": "none",
        "camera": "none",
        "geolocation": "none",
        "gyroscope": "none",
        "magnetometer": "none",
        "microphone": "none",
        "payment": "none",
        "usb": "none",
    })
)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    secure_headers.framework.fastapi(response)
    return response

# Add request timing and logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Get user ID from headers or query parameters if available
    user_id = request.headers.get("user-id") or request.query_params.get("user_id")

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # Log the request
        logging_service.log_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            response_time=process_time,
            user_id=user_id
        )

        return response
    except Exception as e:
        process_time = time.time() - start_time
        logging_service.log_exception(
            f"Request failed: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "user_id": user_id,
                "response_time": process_time
            }
        )
        raise

# Add rate limiter to the app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, configure this properly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from .chat_router import router as chat_router
app.include_router(chat_router, prefix="/api", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "RAG Chatbot API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)