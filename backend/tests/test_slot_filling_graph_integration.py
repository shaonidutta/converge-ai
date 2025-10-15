"""
Integration Tests for Slot-Filling Graph

Tests complete conversation flows with real services (mocked LLM calls).

Test Scenarios:
1. Complete booking flow (happy path)
2. Validation error flow (invalid date)
3. Follow-up detection flow
4. Error handling flow
"""

import sys
import os
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graphs.slot_filling_graph import run_slot_filling_graph
from src.graphs.state import create_initial_state
from src.nlp.intent.classifier import IntentClassifier
from src.services.dialog_state_manager import DialogStateManager
from src.services.question_generator import QuestionGenerator
from src.services.entity_extractor import EntityExtractor
from src.services.entity_validator import EntityValidator
from src.nlp.intent.config import IntentType, EntityType
from src.schemas.intent import IntentClassificationResult, IntentResult


def create_mock_services():
    """Create mocked services for testing"""
    mock_db = AsyncMock()
    
    # Mock classifier
    mock_classifier = AsyncMock()
    
    # Mock dialog manager
    mock_dialog_manager = AsyncMock()
    mock_dialog_manager.get_active_state = AsyncMock(return_value=None)
    mock_dialog_manager.is_follow_up_response = AsyncMock()
    mock_dialog_manager.add_entity = AsyncMock()
    mock_dialog_manager.remove_needed_entity = AsyncMock()
    
    # Real question generator (no LLM calls)
    question_generator = QuestionGenerator()
    
    # Real entity extractor (no LLM calls for pattern matching)
    entity_extractor = EntityExtractor(llm_client=None)
    
    # Real entity validator
    entity_validator = EntityValidator(mock_db)
    
    return mock_db, mock_classifier, mock_dialog_manager, question_generator, entity_extractor, entity_validator


def test_complete_booking_flow():
    """
    Test: Complete booking flow (happy path)
    
    Flow:
    1. User: "I want to book AC service"
    2. System: "What date would you like?"
    3. User: "tomorrow"
    4. System: "What time works best for you?"
    5. User: "2 PM"
    6. System: "What's your location?"
    7. User: "Mumbai"
    8. System: "Let me confirm..."
    """
    print("\n" + "="*80)
    print("INTEGRATION TEST 1: Complete Booking Flow")
    print("="*80)
    
    # Create services
    mock_db, mock_classifier, mock_dialog_manager, question_generator, entity_extractor, entity_validator = create_mock_services()
    
    # Step 1: Initial message "I want to book AC service"
    print("\n--- Step 1: Initial Intent ---")
    
    # Mock intent classification
    import json
    intent_result = IntentClassificationResult(
        primary_intent=IntentType.BOOKING_MANAGEMENT.value,
        intents=[
            IntentResult(
                intent=IntentType.BOOKING_MANAGEMENT.value,
                confidence=0.95,
                entities_json=json.dumps({"action": "book", "service_type": "ac"})
            )
        ],
        context_used=False
    )
    mock_classifier.classify = AsyncMock(return_value=(intent_result, "pattern"))
    
    # Mock follow-up detection (not a follow-up)
    follow_up_result = MagicMock()
    follow_up_result.is_follow_up = False
    follow_up_result.confidence = 0.3
    follow_up_result.expected_entity = None
    mock_dialog_manager.is_follow_up_response = AsyncMock(return_value=follow_up_result)
    
    # Create initial state
    state = create_initial_state(
        user_id=1,
        session_id="test_session_1",
        current_message="I want to book AC service",
        channel="web",
        conversation_history=[]
    )
    
    # Run graph
    final_state = asyncio.run(run_slot_filling_graph(
        state=state,
        db=mock_db,
        classifier=mock_classifier,
        dialog_manager=mock_dialog_manager,
        question_generator=question_generator,
        entity_extractor=entity_extractor,
        entity_validator=entity_validator
    ))
    
    print(f"Final response: {final_state.get('final_response')}")
    print(f"Response type: {final_state.get('response_type')}")
    print(f"Collected entities: {final_state.get('collected_entities')}")
    print(f"Needed entities: {final_state.get('needed_entities')}")
    
    # Assertions
    assert final_state.get('response_type') == 'question'
    assert 'date' in final_state.get('final_response', '').lower()
    assert final_state.get('collected_entities', {}).get('service_type') == 'ac'
    assert 'date' in final_state.get('needed_entities', [])
    
    print("✅ Step 1 passed: System asks for date")
    
    # Step 2: User provides date "tomorrow"
    print("\n--- Step 2: Provide Date ---")

    # Mock follow-up detection (is a follow-up)
    follow_up_result.is_follow_up = True
    follow_up_result.confidence = 0.9
    follow_up_result.expected_entity = "date"

    # Create new state for next turn (preserve collected entities)
    state = create_initial_state(
        user_id=1,
        session_id="test_session_1",
        current_message="tomorrow",
        channel="web",
        conversation_history=[
            {"role": "user", "content": "I want to book AC service"},
            {"role": "assistant", "content": final_state.get('final_response')}
        ]
    )
    # Preserve collected entities from previous turn
    state['collected_entities'] = final_state.get('collected_entities', {})
    state['needed_entities'] = final_state.get('needed_entities', [])
    state['primary_intent'] = final_state.get('primary_intent')

    # Run graph
    final_state = asyncio.run(run_slot_filling_graph(
        state=state,
        db=mock_db,
        classifier=mock_classifier,
        dialog_manager=mock_dialog_manager,
        question_generator=question_generator,
        entity_extractor=entity_extractor,
        entity_validator=entity_validator
    ))
    
    print(f"Final response: {final_state.get('final_response')}")
    print(f"Collected entities: {final_state.get('collected_entities')}")
    print(f"Needed entities: {final_state.get('needed_entities')}")
    
    # Assertions
    assert final_state.get('response_type') == 'question'
    assert 'time' in final_state.get('final_response', '').lower()
    assert 'date' in final_state.get('collected_entities', {})
    assert 'time' in final_state.get('needed_entities', [])
    
    print("✅ Step 2 passed: Date collected, system asks for time")
    
    # Step 3: User provides time "2 PM"
    print("\n--- Step 3: Provide Time ---")

    follow_up_result.expected_entity = "time"

    # Create new state for next turn
    state = create_initial_state(
        user_id=1,
        session_id="test_session_1",
        current_message="2 PM",
        channel="web",
        conversation_history=[]
    )
    # Preserve collected entities (make a copy)
    state['collected_entities'] = final_state.get('collected_entities', {}).copy()
    state['needed_entities'] = final_state.get('needed_entities', []).copy()
    state['primary_intent'] = final_state.get('primary_intent')

    print(f"DEBUG Step 3 - Preserved entities: {state['collected_entities']}")

    final_state = asyncio.run(run_slot_filling_graph(
        state=state,
        db=mock_db,
        classifier=mock_classifier,
        dialog_manager=mock_dialog_manager,
        question_generator=question_generator,
        entity_extractor=entity_extractor,
        entity_validator=entity_validator
    ))
    
    print(f"Final response: {final_state.get('final_response')}")
    print(f"Collected entities: {final_state.get('collected_entities')}")
    print(f"Needed entities: {final_state.get('needed_entities')}")
    
    # Assertions
    assert final_state.get('response_type') == 'question'
    assert 'location' in final_state.get('final_response', '').lower() or 'pincode' in final_state.get('final_response', '').lower()
    assert 'time' in final_state.get('collected_entities', {})
    assert 'location' in final_state.get('needed_entities', [])
    
    print("✅ Step 3 passed: Time collected, system asks for location")
    
    # Step 4: User provides location "Mumbai"
    print("\n--- Step 4: Provide Location ---")

    follow_up_result.expected_entity = "location"

    # Create new state for next turn
    state = create_initial_state(
        user_id=1,
        session_id="test_session_1",
        current_message="Mumbai",
        channel="web",
        conversation_history=[]
    )
    # Preserve collected entities
    state['collected_entities'] = final_state.get('collected_entities', {})
    state['needed_entities'] = final_state.get('needed_entities', [])
    state['primary_intent'] = final_state.get('primary_intent')

    final_state = asyncio.run(run_slot_filling_graph(
        state=state,
        db=mock_db,
        classifier=mock_classifier,
        dialog_manager=mock_dialog_manager,
        question_generator=question_generator,
        entity_extractor=entity_extractor,
        entity_validator=entity_validator
    ))
    
    print(f"Final response: {final_state.get('final_response')}")
    print(f"Response type: {final_state.get('response_type')}")
    print(f"Collected entities: {final_state.get('collected_entities')}")
    print(f"Needed entities: {final_state.get('needed_entities')}")
    
    # Assertions
    assert final_state.get('response_type') == 'confirmation'
    assert 'confirm' in final_state.get('final_response', '').lower()
    assert 'location' in final_state.get('collected_entities', {})
    assert len(final_state.get('needed_entities', [])) == 0
    
    print("✅ Step 4 passed: All entities collected, system asks for confirmation")
    print("\n🎉 INTEGRATION TEST 1 PASSED: Complete booking flow works!")


def test_validation_error_flow():
    """
    Test: Validation error flow

    Flow:
    1. User: "I want to book AC service"
    2. System: "What date would you like?"
    3. User: "2026-12-31" (invalid - too far in future, beyond 90-day window)
    4. System: "Sorry, date must be within 90 days. Please try again..."
    """
    print("\n" + "="*80)
    print("INTEGRATION TEST 2: Validation Error Flow")
    print("="*80)
    
    # Create services
    mock_db, mock_classifier, mock_dialog_manager, question_generator, entity_extractor, entity_validator = create_mock_services()
    
    # Step 1: Initial message
    print("\n--- Step 1: Initial Intent ---")
    
    import json
    intent_result = IntentClassificationResult(
        primary_intent=IntentType.BOOKING_MANAGEMENT.value,
        intents=[
            IntentResult(
                intent=IntentType.BOOKING_MANAGEMENT.value,
                confidence=0.95,
                entities_json=json.dumps({"action": "book", "service_type": "ac"})
            )
        ],
        context_used=False
    )
    mock_classifier.classify = AsyncMock(return_value=(intent_result, "pattern"))
    
    follow_up_result = MagicMock()
    follow_up_result.is_follow_up = False
    follow_up_result.confidence = 0.3
    mock_dialog_manager.is_follow_up_response = AsyncMock(return_value=follow_up_result)
    
    state = create_initial_state(
        user_id=1,
        session_id="test_session_2",
        current_message="I want to book AC service",
        channel="web",
        conversation_history=[]
    )
    
    final_state = asyncio.run(run_slot_filling_graph(
        state=state,
        db=mock_db,
        classifier=mock_classifier,
        dialog_manager=mock_dialog_manager,
        question_generator=question_generator,
        entity_extractor=entity_extractor,
        entity_validator=entity_validator
    ))
    
    print(f"System asks: {final_state.get('final_response')}")
    assert 'date' in final_state.get('final_response', '').lower()
    print("✅ Step 1 passed")
    
    # Step 2: User provides invalid date "2026-12-31" (too far in future)
    print("\n--- Step 2: Provide Invalid Date ---")

    follow_up_result.is_follow_up = True
    follow_up_result.confidence = 0.9
    follow_up_result.expected_entity = "date"

    # Create new state for next turn
    state = create_initial_state(
        user_id=1,
        session_id="test_session_2",
        current_message="2026-12-31",
        channel="web",
        conversation_history=[]
    )
    # Preserve collected entities
    state['collected_entities'] = final_state.get('collected_entities', {}).copy()
    state['needed_entities'] = final_state.get('needed_entities', []).copy()
    state['primary_intent'] = final_state.get('primary_intent')

    final_state = asyncio.run(run_slot_filling_graph(
        state=state,
        db=mock_db,
        classifier=mock_classifier,
        dialog_manager=mock_dialog_manager,
        question_generator=question_generator,
        entity_extractor=entity_extractor,
        entity_validator=entity_validator
    ))
    
    print(f"System response: {final_state.get('final_response')}")
    print(f"Response type: {final_state.get('response_type')}")
    print(f"Collected entities: {final_state.get('collected_entities')}")

    # Assertions
    # The system should either:
    # 1. Show a validation error and re-ask (response_type='question' with error message)
    # 2. Or route to error node (response_type='error')
    # In both cases, the invalid date should NOT be collected
    assert final_state.get('response_type') in ['question', 'error']
    assert 'date' not in final_state.get('collected_entities', {}) or final_state.get('collected_entities', {}).get('date') != '2026-12-31'

    print("✅ Step 2 passed: Invalid date not collected, system handles gracefully")
    print("\n🎉 INTEGRATION TEST 2 PASSED: Validation error flow works!")


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*80)
    print("SLOT-FILLING GRAPH - INTEGRATION TEST SUITE")
    print("="*80)
    
    tests = [
        test_complete_booking_flow,
        test_validation_error_flow,
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
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*80)
    print("INTEGRATION TEST SUMMARY")
    print("="*80)
    print(f"Total tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print("="*80)
    
    if failed == 0:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

