"""
Database connection management
Async SQLAlchemy engine and session factory
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool
from sqlalchemy import event, text
from typing import AsyncGenerator
import logging

from src.core.config import settings

logger = logging.getLogger(__name__)


# Create async engine
def create_engine():
    """
    Create async SQLAlchemy engine with connection pooling
    """
    # Convert mysql+pymysql to mysql+aiomysql for async
    database_url = settings.DATABASE_URL.replace("mysql+pymysql://", "mysql+aiomysql://")
    
    engine_kwargs = {
        "echo": settings.DB_ECHO,
        "pool_pre_ping": True,  # Enable connection health checks
        "pool_recycle": settings.DB_POOL_RECYCLE,
    }
    
    # Use connection pooling in production, NullPool in testing
    if settings.is_production or settings.is_staging:
        engine_kwargs.update({
            "poolclass": AsyncAdaptedQueuePool,
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
            "pool_timeout": settings.DB_POOL_TIMEOUT,
        })
    else:
        # Development: smaller pool
        engine_kwargs.update({
            "poolclass": AsyncAdaptedQueuePool,
            "pool_size": 5,
            "max_overflow": 5,
            "pool_timeout": 30,
        })
    
    engine = create_async_engine(database_url, **engine_kwargs)
    
    logger.info(f"Database engine created: {database_url.split('@')[1] if '@' in database_url else 'local'}")
    
    return engine


# Create engine instance
engine = create_engine()


# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to get database session

    Usage:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()

    Note: Services are responsible for their own transaction management.
    This dependency only provides the session and handles rollback on errors.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # Don't auto-commit - let services handle their own transactions
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def check_db_connection() -> bool:
    """
    Check if database connection is healthy
    
    Returns:
        bool: True if connection is healthy, False otherwise
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            logger.info("Database connection is healthy")
            return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


async def close_db_connection():
    """
    Close database connection pool
    Call this on application shutdown
    """
    await engine.dispose()
    logger.info("Database connection pool closed")


# Event listeners for connection management
@event.listens_for(engine.sync_engine, "connect")
def set_mysql_pragma(dbapi_conn, connection_record):
    """
    Set MySQL connection parameters on connect
    """
    cursor = dbapi_conn.cursor()
    # Set connection charset
    cursor.execute("SET NAMES utf8mb4")
    # Set timezone to UTC
    cursor.execute("SET time_zone = '+00:00'")
    cursor.close()


@event.listens_for(engine.sync_engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """
    Log when connection is checked out from pool
    """
    if settings.DEBUG:
        logger.debug("Connection checked out from pool")


@event.listens_for(engine.sync_engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """
    Log when connection is returned to pool
    """
    if settings.DEBUG:
        logger.debug("Connection returned to pool")


# Connection pool statistics
async def get_pool_stats() -> dict:
    """
    Get connection pool statistics
    
    Returns:
        dict: Pool statistics
    """
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total_connections": pool.size() + pool.overflow(),
    }


# Export
__all__ = [
    "engine",
    "AsyncSessionLocal",
    "get_db",
    "check_db_connection",
    "close_db_connection",
    "get_pool_stats",
]

