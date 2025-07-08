from app.config.OAuth import oauth
from app.core.models import User
from app.services.jwt_service import create_access_token
from sqlalchemy.orm import Session
from fastapi import HTTPException, Request
from typing import Dict, Any
from app.utils.logging_utils import get_secure_logger

logger = get_secure_logger(__name__)

async def google_login_callback(request: Request, db: Session) -> dict:
    """Handle Google OAuth callback and create/login user"""
    logger.info("Processing Google OAuth callback")
    
    try:
        # Get the access token from Google
        token = await oauth.google.authorize_access_token(request)
        logger.debug("Google token received successfully")
        
        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            logger.debug("Parsing ID token for user info")
            user_info = await oauth.google.parse_id_token(request, token)
        
        email = user_info.get('email')
        
        if not email:
            logger.error("Google OAuth user did not provide email")
            raise HTTPException(status_code=400, detail="Email not provided by Google")
        
        logger.debug("OAuth user email retrieved", email=email)
        
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Create new user - OAuth users get empty password and auto-activation
            user = User(
                email=email,
                hashed_password="",  # Empty for OAuth identification
                is_active=True,      # Auto-activate OAuth users
                credits=10           # Give initial credits
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info("New Google OAuth user created", user_id=user.id, email=email)
        else:
            # If existing user, activate if not active
            if not user.is_active:
                user.is_active = True
                db.commit()
                logger.info("Existing OAuth user activated", user_id=user.id, email=email)
        
        # Generate JWT token (same as normal login)
        access_token = create_access_token(data={
            "email": user.email,
            "id": str(user.id),
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "auth_method": "oauth"
        })
        
        logger.info("Google OAuth user authenticated successfully", user_id=user.id, email=email)
        return {
            "access_token": access_token, 
            "token_type": "bearer", 
            "user": {"email": user.email, "auth_method": "oauth"}
        }

    except Exception as e:
        logger.error("Google OAuth authentication failed", error=str(e))
        raise HTTPException(status_code=400, detail=f"OAuth authentication failed: {str(e)}")
    
async def get_google_auth_url(request: Request) -> str:
    """Get Google OAuth authorization URL"""
    logger.debug("Generating Google OAuth authorization URL")
    
    try:
        redirect_uri = request.url_for('google_callback')
        auth_url = await oauth.google.authorize_redirect(request, redirect_uri)
        logger.debug("Google OAuth URL generated successfully")
        return auth_url
    except Exception as e:
        logger.error("Error generating Google OAuth URL", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate OAuth URL")