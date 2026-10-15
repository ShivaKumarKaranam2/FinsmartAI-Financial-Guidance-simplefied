"""FinRAG document intelligence request and response schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class IngestResponse(BaseModel):
    """Response returned upon successful document ingestion."""
    session_id: str
    chunks_ingested: int
    message: str


class QueryRequest(BaseModel):
    """Request model for document retrieval query."""
    session_id: str = Field(..., description="Active session ID for document context")
    question: str = Field(..., description="User query about the ingested document")
    user_id: Optional[str] = Field("default_user", description="User identifier for isolation")
    chat_history: Optional[List[Dict[str, str]]] = Field(default_factory=list, description="Recent conversation turns")


class QueryResponse(BaseModel):
    """Response containing synthesized answer and cited sources."""
    answer: str
    sources: List[str] = Field(default_factory=list)
