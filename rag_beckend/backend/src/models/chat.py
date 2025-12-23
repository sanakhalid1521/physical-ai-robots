import re
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """
    Represents a user's query with mode and optional selected text
    """
    message: str = Field(..., description="The user's question", min_length=1, max_length=5000)
    mode: str = Field(..., description="The chat mode being used", pattern="^(book|selection)$")
    selectedText: Optional[str] = Field(None, description="The highlighted text when in selection mode", max_length=10000)
    userId: Optional[str] = Field(None, description="Identifier for the user session", max_length=255)
    language: Optional[str] = Field(None, description="Detected or specified language", pattern="^(en|ur)?$")

    class Config:
        # Allow extra fields for flexibility
        extra = "allow"

    @validator('message', 'selectedText', pre=True)
    def validate_input_strings(cls, v):
        """Validate input strings to prevent injection attacks"""
        if v is None:
            return v

        # Remove any potential SQL injection patterns
        v = re.sub(r"(?i)(union|select|insert|update|delete|drop|create|alter|exec|execute)\s", "", v)

        # Remove potential script tags
        v = re.sub(r"(?i)<script[^>]*>.*?</script>", "", v)

        # Remove potential JavaScript event handlers
        v = re.sub(r"(?i)on\w+\s*=", "", v)

        # Remove potential command injection patterns
        v = re.sub(r"[;&|`$()]", "", v)

        # Remove potential path traversal
        v = v.replace("../", "").replace("..\\", "")

        return v.strip()

    def validate_for_selection_mode(self):
        """
        Validate that selectedText is provided when mode is 'selection'
        """
        if self.mode == "selection" and (not self.selectedText or self.selectedText.strip() == ""):
            raise ValueError("selectedText is required when mode is 'selection'")


class ChatResponse(BaseModel):
    """
    Contains the answer and sources that informed the response
    """
    answer: str = Field(..., description="The chatbot's response to the user's question", max_length=10000)
    sources: Optional[List[str]] = Field(None, description="List of source identifiers used to generate the answer")
    language: str = Field(..., description="The language of the response", pattern="^(en|ur)$")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the response was generated")

    class Config:
        # Allow extra fields for flexibility
        extra = "allow"