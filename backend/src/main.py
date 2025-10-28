"""
ConvergeAI Backend - Main Application Entry Point

This file initializes and configures the FastAPI app with:
- Secure middleware
- Rate limiting
- Structured logging
- Startup/shutdown hooks
- Router inclusion
- Central exception handling
- Health & metrics endpoints
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import uvicorn

# Load environment variables from .env file
from dotenv import load_dotenv

# Get the backend directory (parent of src)
backend_dir = Path(__file__).parent.parent
env_file = backend_dir / ".env"

# Load .env file if it exists
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
    print(f"[OK] Loaded environment variables from: {env_file}")
else:
    print(f"[WARNING] .env file not found at: {env_file}")

# =============================================
# Configuration
# =============================================
APP_NAME = "ConvergeAI Backend API"
VERSION = "1.0.0"
ENV = os.getenv("APP_ENV", "development")
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Customer frontend (React)
    "http://localhost:3001",  # Ops frontend
    "http://localhost:5173",  # Customer frontend (Vite dev server)
    "https://convergeAI.app",
]

# =============================================
# Rate Limiting
# =============================================
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],  # global default
    storage_uri="memory://",  # change to redis://<host>:6379 for production
)

# =============================================
# Logging Configuration
# =============================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(APP_NAME)

# =============================================
# Application Lifecycle Manager
# =============================================
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan: handles startup/shutdown hooks.
    """
    from src.core.database.connection import engine
    from src.core.cache.redis_client import redis_client

    logger.info(f"Starting {APP_NAME} (env={ENV})")

    # Test database connection
    try:
        from sqlalchemy import text
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"[ERROR] Database connection failed: {e}")

    # Test Redis connection
    try:
        await redis_client.ping()
        logger.info("[OK] Redis connection successful")
    except Exception as e:
        logger.warning(f"[WARNING] Redis connection failed: {e}")

    logger.info("All services initialized successfully")
    yield
    logger.info("Shutting down ConvergeAI backend...")

    # Close database connections
    await engine.dispose()
    logger.info("[OK] Database connections closed")

    # Close Redis connections (if method exists)
    try:
        if hasattr(redis_client, 'close'):
            await redis_client.close()
        logger.info("[OK] Redis connections closed")
    except Exception as e:
        logger.warning(f"Redis close warning: {e}")

    logger.info("Shutdown complete.")

# =============================================
# FastAPI Application Setup
# =============================================
app = FastAPI(
    title=APP_NAME,
    description="Multi-Agent Marketplace Backend powered by Gemini & RAG",
    version=VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# =============================================
# Security Middleware (CORS, Headers, Rate Limit)
# =============================================

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)

# --- Rate Limiting ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Security Headers Middleware ---
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# --- Prometheus Monitoring Middleware ---
from src.middleware.prometheus_middleware import PrometheusMiddleware
app.add_middleware(PrometheusMiddleware)

# =============================================
# Routers
# =============================================
from src.api.v1.router import api_router

app.include_router(api_router, prefix="/api")

# =============================================
# Health & Root Endpoints
# =============================================

@app.get("/health", tags=["Health"])
@limiter.limit("5/second")
async def health_check(request: Request):
    """
    Health Check Endpoint.
    Includes service component checks when available.
    """
    from src.core.database.connection import engine
    from src.core.cache.redis_client import redis_client

    # Check database
    db_status = "ok"
    try:
        from sqlalchemy import text
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    # Check Redis
    redis_status = "ok"
    try:
        await redis_client.ping()
    except Exception as e:
        redis_status = f"error: {str(e)}"

    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": APP_NAME,
            "version": VERSION,
            "components": {
                "api": "ok",
                "database": db_status,
                "redis": redis_status,
            },
        },
    )

@app.get("/", tags=["Root"])
@limiter.limit("2/second")
async def root(request: Request):
    """Root endpoint"""
    return {
        "message": f"Welcome to {APP_NAME}",
        "version": VERSION,
        "docs": "/docs",
        "health": "/health",
    }

# =============================================
# Error & Exception Handling
# =============================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all error handler"""
    logger.exception(f"Unhandled Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "path": str(request.url),
        },
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Access log for every request"""
    logger.info(f"Request: {request.method} {request.url.path} from {request.client.host}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code} {request.url.path}")
    return response

# =============================================
# Metrics Endpoint (Prometheus)
# =============================================
# from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
# @app.get("/metrics", tags=["Monitoring"])
# async def metrics():
#     return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# =============================================
# Entry Point
# =============================================
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=ENV == "development",
        log_level="info",
    )
