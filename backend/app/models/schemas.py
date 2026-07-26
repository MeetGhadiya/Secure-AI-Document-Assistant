from typing import Optional
from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: str
    original_filename: str
    file_type: str
    file_size_bytes: int
    chunk_count: int
    status: str
    created_at: str


class UploadResponse(BaseModel):
    document_id: str
    status: str
    chunk_count: Optional[int] = None
    reason: Optional[str] = None


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    document_id: Optional[str] = None
    top_k: Optional[int] = Field(default=None, ge=1, le=20)


class SourceCitation(BaseModel):
    document_id: str
    chunk_index: int
    redactions: int = 0


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceCitation]


class DeleteResponse(BaseModel):
    document_id: str
    deleted: bool
