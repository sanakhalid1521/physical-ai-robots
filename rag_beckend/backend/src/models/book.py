from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class BookContent(BaseModel):
    """
    Represents book chapters loaded from Markdown files
    """
    id: str = Field(..., description="Unique identifier for the content chunk")
    title: str = Field(..., description="Title of the chapter/section")
    content: str = Field(..., description="The actual text content", max_length=10000)
    sourceFile: str = Field(..., description="Path to the original markdown file")
    chunkIndex: int = Field(..., description="Position of this chunk in the original document")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata about the content")

    class Config:
        # Allow extra fields for flexibility
        extra = "allow"


class BookMetadata(BaseModel):
    """
    Metadata about a book for tracking and management
    """
    bookId: str = Field(..., description="Unique identifier for the book")
    title: str = Field(..., description="Title of the book")
    author: Optional[str] = Field(None, description="Author of the book")
    description: Optional[str] = Field(None, description="Description of the book")
    sourcePath: str = Field(..., description="Path to the original book files")
    chunkCount: int = Field(..., description="Number of chunks in the book")
    createdAt: datetime = Field(default_factory=datetime.utcnow, description="When the book was processed")
    updatedAt: datetime = Field(default_factory=datetime.utcnow, description="When the book was last updated")