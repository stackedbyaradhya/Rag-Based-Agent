from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.chat_history import ChatHistory
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.schemas.admin import DashboardSummaryResponse
from app.services.rag_service import RAGService

router = APIRouter()


@router.get("/summary", response_model=DashboardSummaryResponse)
def summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = datetime.now(UTC).date()
    total_docs = db.query(func.count(Document.id)).filter(Document.organization_id == current_user.organization_id).scalar() or 0
    total_chunks = (
        db.query(func.count(DocumentChunk.id))
        .join(Document, Document.id == DocumentChunk.document_id)
        .filter(Document.organization_id == current_user.organization_id)
        .scalar()
        or 0
    )
    questions_today = (
        db.query(func.count(ChatHistory.id))
        .filter(ChatHistory.organization_id == current_user.organization_id, func.date(ChatHistory.created_at) == today)
        .scalar()
        or 0
    )
    active_users = (
        db.query(func.count(User.id)).filter(User.organization_id == current_user.organization_id, User.is_active.is_(True)).scalar() or 0
    )
    topics = RAGService.most_searched_topics_today(db=db, organization_id=current_user.organization_id)
    return DashboardSummaryResponse(
        total_docs=total_docs,
        total_chunks=total_chunks,
        questions_asked_today=questions_today,
        most_searched_topics=topics,
        active_users=active_users,
    )
