"""
Simple test to verify chatbot scenarios
Run from backend directory: python -m pytest test_simple.py -v -s
"""

import asyncio
import pytest
from sqlalchemy import select
from database.session import async_session_maker
from agents.coordinator.coordinator_agent import CoordinatorAgent
from models.user import User


@pytest.fixture
async def db_session():
    """Create a database session for testing"""
    async with async_session_maker() as session:
        yield session


@pytest.fixture
async def test_user(db_session):
    """Get test user"""
    result = await db_session.execute(
        select(User).where(User.email == "test@example.com")
    )
    user = result.scalar_one_or_none()
    if not user:
        pytest.skip("Test user not found. Create user with email: test@example.com")
    return user


@pytest.mark.asyncio
async def test_service_information_routing(db_session, test_user):
    """Test 1: Service information query should route to ServiceAgent"""
    print("\n" + "="*80)
    print("TEST 1: Service Information Routing")
    print("="*80)
    
    coordinator = CoordinatorAgent(db_session)
    
    result = await coordinator.execute(
        user=test_user,
        session_id="test_service_info",
        message="can u help with services?"
    )
    
    print(f"\n📤 User: can u help with services?")
    print(f"📥 Lisa: {result['response'][:200]}...")
    print(f"🎯 Intent: {result['intent']}")
    print(f"🤖 Agent: {result['agent_used']}")
    
    # Assertions
    assert result['agent_used'] == 'service', f"Expected 'service' agent, got '{result['agent_used']}'"
    assert 'policy' not in result['response'].lower(), "Response should not mention 'policy'"
    print("\n✅ TEST PASSED: Correctly routed to ServiceAgent")


@pytest.mark.asyncio
async def test_booking_slot_filling(db_session, test_user):
    """Test 2: Booking flow with slot-filling and context awareness"""
    print("\n" + "="*80)
    print("TEST 2: Booking Slot-Filling")
    print("="*80)
    
    coordinator = CoordinatorAgent(db_session)
    session_id = "test_booking_flow"
    
    # Turn 1: Initial booking request
    print("\n--- Turn 1 ---")
    result1 = await coordinator.execute(
        user=test_user,
        session_id=session_id,
        message="I want to book a service"
    )
    
    print(f"📤 User: I want to book a service")
    print(f"📥 Lisa: {result1['response']}")
    
    # Should ask for location or other required info
    assert any(word in result1['response'].lower() for word in ['location', 'pincode', 'what', 'which']), \
        "Should ask for missing information"
    print("✅ Lisa asks for required information")
    
    # Turn 2: Provide location
    print("\n--- Turn 2 ---")
    result2 = await coordinator.execute(
        user=test_user,
        session_id=session_id,
        message="282002"
    )
    
    print(f"📤 User: 282002")
    print(f"📥 Lisa: {result2['response']}")
    
    # Should NOT repeat location question
    location_repeated = 'location' in result2['response'].lower() or 'pincode' in result2['response'].lower()
    assert not location_repeated, "Should NOT repeat location question (context awareness failed!)"
    print("✅ Lisa did NOT repeat location question (context maintained)")
    
    # Should ask for next piece of information
    assert any(word in result2['response'].lower() for word in ['date', 'time', 'service', 'what', 'which']), \
        "Should ask for next piece of information"
    print("✅ Lisa asks for next piece of information")
    
    print("\n✅ TEST PASSED: Slot-filling maintains context")


@pytest.mark.asyncio
async def test_no_hardcoded_responses(db_session, test_user):
    """Test 3: Verify no hardcoded responses"""
    print("\n" + "="*80)
    print("TEST 3: No Hardcoded Responses")
    print("="*80)
    
    coordinator = CoordinatorAgent(db_session)
    
    # Test service query
    result = await coordinator.execute(
        user=test_user,
        session_id="test_no_hardcode",
        message="what services do you offer?"
    )
    
    print(f"\n📤 User: what services do you offer?")
    print(f"📥 Lisa: {result['response'][:200]}...")
    
    # Should not have generic hardcoded responses
    hardcoded_phrases = [
        "I'd be happy to help you with policy questions",
        "What would you like to know about our policies"
    ]
    
    for phrase in hardcoded_phrases:
        assert phrase not in result['response'], f"Found hardcoded phrase: {phrase}"
    
    print("✅ TEST PASSED: No hardcoded responses detected")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])

