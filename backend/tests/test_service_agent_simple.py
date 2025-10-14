"""
Simple test to verify ServiceAgent works
This is a quick smoke test before running full integration tests
"""

import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch

# Set environment variables before importing anything else
os.environ["DATABASE_URL"] = "mysql+aiomysql://test:test@localhost/test"
os.environ["JWT_SECRET_KEY"] = "test_secret_key_12345678901234567890"
os.environ["PINECONE_API_KEY"] = "test_pinecone_key"
os.environ["GOOGLE_API_KEY"] = "test_google_key"
os.environ["SECRET_KEY"] = "test_secret_key_12345678901234567890"

from src.agents.service.service_agent import ServiceAgent
from src.core.models import User


@pytest.mark.asyncio
async def test_service_agent_can_be_instantiated():
    """Test that ServiceAgent can be created"""
    # Mock database session
    db_mock = AsyncMock()
    
    # Create agent
    agent = ServiceAgent(db_mock)
    
    # Verify
    assert agent is not None
    assert agent.db == db_mock
    assert agent.category_service is not None
    
    print("\n✅ ServiceAgent instantiation test PASSED")


@pytest.mark.asyncio
async def test_service_agent_execute_unknown_action():
    """Test that ServiceAgent handles unknown actions gracefully"""
    # Mock database session
    db_mock = AsyncMock()
    
    # Create agent
    agent = ServiceAgent(db_mock)
    
    # Create mock user
    user = User(id=1, first_name="Test", last_name="User", mobile="9876543210")
    
    # Execute with unknown action
    result = await agent.execute(
        intent="service_inquiry",
        entities={"action": "unknown_action"},
        user=user,
        session_id="test_session"
    )
    
    # Verify
    assert result["action_taken"] == "unknown_action"
    assert "not sure how to help" in result["response"]
    
    print("\n✅ ServiceAgent unknown action test PASSED")


@pytest.mark.asyncio
async def test_service_agent_browse_categories_missing_data():
    """Test browse_categories when no categories exist"""
    # Mock database session
    db_mock = AsyncMock()
    
    # Create agent
    agent = ServiceAgent(db_mock)
    
    # Mock CategoryService to return empty list
    agent.category_service.list_categories = AsyncMock(return_value=[])
    
    # Create mock user
    user = User(id=1, first_name="Test", last_name="User", mobile="9876543210")
    
    # Execute
    result = await agent._browse_categories({}, user)
    
    # Verify
    assert result["action_taken"] == "no_categories"
    assert "No service categories" in result["response"]
    
    print("\n✅ ServiceAgent browse categories (no data) test PASSED")


@pytest.mark.asyncio
async def test_service_agent_search_missing_query():
    """Test search_services when query is missing"""
    # Mock database session
    db_mock = AsyncMock()
    
    # Create agent
    agent = ServiceAgent(db_mock)
    
    # Create mock user
    user = User(id=1, first_name="Test", last_name="User", mobile="9876543210")
    
    # Execute without query
    result = await agent._search_services({}, user)
    
    # Verify
    assert result["action_taken"] == "missing_entity"
    assert result["metadata"]["missing"] == "query"
    assert "What service are you looking for" in result["response"]
    
    print("\n✅ ServiceAgent search missing query test PASSED")


@pytest.mark.asyncio
async def test_service_agent_get_details_missing_id():
    """Test get_service_details when rate_card_id is missing"""
    # Mock database session
    db_mock = AsyncMock()
    
    # Create agent
    agent = ServiceAgent(db_mock)
    
    # Create mock user
    user = User(id=1, first_name="Test", last_name="User", mobile="9876543210")
    
    # Execute without rate_card_id
    result = await agent._get_service_details({}, user)
    
    # Verify
    assert result["action_taken"] == "missing_entity"
    assert result["metadata"]["missing"] == "rate_card_id"
    assert "Which service would you like to know more about" in result["response"]
    
    print("\n✅ ServiceAgent get details missing ID test PASSED")


@pytest.mark.asyncio
async def test_service_agent_recommend_missing_query():
    """Test recommend_services when query is missing"""
    # Mock database session
    db_mock = AsyncMock()
    
    # Create agent
    agent = ServiceAgent(db_mock)
    
    # Create mock user
    user = User(id=1, first_name="Test", last_name="User", mobile="9876543210")
    
    # Execute without query
    result = await agent._recommend_services({}, user)
    
    # Verify
    assert result["action_taken"] == "missing_entity"
    assert result["metadata"]["missing"] == "query"
    assert "What problem are you trying to solve" in result["response"]
    
    print("\n✅ ServiceAgent recommend missing query test PASSED")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])

