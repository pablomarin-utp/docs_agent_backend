from sqlalchemy.orm import Session
from app.core.models import User
from typing import Dict, Any
from fastapi import HTTPException
from uuid import UUID
from app.utils.logging_utils import get_secure_logger

logger = get_secure_logger(__name__)

async def deduct_credits(
    user_id: UUID,
    amount: int,
    db: Session
) -> bool:
    """
    Deduct credits from a user's account.
    
    Args:
        user_id: UUID of the user
        amount: Number of credits to deduct
        db: Database session
        
    Returns:
        True if credits were successfully deducted, False if insufficient credits
        
    Raises:
        HTTPException: If user not found
    """
    logger.info("Deducting credits", user_id=user_id, amount=amount)
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning("User not found for credit deduction", user_id=user_id)
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.credits < amount:
            logger.warning("Insufficient credits", user_id=user_id, current_credits=user.credits, requested_amount=amount)
            return False
        
        user.credits -= amount
        db.commit()
        db.refresh(user)
        
        logger.info("Credits deducted successfully", user_id=user_id, amount_deducted=amount, remaining_credits=user.credits)
        return True
        
    except Exception as e:
        logger.error("Error deducting credits", user_id=user_id, amount=amount, error=str(e))
        raise

async def add_credits(
    user_id: UUID,
    amount: int,
    db: Session
) -> Dict[str, Any]:
    """
    Add credits to a user's account.
    
    Args:
        user_id: UUID of the user
        amount: Number of credits to add
        db: Database session
        
    Returns:
        Dictionary with updated credit balance and message
        
    Raises:
        HTTPException: If user not found
    """
    logger.info("Adding credits", user_id=user_id, amount=amount)
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning("User not found for credit addition", user_id=user_id)
            raise HTTPException(status_code=404, detail="User not found")
        
        user.credits += amount
        db.commit()
        db.refresh(user)
        
        logger.info("Credits added successfully", user_id=user_id, amount_added=amount, total_credits=user.credits)
        return {"credits": user.credits, "message": f"Added {amount} credits"}
        
    except Exception as e:
        logger.error("Error adding credits", user_id=user_id, amount=amount, error=str(e))
        raise