from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)


class SourceRead(BaseModel):
    citation: str
    document_id: int
    chunk_id: int
    filename: str
    excerpt: str
    similarity: float


class QueryResponse(BaseModel):
    query_id: int
    answer: str
    sources: list[SourceRead]


class QueryHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question: str
    answer: str
    sources: list[dict]
    created_at: datetime
