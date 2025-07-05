from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.oauth_service import google_login_callback, get_google_auth_url
from typing import Dict, Any
from app.config.OAuth import oauth
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
async def google_callback(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Handle Google OAuth callback"""
    try:
        result = await google_login_callback(request, db)
        
        return result
        
    except Exception as e:
        logger.error(f"Google OAuth callback error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/google/url")
async def get_google_login_url(request: Request) -> Dict[str, str]:
    """Get Google OAuth login URL for frontend"""
    try:
        url = str(request.url_for('google_login'))
        return {"login_url": url}
    except Exception as e:
        logger.error(f"Error getting Google login URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate login URL")