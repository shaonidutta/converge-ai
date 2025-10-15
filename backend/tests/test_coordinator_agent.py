"""
Comprehensive tests for CoordinatorAgent

Tests cover:
1. Single intent routing (policy, service, booking)
2. Multi-intent handling
3. Conversation context management
4. Error handling and fallbacks
5. Agent coordination
6. Intent classification integration
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.agents.coordinator.coordinator_agent import CoordinatorAgent
from src.core.models import User
from src.schemas.intent import IntentResult, IntentClassificationResult


# Test fixtures
@pytest.fixture
async def db_session():
    """Create test database session"""
    # Use in-memory SQLite for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session


@pytest.fixture
def test_user():
    """Create test user"""
    user = Mock(spec=User)
    user.id = 1
    user.first_name = "Test"
    user.last_name = "User"
    user.email = "test@example.com"
    user.mobile = "1234567890"
    return user


@pytest.fixture
async def coordinator_agent(db_session):
    """Create CoordinatorAgent instance with mocked dependencies"""
    with patch('src.agents.coordinator.coordinator_agent.LLMClient') as mock_llm_client, \
         patch('src.agents.coordinator.coordinator_agent.PolicyAgent') as mock_policy, \
         patch('src.agents.coordinator.coordinator_agent.ServiceAgent') as mock_service, \
         patch('src.agents.coordinator.coordinator_agent.BookingAgent') as mock_booking:

        # Mock LLM client
        mock_llm_client.create_for_intent_classification.return_value = Mock()

        # Create coordinator agent
        agent = CoordinatorAgent(db=db_session)

        # Store mocked agents for test access
        agent.policy_agent = Mock()
        agent.service_agent = Mock()
        agent.booking_agent = Mock()

        yield agent


# Test 1: Policy Intent Routing
@pytest.mark.asyncio
async def test_policy_intent_routing(coordinator_agent, test_user):
    """Test routing of policy-related queries to PolicyAgent"""
    
    # Mock intent classification
    with patch.object(coordinator_agent.intent_classifier, 'classify') as mock_classify:
        mock_classify.return_value = (
            IntentClassificationResult(
                primary_intent=IntentResult(
                    intent="policy_inquiry",
                    confidence=0.95,
                    entities={"query": "What is your cancellation policy?"}
                ),
                all_intents=[
                    IntentResult(
                        intent="policy_inquiry",
                        confidence=0.95,
                        entities={"query": "What is your cancellation policy?"}
                    )
                ]
            ),
            "pattern_match"
        )
        
        # Mock policy agent response
        with patch.object(coordinator_agent.policy_agent, 'execute') as mock_policy:
            mock_policy.return_value = {
                "response": "Our cancellation policy allows free cancellation up to 24 hours before service.",
                "action_taken": "policy_retrieved",
                "metadata": {"policy_type": "cancellation"}
            }
            
            # Execute
            result = await coordinator_agent.execute(
                message="What is your cancellation policy?",
                user=test_user,
                session_id="test_session_1"
            )
            
            # Assertions
            assert result["intent"] == "policy_inquiry"
            assert result["agent_used"] == "policy"
            assert result["confidence"] == 0.95
            assert "cancellation policy" in result["response"].lower()
            assert mock_policy.called


# Test 2: Service Intent Routing
@pytest.mark.asyncio
async def test_service_intent_routing(coordinator_agent, test_user):
    """Test routing of service discovery queries to ServiceAgent"""
    
    with patch.object(coordinator_agent.intent_classifier, 'classify') as mock_classify:
        mock_classify.return_value = (
            IntentClassificationResult(
                primary_intent=IntentResult(
                    intent="service_discovery",
                    confidence=0.92,
                    entities={"service_type": "plumbing", "location": "Bangalore"}
                ),
                all_intents=[
                    IntentResult(
                        intent="service_discovery",
                        confidence=0.92,
                        entities={"service_type": "plumbing", "location": "Bangalore"}
                    )
                ]
            ),
            "llm"
        )
        
        with patch.object(coordinator_agent.service_agent, 'execute') as mock_service:
            mock_service.return_value = {
                "response": "We offer plumbing services in Bangalore including pipe repair, leak fixing, and installation.",
                "action_taken": "services_found",
                "metadata": {"service_count": 5}
            }
            
            result = await coordinator_agent.execute(
                message="I need a plumber in Bangalore",
                user=test_user,
                session_id="test_session_2"
            )
            
            assert result["intent"] == "service_discovery"
            assert result["agent_used"] == "service"
            assert result["confidence"] == 0.92
            assert "plumbing" in result["response"].lower()
            assert mock_service.called


# Test 3: Booking Intent Routing
@pytest.mark.asyncio
async def test_booking_intent_routing(coordinator_agent, test_user):
    """Test routing of booking queries to BookingAgent"""
    
    with patch.object(coordinator_agent.intent_classifier, 'classify') as mock_classify:
        mock_classify.return_value = (
            IntentClassificationResult(
                primary_intent=IntentResult(
                    intent="booking_create",
                    confidence=0.88,
                    entities={
                        "service_type": "plumbing",
                        "date": "2025-10-20",
                        "time": "14:00"
                    }
                ),
                all_intents=[
                    IntentResult(
                        intent="booking_create",
                        confidence=0.88,
                        entities={
                            "service_type": "plumbing",
                            "date": "2025-10-20",
                            "time": "14:00"
                        }
                    )
                ]
            ),
            "llm"
        )
        
        with patch.object(coordinator_agent.booking_agent, 'execute') as mock_booking:
            mock_booking.return_value = {
                "response": "Your plumbing service has been booked for October 20, 2025 at 2:00 PM.",
                "action_taken": "booking_created",
                "metadata": {"booking_id": 123}
            }
            
            result = await coordinator_agent.execute(
                message="Book a plumber for October 20 at 2 PM",
                user=test_user,
                session_id="test_session_3"
            )
            
            assert result["intent"] == "booking_create"
            assert result["agent_used"] == "booking"
            assert "booked" in result["response"].lower()
            assert mock_booking.called


# Test 4: Multi-Intent Handling
@pytest.mark.asyncio
async def test_multi_intent_handling(coordinator_agent, test_user):
    """Test handling of queries with multiple intents"""
    
    with patch.object(coordinator_agent.intent_classifier, 'classify') as mock_classify:
        mock_classify.return_value = (
            IntentClassificationResult(
                primary_intent=IntentResult(
                    intent="service_discovery",
                    confidence=0.90,
                    entities={"service_type": "plumbing"}
                ),
                all_intents=[
                    IntentResult(
                        intent="service_discovery",
                        confidence=0.90,
                        entities={"service_type": "plumbing"}
                    ),
                    IntentResult(
                        intent="policy_inquiry",
                        confidence=0.85,
                        entities={"query": "cancellation policy"}
                    )
                ]
            ),
            "llm"
        )
        
        with patch.object(coordinator_agent.service_agent, 'execute') as mock_service, \
             patch.object(coordinator_agent.policy_agent, 'execute') as mock_policy:
            
            mock_service.return_value = {
                "response": "We offer plumbing services.",
                "action_taken": "services_found",
                "metadata": {}
            }
            
            mock_policy.return_value = {
                "response": "Free cancellation up to 24 hours before service.",
                "action_taken": "policy_retrieved",
                "metadata": {}
            }
            
            result = await coordinator_agent.execute(
                message="What plumbing services do you offer and what's your cancellation policy?",
                user=test_user,
                session_id="test_session_4"
            )
            
            assert result["agent_used"] == "service, policy"
            assert "plumbing" in result["response"].lower()
            assert "cancellation" in result["response"].lower()
            assert result["metadata"]["intent_count"] == 2


# Test 5: Error Handling
@pytest.mark.asyncio
async def test_error_handling(coordinator_agent, test_user):
    """Test error handling when agent execution fails"""
    
    with patch.object(coordinator_agent.intent_classifier, 'classify') as mock_classify:
        mock_classify.return_value = (
            IntentClassificationResult(
                primary_intent=IntentResult(
                    intent="policy_inquiry",
                    confidence=0.95,
                    entities={"query": "test"}
                ),
                all_intents=[
                    IntentResult(
                        intent="policy_inquiry",
                        confidence=0.95,
                        entities={"query": "test"}
                    )
                ]
            ),
            "pattern_match"
        )
        
        # Mock agent to raise exception
        with patch.object(coordinator_agent.policy_agent, 'execute') as mock_policy:
            mock_policy.side_effect = Exception("Test error")
            
            result = await coordinator_agent.execute(
                message="Test query",
                user=test_user,
                session_id="test_session_5"
            )
            
            assert result["intent"] == "policy_inquiry"
            assert "error" in result["response"].lower()
            assert result["agent_used"] == "policy_error"


# Test 6: Fallback for Unknown Intent
@pytest.mark.asyncio
async def test_unknown_intent_fallback(coordinator_agent, test_user):
    """Test fallback to policy agent for unknown intents"""
    
    with patch.object(coordinator_agent.intent_classifier, 'classify') as mock_classify:
        mock_classify.return_value = (
            IntentClassificationResult(
                primary_intent=IntentResult(
                    intent="unknown_intent",
                    confidence=0.60,
                    entities={}
                ),
                all_intents=[
                    IntentResult(
                        intent="unknown_intent",
                        confidence=0.60,
                        entities={}
                    )
                ]
            ),
            "fallback"
        )
        
        with patch.object(coordinator_agent.policy_agent, 'execute') as mock_policy:
            mock_policy.return_value = {
                "response": "I can help you with that.",
                "action_taken": "fallback_handled",
                "metadata": {}
            }
            
            result = await coordinator_agent.execute(
                message="Random query",
                user=test_user,
                session_id="test_session_6"
            )
            
            assert result["agent_used"] == "policy_fallback"
            assert mock_policy.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

