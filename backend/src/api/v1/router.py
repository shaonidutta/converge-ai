"""
API v1 Router
Combines all v1 endpoints
"""

from fastapi import APIRouter

from src.api.v1.endpoints import auth, users

# Create v1 router
api_router = APIRouter(prefix="/v1")

# Include endpoint routers
api_router.include_router(auth.router)
api_router.include_router(users.router)

# Export
__all__ = ["api_router"]

