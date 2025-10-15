"""
Tests for Slot-Filling Orchestrator Service

Tests:
- Service initialization
- Response building
- Response type determination
- Session status retrieval
- Error handling
"""

import sys
import os
import asyncio
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.slot_filling_service import SlotFillingService
from unittest.mock import AsyncMock, MagicMock


def test_service_initialization():
    """Test: Service initialization with all dependencies"""
    print("\n" + "="*80)
    print("TEST 1: Service Initialization")
    print("="*80)
    
    mock_db = AsyncMock()
    mock_classifier = MagicMock()
    mock_dialog_manager = MagicMock()
    mock_question_generator = MagicMock()
    mock_entity_extractor = MagicMock()
    mock_entity_validator = MagicMock()
    
    service = SlotFillingService(
        db=mock_db,
        classifier=mock_classifier,
        dialog_manager=mock_dialog_manager,
        question_generator=mock_question_generator,
        entity_extractor=mock_entity_extractor,
        entity_validator=mock_entity_validator
    )
    
    print(f"Service initialized: {service}")
    assert service.db == mock_db
    assert service.classifier == mock_classifier
    assert service.dialog_manager == mock_dialog_manager
    print("✅ Test passed: Service initialized with all dependencies")


def test_determine_response_type_question():
    """Test: Determine response type (question)"""
    print("\n" + "="*80)
    print("TEST 2: Determine Response Type (Question)")
    print("="*80)
    
    mock_db = AsyncMock()
    service = SlotFillingService(
        db=mock_db,
        classifier=MagicMock(),
        dialog_manager=MagicMock(),
        question_generator=MagicMock(),
        entity_extractor=MagicMock(),
        entity_validator=MagicMock()
    )
    
    final_state = {
        "current_question": "What date would you like?",
        "needed_entities": ["date"]
    }
    
    response_type = service._determine_response_type(final_state)
    
    print(f"Response type: {response_type}")
    assert response_type == "question"
    print("✅ Test passed: Response type is 'question'")


def test_determine_response_type_confirmation():
    """Test: Determine response type (confirmation)"""
    print("\n" + "="*80)
    print("TEST 3: Determine Response Type (Confirmation)")
    print("="*80)
    
    mock_db = AsyncMock()
    service = SlotFillingService(
        db=mock_db,
        classifier=MagicMock(),
        dialog_manager=MagicMock(),
        question_generator=MagicMock(),
        entity_extractor=MagicMock(),
        entity_validator=MagicMock()
    )
    
    final_state = {
        "confirmation_message": "Let me confirm: You want to book AC service?",
        "needed_entities": []
    }
    
    response_type = service._determine_response_type(final_state)
    
    print(f"Response type: {response_type}")
    assert response_type == "confirmation"
    print("✅ Test passed: Response type is 'confirmation'")


def test_determine_response_type_error():
    """Test: Determine response type (error)"""
    print("\n" + "="*80)
    print("TEST 4: Determine Response Type (Error)")
    print("="*80)
    
    mock_db = AsyncMock()
    service = SlotFillingService(
        db=mock_db,
        classifier=MagicMock(),
        dialog_manager=MagicMock(),
        question_generator=MagicMock(),
        entity_extractor=MagicMock(),
        entity_validator=MagicMock()
    )
    
    final_state = {
        "error": {"message": "Something went wrong"}
    }
    
    response_type = service._determine_response_type(final_state)
    
    print(f"Response type: {response_type}")
    assert response_type == "error"
    print("✅ Test passed: Response type is 'error'")


def test_determine_response_type_ready_for_agent():
    """Test: Determine response type (ready for agent)"""
    print("\n" + "="*80)
    print("TEST 5: Determine Response Type (Ready for Agent)")
    print("="*80)
    
    mock_db = AsyncMock()
    service = SlotFillingService(
        db=mock_db,
        classifier=MagicMock(),
        dialog_manager=MagicMock(),
        question_generator=MagicMock(),
        entity_extractor=MagicMock(),
        entity_validator=MagicMock()
    )
    
    final_state = {
        "next_graph": "agent_execution",
        "needed_entities": []
    }
    
    response_type = service._determine_response_type(final_state)
    
    print(f"Response type: {response_type}")
    assert response_type == "ready_for_agent"
    print("✅ Test passed: Response type is 'ready_for_agent'")


def test_build_response():
    """Test: Build response from final state"""
    print("\n" + "="*80)
    print("TEST 6: Build Response from Final State")
    print("="*80)
    
    mock_db = AsyncMock()
    service = SlotFillingService(
        db=mock_db,
        classifier=MagicMock(),
        dialog_manager=MagicMock(),
        question_generator=MagicMock(),
        entity_extractor=MagicMock(),
        entity_validator=MagicMock()
    )
    
    final_state = {
        "final_response": "What date would you like?",
        "current_question": "What date would you like?",
        "collected_entities": {"service_type": "ac"},
        "needed_entities": ["date", "time"],
        "primary_intent": "booking_management",
        "intent_confidence": 0.95,
        "is_follow_up": False,
        "dialog_state_type": "collecting_info",
        "retry_count": 0
    }
    
    response = service._build_response(final_state)
    
    print(f"Response: {response}")
    assert response.final_response == "What date would you like?"
    assert response.response_type == "question"
    assert response.collected_entities == {"service_type": "ac"}
    assert response.needed_entities == ["date", "time"]
    assert response.should_trigger_agent == False
    assert response.metadata["intent"] == "booking_management"
    print("✅ Test passed: Response built correctly")


def test_build_response_ready_for_agent():
    """Test: Build response when ready for agent"""
    print("\n" + "="*80)
    print("TEST 7: Build Response (Ready for Agent)")
    print("="*80)
    
    mock_db = AsyncMock()
    service = SlotFillingService(
        db=mock_db,
        classifier=MagicMock(),
        dialog_manager=MagicMock(),
        question_generator=MagicMock(),
        entity_extractor=MagicMock(),
        entity_validator=MagicMock()
    )
    
    final_state = {
        "final_response": "Great! Let me book that for you.",
        "collected_entities": {
            "service_type": "ac",
            "date": "2025-10-15",
            "time": "14:00",
            "location": "Mumbai"
        },
        "needed_entities": [],
        "next_graph": "agent_execution",
        "primary_intent": "booking_management",
        "intent_confidence": 0.95
    }
    
    response = service._build_response(final_state)
    
    print(f"Response: {response}")
    assert response.should_trigger_agent == True
    assert len(response.needed_entities) == 0
    assert len(response.collected_entities) == 4
    print("✅ Test passed: Response indicates ready for agent execution")


def test_get_conversation_history_empty():
    """Test: Get conversation history (empty)"""
    print("\n" + "="*80)
    print("TEST 8: Get Conversation History (Empty)")
    print("="*80)
    
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))))
    
    service = SlotFillingService(
        db=mock_db,
        classifier=MagicMock(),
        dialog_manager=MagicMock(),
        question_generator=MagicMock(),
        entity_extractor=MagicMock(),
        entity_validator=MagicMock()
    )
    
    history = asyncio.run(service._get_conversation_history("session_1"))
    
    print(f"History: {history}")
    assert isinstance(history, list)
    print("✅ Test passed: Empty history returned as list")


def test_response_metadata():
    """Test: Response includes comprehensive metadata"""
    print("\n" + "="*80)
    print("TEST 9: Response Includes Comprehensive Metadata")
    print("="*80)
    
    mock_db = AsyncMock()
    service = SlotFillingService(
        db=mock_db,
        classifier=MagicMock(),
        dialog_manager=MagicMock(),
        question_generator=MagicMock(),
        entity_extractor=MagicMock(),
        entity_validator=MagicMock()
    )
    
    final_state = {
        "final_response": "What date?",
        "current_question": "What date?",
        "collected_entities": {},
        "needed_entities": ["date"],
        "primary_intent": "booking_management",
        "intent_confidence": 0.95,
        "is_follow_up": False,
        "dialog_state_type": "collecting_info",
        "retry_count": 0,
        "provenance": {"source": "pattern_match"}
    }
    
    response = service._build_response(final_state)
    
    print(f"Metadata: {response.metadata}")
    assert "intent" in response.metadata
    assert "intent_confidence" in response.metadata
    assert "is_follow_up" in response.metadata
    assert "dialog_state_type" in response.metadata
    assert "retry_count" in response.metadata
    assert "timestamp" in response.metadata
    assert "provenance" in response.metadata
    print("✅ Test passed: Response includes comprehensive metadata")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("SLOT-FILLING ORCHESTRATOR SERVICE - TEST SUITE")
    print("="*80)
    
    tests = [
        test_service_initialization,
        test_determine_response_type_question,
        test_determine_response_type_confirmation,
        test_determine_response_type_error,
        test_determine_response_type_ready_for_agent,
        test_build_response,
        test_build_response_ready_for_agent,
        test_get_conversation_history_empty,
        test_response_metadata,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ Test failed: {test.__name__}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ Test error: {test.__name__}")
            print(f"   Error: {e}")
            failed += 1
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print("="*80)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

