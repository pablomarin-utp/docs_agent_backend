from datetime import datetime, timedelta, timezone
from jose import jwt
from jose.exceptions import JWTError
from typing import Dict, Optional
from app.config.jwt_config import jwt_secret_key, jwt_algorithm
import logging

logger = logging.getLogger(__name__)

ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with optional expiration time."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, jwt_secret_key, algorithm=jwt_algorithm)
    return token

def decode_token(token: str) -> Dict:
    """Decode and validate a JWT token."""
    logger.debug(f"Decoding token")  # Log only the first 10 characters for security
    try:
        logger.debug(f"Token to decode: {token[:10]}..., length: {len(token)}, secret key length: {len(jwt_secret_key)}")
        payload = jwt.decode(token, jwt_secret_key, algorithms=[jwt_algorithm])
        logger.debug(f"Token decoded succesfully")
        return payload
    except JWTError as e:
        logger.error(f"Token decoding failed: {str(e)}")
        raise ValueError(f"Invalid token: {str(e)}")

def verify_token(token: str) -> bool:
    """Verify if a token is valid without decoding."""
    try:
        jwt.decode(token, jwt_secret_key, algorithms=[jwt_algorithm])
        return True
    except JWTError:
        return False

def extract_token_from_header(header: str) -> str:
    """Extract token from Authorization header string."""
    logger.debug(f"Extracting token from Authorization header: {header}")
    
    if not header or not header.startswith("Bearer "):
        raise ValueError("Invalid authorization header format")
    
    token = header.replace("Bearer ", "").strip()

    if not token:
        raise ValueError("Token is empty after stripping")

    logger.debug("Token extracted successfully")
    return token
