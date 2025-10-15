"""
Unit Tests for Slot-Filling Graph Nodes

Tests each node function independently with mocked dependencies.

Test Coverage:
- classify_intent_node
- check_follow_up_node
- extract_entity_node
- validate_entity_node
- update_dialog_state_node
- determine_needed_entities_node
- generate_question_node
- handle_error_node
- Conditional edge functions
"""

import sys
import os
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graphs.slot_filling_graph import (
    classify_intent_node,
    check_follow_up_node,
    extract_entity_node,
    validate_entity_node,
    update_dialog_state_node,
    determine_needed_entities_node,
    generate_question_node,
    handle_error_node,
    should_route_to_error,
    is_follow_up_response,
    are_all_entities_collected,
    is_validation_successful,
    should_trigger_agent_execution
)
from src.nlp.intent.config import IntentType, EntityType


def test_classify_intent_node_success():
    """Test: classify_intent_node with successful classification"""
    print("\n" + "="*80)
    print("TEST 1: Classify Intent Node - Success")
    print("="*80)
    
    # Mock services
    mock_classifier = AsyncMock()
    mock_dialog_manager = AsyncMock()
    
    # Mock intent result
    mock_intent_result = MagicMock()
    mock_intent_result.primary_intent = IntentType.BOOKING_MANAGEMENT
    mock_intent_result.confidence = 0.95

    # Mock intent with entities property
    mock_intent = MagicMock()
    mock_intent.confidence = 0.95
    mock_intent.entities = {"service_type": "ac"}  # This is now a property that returns dict

    mock_intent_result.intents = [mock_intent]
    mock_intent_result.model_dump = MagicMock(return_value={"primary_intent": "booking_management"})
    
    mock_classifier.classify = AsyncMock(return_value=(mock_intent_result, "pattern"))
    mock_dialog_manager.get_active_state = AsyncMock(return_value=None)
    
    # State
    state = {
        "session_id": "test_session",
        "current_message": "I want to book AC service",
        "conversation_history": [],
        "metadata": {}
    }
    
    # Execute
    result = asyncio.run(classify_intent_node(state, mock_classifier, mock_dialog_manager))
    
    print(f"Result: {result}")
    assert result["primary_intent"] == IntentType.BOOKING_MANAGEMENT
    assert result["intent_confidence"] == 0.95
    assert result["classification_method"] == "pattern"
    assert "error" not in result
    print("✅ Test passed: Intent classified successfully")


def test_classify_intent_node_error():
    """Test: classify_intent_node with error"""
    print("\n" + "="*80)
    print("TEST 2: Classify Intent Node - Error Handling")
    print("="*80)
    
    # Mock services
    mock_classifier = AsyncMock()
    mock_dialog_manager = AsyncMock()
    
    mock_classifier.classify = AsyncMock(side_effect=Exception("Classification failed"))
    mock_dialog_manager.get_active_state = AsyncMock(return_value=None)
    
    # State
    state = {
        "session_id": "test_session",
        "current_message": "test",
        "metadata": {}
    }
    
    # Execute
    result = asyncio.run(classify_intent_node(state, mock_classifier, mock_dialog_manager))
    
    print(f"Result: {result}")
    assert "error" in result
    assert result["error"]["type"] == "IntentClassificationError"
    print("✅ Test passed: Error handled correctly")


def test_check_follow_up_node_success():
    """Test: check_follow_up_node with follow-up detected"""
    print("\n" + "="*80)
    print("TEST 3: Check Follow-Up Node - Follow-Up Detected")
    print("="*80)
    
    # Mock service
    mock_dialog_manager = AsyncMock()
    
    # Mock follow-up result
    mock_follow_up_result = MagicMock()
    mock_follow_up_result.is_follow_up = True
    mock_follow_up_result.confidence = 0.9
    mock_follow_up_result.expected_entity = "date"
    
    mock_dialog_manager.is_follow_up_response = AsyncMock(return_value=mock_follow_up_result)
    
    # State
    state = {
        "session_id": "test_session",
        "current_message": "tomorrow",
        "metadata": {}
    }
    
    # Execute
    result = asyncio.run(check_follow_up_node(state, mock_dialog_manager))
    
    print(f"Result: {result}")
    assert result["is_follow_up"] == True
    assert result["follow_up_confidence"] == 0.9
    assert result["expected_entity"] == "date"
    print("✅ Test passed: Follow-up detected correctly")


def test_extract_entity_node_success():
    """Test: extract_entity_node with successful extraction"""
    print("\n" + "="*80)
    print("TEST 4: Extract Entity Node - Success")
    print("="*80)
    
    # Mock service
    mock_extractor = AsyncMock()
    
    # Mock extraction result
    mock_extraction_result = MagicMock()
    mock_extraction_result.entity_type = "date"
    mock_extraction_result.entity_value = "tomorrow"
    mock_extraction_result.normalized_value = "2025-10-10"
    mock_extraction_result.confidence = 0.95
    mock_extraction_result.model_dump = MagicMock(return_value={
        "entity_type": "date",
        "entity_value": "tomorrow",
        "normalized_value": "2025-10-10"
    })
    
    mock_extractor.extract_from_follow_up = AsyncMock(return_value=mock_extraction_result)
    
    # State
    state = {
        "current_message": "tomorrow",
        "expected_entity": "date",
        "collected_entities": {},
        "user_id": 1,
        "metadata": {}
    }
    
    # Execute
    result = asyncio.run(extract_entity_node(state, mock_extractor))
    
    print(f"Result: {result}")
    assert "extracted_entity" in result
    assert result["extracted_entity"]["entity_type"] == "date"
    print("✅ Test passed: Entity extracted successfully")


def test_validate_entity_node_valid():
    """Test: validate_entity_node with valid entity"""
    print("\n" + "="*80)
    print("TEST 5: Validate Entity Node - Valid Entity")
    print("="*80)
    
    # Mock service
    mock_validator = AsyncMock()
    
    # Mock validation result
    mock_validation_result = MagicMock()
    mock_validation_result.is_valid = True
    mock_validation_result.normalized_value = "2025-10-10"
    mock_validation_result.model_dump = MagicMock(return_value={
        "is_valid": True,
        "normalized_value": "2025-10-10"
    })
    
    mock_validator.validate = AsyncMock(return_value=mock_validation_result)
    
    # State
    state = {
        "extracted_entity": {
            "entity_type": "date",
            "entity_value": "tomorrow",
            "normalized_value": "2025-10-10"
        },
        "user_id": 1,
        "collected_entities": {},
        "metadata": {}
    }
    
    # Execute
    result = asyncio.run(validate_entity_node(state, mock_validator))
    
    print(f"Result: {result}")
    assert result["validation_result"]["is_valid"] == True
    print("✅ Test passed: Entity validated successfully")


def test_validate_entity_node_invalid():
    """Test: validate_entity_node with invalid entity"""
    print("\n" + "="*80)
    print("TEST 6: Validate Entity Node - Invalid Entity")
    print("="*80)
    
    # Mock service
    mock_validator = AsyncMock()
    
    # Mock validation result
    mock_validation_result = MagicMock()
    mock_validation_result.is_valid = False
    mock_validation_result.error_message = "Date must be in the future"
    mock_validation_result.suggestions = ["today", "tomorrow"]
    mock_validation_result.model_dump = MagicMock(return_value={
        "is_valid": False,
        "error_message": "Date must be in the future",
        "suggestions": ["today", "tomorrow"]
    })
    
    mock_validator.validate = AsyncMock(return_value=mock_validation_result)
    
    # State
    state = {
        "extracted_entity": {
            "entity_type": "date",
            "entity_value": "yesterday",
            "normalized_value": "2025-10-08"
        },
        "user_id": 1,
        "collected_entities": {},
        "metadata": {}
    }
    
    # Execute
    result = asyncio.run(validate_entity_node(state, mock_validator))
    
    print(f"Result: {result}")
    assert result["validation_result"]["is_valid"] == False
    assert "error_message" in result["validation_result"]
    print("✅ Test passed: Invalid entity detected")


def test_update_dialog_state_node_success():
    """Test: update_dialog_state_node with valid entity"""
    print("\n" + "="*80)
    print("TEST 7: Update Dialog State Node - Success")
    print("="*80)
    
    # Mock service
    mock_dialog_manager = AsyncMock()
    mock_dialog_manager.add_entity = AsyncMock()
    mock_dialog_manager.remove_needed_entity = AsyncMock()
    
    # State
    state = {
        "session_id": "test_session",
        "validation_result": {
            "is_valid": True,
            "normalized_value": "2025-10-10"
        },
        "extracted_entity": {
            "entity_type": "date",
            "entity_value": "tomorrow"
        },
        "collected_entities": {"service_type": "ac"},
        "needed_entities": ["date", "time"],
        "metadata": {}
    }
    
    # Execute
    result = asyncio.run(update_dialog_state_node(state, mock_dialog_manager))
    
    print(f"Result: {result}")
    assert "date" in result["collected_entities"]
    assert result["collected_entities"]["date"] == "2025-10-10"
    assert "date" not in result["needed_entities"]
    print("✅ Test passed: Dialog state updated successfully")


def test_determine_needed_entities_node():
    """Test: determine_needed_entities_node"""
    print("\n" + "="*80)
    print("TEST 8: Determine Needed Entities Node")
    print("="*80)
    
    # State
    state = {
        "primary_intent": "booking_management",
        "collected_entities": {"action": "book", "service_type": "ac"},
        "metadata": {}
    }
    
    # Execute
    result = asyncio.run(determine_needed_entities_node(state))
    
    print(f"Result: {result}")
    assert "needed_entities" in result
    # For booking, we need: service_type, date, time, location
    # We have: service_type
    # So we need: date, time, location
    assert "date" in result["needed_entities"]
    assert "time" in result["needed_entities"]
    assert "location" in result["needed_entities"]
    print("✅ Test passed: Needed entities determined correctly")


def test_generate_question_node():
    """Test: generate_question_node"""
    print("\n" + "="*80)
    print("TEST 9: Generate Question Node")
    print("="*80)
    
    # Mock service
    mock_question_generator = MagicMock()
    mock_question_generator.generate = MagicMock(return_value="What date would you like?")
    
    # State
    state = {
        "needed_entities": ["date", "time"],
        "primary_intent": "booking_management",
        "collected_entities": {"service_type": "ac"},
        "metadata": {}
    }
    
    # Execute
    result = asyncio.run(generate_question_node(state, mock_question_generator))
    
    print(f"Result: {result}")
    assert "current_question" in result
    assert result["response_type"] == "question"
    assert result["expected_entity"] == "date"
    print("✅ Test passed: Question generated successfully")


def test_generate_question_node_confirmation():
    """Test: generate_question_node with all entities collected (confirmation)"""
    print("\n" + "="*80)
    print("TEST 10: Generate Question Node - Confirmation")
    print("="*80)
    
    # Mock service
    mock_question_generator = MagicMock()
    mock_question_generator.generate_confirmation = MagicMock(
        return_value="Let me confirm: You want to book AC service on 2025-10-10 at 14:00 in Mumbai. Should I proceed?"
    )
    
    # State
    state = {
        "needed_entities": [],
        "primary_intent": "booking_management",
        "collected_entities": {
            "service_type": "ac",
            "date": "2025-10-10",
            "time": "14:00",
            "location": "Mumbai"
        },
        "metadata": {}
    }
    
    # Execute
    result = asyncio.run(generate_question_node(state, mock_question_generator))
    
    print(f"Result: {result}")
    assert "confirmation_message" in result
    assert result["response_type"] == "confirmation"
    print("✅ Test passed: Confirmation generated successfully")


def test_handle_error_node():
    """Test: handle_error_node"""
    print("\n" + "="*80)
    print("TEST 11: Handle Error Node")
    print("="*80)
    
    # State with error
    state = {
        "error": {
            "type": "IntentClassificationError",
            "message": "Failed to classify intent",
            "node": "classify_intent"
        },
        "metadata": {}
    }
    
    # Execute
    result = asyncio.run(handle_error_node(state))
    
    print(f"Result: {result}")
    assert "final_response" in result
    assert result["response_type"] == "error"
    assert result["should_end"] == True
    print("✅ Test passed: Error handled gracefully")


def test_conditional_edge_should_route_to_error():
    """Test: should_route_to_error conditional edge"""
    print("\n" + "="*80)
    print("TEST 12: Conditional Edge - Should Route to Error")
    print("="*80)
    
    # State with error
    state_with_error = {"error": {"message": "test error"}}
    result = should_route_to_error(state_with_error)
    print(f"With error: {result}")
    assert result == "error"
    
    # State without error
    state_without_error = {}
    result = should_route_to_error(state_without_error)
    print(f"Without error: {result}")
    assert result == "continue"
    
    print("✅ Test passed: Error routing works correctly")


def test_conditional_edge_is_follow_up():
    """Test: is_follow_up_response conditional edge"""
    print("\n" + "="*80)
    print("TEST 13: Conditional Edge - Is Follow-Up Response")
    print("="*80)
    
    # Follow-up state
    follow_up_state = {"is_follow_up": True, "follow_up_confidence": 0.9}
    result = is_follow_up_response(follow_up_state)
    print(f"Follow-up: {result}")
    assert result == "follow_up"
    
    # New intent state
    new_intent_state = {"is_follow_up": False, "follow_up_confidence": 0.3}
    result = is_follow_up_response(new_intent_state)
    print(f"New intent: {result}")
    assert result == "new_intent"
    
    print("✅ Test passed: Follow-up detection works correctly")


def test_conditional_edge_all_entities_collected():
    """Test: are_all_entities_collected conditional edge"""
    print("\n" + "="*80)
    print("TEST 14: Conditional Edge - All Entities Collected")
    print("="*80)
    
    # All collected
    all_collected_state = {"needed_entities": []}
    result = are_all_entities_collected(all_collected_state)
    print(f"All collected: {result}")
    assert result == "all_collected"
    
    # More needed
    more_needed_state = {"needed_entities": ["date", "time"]}
    result = are_all_entities_collected(more_needed_state)
    print(f"More needed: {result}")
    assert result == "more_needed"
    
    print("✅ Test passed: Entity collection check works correctly")


def test_conditional_edge_validation_successful():
    """Test: is_validation_successful conditional edge"""
    print("\n" + "="*80)
    print("TEST 15: Conditional Edge - Validation Successful")
    print("="*80)
    
    # Valid
    valid_state = {"validation_result": {"is_valid": True}}
    result = is_validation_successful(valid_state)
    print(f"Valid: {result}")
    assert result == "valid"
    
    # Invalid
    invalid_state = {"validation_result": {"is_valid": False}}
    result = is_validation_successful(invalid_state)
    print(f"Invalid: {result}")
    assert result == "invalid"
    
    print("✅ Test passed: Validation check works correctly")


def run_all_tests():
    """Run all unit tests"""
    print("\n" + "="*80)
    print("SLOT-FILLING GRAPH - UNIT TEST SUITE")
    print("="*80)
    
    tests = [
        test_classify_intent_node_success,
        test_classify_intent_node_error,
        test_check_follow_up_node_success,
        test_extract_entity_node_success,
        test_validate_entity_node_valid,
        test_validate_entity_node_invalid,
        test_update_dialog_state_node_success,
        test_determine_needed_entities_node,
        test_generate_question_node,
        test_generate_question_node_confirmation,
        test_handle_error_node,
        test_conditional_edge_should_route_to_error,
        test_conditional_edge_is_follow_up,
        test_conditional_edge_all_entities_collected,
        test_conditional_edge_validation_successful,
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
        print("\n🎉 ALL UNIT TESTS PASSED!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

