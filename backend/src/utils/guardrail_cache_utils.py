"""
Caching utilities for guardrail results.

This module provides Redis-based caching for guardrail results to improve
performance by avoiding redundant checks on identical inputs.
"""

import hashlib
import json
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

# Redis client will be initialized from the main app
_redis_client = None


def init_redis_client(redis_client):
    """
    Initialize the Redis client for caching.
    
    Args:
        redis_client: Redis client instance
    """
    global _redis_client
    _redis_client = redis_client
    logger.info("Guardrail cache Redis client initialized")


def get_cache_key(guardrail_name: str, text: str, context: dict = None) -> str:
    """
    Generate a cache key for a guardrail check.
    
    Args:
        guardrail_name: Name of the guardrail
        text: Text being checked
        context: Additional context (optional)
    
    Returns:
        Cache key string
    """
    # Create a unique key based on guardrail name, text, and relevant context
    key_parts = [guardrail_name, text]
    
    # Add relevant context fields (exclude user_id for privacy)
    if context:
        # Only include context fields that affect the check result
        relevant_fields = ['check_type']  # Add more fields as needed
        for field in relevant_fields:
            if field in context:
                key_parts.append(f"{field}:{context[field]}")
    
    # Create hash of the key parts
    key_string = "|".join(key_parts)
    key_hash = hashlib.sha256(key_string.encode()).hexdigest()
    
    return f"guardrail:{guardrail_name}:{key_hash}"


async def get_cached_result(
    guardrail_name: str,
    text: str,
    context: dict = None
) -> Optional[dict]:
    """
    Get cached guardrail result.
    
    Args:
        guardrail_name: Name of the guardrail
        text: Text being checked
        context: Additional context
    
    Returns:
        Cached result dictionary or None if not found
    """
    if _redis_client is None:
        return None
    
    try:
        cache_key = get_cache_key(guardrail_name, text, context)
        cached_data = await _redis_client.get(cache_key)
        
        if cached_data:
            logger.debug(f"Cache hit for {guardrail_name}")
            return json.loads(cached_data)
        
        logger.debug(f"Cache miss for {guardrail_name}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting cached result: {str(e)}")
        return None


async def set_cached_result(
    guardrail_name: str,
    text: str,
    result: dict,
    ttl: int = 3600,
    context: dict = None
):
    """
    Cache a guardrail result.
    
    Args:
        guardrail_name: Name of the guardrail
        text: Text that was checked
        result: Result dictionary to cache
        ttl: Time to live in seconds (default: 1 hour)
        context: Additional context
    """
    if _redis_client is None:
        return
    
    try:
        cache_key = get_cache_key(guardrail_name, text, context)
        cached_data = json.dumps(result)
        
        await _redis_client.setex(cache_key, ttl, cached_data)
        logger.debug(f"Cached result for {guardrail_name} (TTL: {ttl}s)")
        
    except Exception as e:
        logger.error(f"Error caching result: {str(e)}")


async def invalidate_cache(guardrail_name: str = None):
    """
    Invalidate cached results.
    
    Args:
        guardrail_name: Name of guardrail to invalidate (None = all guardrails)
    """
    if _redis_client is None:
        return
    
    try:
        if guardrail_name:
            # Invalidate specific guardrail
            pattern = f"guardrail:{guardrail_name}:*"
        else:
            # Invalidate all guardrails
            pattern = "guardrail:*"
        
        # Find and delete matching keys
        cursor = 0
        deleted_count = 0
        
        while True:
            cursor, keys = await _redis_client.scan(cursor, match=pattern, count=100)
            if keys:
                await _redis_client.delete(*keys)
                deleted_count += len(keys)
            
            if cursor == 0:
                break
        
        logger.info(f"Invalidated {deleted_count} cached results for pattern: {pattern}")
        
    except Exception as e:
        logger.error(f"Error invalidating cache: {str(e)}")


async def get_cache_stats() -> dict:
    """
    Get cache statistics.
    
    Returns:
        Dictionary with cache statistics
    """
    if _redis_client is None:
        return {"error": "Redis client not initialized"}
    
    try:
        # Count total guardrail cache keys
        cursor = 0
        total_keys = 0
        
        while True:
            cursor, keys = await _redis_client.scan(cursor, match="guardrail:*", count=100)
            total_keys += len(keys)
            
            if cursor == 0:
                break
        
        return {
            "total_cached_results": total_keys,
            "redis_connected": True
        }
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        return {"error": str(e), "redis_connected": False}

