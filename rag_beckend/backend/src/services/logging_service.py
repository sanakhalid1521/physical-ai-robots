import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pythonjsonlogger import jsonlogger
from src.utils.config import get_settings

class LoggingService:
    """
    Service class for managing structured logging and monitoring
    """
    def __init__(self):
        self.settings = get_settings()
        self.logger = self._setup_logger()
        self.error_count = 0
        self.request_count = 0

    def _setup_logger(self):
        """
        Set up structured logger with JSON formatting for better monitoring
        """
        logger = logging.getLogger("rag_chatbot")
        logger.setLevel(getattr(logging, self.settings.log_level.upper()))

        # Prevent duplicate handlers if logger already has handlers
        if not logger.handlers:
            # Create handler
            handler = logging.StreamHandler(sys.stdout)

            # Create formatter
            formatter = jsonlogger.JsonFormatter(
                '%(timestamp)s %(level)s %(name)s %(message)s %(module)s %(function)s %(line)s',
                rename_fields={
                    'timestamp': '@timestamp',
                    'level': 'level',
                    'name': 'logger',
                }
            )

            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def log_info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log an info message"""
        self.logger.info(message, extra=self._add_context(extra))

    def log_warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log a warning message"""
        self.logger.warning(message, extra=self._add_context(extra))

    def log_error(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        """Log an error message"""
        self.error_count += 1
        self.logger.error(message, extra=self._add_context(extra), exc_info=exc_info)

    def log_exception(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log an exception with traceback"""
        self.error_count += 1
        self.logger.exception(message, extra=self._add_context(extra))

    def log_request(self, method: str, path: str, status_code: int, response_time: float,
                   user_id: Optional[str] = None):
        """Log API request for monitoring"""
        self.request_count += 1

        extra = {
            "type": "request",
            "method": method,
            "path": path,
            "status_code": status_code,
            "response_time_ms": round(response_time * 1000, 2),
        }

        if user_id:
            extra["user_id"] = user_id

        level = logging.INFO if status_code < 400 else logging.WARNING
        self.logger.log(level, f"API request completed: {method} {path}", extra=self._add_context(extra))

    def log_query(self, user_id: str, query: str, response: str, sources: Optional[list] = None):
        """Log a user query for analytics"""
        extra = {
            "type": "query",
            "user_id": user_id,
            "query_length": len(query),
            "response_length": len(response),
            "sources_count": len(sources) if sources else 0
        }

        self.logger.info("User query processed", extra=self._add_context(extra))

    def get_stats(self) -> Dict[str, Any]:
        """Get current logging statistics"""
        return {
            "error_count": self.error_count,
            "request_count": self.request_count,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _add_context(self, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add common context to log entries"""
        if extra is None:
            extra = {}

        extra.update({
            "app": "rag_chatbot",
            "env": self.settings.app_env,
            "timestamp": datetime.utcnow().isoformat()
        })

        return extra

# Global instance for use throughout the application
logging_service = LoggingService()