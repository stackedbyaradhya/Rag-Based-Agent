from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import admin_required
from app.db.session import get_db
from app.models.chat_history import ChatHistory
from app.models.document import Document
from app.models.user import User
from app.schemas.admin import AdminUserStatusUpdate
from app.schemas.auth import CurrentUserResponse

router = APIRouter()


@router.get("/users", response_model=list[CurrentUserResponse])
def list_users(db: Session = Depends(get_db), _: User = Depends(admin_required)):
    users = db.query(User).all()
    return [
        CurrentUserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            organization_id=user.organization_id,
            is_active=user.is_active,
            created_at=user.created_at,
        )
        for user in users
    ]


@router.patch("/users/{user_id}/status", response_model=CurrentUserResponse)
def update_user_status(
    user_id: int, payload: AdminUserStatusUpdate, db: Session = Depends(get_db), _: User = Depends(admin_required)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return CurrentUserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        organization_id=user.organization_id,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.get("/stats")
def admin_stats(db: Session = Depends(get_db), _: User = Depends(admin_required)):
    return {
        "users": db.query(func.count(User.id)).scalar() or 0,
        "documents": db.query(func.count(Document.id)).scalar() or 0,
        "questions": db.query(func.count(ChatHistory.id)).scalar() or 0,
    }
