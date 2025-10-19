"""
Health check endpoints for monitoring and load balancers

Provides three types of health checks:
1. /health - Basic health check (always returns 200)
2. /health/ready - Readiness check (checks all dependencies)
3. /health/live - Liveness check (checks if app is running)
"""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.core.database.connection import get_db
from src.rag.vector_store.pinecone_service import PineconeService
from src.core.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Basic health check
    
    Always returns 200 OK if the application is running.
    Used by load balancers for basic health monitoring.
    
    Returns:
        Status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "convergeai-backend"
    }


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Liveness check
    
    Checks if the application is alive and responsive.
    Used by Kubernetes for liveness probes.
    
    Returns 200 if app is running, otherwise container should be restarted.
    
    Returns:
        Status indicating app is alive
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness check
    
    Checks if the application is ready to serve traffic.
    Verifies all critical dependencies:
    - Database connectivity
    - Pinecone connectivity
    - Redis connectivity (optional)
    
    Used by Kubernetes for readiness probes.
    
    Returns:
        200 if all dependencies are healthy
        503 if any dependency is unhealthy
    """
    checks = {}
    all_healthy = True
    
    # Check database
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        checks["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
        logger.debug("Database health check: OK")
    except Exception as e:
        checks["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        all_healthy = False
        logger.error(f"Database health check failed: {e}")
    
    # Check Pinecone
    try:
        pinecone_service = PineconeService()
        health = pinecone_service.health_check()
        
        if health.get("status") == "healthy":
            checks["pinecone"] = {
                "status": "healthy",
                "message": "Pinecone connection successful",
                "index": health.get("index_name"),
                "dimension": health.get("dimension")
            }
            logger.debug("Pinecone health check: OK")
        else:
            checks["pinecone"] = {
                "status": "unhealthy",
                "message": "Pinecone connection failed"
            }
            all_healthy = False
            logger.error("Pinecone health check failed")
    except Exception as e:
        checks["pinecone"] = {
            "status": "unhealthy",
            "message": f"Pinecone connection failed: {str(e)}"
        }
        all_healthy = False
        logger.error(f"Pinecone health check failed: {e}")
    
    # Check Redis (optional - don't fail if Redis is down)
    try:
        import redis
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        checks["redis"] = {
            "status": "healthy",
            "message": "Redis connection successful"
        }
        logger.debug("Redis health check: OK")
    except Exception as e:
        checks["redis"] = {
            "status": "degraded",
            "message": f"Redis connection failed: {str(e)}"
        }
        # Don't mark as unhealthy - Redis is optional
        logger.warning(f"Redis health check failed: {e}")
    
    # Determine overall status
    overall_status = "healthy" if all_healthy else "unhealthy"
    status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    
    response_data = {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }
    
    return JSONResponse(
        status_code=status_code,
        content=response_data
    )

