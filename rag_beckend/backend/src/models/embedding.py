from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Embedding(BaseModel):
    """
    Vector representation of book content chunks for retrieval
    """
    chunkId: str = Field(..., description="Reference to the source content chunk")
    vector: List[float] = Field(..., description="The embedding vector values")
    content: str = Field(..., description="The text that was embedded")
    bookId: str = Field(..., description="Reference to the book this belongs to")
    createdAt: datetime = Field(default_factory=datetime.utcnow, description="When the embedding was generated")

    class Config:
        # Allow extra fields for flexibility
        extra = "allow"

    def validate_vector_dimensions(self, expected_dimension: Optional[int] = None) -> bool:
        """
        Validate that the vector has consistent dimensions
        """
        if expected_dimension is not None:
            return len(self.vector) == expected_dimension
        return len(self.vector) > 0


class EmbeddingRequest(BaseModel):
    """
    Request to generate embeddings for text content
    """
    text: str = Field(..., description="Text to generate embeddings for", min_length=1)
    bookId: str = Field(..., description="Reference to the book this belongs to")
    chunkId: str = Field(..., description="Reference to the content chunk")


class EmbeddingResponse(BaseModel):
    """
    Response with generated embeddings
    """
    chunkId: str = Field(..., description="Reference to the content chunk")
    vector: List[float] = Field(..., description="The generated embedding vector values")
    success: bool = Field(..., description="Whether the embedding generation was successful")
    message: Optional[str] = Field(None, description="Additional information about the operation")