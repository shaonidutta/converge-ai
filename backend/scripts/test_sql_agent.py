"""
Comprehensive Test Suite for SQLAgent

Tests all SQL agent scenarios:
1. Valid SELECT query generation and execution
2. Security validation (block dangerous queries)
3. User-specific data filtering
4. Query result formatting
5. Error handling
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


async def test_sql_agent():
    """Test SQLAgent with all scenarios"""
    print("\n" + "="*80)
    print("SQL AGENT - COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    # Create mock user
    user = Mock()
    user.id = 1
    user.first_name = "Test"
    user.last_name = "User"
    user.email = "test@example.com"
    user.mobile = "1234567890"
    
    print(f"\n✅ Mock user created: {user.first_name} {user.last_name} (ID: {user.id})")
    
    # Create mock database session
    db_session = AsyncMock()
    
    print("✅ Mock database session created")
    
    # Import SQLAgent
    from src.agents.sql.sql_agent import SQLAgent
    
    # Test 1: Valid SELECT Query
    print("\n" + "-"*80)
    print("TEST 1: Valid SELECT Query - Recent Bookings")
    print("-"*80)
    
    # Mock LLM response
    mock_llm_response = f"SELECT b.id, b.booking_number, b.status, b.total, b.created_at FROM bookings b WHERE b.user_id = {user.id} ORDER BY b.created_at DESC LIMIT 10;"
    
    # Mock query results
    mock_results = [
        {
            'id': 1,
            'booking_number': 'BK001',
            'status': 'confirmed',
            'total': 5000.00,
            'created_at': datetime.now(timezone.utc)
        },
        {
            'id': 2,
            'booking_number': 'BK002',
            'status': 'completed',
            'total': 3000.00,
            'created_at': datetime.now(timezone.utc)
        }
    ]
    
    # Mock database execute
    mock_result = Mock()
    mock_result.fetchall = Mock(return_value=[
        (1, 'BK001', 'confirmed', 5000.00, datetime.now(timezone.utc)),
        (2, 'BK002', 'completed', 3000.00, datetime.now(timezone.utc))
    ])
    mock_result.keys = Mock(return_value=['id', 'booking_number', 'status', 'total', 'created_at'])
    
    async def mock_execute(query):
        return mock_result
    
    db_session.execute = mock_execute
    
    # Create agent with mocked LLM
    with patch('src.agents.sql.sql_agent.LLMClient') as MockLLMClient:
        mock_llm_instance = AsyncMock()
        mock_llm_instance.generate_text = AsyncMock(return_value=mock_llm_response)
        MockLLMClient.create_for_intent_classification = Mock(return_value=mock_llm_instance)
        
        agent = SQLAgent(db_session)
        
        result = await agent.execute(
            message="Show my recent bookings",
            user=user,
            session_id="test_1",
            entities={"query": "Show my recent bookings"}
        )
    
    print(f"✅ Response: {result['response'][:200]}...")
    print(f"✅ Action: {result['action_taken']}")
    print(f"✅ Row Count: {result['metadata']['row_count']}")
    print(f"✅ SQL Query: {result['metadata']['sql_query']}")
    
    assert result['action_taken'] == "query_executed"
    assert result['metadata']['row_count'] == 2
    assert "SELECT" in result['metadata']['sql_query'].upper()
    print("✅ TEST 1 PASSED")
    
    # Test 2: Security Validation - Block DELETE Query
    print("\n" + "-"*80)
    print("TEST 2: Security Validation - Block DELETE Query")
    print("-"*80)
    
    # Mock dangerous SQL
    dangerous_sql = "DELETE FROM bookings WHERE user_id = 1;"
    
    with patch('src.agents.sql.sql_agent.LLMClient') as MockLLMClient:
        mock_llm_instance = AsyncMock()
        mock_llm_instance.generate_text = AsyncMock(return_value=dangerous_sql)
        MockLLMClient.create_for_intent_classification = Mock(return_value=mock_llm_instance)
        
        agent = SQLAgent(db_session)
        
        result = await agent.execute(
            message="Delete all my bookings",
            user=user,
            session_id="test_2",
            entities={"query": "Delete all my bookings"}
        )
    
    print(f"✅ Response: {result['response']}")
    print(f"✅ Action: {result['action_taken']}")
    
    assert result['action_taken'] == "unsafe_query"
    assert "Security Error" in result['response']
    print("✅ TEST 2 PASSED")
    
    # Test 3: Security Validation - Block UPDATE Query
    print("\n" + "-"*80)
    print("TEST 3: Security Validation - Block UPDATE Query")
    print("-"*80)
    
    update_sql = "UPDATE users SET wallet_balance = 10000 WHERE id = 1;"
    
    with patch('src.agents.sql.sql_agent.LLMClient') as MockLLMClient:
        mock_llm_instance = AsyncMock()
        mock_llm_instance.generate_text = AsyncMock(return_value=update_sql)
        MockLLMClient.create_for_intent_classification = Mock(return_value=mock_llm_instance)
        
        agent = SQLAgent(db_session)
        
        result = await agent.execute(
            message="Update my wallet balance",
            user=user,
            session_id="test_3",
            entities={"query": "Update my wallet balance"}
        )
    
    print(f"✅ Response: {result['response']}")
    print(f"✅ Action: {result['action_taken']}")
    
    assert result['action_taken'] == "unsafe_query"
    print("✅ TEST 3 PASSED")
    
    # Test 4: Security Validation - Block DROP Query
    print("\n" + "-"*80)
    print("TEST 4: Security Validation - Block DROP Query")
    print("-"*80)
    
    drop_sql = "DROP TABLE bookings;"
    
    with patch('src.agents.sql.sql_agent.LLMClient') as MockLLMClient:
        mock_llm_instance = AsyncMock()
        mock_llm_instance.generate_text = AsyncMock(return_value=drop_sql)
        MockLLMClient.create_for_intent_classification = Mock(return_value=mock_llm_instance)
        
        agent = SQLAgent(db_session)
        
        result = await agent.execute(
            message="Drop the bookings table",
            user=user,
            session_id="test_4",
            entities={"query": "Drop the bookings table"}
        )
    
    print(f"✅ Response: {result['response']}")
    print(f"✅ Action: {result['action_taken']}")

    assert result['action_taken'] == "unsafe_query"
    assert "SELECT" in result['metadata']['error'].upper()  # Error says "Only SELECT queries allowed"
    print("✅ TEST 4 PASSED")
    
    # Test 5: Empty Results
    print("\n" + "-"*80)
    print("TEST 5: Empty Results - No Data Found")
    print("-"*80)
    
    empty_sql = f"SELECT * FROM complaints WHERE user_id = {user.id};"
    
    # Mock empty results
    mock_empty_result = Mock()
    mock_empty_result.fetchall = Mock(return_value=[])
    mock_empty_result.keys = Mock(return_value=[])
    
    async def mock_execute_empty(query):
        return mock_empty_result
    
    db_session.execute = mock_execute_empty
    
    with patch('src.agents.sql.sql_agent.LLMClient') as MockLLMClient:
        mock_llm_instance = AsyncMock()
        mock_llm_instance.generate_text = AsyncMock(return_value=empty_sql)
        MockLLMClient.create_for_intent_classification = Mock(return_value=mock_llm_instance)
        
        agent = SQLAgent(db_session)
        
        result = await agent.execute(
            message="Show my complaints",
            user=user,
            session_id="test_5",
            entities={"query": "Show my complaints"}
        )
    
    print(f"✅ Response: {result['response']}")
    print(f"✅ Action: {result['action_taken']}")
    print(f"✅ Row Count: {result['metadata']['row_count']}")
    
    assert result['action_taken'] == "query_executed"
    assert result['metadata']['row_count'] == 0
    assert "No results found" in result['response']
    print("✅ TEST 5 PASSED")
    
    # Test 6: Missing Query
    print("\n" + "-"*80)
    print("TEST 6: Missing Query - No Question Provided")
    print("-"*80)
    
    with patch('src.agents.sql.sql_agent.LLMClient') as MockLLMClient:
        mock_llm_instance = AsyncMock()
        MockLLMClient.create_for_intent_classification = Mock(return_value=mock_llm_instance)
        
        agent = SQLAgent(db_session)
        
        result = await agent.execute(
            message="",
            user=user,
            session_id="test_6",
            entities={}
        )
    
    print(f"✅ Response: {result['response']}")
    print(f"✅ Action: {result['action_taken']}")
    
    assert result['action_taken'] == "missing_query"
    assert "specific question" in result['response'].lower()
    print("✅ TEST 6 PASSED")
    
    # Test 7: SQL Injection Attempt - Multiple Statements
    print("\n" + "-"*80)
    print("TEST 7: SQL Injection Attempt - Multiple Statements")
    print("-"*80)
    
    injection_sql = f"SELECT * FROM bookings WHERE user_id = {user.id}; DROP TABLE users;"
    
    with patch('src.agents.sql.sql_agent.LLMClient') as MockLLMClient:
        mock_llm_instance = AsyncMock()
        mock_llm_instance.generate_text = AsyncMock(return_value=injection_sql)
        MockLLMClient.create_for_intent_classification = Mock(return_value=mock_llm_instance)
        
        agent = SQLAgent(db_session)
        
        result = await agent.execute(
            message="Show bookings and drop users",
            user=user,
            session_id="test_7",
            entities={"query": "Show bookings and drop users"}
        )
    
    print(f"✅ Response: {result['response']}")
    print(f"✅ Action: {result['action_taken']}")

    assert result['action_taken'] == "unsafe_query"
    # Either "Multiple SQL statements" or "Dangerous keyword 'DROP'" is acceptable
    assert ("Multiple SQL statements" in result['metadata']['error'] or
            "DROP" in result['metadata']['error'])
    print("✅ TEST 7 PASSED")
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print("\n✅ All 7 tests PASSED!")
    print("\n🎉 SQLAgent is working correctly!")
    print("\nTest Coverage:")
    print("  ✅ Valid SELECT query execution")
    print("  ✅ Block DELETE queries")
    print("  ✅ Block UPDATE queries")
    print("  ✅ Block DROP queries")
    print("  ✅ Empty result handling")
    print("  ✅ Missing query validation")
    print("  ✅ SQL injection prevention (multiple statements)")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(test_sql_agent())
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

