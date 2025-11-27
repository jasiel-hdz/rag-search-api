from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class RAGQueryRequest(BaseModel):
    """Schema for RAG query"""
    query: str = Field(..., description="User question or query", min_length=1)
    document_id: Optional[int] = Field(default=None, description="Optional document ID to filter search")


class ChunkResult(BaseModel):
    """Schema for a found chunk"""
    chunk_id: Optional[int]
    document_id: Optional[int]
    text: str
    score: Optional[float]
    metadata: Dict[str, Any]


class RAGQueryResponse(BaseModel):
    """Schema for RAG response"""
    query: str
    chunks_found: int
    chunks: List[ChunkResult]
    response: str
    context_used: Optional[str] = None

