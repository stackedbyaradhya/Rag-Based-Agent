from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.schemas.chat import ChunkSource
from app.services.embedding_service import EmbeddingService

router = APIRouter()


@router.get("")
async def semantic_search(
    q: str = Query(min_length=2),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    embedding = await EmbeddingService().embed(q)
    stmt = (
        select(DocumentChunk)
        .join(Document, Document.id == DocumentChunk.document_id)
        .options(joinedload(DocumentChunk.document))
        .where(Document.organization_id == current_user.organization_id)
        .order_by(DocumentChunk.embedding.cosine_distance(embedding))
        .limit(10)
    )
    chunks = db.execute(stmt).scalars().all()
    return [
        ChunkSource(
            document_id=chunk.document_id,
            document_title=chunk.document.title,
            chunk_id=chunk.id,
            chunk_index=chunk.chunk_index,
            excerpt=chunk.content[:300],
            score=0.0,
        )
        for chunk in chunks
    ]
