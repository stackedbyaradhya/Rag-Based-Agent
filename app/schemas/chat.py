from datetime import datetime

from pydantic import BaseModel, Field


class AskQuestionRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)


class ChunkSource(BaseModel):
    document_id: int
    document_title: str
    chunk_id: int
    chunk_index: int
    excerpt: str
    score: float


class AskQuestionResponse(BaseModel):
    answer: str
    confidence: float
    sources: list[ChunkSource]


class ChatHistoryResponse(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime
