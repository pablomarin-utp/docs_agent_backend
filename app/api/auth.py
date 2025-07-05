from app.services.auth_service import register_user, login_user, get_current_user
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.auth_schema import RegisterRequest, LoginRequest
from app.core.database import get_db
from app.core.models import User

router = APIRouter()

@router.post("/register")
async def register(data: RegisterRequest, db: Session = Depends(get_db)):
    return await register_user(data, db)

@router.post("/login")
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    return await login_user(data, db)

@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    """
    Get current user information.
    Requires a valid JWT token.
    """
    return {
        "id": user.id,
        "email": user.email,
        "is_admin": user.is_admin,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() + "Z",
        "credits": user.credits
    }