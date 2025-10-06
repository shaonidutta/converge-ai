# Database base configuration and session management

from datetime import datetime
from typing import Any
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import Column, BigInteger, DateTime

# Base class for all models
Base = declarative_base()


class TimestampMixin:
    """
    Mixin to add created_at and updated_at timestamps to models
    """
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# Database engine and session will be initialized in config
engine = None
async_engine = None
SessionLocal = None
AsyncSessionLocal = None


def init_db(database_url: str, async_database_url: str = None):
    """
    Initialize database engines and session makers
    
    Args:
        database_url: Synchronous database URL
        async_database_url: Asynchronous database URL (optional)
    """
    global engine, async_engine, SessionLocal, AsyncSessionLocal
    
    # Synchronous engine
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Async engine (if provided)
    if async_database_url:
        async_engine = create_async_engine(
            async_database_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            echo=False
        )
        AsyncSessionLocal = async_sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )


def get_db() -> Session:
    """
    Dependency for getting database session (synchronous)
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncSession:
    """
    Dependency for getting database session (asynchronous)
    
    Yields:
        AsyncSession: Async database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def create_all_tables():
    """
    Create all tables in the database
    """
    Base.metadata.create_all(bind=engine)


def drop_all_tables():
    """
    Drop all tables in the database (use with caution!)
    """
    Base.metadata.drop_all(bind=engine)

