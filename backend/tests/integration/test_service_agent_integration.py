"""
Integration test for ServiceAgent - Tests actual database operations
"""

import pytest
import asyncio
from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, delete
import os
from dotenv import load_dotenv

from backend.src.agents.service.service_agent import ServiceAgent
from backend.src.core.models import (
    User, Category, Subcategory, RateCard, Provider, Pincode
)
from backend.src.core.database.base import Base

# Load environment variables
load_dotenv()

# Test database URL
TEST_DB_URL = os.getenv("DATABASE_URL")


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Create test database engine"""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
async def async_session_maker(engine):
    """Create async session maker"""
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def db_session(async_session_maker):
    """Create database session for each test"""
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def test_data(db_session):
    """Create test data for integration tests"""
    
    # Create user
    user = User(
        first_name="Test",
        last_name="User",
        mobile="9876543210",
        email="test@example.com",
        password_hash="hashed_password"
    )
    db_session.add(user)
    await db_session.flush()
    
    # Create provider
    provider = Provider(
        first_name="Test",
        last_name="Provider",
        mobile="9876543211",
        email="provider@example.com",
        is_active=True,
        is_verified=True
    )
    db_session.add(provider)
    await db_session.flush()
    
    # Create category
    category = Category(
        name="Test AC Services",
        slug="test-ac-services",
        description="Test AC services category",
        is_active=True,
        display_order=1
    )
    db_session.add(category)
    await db_session.flush()
    
    # Create subcategory
    subcategory = Subcategory(
        name="Test AC Repair",
        slug="test-ac-repair",
        description="Test AC repair subcategory",
        category_id=category.id,
        is_active=True,
        display_order=1
    )
    db_session.add(subcategory)
    await db_session.flush()
    
    # Create rate cards
    rate_card_1 = RateCard(
        name="Test Basic AC Repair",
        description="Basic AC repair service for testing",
        price=Decimal("1500.00"),
        strike_price=Decimal("2000.00"),
        category_id=category.id,
        subcategory_id=subcategory.id,
        provider_id=provider.id,
        is_active=True
    )
    db_session.add(rate_card_1)
    
    rate_card_2 = RateCard(
        name="Test Deep AC Cleaning",
        description="Deep cleaning service for AC units",
        price=Decimal("2500.00"),
        category_id=category.id,
        subcategory_id=subcategory.id,
        provider_id=provider.id,
        is_active=True
    )
    db_session.add(rate_card_2)
    
    await db_session.commit()
    
    return {
        "user": user,
        "provider": provider,
        "category": category,
        "subcategory": subcategory,
        "rate_card_1": rate_card_1,
        "rate_card_2": rate_card_2
    }


@pytest.mark.asyncio
async def test_service_agent_browse_categories(db_session, test_data):
    """Integration test: Browse categories"""
    
    # Create ServiceAgent
    agent = ServiceAgent(db_session)
    
    # Execute browse categories
    result = await agent._browse_categories({}, test_data["user"])
    
    # Verify response
    assert result["action_taken"] == "categories_listed"
    assert "Test AC Services" in result["response"]
    assert len(result["metadata"]["categories"]) > 0
    
    # Find our test category
    test_cat = next((c for c in result["metadata"]["categories"] if c["name"] == "Test AC Services"), None)
    assert test_cat is not None
    assert test_cat["id"] == test_data["category"].id
    
    print("\n✅ Browse Categories Integration Test PASSED")
    print(f"   Found {len(result['metadata']['categories'])} categories")


@pytest.mark.asyncio
async def test_service_agent_browse_subcategories(db_session, test_data):
    """Integration test: Browse subcategories"""
    
    # Create ServiceAgent
    agent = ServiceAgent(db_session)
    
    # Execute browse subcategories
    entities = {"category_id": test_data["category"].id}
    result = await agent._browse_subcategories(entities, test_data["user"])
    
    # Verify response
    assert result["action_taken"] == "subcategories_listed"
    assert "Test AC Repair" in result["response"]
    assert len(result["metadata"]["subcategories"]) > 0
    
    # Find our test subcategory
    test_subcat = next((s for s in result["metadata"]["subcategories"] if s["name"] == "Test AC Repair"), None)
    assert test_subcat is not None
    assert test_subcat["id"] == test_data["subcategory"].id
    
    print("\n✅ Browse Subcategories Integration Test PASSED")
    print(f"   Found {len(result['metadata']['subcategories'])} subcategories")


@pytest.mark.asyncio
async def test_service_agent_browse_services(db_session, test_data):
    """Integration test: Browse services"""
    
    # Create ServiceAgent
    agent = ServiceAgent(db_session)
    
    # Execute browse services
    entities = {"subcategory_id": test_data["subcategory"].id}
    result = await agent._browse_services(entities, test_data["user"])
    
    # Verify response
    assert result["action_taken"] == "services_listed"
    assert "Test Basic AC Repair" in result["response"]
    assert "Test Deep AC Cleaning" in result["response"]
    assert len(result["metadata"]["services"]) >= 2
    
    print("\n✅ Browse Services Integration Test PASSED")
    print(f"   Found {len(result['metadata']['services'])} services")


@pytest.mark.asyncio
async def test_service_agent_search_services(db_session, test_data):
    """Integration test: Search services"""
    
    # Create ServiceAgent
    agent = ServiceAgent(db_session)
    
    # Execute search
    entities = {"query": "AC Repair"}
    result = await agent._search_services(entities, test_data["user"])
    
    # Verify response
    assert result["action_taken"] == "services_found"
    assert "Test Basic AC Repair" in result["response"]
    assert result["metadata"]["results_count"] >= 1
    
    print("\n✅ Search Services Integration Test PASSED")
    print(f"   Found {result['metadata']['results_count']} matching services")


@pytest.mark.asyncio
async def test_service_agent_get_details(db_session, test_data):
    """Integration test: Get service details"""
    
    # Create ServiceAgent
    agent = ServiceAgent(db_session)
    
    # Execute get details
    entities = {"rate_card_id": test_data["rate_card_1"].id}
    result = await agent._get_service_details(entities, test_data["user"])
    
    # Verify response
    assert result["action_taken"] == "service_details_shown"
    assert "Test Basic AC Repair" in result["response"]
    assert "1,500.00" in result["response"]
    assert "Test AC Services" in result["response"]
    assert result["metadata"]["service"]["id"] == test_data["rate_card_1"].id
    
    print("\n✅ Get Service Details Integration Test PASSED")
    print(f"   Retrieved details for: {result['metadata']['service']['name']}")


@pytest.mark.asyncio
async def test_service_agent_execute_routing(db_session, test_data):
    """Integration test: Test execute method routing"""
    
    # Create ServiceAgent
    agent = ServiceAgent(db_session)
    
    # Test browse_categories action
    result = await agent.execute(
        intent="service_inquiry",
        entities={"action": "browse_categories"},
        user=test_data["user"],
        session_id="test_session"
    )
    assert result["action_taken"] == "categories_listed"
    
    # Test search action
    result = await agent.execute(
        intent="service_inquiry",
        entities={"action": "search", "query": "AC"},
        user=test_data["user"],
        session_id="test_session"
    )
    assert result["action_taken"] == "services_found"
    
    print("\n✅ Execute Routing Integration Test PASSED")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])

