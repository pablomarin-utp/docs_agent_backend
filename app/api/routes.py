from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.conversations import router as chat_router
from app.api.oauth_routes import router as oauth_router 
from app.api.health import router as health_router  # Add health router

router = APIRouter()
router.include_router(health_router, tags=["Health"])  # Add health endpoints
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(oauth_router, prefix="/auth/oauth", tags=["OAuth"])
router.include_router(chat_router, tags=["Chat"])