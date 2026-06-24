"""API request and response schemas"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class UploadResponse(BaseModel):
    """Response for file upload"""

    document_id: int
    filename: str
    message: str
    status: str


class AskRequest(BaseModel):
    """Request for asking a question"""

    question: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    include_sources: bool = Field(default=True)


class SourceReference(BaseModel):
    """Reference to a source document chunk"""

    chunk_id: int
    document_id: int
    similarity_score: float
    text_preview: str


class AskResponse(BaseModel):
    """Response for question asking"""

    answer: str
    sources: List[SourceReference] = []
    query_time_ms: float


class DocumentInfo(BaseModel):
    """Information about a document"""

    id: int
    filename: str
    original_filename: str
    file_size: int
    upload_date: datetime
    status: str
    error_message: Optional[str] = None

    class Config:
        """Pydantic config"""

        from_attributes = True


class DocumentListResponse(BaseModel):
    """Response for document listing"""

    documents: List[DocumentInfo]
    total: int
    offset: int
    limit: int


class HealthResponse(BaseModel):
    """Response for health check"""

    status: str
    version: str
    database: str
    openai: str


class ErrorResponse(BaseModel):
    """Error response"""

    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
