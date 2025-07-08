from app.schemas.auth_schema import RegisterRequest, LoginRequest
import bcrypt
from app.core.models import User
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends, Header
from app.services.jwt_service import create_access_token, decode_token, extract_token_from_header
from app.core.database import get_db
from app.utils.logging_utils import get_secure_logger

logger = get_secure_logger(__name__)

# ============= AUTHENTICATION FUNCTIONS =============

async def register_user(data: RegisterRequest, db: Session) -> dict:
    """Register a new user in the system."""
    
    logger.info("Starting user registration", email=data.email)
    
    # Check if user already exists
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        logger.warning("Registration failed - duplicate email", email=data.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The email is already registered."
        )

    # Hash password
    try:
        hashed_pw = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt())
        logger.debug("Password hashed successfully")
    except Exception as e:
        logger.error("Password hashing failed", error=str(e))
        raise HTTPException(status_code=500, detail="Registration failed")

    # Create new user
    try:
        new_user = User(
            email=data.email,
            hashed_password=hashed_pw.decode(),
            is_active=False,  
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info("User registered successfully", user_id=new_user.id, email=data.email)
        return {"msg": "User registered successfully. Pending activation."}
    except Exception as e:
        logger.error("Database error during registration", error=str(e), email=data.email)
        db.rollback()
        raise HTTPException(status_code=500, detail="Registration failed")

async def login_user(data: LoginRequest, db: Session) -> dict:
    """Authenticate a user and return a JWT token."""
    
    logger.info("Login attempt", email=data.email)
    
    # Find user by email
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        logger.warning("Login failed - user not found", email=data.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials."
        )

    # Check if user is OAuth-only (empty password)
    if not user.hashed_password or user.hashed_password == "":
        logger.warning("OAuth user attempting password login", email=data.email, user_id=user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account uses Google sign-in. Please use the Google login option."
        )
    
    # Verify password
    try:
        if not bcrypt.checkpw(data.password.encode(), user.hashed_password.encode()):
            logger.warning("Login failed - invalid password", email=data.email, user_id=user.id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid credentials."
            )
    except Exception as e:
        logger.error("Password verification error", error=str(e), email=data.email)
        raise HTTPException(status_code=500, detail="Authentication failed")

    # Check if user is active
    if not user.is_active:
        logger.warning("Login failed - inactive user", email=data.email, user_id=user.id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Account not activated. Please contact administrator."
        )

    # Generate JWT token
    try:
        access_token = create_access_token(data={
            "email": user.email, 
            "id": str(user.id), 
            "is_active": user.is_active, 
            "is_admin": user.is_admin,
            "auth_method": "password" 
        })

        logger.info("User login successful", user_id=user.id, email=data.email)
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error("Token generation failed", error=str(e), email=data.email)
        raise HTTPException(status_code=500, detail="Authentication failed")

# ============= AUTHORIZATION FUNCTIONS =============

def get_token_from_header(authorization: str = Header(...)) -> str:
    """Extract and validate JWT token from Authorization header."""
    logger.debug("Extracting token from authorization header")
    try:
        return extract_token_from_header(authorization)
    except ValueError as e:
        logger.warning("Invalid authorization header", error=str(e))
        raise HTTPException(status_code=401, detail=str(e))

def get_current_user_payload(token: str = Depends(get_token_from_header)) -> dict:
    """Get current user payload from JWT token."""

    logger.debug("Decoding JWT token")
    try:
        payload = decode_token(token)
        if not payload.get("id"):
            logger.warning("Invalid token payload - missing user ID")
            raise HTTPException(status_code=401, detail="Invalid token payload")
        logger.debug("Token payload decoded successfully")
        return payload
    except ValueError as e:
        logger.warning("Token decoding failed", error=str(e))
        raise HTTPException(status_code=401, detail=str(e))

async def get_current_user(
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
) -> User:
    """Get the currently logged-in user from database."""
    
    try:
        user_id = payload.get("id")
        logger.debug("Fetching current user from database", user_id=user_id)
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.warning("Current user not found in database", user_id=user_id)
            raise HTTPException(status_code=401, detail="User not found")
        
        if not user.is_active:
            logger.warning("Current user is not active", user_id=user_id, email=user.email)
            raise HTTPException(status_code=403, detail="Account not activated")
        
        logger.debug("Current user retrieved successfully", user_id=user_id)
        return user
    except Exception as e:
        logger.error("Error getting current user", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current user ensuring they are active."""
    if not current_user.is_active:
        logger.warning("Inactive user access attempt", user_id=current_user.id)
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current user ensuring they have admin privileges."""
    if not current_user.is_admin:
        logger.warning("Non-admin user attempting admin access", user_id=current_user.id)
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

