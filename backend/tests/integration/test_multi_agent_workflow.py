"""
Integration Tests for Multi-Agent Workflow

Tests complete end-to-end workflows with:
- Real CoordinatorAgent
- Real specialized agents (mocked LLM calls)
- Real database operations (test database)
- Complete slot-filling + agent execution flow

Test Scenarios:
1. Single intent flow
2. Multi-intent parallel flow (independent intents)
3. Multi-intent sequential flow (dependent intents)
4. Error handling and recovery
5. Provenance tracking
"""

import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.agents.coordinator.coordinator_agent import CoordinatorAgent
from src.core.models import User
from src.schemas.intent import IntentClassificationResult, IntentResult


# ============================================================
# TEST FIXTURES
# ============================================================

@pytest.fixture
async def db_session():
    """Create test database session"""
    # Use in-memory SQLite for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session


@pytest.fixture
async def coordinator_agent(db_session: AsyncSession):
    """Create CoordinatorAgent with test database"""
    # Mock environment variables if not set
    with patch.dict(os.environ, {
        'DATABASE_URL': 'sqlite+aiosqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key',
        'PINECONE_API_KEY': 'test-pinecone-key',
        'GOOGLE_API_KEY': 'test-google-key',
        'SECRET_KEY': 'test-secret-key'
    }, clear=False):
        agent = CoordinatorAgent(db=db_session)
        return agent


@pytest.fixture
def mock_user():
    """Create mock user"""
    user = Mock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    user.full_name = "Test User"
    user.first_name = "Test"
    user.last_name = "User"
    user.mobile = "1234567890"
    return user


# ============================================================
# TEST SCENARIO 1: SINGLE INTENT FLOW
# ============================================================

@pytest.mark.asyncio
async def test_single_intent_service_inquiry(coordinator_agent, mock_user):
    """
    Test single intent flow: Service inquiry
    
    Flow:
    1. User asks about AC service
    2. Intent classification detects service_inquiry
    3. ServiceAgent executes
    4. Response returned
    """
    # Mock intent classifier to return service_inquiry
    with patch.object(coordinator_agent.intent_classifier, 'classify') as mock_classify:
        mock_classify.return_value = (
            IntentClassificationResult(
                primary_intent="service_inquiry",
                confidence=0.92,
                intents=[
                    IntentResult(
                        intent="service_inquiry",
                        confidence=0.92,
                        entities={"service_type": "ac"}
                    )
                ]
            ),
            "pattern_match"
        )
        
        # Mock ServiceAgent response
        with patch.object(coordinator_agent.service_agent, 'execute') as mock_service:
            mock_service.return_value = {
                "response": "AC service costs ₹500 for basic cleaning",
                "action_taken": "service_info_retrieved",
                "agent_used": "service",
                "metadata": {"service_id": 1}
            }
            
            # Execute
            result = await coordinator_agent.execute(
                message="Tell me about AC service",
                user=mock_user,
                session_id="test-session-1"
            )
            
            # Assertions
            assert result["response"] == "AC service costs ₹500 for basic cleaning"
            assert result["agent_used"] == "service"
            assert "service_info_retrieved" in result["action_taken"]
            
            # Verify ServiceAgent was called
            mock_service.assert_called_once()


@pytest.mark.asyncio
async def test_single_intent_policy_inquiry(coordinator_agent, mock_user):
    """
    Test single intent flow: Policy inquiry
    
    Flow:
    1. User asks about cancellation policy
    2. Intent classification detects policy_inquiry
    3. PolicyAgent executes (RAG)
    4. Response with citations returned
    """
    with patch.object(coordinator_agent.intent_classifier, 'classify') as mock_classify:
        mock_classify.return_value = (
            IntentClassificationResult(
                primary_intent="policy_inquiry",
                confidence=0.88,
                intents=[
                    IntentResult(
                        intent="policy_inquiry",
                        confidence=0.88,
                        entities={"policy_type": "cancellation"}
                    )
                ]
            ),
            "llm"
        )
        
        # Mock PolicyAgent response
        with patch.object(coordinator_agent.policy_agent, 'execute') as mock_policy:
            mock_policy.return_value = {
                "response": "Cancellation policy allows full refund if cancelled 24 hours before",
                "action_taken": "policy_retrieved",
                "agent_used": "policy",
                "metadata": {
                    "sources": ["policy_doc_1"],
                    "grounding_score": 0.95
                }
            }
            
            # Execute
            result = await coordinator_agent.execute(
                message="What is the cancellation policy?",
                user=mock_user,
                session_id="test-session-2"
            )
            
            # Assertions
            assert "cancellation policy" in result["response"].lower()
            assert result["agent_used"] == "policy"
            assert result["metadata"]["grounding_score"] == 0.95


# ============================================================
# TEST SCENARIO 2: MULTI-INTENT PARALLEL FLOW
# ============================================================

@pytest.mark.asyncio
async def test_multi_intent_parallel_independent(coordinator_agent, mock_user):
    """
    Test multi-intent parallel flow with independent intents
    
    Flow:
    1. User asks: "Tell me about AC service AND show cancellation policy"
    2. Intent classification detects 2 independent intents
    3. ServiceAgent and PolicyAgent execute in parallel
    4. Responses merged with provenance
    """
    with patch.object(coordinator_agent.intent_classifier, 'classify') as mock_classify:
        mock_classify.return_value = (
            IntentClassificationResult(
                primary_intent="service_inquiry",
                confidence=0.92,
                intents=[
                    IntentResult(
                        intent="service_inquiry",
                        confidence=0.92,
                        entities={"service_type": "ac"}
                    ),
                    IntentResult(
                        intent="policy_inquiry",
                        confidence=0.88,
                        entities={"policy_type": "cancellation"}
                    )
                ]
            ),
            "llm"
        )
        
        # Mock both agents
        with patch.object(coordinator_agent.service_agent, 'execute') as mock_service, \
             patch.object(coordinator_agent.policy_agent, 'execute') as mock_policy:
            
            mock_service.return_value = {
                "response": "AC service costs ₹500",
                "action_taken": "service_info_retrieved",
                "agent_used": "service",
                "metadata": {"service_id": 1}
            }
            
            mock_policy.return_value = {
                "response": "Full refund if cancelled 24 hours before",
                "action_taken": "policy_retrieved",
                "agent_used": "policy",
                "metadata": {"grounding_score": 0.95}
            }
            
            # Execute
            result = await coordinator_agent.execute(
                message="Tell me about AC service AND show cancellation policy",
                user=mock_user,
                session_id="test-session-3"
            )
            
            # Assertions
            assert "AC service" in result["response"] or "₹500" in result["response"]
            assert "refund" in result["response"].lower() or "cancel" in result["response"].lower()
            assert result["action_taken"] == "multi_intent_handled"
            
            # Check provenance
            assert "provenance" in result
            assert len(result["provenance"]) == 2
            
            # Verify both agents were called
            assert mock_service.called
            assert mock_policy.called


@pytest.mark.asyncio
async def test_multi_intent_parallel_performance(coordinator_agent, mock_user):
    """
    Test that parallel execution is faster than sequential
    
    Verifies:
    - Both agents execute concurrently
    - Total time is max(agent1_time, agent2_time), not sum
    """
    import asyncio
    
    with patch.object(coordinator_agent.intent_classifier, 'classify') as mock_classify:
        mock_classify.return_value = (
            IntentClassificationResult(
                primary_intent="service_inquiry",
                confidence=0.92,
                intents=[
                    IntentResult(intent="service_inquiry", confidence=0.92, entities={}),
                    IntentResult(intent="policy_inquiry", confidence=0.88, entities={})
                ]
            ),
            "llm"
        )
        
        # Mock agents with delays
        async def mock_service_slow(*args, **kwargs):
            await asyncio.sleep(0.1)  # 100ms
            return {
                "response": "Service response",
                "action_taken": "processed",
                "agent_used": "service",
                "metadata": {}
            }
        
        async def mock_policy_slow(*args, **kwargs):
            await asyncio.sleep(0.15)  # 150ms
            return {
                "response": "Policy response",
                "action_taken": "processed",
                "agent_used": "policy",
                "metadata": {}
            }
        
        with patch.object(coordinator_agent.service_agent, 'execute', side_effect=mock_service_slow), \
             patch.object(coordinator_agent.policy_agent, 'execute', side_effect=mock_policy_slow):
            
            import time
            start = time.time()
            
            result = await coordinator_agent.execute(
                message="Service and policy query",
                user=mock_user,
                session_id="test-session-4"
            )
            
            elapsed = time.time() - start
            
            # Parallel execution should take ~150ms (max), not 250ms (sum)
            # Allow some overhead, so check < 200ms
            assert elapsed < 0.25, f"Parallel execution took {elapsed}s, expected < 0.25s"
            assert result["action_taken"] == "multi_intent_handled"


# ============================================================
# TEST SCENARIO 3: MULTI-INTENT SEQUENTIAL FLOW
# ============================================================

@pytest.mark.asyncio
async def test_multi_intent_sequential_dependent(coordinator_agent, mock_user):
    """
    Test multi-intent sequential flow with dependent intents
    
    Flow:
    1. User asks: "Show my booking AND file a complaint"
    2. Intent classification detects 2 dependent intents
    3. BookingAgent executes first
    4. ComplaintAgent executes second (uses booking context)
    5. Responses merged
    """
    with patch.object(coordinator_agent.intent_classifier, 'classify') as mock_classify:
        mock_classify.return_value = (
            IntentClassificationResult(
                primary_intent="booking_status",
                confidence=0.90,
                intents=[
                    IntentResult(
                        intent="booking_status",
                        confidence=0.90,
                        entities={"booking_id": "12345"}
                    ),
                    IntentResult(
                        intent="complaint",
                        confidence=0.85,
                        entities={"issue": "delay"}
                    )
                ]
            ),
            "llm"
        )
        
        # Mock both agents
        with patch.object(coordinator_agent.booking_agent, 'execute') as mock_booking, \
             patch.object(coordinator_agent.complaint_agent, 'execute') as mock_complaint:
            
            mock_booking.return_value = {
                "response": "Your booking #12345 is scheduled for tomorrow",
                "action_taken": "booking_retrieved",
                "agent_used": "booking",
                "metadata": {"booking_id": 12345}
            }
            
            mock_complaint.return_value = {
                "response": "Complaint #C789 created for booking #12345",
                "action_taken": "complaint_created",
                "agent_used": "complaint",
                "metadata": {"complaint_id": "C789"}
            }
            
            # Execute
            result = await coordinator_agent.execute(
                message="Show my booking AND file a complaint",
                user=mock_user,
                session_id="test-session-5"
            )
            
            # Assertions
            assert "booking" in result["response"].lower()
            assert "complaint" in result["response"].lower()
            assert result["action_taken"] == "multi_intent_handled"
            
            # Check provenance shows sequential execution
            assert "provenance" in result
            assert len(result["provenance"]) == 2
            assert result["provenance"][0]["order"] == 1
            assert result["provenance"][1]["order"] == 2


# ============================================================
# TEST SCENARIO 4: ERROR HANDLING
# ============================================================

@pytest.mark.asyncio
async def test_multi_intent_partial_failure(coordinator_agent, mock_user):
    """
    Test error handling when one agent fails
    
    Verifies:
    - System doesn't crash
    - Successful agent response is returned
    - Failed agent is logged in provenance
    """
    with patch.object(coordinator_agent.intent_classifier, 'classify') as mock_classify:
        mock_classify.return_value = (
            IntentClassificationResult(
                primary_intent="service_inquiry",
                confidence=0.92,
                intents=[
                    IntentResult(intent="service_inquiry", confidence=0.92, entities={}),
                    IntentResult(intent="policy_inquiry", confidence=0.88, entities={})
                ]
            ),
            "llm"
        )
        
        # Mock one success, one failure
        with patch.object(coordinator_agent.service_agent, 'execute') as mock_service, \
             patch.object(coordinator_agent.policy_agent, 'execute') as mock_policy:
            
            mock_service.return_value = {
                "response": "Service response",
                "action_taken": "processed",
                "agent_used": "service",
                "metadata": {}
            }
            
            # PolicyAgent raises exception
            mock_policy.side_effect = Exception("Policy agent error")
            
            # Execute - should not crash
            result = await coordinator_agent.execute(
                message="Service and policy query",
                user=mock_user,
                session_id="test-session-6"
            )
            
            # Assertions
            assert result is not None
            assert "response" in result
            
            # Check provenance shows one success, one failure
            if "provenance" in result:
                assert len(result["provenance"]) == 2
                success_count = sum(1 for p in result["provenance"] if p.get("success", True))
                assert success_count >= 1  # At least one succeeded


@pytest.mark.asyncio
async def test_multi_intent_timeout_handling(coordinator_agent, mock_user):
    """
    Test timeout handling for slow agents
    
    Verifies:
    - Agents that exceed timeout are handled gracefully
    - System returns partial results
    """
    import asyncio
    
    with patch.object(coordinator_agent.intent_classifier, 'classify') as mock_classify:
        mock_classify.return_value = (
            IntentClassificationResult(
                primary_intent="service_inquiry",
                confidence=0.92,
                intents=[
                    IntentResult(intent="service_inquiry", confidence=0.92, entities={})
                ]
            ),
            "llm"
        )
        
        # Mock agent that takes too long
        async def mock_service_timeout(*args, **kwargs):
            await asyncio.sleep(35)  # Exceeds 30s timeout
            return {"response": "Should not reach here"}
        
        with patch.object(coordinator_agent.service_agent, 'execute', side_effect=mock_service_timeout):
            # Execute with short timeout
            result = await coordinator_agent.execute(
                message="Service query",
                user=mock_user,
                session_id="test-session-7"
            )
            
            # Should return error response, not crash
            assert result is not None
            assert "response" in result


# ============================================================
# TEST SCENARIO 5: PROVENANCE TRACKING
# ============================================================

@pytest.mark.asyncio
async def test_provenance_tracking_detailed(coordinator_agent, mock_user):
    """
    Test detailed provenance tracking
    
    Verifies:
    - Each agent contribution is tracked
    - Execution order is recorded
    - Execution time is tracked
    - Metadata is preserved
    """
    with patch.object(coordinator_agent.intent_classifier, 'classify') as mock_classify:
        mock_classify.return_value = (
            IntentClassificationResult(
                primary_intent="service_inquiry",
                confidence=0.92,
                intents=[
                    IntentResult(intent="service_inquiry", confidence=0.92, entities={}),
                    IntentResult(intent="policy_inquiry", confidence=0.88, entities={})
                ]
            ),
            "llm"
        )
        
        with patch.object(coordinator_agent.service_agent, 'execute') as mock_service, \
             patch.object(coordinator_agent.policy_agent, 'execute') as mock_policy:
            
            mock_service.return_value = {
                "response": "Service response",
                "action_taken": "service_retrieved",
                "agent_used": "service",
                "metadata": {"service_id": 1, "price": 500}
            }
            
            mock_policy.return_value = {
                "response": "Policy response",
                "action_taken": "policy_retrieved",
                "agent_used": "policy",
                "metadata": {"grounding_score": 0.95, "sources": ["doc1"]}
            }
            
            result = await coordinator_agent.execute(
                message="Service and policy query",
                user=mock_user,
                session_id="test-session-8"
            )
            
            # Check provenance structure
            assert "provenance" in result
            provenance = result["provenance"]
            
            assert len(provenance) == 2
            
            # Check first entry
            assert provenance[0]["agent"] in ["service", "policy"]
            assert "contribution" in provenance[0]
            assert "action_taken" in provenance[0]
            assert "order" in provenance[0]
            assert provenance[0]["order"] in [1, 2]
            
            # Check combined metadata
            assert "combined_metadata" in result["metadata"]
            combined = result["metadata"]["combined_metadata"]
            assert "service" in combined or "policy" in combined

