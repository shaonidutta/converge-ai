"""
Unit Tests for Agent Execution Graph

Tests:
- Dependency resolution
- Parallel agent execution
- Sequential agent execution
- Response merging with provenance
- Timeout handling
- Error recovery
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.graphs.agent_execution_graph import (
    has_dependencies,
    prepare_agent_execution_node,
    execute_parallel_agents_node,
    execute_sequential_agents_node,
    merge_responses_node,
    create_agent_execution_graph
)
from src.graphs.state import AgentExecutionState


# ============================================================
# TEST FIXTURES
# ============================================================

@pytest.fixture
def mock_coordinator_agent():
    """Create mock CoordinatorAgent"""
    agent = MagicMock()
    
    # Mock _route_to_agent_with_timing to return successful response
    async def mock_route(intent_result, user, session_id):
        await asyncio.sleep(0.01)  # Simulate processing time
        return {
            "response": f"Response for {intent_result.get('intent', 'unknown')}",
            "action_taken": "processed",
            "agent_used": intent_result.get("intent", "unknown"),
            "execution_time_ms": 10,
            "metadata": {"test": True}
        }
    
    agent._route_to_agent_with_timing = mock_route
    
    return agent


@pytest.fixture
def sample_state():
    """Create sample state for testing"""
    return AgentExecutionState(
        user_id=1,
        session_id="test-session",
        current_message="Test message",
        intent_result={
            "primary_intent": "service_inquiry",
            "intents": [
                {"intent": "service_inquiry", "confidence": 0.9},
                {"intent": "policy_inquiry", "confidence": 0.8}
            ]
        },
        collected_entities={},
        needed_entities=[],
        validation_errors=[],
        metadata={"nodes_executed": []},
        question_attempt_count=0,
        retry_count=0,
        max_retries=3,
        should_end=False,
        final_response="",
        independent_intents=[],
        dependent_intents=[],
        parallel_responses=[],
        sequential_responses=[],
        agent_timeout=30,
        agents_used=[]
    )


# ============================================================
# TEST DEPENDENCY RESOLUTION
# ============================================================

def test_has_dependencies_no_dependencies():
    """Test intent with no dependencies"""
    intent = {"intent": "service_inquiry"}
    all_intents = [
        {"intent": "service_inquiry"},
        {"intent": "policy_inquiry"}
    ]
    
    assert has_dependencies(intent, all_intents) is False


def test_has_dependencies_with_dependencies():
    """Test intent with dependencies"""
    intent = {"intent": "booking_modify"}
    all_intents = [
        {"intent": "booking_status"},
        {"intent": "booking_modify"}
    ]
    
    assert has_dependencies(intent, all_intents) is True


def test_has_dependencies_complaint_depends_on_booking():
    """Test complaint depends on booking_status"""
    intent = {"intent": "complaint"}
    all_intents = [
        {"intent": "booking_status"},
        {"intent": "complaint"}
    ]
    
    assert has_dependencies(intent, all_intents) is True


def test_has_dependencies_no_required_intent():
    """Test intent with dependencies but required intent not present"""
    intent = {"intent": "booking_modify"}
    all_intents = [
        {"intent": "service_inquiry"},
        {"intent": "booking_modify"}
    ]
    
    assert has_dependencies(intent, all_intents) is False


# ============================================================
# TEST PREPARE AGENT EXECUTION NODE
# ============================================================

@pytest.mark.asyncio
async def test_prepare_agent_execution_node_success(sample_state):
    """Test successful preparation of agent execution"""
    result = await prepare_agent_execution_node(sample_state)
    
    assert "independent_intents" in result
    assert "dependent_intents" in result
    assert "execution_plan" in result
    assert len(result["independent_intents"]) == 2  # Both intents are independent
    assert len(result["dependent_intents"]) == 0


@pytest.mark.asyncio
async def test_prepare_agent_execution_node_with_dependencies(sample_state):
    """Test preparation with dependent intents"""
    sample_state["intent_result"] = {
        "primary_intent": "booking_modify",
        "intents": [
            {"intent": "booking_status", "confidence": 0.9},
            {"intent": "booking_modify", "confidence": 0.8}
        ]
    }
    
    result = await prepare_agent_execution_node(sample_state)
    
    assert len(result["independent_intents"]) == 1  # booking_status
    assert len(result["dependent_intents"]) == 1  # booking_modify
    assert result["execution_plan"]["parallel_count"] == 1
    assert result["execution_plan"]["sequential_count"] == 1


@pytest.mark.asyncio
async def test_prepare_agent_execution_node_no_intents(sample_state):
    """Test preparation with no intents"""
    sample_state["intent_result"] = {"intents": []}
    
    result = await prepare_agent_execution_node(sample_state)
    
    assert len(result["independent_intents"]) == 0
    assert len(result["dependent_intents"]) == 0


@pytest.mark.asyncio
async def test_prepare_agent_execution_node_error_handling(sample_state):
    """Test error handling in preparation - handles missing intent_result gracefully"""
    # Remove intent_result - should handle gracefully, not error
    del sample_state["intent_result"]

    result = await prepare_agent_execution_node(sample_state)

    # Should return empty execution plan, not error
    assert "independent_intents" in result
    assert len(result["independent_intents"]) == 0
    assert len(result["dependent_intents"]) == 0


# ============================================================
# TEST PARALLEL AGENT EXECUTION NODE
# ============================================================

@pytest.mark.asyncio
async def test_execute_parallel_agents_node_success(sample_state, mock_coordinator_agent):
    """Test successful parallel agent execution"""
    sample_state["independent_intents"] = [
        {"intent": "service_inquiry", "confidence": 0.9},
        {"intent": "policy_inquiry", "confidence": 0.8}
    ]
    sample_state["user"] = MagicMock(id=1)
    
    result = await execute_parallel_agents_node(sample_state, mock_coordinator_agent)
    
    assert "parallel_responses" in result
    assert len(result["parallel_responses"]) == 2
    assert "agents_used" in result
    assert "metadata" in result
    assert result["metadata"]["parallel_agents_count"] == 2


@pytest.mark.asyncio
async def test_execute_parallel_agents_node_no_intents(sample_state, mock_coordinator_agent):
    """Test parallel execution with no intents"""
    sample_state["independent_intents"] = []
    
    result = await execute_parallel_agents_node(sample_state, mock_coordinator_agent)
    
    assert len(result["parallel_responses"]) == 0


@pytest.mark.asyncio
async def test_execute_parallel_agents_node_with_exception(sample_state, mock_coordinator_agent):
    """Test parallel execution with agent exception"""
    sample_state["independent_intents"] = [
        {"intent": "service_inquiry", "confidence": 0.9}
    ]
    sample_state["user"] = MagicMock(id=1)
    
    # Mock agent to raise exception
    async def mock_route_error(intent_result, user, session_id):
        raise ValueError("Test error")
    
    mock_coordinator_agent._route_to_agent_with_timing = mock_route_error
    
    result = await execute_parallel_agents_node(sample_state, mock_coordinator_agent)
    
    assert len(result["parallel_responses"]) == 1
    assert "error" in result["parallel_responses"][0]


@pytest.mark.asyncio
async def test_execute_parallel_agents_node_timeout(sample_state, mock_coordinator_agent):
    """Test parallel execution with timeout"""
    sample_state["independent_intents"] = [
        {"intent": "service_inquiry", "confidence": 0.9}
    ]
    sample_state["user"] = MagicMock(id=1)
    sample_state["agent_timeout"] = 0.001  # Very short timeout
    
    # Mock agent to take longer than timeout
    async def mock_route_slow(intent_result, user, session_id):
        await asyncio.sleep(1)
        return {"response": "Slow response"}
    
    mock_coordinator_agent._route_to_agent_with_timing = mock_route_slow
    
    result = await execute_parallel_agents_node(sample_state, mock_coordinator_agent)
    
    assert len(result["parallel_responses"]) == 1
    assert "timeout" in result["parallel_responses"][0]["action_taken"].lower() or \
           "error" in result["parallel_responses"][0]


# ============================================================
# TEST SEQUENTIAL AGENT EXECUTION NODE
# ============================================================

@pytest.mark.asyncio
async def test_execute_sequential_agents_node_success(sample_state, mock_coordinator_agent):
    """Test successful sequential agent execution"""
    sample_state["dependent_intents"] = [
        {"intent": "booking_modify", "confidence": 0.9}
    ]
    sample_state["parallel_responses"] = [
        {"response": "Booking found", "agent_used": "booking"}
    ]
    sample_state["user"] = MagicMock(id=1)
    
    result = await execute_sequential_agents_node(sample_state, mock_coordinator_agent)
    
    assert "sequential_responses" in result
    assert len(result["sequential_responses"]) == 1
    assert "agents_used" in result


@pytest.mark.asyncio
async def test_execute_sequential_agents_node_no_intents(sample_state, mock_coordinator_agent):
    """Test sequential execution with no intents"""
    sample_state["dependent_intents"] = []
    
    result = await execute_sequential_agents_node(sample_state, mock_coordinator_agent)
    
    assert len(result["sequential_responses"]) == 0


@pytest.mark.asyncio
async def test_execute_sequential_agents_node_with_context(sample_state, mock_coordinator_agent):
    """Test sequential execution receives context from parallel execution"""
    sample_state["dependent_intents"] = [
        {"intent": "complaint", "confidence": 0.9}
    ]
    sample_state["parallel_responses"] = [
        {"response": "Booking info", "agent_used": "booking"}
    ]
    sample_state["user"] = MagicMock(id=1)
    
    # Track if context was passed
    context_received = []
    
    async def mock_route_with_context(intent_result, user, session_id):
        context_received.append(intent_result.get("context"))
        return {
            "response": "Complaint created",
            "action_taken": "processed",
            "agent_used": "complaint",
            "execution_time_ms": 10
        }
    
    mock_coordinator_agent._route_to_agent_with_timing = mock_route_with_context
    
    result = await execute_sequential_agents_node(sample_state, mock_coordinator_agent)
    
    assert len(context_received) == 1
    assert "parallel_results" in context_received[0]
    assert len(context_received[0]["parallel_results"]) == 1


# ============================================================
# TEST MERGE RESPONSES NODE
# ============================================================

@pytest.mark.asyncio
async def test_merge_responses_node_single_response(sample_state):
    """Test merging single response"""
    sample_state["parallel_responses"] = [
        {
            "response": "Service info",
            "action_taken": "processed",
            "agent_used": "service",
            "execution_time_ms": 100
        }
    ]
    sample_state["sequential_responses"] = []
    
    result = await merge_responses_node(sample_state)
    
    assert result["final_response"] == "Service info"
    assert len(result["provenance"]) == 1
    assert result["provenance"][0]["agent"] == "service"
    assert result["metadata"]["successful_agents"] == 1
    assert result["metadata"]["failed_agents"] == 0


@pytest.mark.asyncio
async def test_merge_responses_node_multiple_responses(sample_state):
    """Test merging multiple responses"""
    sample_state["parallel_responses"] = [
        {
            "response": "Service info",
            "action_taken": "processed",
            "agent_used": "service",
            "execution_time_ms": 100
        },
        {
            "response": "Policy info",
            "action_taken": "processed",
            "agent_used": "policy",
            "execution_time_ms": 150
        }
    ]
    sample_state["sequential_responses"] = []

    result = await merge_responses_node(sample_state)

    assert "Service" in result["final_response"]
    assert "Policy" in result["final_response"]
    assert len(result["provenance"]) == 2
    assert result["provenance"][0]["order"] == 1
    assert result["provenance"][1]["order"] == 2
    assert result["metadata"]["successful_agents"] == 2


@pytest.mark.asyncio
async def test_merge_responses_node_with_errors(sample_state):
    """Test merging responses with errors"""
    sample_state["parallel_responses"] = [
        {
            "response": "Service info",
            "action_taken": "processed",
            "agent_used": "service",
            "execution_time_ms": 100
        },
        {
            "response": "Error occurred",
            "action_taken": "error",
            "agent_used": "error",
            "error": "Test error",
            "execution_time_ms": 50
        }
    ]
    sample_state["sequential_responses"] = []

    result = await merge_responses_node(sample_state)

    assert "Service info" in result["final_response"]
    assert len(result["provenance"]) == 2
    assert result["provenance"][1]["success"] is False
    assert result["metadata"]["successful_agents"] == 1
    assert result["metadata"]["failed_agents"] == 1


@pytest.mark.asyncio
async def test_merge_responses_node_no_responses(sample_state):
    """Test merging with no responses"""
    sample_state["parallel_responses"] = []
    sample_state["sequential_responses"] = []

    result = await merge_responses_node(sample_state)

    assert "couldn't process" in result["final_response"].lower()
    assert result["response_type"] == "error"


@pytest.mark.asyncio
async def test_merge_responses_node_all_errors(sample_state):
    """Test merging when all agents failed"""
    sample_state["parallel_responses"] = [
        {
            "response": "Error 1",
            "action_taken": "error",
            "agent_used": "error",
            "error": "Test error 1"
        },
        {
            "response": "Error 2",
            "action_taken": "error",
            "agent_used": "error",
            "error": "Test error 2"
        }
    ]
    sample_state["sequential_responses"] = []

    result = await merge_responses_node(sample_state)

    assert "error" in result["final_response"].lower()
    assert result["metadata"]["failed_agents"] == 2
    assert result["metadata"]["successful_agents"] == 0


@pytest.mark.asyncio
async def test_merge_responses_node_provenance_tracking(sample_state):
    """Test detailed provenance tracking"""
    sample_state["parallel_responses"] = [
        {
            "response": "Service response",
            "action_taken": "service_retrieved",
            "agent_used": "service",
            "execution_time_ms": 120,
            "metadata": {"service_id": 1}
        }
    ]
    sample_state["sequential_responses"] = [
        {
            "response": "Booking response",
            "action_taken": "booking_created",
            "agent_used": "booking",
            "execution_time_ms": 200,
            "metadata": {"booking_id": 123}
        }
    ]

    result = await merge_responses_node(sample_state)

    assert len(result["provenance"]) == 2

    # Check first provenance entry
    prov1 = result["provenance"][0]
    assert prov1["agent"] == "service"
    assert prov1["action_taken"] == "service_retrieved"
    assert prov1["execution_time_ms"] == 120
    assert prov1["order"] == 1
    assert prov1["success"] is True

    # Check second provenance entry
    prov2 = result["provenance"][1]
    assert prov2["agent"] == "booking"
    assert prov2["action_taken"] == "booking_created"
    assert prov2["execution_time_ms"] == 200
    assert prov2["order"] == 2

    # Check combined metadata
    assert "service" in result["combined_metadata"]
    assert "booking" in result["combined_metadata"]
    assert result["combined_metadata"]["service"]["service_id"] == 1
    assert result["combined_metadata"]["booking"]["booking_id"] == 123


# ============================================================
# TEST GRAPH CREATION
# ============================================================

def test_create_agent_execution_graph(mock_coordinator_agent):
    """Test graph creation"""
    graph = create_agent_execution_graph(mock_coordinator_agent)

    assert graph is not None
    # Graph should be compiled and ready to execute


@pytest.mark.asyncio
async def test_agent_execution_graph_end_to_end(mock_coordinator_agent):
    """Test complete graph execution end-to-end"""
    graph = create_agent_execution_graph(mock_coordinator_agent)

    initial_state = {
        "user": MagicMock(id=1),
        "user_id": 1,
        "session_id": "test-session",
        "intent_result": {
            "primary_intent": "service_inquiry",
            "intents": [
                {"intent": "service_inquiry", "confidence": 0.9},
                {"intent": "policy_inquiry", "confidence": 0.8}
            ]
        },
        "agent_timeout": 30,
        "metadata": {"nodes_executed": []}
    }

    result = await graph.ainvoke(initial_state)

    # Check that all nodes were executed
    assert "final_response" in result
    assert "provenance" in result
    assert len(result["provenance"]) == 2
    assert result["metadata"]["successful_agents"] == 2
    assert result["metadata"]["failed_agents"] == 0


@pytest.mark.asyncio
async def test_agent_execution_graph_with_dependencies(mock_coordinator_agent):
    """Test graph execution with dependent intents"""
    graph = create_agent_execution_graph(mock_coordinator_agent)

    initial_state = {
        "user": MagicMock(id=1),
        "user_id": 1,
        "session_id": "test-session",
        "intent_result": {
            "primary_intent": "booking_modify",
            "intents": [
                {"intent": "booking_status", "confidence": 0.9},
                {"intent": "booking_modify", "confidence": 0.8}
            ]
        },
        "agent_timeout": 30,
        "metadata": {"nodes_executed": []}
    }

    result = await graph.ainvoke(initial_state)

    # Check execution plan
    assert result["execution_plan"]["parallel_count"] == 1
    assert result["execution_plan"]["sequential_count"] == 1

    # Check responses
    assert len(result["parallel_responses"]) == 1
    assert len(result["sequential_responses"]) == 1

    # Check final response
    assert "final_response" in result
    assert len(result["provenance"]) == 2

