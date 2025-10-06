"""
API v1 Router
Combines all v1 routes
"""

from fastapi import APIRouter

from src.api.v1.routes import auth, users, ops, categories, cart, bookings, addresses

# Create v1 router
api_router = APIRouter(prefix="/v1")

# Include route routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(ops.router)
api_router.include_router(categories.router)
api_router.include_router(cart.router)
api_router.include_router(bookings.router)
api_router.include_router(addresses.router)

# Export
__all__ = ["api_router"]

