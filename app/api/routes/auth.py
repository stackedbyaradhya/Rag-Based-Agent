from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import AuthTokenResponse, CurrentUserResponse, LoginRequest, RegisterRequest
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=CurrentUserResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = AuthService.register(db, payload)
    return CurrentUserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        organization_id=user.organization_id,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.post("/login", response_model=AuthTokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    token = AuthService.login(db, payload)
    return AuthTokenResponse(access_token=token)


@router.get("/me", response_model=CurrentUserResponse)
def me(current_user: User = Depends(get_current_user)):
    return CurrentUserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        organization_id=current_user.organization_id,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )
