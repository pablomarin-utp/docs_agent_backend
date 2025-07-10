from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text  # ← AGREGAR IMPORT
from app.core.database import get_db
from app.config.qdrant import qdrant_client
from typing import Dict, Any
from app.utils.logging_utils import get_secure_logger

logger = get_secure_logger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Health check endpoint for monitoring application status.
    
    Returns:
        Dictionary with health status of all components
    """
    logger.debug("Performing health check")
    
    health_status = {
        "status": "healthy",
        "components": {}
    }
    
    # Check database connection
    try:
        db.execute(text("SELECT 1"))  # ← USAR text()
        health_status["components"]["database"] = "healthy"
        logger.debug("Database health check passed")
    except Exception as e:
        health_status["components"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
        logger.error("Database health check failed", error=str(e))
    
    # Check Qdrant connection
    try:
        qdrant_client.get_collections()
        health_status["components"]["qdrant"] = "healthy"
        logger.debug("Qdrant health check passed")
    except Exception as e:
        health_status["components"]["qdrant"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
        logger.error("Qdrant health check failed", error=str(e))
    
    logger.info("Health check completed", status=health_status["status"])
    return health_status