"""
Prometheus middleware for FastAPI

Automatically tracks HTTP request metrics:
- Request count by method, endpoint, status code
- Request duration by method, endpoint
- Requests in progress by method, endpoint
"""
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.monitoring.metrics.prometheus_metrics import (
    http_requests_total,
    http_request_duration_seconds,
    http_requests_in_progress,
)

logger = logging.getLogger(__name__)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track HTTP request metrics
    
    Tracks:
    - Total requests (counter)
    - Request duration (histogram)
    - Requests in progress (gauge)
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        logger.info("PrometheusMiddleware initialized")
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and track metrics
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response with metrics tracked
        """
        # Get method and path
        method = request.method
        path = request.url.path
        
        # Normalize path (remove IDs, UUIDs, etc.)
        normalized_path = self._normalize_path(path)
        
        # Track request in progress
        http_requests_in_progress.labels(method=method, endpoint=normalized_path).inc()
        
        # Start timer
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Get status code
            status_code = response.status_code
            
            # Track request completion
            duration = time.time() - start_time
            
            # Record metrics
            http_requests_total.labels(
                method=method,
                endpoint=normalized_path,
                status_code=status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=normalized_path
            ).observe(duration)
            
            return response
        
        except Exception as e:
            # Track error
            duration = time.time() - start_time
            
            http_requests_total.labels(
                method=method,
                endpoint=normalized_path,
                status_code=500
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=normalized_path
            ).observe(duration)
            
            logger.error(f"Error processing request: {e}")
            raise
        
        finally:
            # Decrement in-progress counter
            http_requests_in_progress.labels(method=method, endpoint=normalized_path).dec()
    
    def _normalize_path(self, path: str) -> str:
        """
        Normalize path by removing IDs, UUIDs, etc.
        
        Examples:
        - /api/v1/users/123 -> /api/v1/users/{id}
        - /api/v1/bookings/abc-123-def -> /api/v1/bookings/{id}
        
        Args:
            path: Original path
            
        Returns:
            Normalized path
        """
        # Skip metrics endpoint
        if path == "/metrics":
            return path
        
        # Skip health endpoints
        if path in ["/health", "/health/ready", "/health/live"]:
            return path
        
        # Split path into parts
        parts = path.split("/")
        normalized_parts = []
        
        for part in parts:
            # Skip empty parts
            if not part:
                normalized_parts.append(part)
                continue
            
            # Check if part looks like an ID
            if self._is_id(part):
                normalized_parts.append("{id}")
            else:
                normalized_parts.append(part)
        
        return "/".join(normalized_parts)
    
    def _is_id(self, part: str) -> bool:
        """
        Check if path part looks like an ID
        
        Args:
            part: Path part
            
        Returns:
            True if looks like ID, False otherwise
        """
        # Check if numeric (e.g., 123, 456)
        if part.isdigit():
            return True
        
        # Check if UUID-like (contains hyphens and alphanumeric)
        if "-" in part and len(part) > 10:
            return True
        
        # Check if looks like hash (long alphanumeric)
        if len(part) > 20 and part.isalnum():
            return True
        
        return False

