"""
Core Services Module

Provides singleton instances of heavy services that should be reused across requests.
"""

import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Global cache for CoordinatorAgent (singleton per application instance)
_coordinator_agent_cache: Optional[object] = None


async def get_coordinator_agent(db: AsyncSession):
    """
    Get or create CoordinatorAgent instance (singleton pattern)

    The CoordinatorAgent is expensive to initialize (loads LLM clients, etc.)
    so we cache it at the application level and reuse it across requests.

    Note: The agent uses lazy initialization for sub-agents, so they're only
    created when actually needed.

    Args:
        db: Database session (passed to agent for operations)

    Returns:
        CoordinatorAgent instance
    """
    global _coordinator_agent_cache

    if _coordinator_agent_cache is None:
        logger.info("[ServiceCache] Initializing CoordinatorAgent (first time)")
        from src.agents.coordinator.coordinator_agent import CoordinatorAgent
        _coordinator_agent_cache = CoordinatorAgent(db=db)
        logger.info("[ServiceCache] CoordinatorAgent cached successfully")

    # Update the db session for this request
    _coordinator_agent_cache.db = db

    return _coordinator_agent_cache


def clear_coordinator_cache():
    """Clear the coordinator agent cache (useful for testing or reloading)"""
    global _coordinator_agent_cache
    _coordinator_agent_cache = None
    logger.info("[ServiceCache] CoordinatorAgent cache cleared")
