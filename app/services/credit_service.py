from sqlalchemy.orm import Session
from app.core.models import User
from typing import Dict, Any
import logging
from fastapi import HTTPException
from uuid import UUID

logger = logging.getLogger(__name__)

async def deduct_credits(
    user_id: UUID,
    amount: int,
    db: Session
) -> bool:
    """Deduct credits from user account."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.credits < amount:
            logger.warning(f"Insufficient credits for user {user_id}: {user.credits} < {amount}")
            return False
        
        user.credits -= amount
        db.commit()
        db.refresh(user)
        
        logger.info(f"Deducted {amount} credits from user {user_id}. Remaining: {user.credits}")
        return True
        
    except Exception as e:
        logger.error(f"Error deducting credits: {str(e)}")
        raise

async def add_credits(
    user_id: UUID,
    amount: int,
    db: Session
) -> Dict[str, Any]:
    """Add credits to user account."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.credits += amount
        db.commit()
        db.refresh(user)
        
        logger.info(f"Added {amount} credits to user {user_id}. Total: {user.credits}")
        return {"credits": user.credits, "message": f"Added {amount} credits"}
        
    except Exception as e:
        logger.error(f"Error adding credits: {str(e)}")
        raise