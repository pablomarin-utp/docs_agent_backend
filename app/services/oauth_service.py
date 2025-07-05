
from app.config.OAuth import oauth
from app.core.models import User
from app.services.jwt_service import create_access_token
from sqlalchemy.orm import Session
from fastapi import HTTPException, Request
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

async def google_login_callback(request: Request, db: Session) -> Dict[str, Any]:
    """Handle Google OAuth callback and create/login user"""
    try:
        # Get the access token from Google
        token = await oauth.google.authorize_access_token(request)
        
        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            user_info = await oauth.google.parse_id_token(request, token)
        
        email = user_info.get('email')
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")
        
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
            logger.info(f"New Google OAuth user created: {email}")
        else:
            # If existing user, activate if not active
            if not user.is_active:
                user.is_active = True
                db.commit()
        
        # Generate JWT token (same as normal login)
        access_token = create_access_token(data={
            "email": user.email,
            "id": str(user.id),
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "auth_method": "oauth"
        })
        
        logger.info(f"Google OAuth user authenticated: {email}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "is_active": user.is_active,
                "auth_method": "oauth"
            }
        }
        
    except Exception as e:
        logger.error(f"Google OAuth error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"OAuth authentication failed: {str(e)}")
    
async def get_google_auth_url(request: Request) -> str:
    """Get Google OAuth authorization URL"""
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)