"""
Request Timeout Middleware

Prevents requests from hanging indefinitely by enforcing timeout limits.
Different endpoints can have different timeout configurations.
"""

import asyncio
import logging
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class TimeoutMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce request timeouts
    
    Prevents endpoints from hanging indefinitely by setting
    appropriate timeout limits based on the endpoint type.
    """
    
    def __init__(self, app, default_timeout: int = 30):
        """
        Initialize timeout middleware
        
        Args:
            app: FastAPI application
            default_timeout: Default timeout in seconds
        """
        super().__init__(app)
        self.default_timeout = default_timeout
        
        # Configure timeouts per endpoint pattern
        self.endpoint_timeouts: Dict[str, int] = {
            # Read operations - shorter timeout
            "GET": 15,
            
            # Write operations - longer timeout
            "POST": 30,
            "PUT": 30,
            "PATCH": 30,
            "DELETE": 20,
            
            # Specific endpoint overrides
            "/api/v1/ops/dashboard/metrics": 45,  # Complex metrics queries
            "/api/v1/ops/complaints": 20,        # Complaint operations
            "/api/v1/ops/users": 25,             # User operations
        }
    
    def get_timeout_for_request(self, request: Request) -> int:
        """
        Get appropriate timeout for the request
        
        Args:
            request: FastAPI request object
            
        Returns:
            Timeout in seconds
        """
        # Check for specific endpoint override
        path = request.url.path
        if path in self.endpoint_timeouts:
            return self.endpoint_timeouts[path]
        
        # Check for method-based timeout
        method = request.method
        if method in self.endpoint_timeouts:
            return self.endpoint_timeouts[method]
        
        # Return default timeout
        return self.default_timeout
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request with timeout enforcement
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/endpoint in chain
            
        Returns:
            Response or timeout error
        """
        timeout = self.get_timeout_for_request(request)
        
        try:
            # Execute request with timeout
            response = await asyncio.wait_for(
                call_next(request),
                timeout=timeout
            )
            return response
            
        except asyncio.TimeoutError:
            # Log timeout for monitoring
            logger.warning(
                f"Request timeout: {request.method} {request.url.path} "
                f"(timeout: {timeout}s, client: {request.client.host if request.client else 'unknown'})"
            )
            
            # Return timeout error response
            return JSONResponse(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                content={
                    "error": "Request Timeout",
                    "message": f"Request took longer than {timeout} seconds to complete",
                    "timeout_seconds": timeout,
                    "endpoint": request.url.path,
                    "method": request.method
                }
            )
            
        except Exception as e:
            # Log unexpected errors
            logger.error(
                f"Unexpected error in timeout middleware: {e} "
                f"(endpoint: {request.method} {request.url.path})"
            )
            raise
