import bcrypt
import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.core.models import User

logger = logging.getLogger(__name__)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    result = bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    logger.debug(f"Password verification result: {result}")
    return result

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    logger.debug(f"Password hashed successfully")
    return hashed

async def change_password(
    user_id: str, 
    old_password: str, 
    new_password: str, 
    db: Session
) -> dict:
    """Change user password after verifying old password."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid current password")
    
    user.hashed_password = hash_password(new_password)
    db.commit()
    
    logger.info(f"Password changed for user: {user.email}")
    return {"msg": "Password changed successfully"}