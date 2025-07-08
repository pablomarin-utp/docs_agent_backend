from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api.routes import router as api_router
from app.core.database import test_connection
from app.config.middleware import add_middlewares
from contextlib import asynccontextmanager
from app.utils.logging_utils import get_secure_logger

# Setup secure logging
logger = get_secure_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up")
    try:
        test_connection()
        logger.info("Database connection established successfully")
    except Exception as e:
        logger.critical("Failed to establish database connection", error=str(e))
        raise
    yield
    logger.info("Application shutting down")

app = FastAPI(
    title="AI Docs Agent",
    description="Backend API for AI Assistant",
    version="1.0.0",
    lifespan=lifespan,
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174"
]

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
logger.info("Custom middlewares added")

app.include_router(api_router)
logger.info("API router included")

if __name__ == "__main__":
    logger.info("Starting application server", host="127.0.0.1", port=8001)
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)