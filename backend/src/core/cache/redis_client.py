"""
Redis client for caching and session management
"""

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
from typing import Optional, Any, Union
import json
import pickle
import logging
from functools import wraps

from backend.src.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Async Redis client wrapper with connection pooling
    """
    
    def __init__(self):
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[redis.Redis] = None
    
    async def connect(self):
        """
        Initialize Redis connection pool
        """
        try:
            self.pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=settings.REDIS_POOL_SIZE,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
                decode_responses=False,  # We'll handle encoding/decoding
            )
            
            self.client = redis.Redis(connection_pool=self.pool)
            
            # Test connection
            await self.client.ping()
            logger.info(f"Redis connected: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise
    
    async def disconnect(self):
        """
        Close Redis connection pool
        """
        if self.client:
            await self.client.close()
        if self.pool:
            await self.pool.disconnect()
        logger.info("Redis connection closed")
    
    async def ping(self) -> bool:
        """
        Check if Redis is connected
        
        Returns:
            bool: True if connected, False otherwise
        """
        try:
            return await self.client.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False
    
    async def get(self, key: str, default: Any = None) -> Optional[Any]:
        """
        Get value from Redis
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        try:
            value = await self.client.get(key)
            if value is None:
                return default
            
            # Try to deserialize
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # If JSON fails, try pickle
                try:
                    return pickle.loads(value)
                except:
                    # Return as string
                    return value.decode('utf-8') if isinstance(value, bytes) else value
        
        except Exception as e:
            logger.error(f"Redis GET error for key '{key}': {e}")
            return default
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """
        Set value in Redis
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            nx: Only set if key doesn't exist
            xx: Only set if key exists
            
        Returns:
            bool: True if successful
        """
        try:
            # Serialize value
            if isinstance(value, (dict, list, tuple)):
                serialized = json.dumps(value)
            elif isinstance(value, (str, int, float, bool)):
                serialized = json.dumps(value)
            else:
                # Use pickle for complex objects
                serialized = pickle.dumps(value)
            
            # Set with options
            result = await self.client.set(
                key,
                serialized,
                ex=ttl,
                nx=nx,
                xx=xx
            )
            
            return bool(result)
        
        except Exception as e:
            logger.error(f"Redis SET error for key '{key}': {e}")
            return False
    
    async def delete(self, *keys: str) -> int:
        """
        Delete one or more keys
        
        Args:
            *keys: Keys to delete
            
        Returns:
            int: Number of keys deleted
        """
        try:
            return await self.client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return 0
    
    async def exists(self, *keys: str) -> int:
        """
        Check if keys exist
        
        Args:
            *keys: Keys to check
            
        Returns:
            int: Number of keys that exist
        """
        try:
            return await self.client.exists(*keys)
        except Exception as e:
            logger.error(f"Redis EXISTS error: {e}")
            return 0
    
    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration time for a key
        
        Args:
            key: Cache key
            seconds: Expiration time in seconds
            
        Returns:
            bool: True if successful
        """
        try:
            return await self.client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key '{key}': {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """
        Get time to live for a key
        
        Args:
            key: Cache key
            
        Returns:
            int: TTL in seconds, -1 if no expiry, -2 if key doesn't exist
        """
        try:
            return await self.client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL error for key '{key}': {e}")
            return -2
    
    async def incr(self, key: str, amount: int = 1) -> int:
        """
        Increment value
        
        Args:
            key: Cache key
            amount: Amount to increment
            
        Returns:
            int: New value
        """
        try:
            return await self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis INCR error for key '{key}': {e}")
            return 0
    
    async def decr(self, key: str, amount: int = 1) -> int:
        """
        Decrement value
        
        Args:
            key: Cache key
            amount: Amount to decrement
            
        Returns:
            int: New value
        """
        try:
            return await self.client.decrby(key, amount)
        except Exception as e:
            logger.error(f"Redis DECR error for key '{key}': {e}")
            return 0
    
    async def keys(self, pattern: str = "*") -> list:
        """
        Get keys matching pattern
        
        Args:
            pattern: Key pattern (e.g., "user:*")
            
        Returns:
            list: List of matching keys
        """
        try:
            keys = await self.client.keys(pattern)
            return [k.decode('utf-8') if isinstance(k, bytes) else k for k in keys]
        except Exception as e:
            logger.error(f"Redis KEYS error for pattern '{pattern}': {e}")
            return []
    
    async def flushdb(self):
        """
        Clear all keys in current database
        WARNING: Use with caution!
        """
        try:
            await self.client.flushdb()
            logger.warning("Redis database flushed")
        except Exception as e:
            logger.error(f"Redis FLUSHDB error: {e}")


# Create global Redis client instance
redis_client = RedisClient()


# Dependency for FastAPI
async def get_redis() -> RedisClient:
    """
    Dependency to get Redis client
    
    Usage:
        @app.get("/cached")
        async def get_cached(redis: RedisClient = Depends(get_redis)):
            value = await redis.get("my_key")
            return {"value": value}
    """
    return redis_client


# Cache decorator
def cache(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorator to cache function results in Redis
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
        
    Usage:
        @cache(ttl=300, key_prefix="user")
        async def get_user(user_id: int):
            # Expensive operation
            return user_data
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix or func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached = await redis_client.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached
            
            # Cache miss - execute function
            logger.debug(f"Cache MISS: {cache_key}")
            result = await func(*args, **kwargs)
            
            # Store in cache
            await redis_client.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator


# Export
__all__ = [
    "RedisClient",
    "redis_client",
    "get_redis",
    "cache",
]

