from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.oauth_service import google_login_callback, get_google_auth_url
from typing import Dict, Any
from app.config.OAuth import oauth
from app.config.urls import FRONTEND_URL
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/google/login")
async def google_login(request: Request):
    """Initiate Google OAuth login"""
    try:
        # Redirect to Google OAuth
        redirect_uri = request.url_for('google_callback')
        return await oauth.google.authorize_redirect(request, redirect_uri)
    except Exception as e:
        logger.error(f"Error initiating Google OAuth: {str(e)}")
        raise HTTPException(status_code=500, detail="OAuth initiation failed")

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback and redirect to frontend"""
    try:
        # Process OAuth and get JWT token
        result = await google_login_callback(request, db)
        
        # Extract token and user info
        logger.debug(f"Google OAuth result: {result}")
        access_token = result["access_token"]
        user_info = result.get("user", {})
        
        # Redirect to frontend with token
        frontend_url = FRONTEND_URL + "/oauth/callback"
        redirect_url = f"{frontend_url}?token={access_token}&email={user_info.get('email', '')}&auth_method={user_info.get('auth_method', 'oauth')}"
        
        logger.info(f"Redirecting OAuth user to frontend: {user_info}")
        return RedirectResponse(url=redirect_url, status_code=302)
        
    except Exception as e:
        logger.error(f"Google OAuth callback error: {str(e)}")
        # Redirect to login with error
        error_url = f"{FRONTEND_URL}/login?error=oauth_failed&message={str(e)}"
        return RedirectResponse(url=error_url, status_code=302)
    

@router.get("/google/url")
async def get_google_login_url(request: Request) -> Dict[str, str]:
    """Get Google OAuth login URL for frontend"""
    try:
        url = str(request.url_for('google_login'))
        return {"login_url": url}
    except Exception as e:
        logger.error(f"Error getting Google login URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate login URL")