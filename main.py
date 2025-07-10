from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from app.api.routes import router as api_router
from app.core.database import test_connection, init_db
from app.config.middleware import add_middlewares
from app.config.load import FRONTEND_URL_PROD as frontend_url,FRONTEND_URL_DEV as frontend_url_dev, BACKEND_URL as backend_url
from contextlib import asynccontextmanager
from app.utils.logging_utils import get_secure_logger
from app.config.urls_config import origins
# Setup secure logging
logger = get_secure_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up")
    try:
        # Test Supabase connection and check existing tables
        init_db()
        logger.info("Supabase connection and tables verified successfully")
        
    except Exception as e:
        logger.critical("Failed to connect to Supabase", error=str(e))
        raise
    yield
    logger.info("Application shutting down")

app = FastAPI(
    title="AI Docs Agent",
    description="Backend API for AI Assistant with Azure OpenAI and Supabase",
    version="1.0.0",
    lifespan=lifespan,
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS middleware configured", origins=origins)

# Add custom middlewares
add_middlewares(app)

# Include API routes
app.include_router(api_router)

if __name__ == "__main__":
    # Get port from environment (Render sets PORT automatically)
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)