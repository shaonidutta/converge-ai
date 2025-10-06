"""
ConvergeAI Backend - Main Application Entry Point

This module initializes and configures the FastAPI application with all
necessary middleware, routers, and startup/shutdown events.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import configuration (will be created in Phase 3)
# from src.config.settings import get_settings

# Import routers (will be created in later phases)
# from src.api.v1.endpoints import auth, users, chat, bookings, complaints

# Import middleware (will be created in later phases)
# from src.api.middleware.logging import LoggingMiddleware
# from src.api.middleware.rate_limit import RateLimitMiddleware

# Import monitoring (will be created in later phases)
# from src.monitoring.metrics import setup_metrics
# from src.monitoring.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the application.
    """
    # Startup
    print("Starting ConvergeAI Backend...")

    # Initialize database connection
    # await init_database()

    # Initialize Redis connection
    # await init_redis()

    # Initialize Pinecone
    # await init_pinecone()

    # Load ML models
    # await load_ml_models()

    # Setup monitoring
    # setup_logging()
    # setup_metrics()

    print("ConvergeAI Backend started successfully!")

    yield

    # Shutdown
    print("Shutting down ConvergeAI Backend...")

    # Close database connections
    # await close_database()

    # Close Redis connections
    # await close_redis()

    print("ConvergeAI Backend shut down successfully!")


# Create FastAPI application
app = FastAPI(
    title="ConvergeAI Backend API",
    description="Multi-Agent Customer Service Platform powered by LangChain, LangGraph, and Google Gemini",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ============================================
# CORS Middleware
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Customer frontend
        "http://localhost:3001",  # Ops frontend
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Custom Middleware (will be added in later phases)
# ============================================
# app.add_middleware(LoggingMiddleware)
# app.add_middleware(RateLimitMiddleware)


# ============================================
# Health Check Endpoint
# ============================================
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns the health status of the application and its dependencies.
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "ConvergeAI Backend",
            "version": "1.0.0",
            "components": {
                "api": "healthy",
                # "database": "healthy",  # Will be implemented in Phase 2
                # "redis": "healthy",     # Will be implemented in Phase 3
                # "pinecone": "healthy",  # Will be implemented in Phase 7
            }
        }
    )


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint.
    
    Returns basic information about the API.
    """
    return {
        "message": "Welcome to ConvergeAI Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


# ============================================
# API Routers (will be added in later phases)
# ============================================
# API v1 routes
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
# app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
# app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
# app.include_router(bookings.router, prefix="/api/v1/bookings", tags=["Bookings"])
# app.include_router(complaints.router, prefix="/api/v1/complaints", tags=["Complaints"])


# ============================================
# Exception Handlers
# ============================================
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler.
    
    Catches all unhandled exceptions and returns a standardized error response.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "path": str(request.url),
        }
    )


# ============================================
# Metrics Endpoint (Prometheus)
# ============================================
# @app.get("/metrics", tags=["Monitoring"])
# async def metrics():
#     """
#     Prometheus metrics endpoint.
#     """
#     return Response(
#         content=generate_latest(),
#         media_type="text/plain"
#     )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

