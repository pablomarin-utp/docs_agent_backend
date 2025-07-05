from app.schemas.auth_schema import RegisterRequest, LoginRequest
import bcrypt
import logging
from app.core.models import User
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends, Header
from app.services.jwt_service import create_access_token, decode_token, extract_token_from_header
from app.core.database import get_db

logger = logging.getLogger(__name__)

# ============= AUTHENTICATION FUNCTIONS =============

async def register_user(data: RegisterRequest, db: Session) -> dict:
    """Register a new user in the system."""
    
    # Check if user already exists
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        logger.warning(f"Register attempt failed (duplicate email): {data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The email is already registered."
        )

    # Hash password
    hashed_pw = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt())

    # Create new user
    new_user = User(
        email=data.email,
        hashed_password=hashed_pw.decode(),
        is_active=False,  
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"User registered successfully: {new_user.email}")
    return {"msg": "User registered successfully. Pending activation."}

async def login_user(data: LoginRequest, db: Session) -> dict:
    """Authenticate a user and return a JWT token."""
    
    # Find user by email
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        logger.warning(f"Login attempt failed (user not found): {data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials."
        )

    # Verify password
    if not bcrypt.checkpw(data.password.encode(), user.hashed_password.encode()):
        logger.warning(f"Login attempt failed (wrong password): {data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials."
        )

    # Check if user is active
    if not user.is_active:
        logger.warning(f"Login attempt failed (inactive user): {data.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Account not activated. Please contact administrator."
        )

    # Generate JWT token
    access_token = create_access_token(data={
        "email": user.email, 
        "id": str(user.id), 
        "is_active": user.is_active, 
        "is_admin": user.is_admin
    })

    logger.info(f"User authenticated successfully: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}

# ============= AUTHORIZATION FUNCTIONS =============

def get_token_from_header(authorization: str = Header(...)) -> str:
    """Extract and validate JWT token from Authorization header."""
    logger.debug("Verifying the JWT")
    try:
        return extract_token_from_header(authorization)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

def get_current_user_payload(token: str = Depends(get_token_from_header)) -> dict:
    """Get current user payload from JWT token."""

    try:
        payload = decode_token(token)
        if not payload.get("id"):
            raise HTTPException(status_code=401, detail="Invalid token payload")
        logger.debug(f"Token payload decoded successfully")
        return payload
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

async def get_current_user(
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
) -> User:
    """Get the currently logged-in user from database."""
    
    try:
        user_id = payload.get("id")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.warning(f"Current user not found: {user_id}")
            raise HTTPException(status_code=401, detail="User not found")
        
        if not user.is_active:
            logger.warning(f"Current user is not active: {user.email}")
            raise HTTPException(status_code=403, detail="Account not activated")
        
        logger.info(f"Current user retrieved successfully: {user}, type: {type(user)}")
        return user
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current user ensuring they are active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current user ensuring they have admin privileges."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

