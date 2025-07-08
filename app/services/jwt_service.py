from datetime import datetime, timedelta, timezone
from jose import jwt
from jose.exceptions import JWTError
from typing import Dict, Optional
from app.config.jwt_config import jwt_secret_key, jwt_algorithm
from app.utils.logging_utils import get_secure_logger

logger = get_secure_logger(__name__)

ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with optional expiration time."""
    logger.debug("Creating access token", user_id=data.get("id"), email=data.get("email"))
    
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    
    try:
        token = jwt.encode(to_encode, jwt_secret_key, algorithm=jwt_algorithm)
        logger.debug("Access token created successfully", expires_at=expire.isoformat())
        return token
    except Exception as e:
        logger.error("Token creation failed", error=str(e))
        raise ValueError(f"Token creation failed: {str(e)}")

def decode_token(token: str) -> Dict:
    """Decode and validate a JWT token."""
    logger.debug("Decoding JWT token", token_preview=token[:10] + "...")
    
    try:
        payload = jwt.decode(token, jwt_secret_key, algorithms=[jwt_algorithm])
        logger.debug("Token decoded successfully", user_id=payload.get("id"))
        return payload
    except JWTError as e:
        logger.warning("Token decoding failed", error=str(e), token_preview=token[:10] + "...")
        raise ValueError(f"Invalid token: {str(e)}")

def verify_token(token: str) -> bool:
    """Verify if a token is valid without decoding."""
    logger.debug("Verifying token validity", token_preview=token[:10] + "...")
    
    try:
        jwt.decode(token, jwt_secret_key, algorithms=[jwt_algorithm])
        logger.debug("Token verification successful")
        return True
    except JWTError as e:
        logger.debug("Token verification failed", error=str(e))
        return False

def extract_token_from_header(header: str) -> str:
    """Extract token from Authorization header string."""
    logger.debug("Extracting token from authorization header")
    
    if not header or not header.startswith("Bearer "):
        logger.warning("Invalid authorization header format")
        raise ValueError("Invalid authorization header format")
    
    token = header.replace("Bearer ", "").strip()

    if not token:
        logger.warning("Empty token after extraction")
        raise ValueError("Token is empty after stripping")

    logger.debug("Token extracted successfully", token_preview=token[:10] + "...")
    return token
