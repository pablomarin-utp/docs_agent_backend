from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth_service import get_current_user, get_current_admin_user
from app.core.models import User
from app.schemas.credits_schema import UpdateCreditsRequest
from app.services.credit_service import add_credits
from typing import Dict, Any
from uuid import UUID

router = APIRouter()

@router.get("/credits")
async def get_user_credits(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """Get current user's credit balance."""
    return {"credits": current_user.credits, "email": current_user.email}

@router.post("/credits/add")
async def add_user_credits(
    request: UpdateCreditsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Add credits to current user (for testing or admin purposes)."""
    return await add_credits(current_user.id, request.credits, db)

@router.post("/admin/users/{user_id}/credits")
async def admin_update_credits(
    user_id: str,
    request: UpdateCreditsRequest,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Admin endpoint to update any user's credits."""
    try:
        user_uuid = UUID(user_id)
        return await add_credits(user_uuid, request.credits, db)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
