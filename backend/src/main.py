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

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import uvicorn

# =============================================
# Configuration
# =============================================
APP_NAME = "ConvergeAI Backend API"
VERSION = "1.0.0"
ENV = os.getenv("APP_ENV", "development")
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Customer frontend
    "http://localhost:3001",  # Ops frontend
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
    logger.info(f"Starting {APP_NAME} (env={ENV})")

    # Initialize connections
    # await init_database()
    # await init_redis()
    # await init_pinecone()
    # await load_ml_models()

    logger.info("All services initialized successfully")
    yield
    logger.info("Shutting down ConvergeAI backend...")
    # await close_database()
    # await close_redis()
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

# =============================================
# Routers (to be imported later)
# =============================================
# from src.api.v1 import auth, users, chat, bookings, complaints
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
# app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
# app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
# app.include_router(bookings.router, prefix="/api/v1/bookings", tags=["Bookings"])
# app.include_router(complaints.router, prefix="/api/v1/complaints", tags=["Complaints"])

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
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": APP_NAME,
            "version": VERSION,
            "components": {
                "api": "ok",
                # "database": "ok",
                # "redis": "ok",
                # "pinecone": "ok",
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
