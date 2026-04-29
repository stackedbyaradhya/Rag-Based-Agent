from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.chat_history import ChatHistory
from app.models.user import User
from app.schemas.chat import AskQuestionRequest, AskQuestionResponse, ChatHistoryResponse
from app.services.rag_service import RAGService

router = APIRouter()


@router.post("/ask", response_model=AskQuestionResponse)
async def ask_question(
    payload: AskQuestionRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if not payload.question.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Question cannot be empty")
    rag_service = RAGService()
    return await rag_service.ask(db=db, user=current_user, question=payload.question.strip())


@router.get("/history", response_model=list[ChatHistoryResponse])
def history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == current_user.id)
        .order_by(ChatHistory.created_at.desc())
        .limit(100)
        .all()
    )
    return [ChatHistoryResponse(id=row.id, question=row.question, answer=row.answer, created_at=row.created_at) for row in rows]


@router.get("/history/{history_id}", response_model=ChatHistoryResponse)
def history_item(history_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = db.query(ChatHistory).filter(ChatHistory.id == history_id, ChatHistory.user_id == current_user.id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History item not found")
    return ChatHistoryResponse(id=row.id, question=row.question, answer=row.answer, created_at=row.created_at)
