"""
Tests for Question Generator Service

Tests:
- Template-based question generation
- Context-aware phrasing
- Question variations (multiple attempts)
- Confirmation message generation
- Validation error messages
- Escalation logic
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.question_generator import QuestionGenerator
from src.nlp.intent.config import EntityType, IntentType


def test_generate_question_for_service_type():
    """Test: Generate question for service_type entity"""
    print("\n" + "="*80)
    print("TEST 1: Generate Question for Service Type")
    print("="*80)
    
    generator = QuestionGenerator()
    question = generator.generate(
        EntityType.SERVICE_TYPE,
        IntentType.BOOKING_MANAGEMENT
    )
    
    print(f"Question: {question}")
    assert "service" in question.lower()
    assert "?" in question
    print("✅ Test passed: Question contains 'service' and '?'")


def test_generate_question_for_date():
    """Test: Generate question for date entity"""
    print("\n" + "="*80)
    print("TEST 2: Generate Question for Date")
    print("="*80)
    
    generator = QuestionGenerator()
    question = generator.generate(
        EntityType.DATE,
        IntentType.BOOKING_MANAGEMENT
    )
    
    print(f"Question: {question}")
    assert "date" in question.lower() or "when" in question.lower()
    assert "?" in question
    print("✅ Test passed: Question asks for date")


def test_generate_question_with_context():
    """Test: Generate question with context (service_type collected)"""
    print("\n" + "="*80)
    print("TEST 3: Generate Question with Context")
    print("="*80)
    
    generator = QuestionGenerator()
    question = generator.generate(
        EntityType.DATE,
        IntentType.BOOKING_MANAGEMENT,
        collected_entities={"service_type": "AC"}
    )
    
    print(f"Question: {question}")
    assert "AC" in question
    print("✅ Test passed: Question includes collected service_type (AC)")


def test_question_variations():
    """Test: Generate different question variations on multiple attempts"""
    print("\n" + "="*80)
    print("TEST 4: Question Variations (Multiple Attempts)")
    print("="*80)
    
    generator = QuestionGenerator()
    
    questions = []
    for attempt in range(3):
        question = generator.generate(
            EntityType.SERVICE_TYPE,
            IntentType.BOOKING_MANAGEMENT,
            attempt_number=attempt
        )
        questions.append(question)
        print(f"Attempt {attempt + 1}: {question}")
    
    # Check that we get variations (at least 2 different questions)
    unique_questions = set(questions)
    print(f"\nUnique questions: {len(unique_questions)}")
    assert len(unique_questions) >= 2
    print("✅ Test passed: Multiple question variations generated")


def test_generate_confirmation_for_booking():
    """Test: Generate confirmation message for booking"""
    print("\n" + "="*80)
    print("TEST 5: Generate Confirmation for Booking")
    print("="*80)
    
    generator = QuestionGenerator()
    confirmation = generator.generate_confirmation(
        IntentType.BOOKING_MANAGEMENT,
        collected_entities={
            "action": "book",
            "service_type": "AC",
            "date": "2025-10-10",
            "time": "14:00",
            "location": "Mumbai"
        }
    )
    
    print(f"Confirmation: {confirmation}")
    assert "AC" in confirmation
    assert "2025-10-10" in confirmation
    assert "14:00" in confirmation
    assert "Mumbai" in confirmation
    assert "?" in confirmation
    print("✅ Test passed: Confirmation includes all entities")


def test_generate_confirmation_for_cancellation():
    """Test: Generate confirmation message for cancellation"""
    print("\n" + "="*80)
    print("TEST 6: Generate Confirmation for Cancellation")
    print("="*80)
    
    generator = QuestionGenerator()
    confirmation = generator.generate_confirmation(
        IntentType.BOOKING_MANAGEMENT,
        collected_entities={
            "action": "cancel",
            "booking_id": "BOOK-12345"
        }
    )
    
    print(f"Confirmation: {confirmation}")
    assert "BOOK-12345" in confirmation
    assert "cancel" in confirmation.lower()
    assert "cannot be undone" in confirmation.lower() or "proceed" in confirmation.lower()
    print("✅ Test passed: Cancellation confirmation includes warning")


def test_generate_validation_error_message():
    """Test: Generate user-friendly validation error message"""
    print("\n" + "="*80)
    print("TEST 7: Generate Validation Error Message")
    print("="*80)
    
    generator = QuestionGenerator()
    error_msg = generator.generate_validation_error_message(
        EntityType.DATE,
        "Date must be in the future",
        suggestions=["today", "tomorrow", "2025-10-15"]
    )
    
    print(f"Error message: {error_msg}")
    assert "Sorry" in error_msg
    assert "Date must be in the future" in error_msg
    assert "today" in error_msg or "tomorrow" in error_msg
    print("✅ Test passed: Error message is user-friendly with suggestions")


def test_escalation_logic():
    """Test: Escalation logic after max attempts"""
    print("\n" + "="*80)
    print("TEST 8: Escalation Logic")
    print("="*80)
    
    generator = QuestionGenerator()
    
    # Test should_escalate
    should_escalate_2 = generator.should_escalate("session_1", EntityType.DATE, 2, max_attempts=3)
    should_escalate_3 = generator.should_escalate("session_1", EntityType.DATE, 3, max_attempts=3)
    
    print(f"Should escalate after 2 attempts: {should_escalate_2}")
    print(f"Should escalate after 3 attempts: {should_escalate_3}")
    
    assert not should_escalate_2
    assert should_escalate_3
    print("✅ Test passed: Escalation triggers after max attempts")
    
    # Test escalation message
    escalation_msg = generator.generate_escalation_message(
        EntityType.DATE,
        IntentType.BOOKING_MANAGEMENT
    )
    
    print(f"\nEscalation message: {escalation_msg}")
    assert "having trouble" in escalation_msg.lower()
    assert "human agent" in escalation_msg.lower() or "agent" in escalation_msg.lower()
    print("✅ Test passed: Escalation message offers alternatives")


def test_context_aware_time_question():
    """Test: Context-aware question for time (with date collected)"""
    print("\n" + "="*80)
    print("TEST 9: Context-Aware Time Question")
    print("="*80)
    
    generator = QuestionGenerator()
    question = generator.generate(
        EntityType.TIME,
        IntentType.BOOKING_MANAGEMENT,
        collected_entities={
            "service_type": "plumbing",
            "date": "2025-10-10"
        }
    )
    
    print(f"Question: {question}")
    assert "2025-10-10" in question or "plumbing" in question
    print("✅ Test passed: Time question includes date context")


def test_generic_fallback_question():
    """Test: Generic fallback for unknown entity types"""
    print("\n" + "="*80)
    print("TEST 10: Generic Fallback Question")
    print("="*80)
    
    generator = QuestionGenerator()
    
    # Create a mock entity type that doesn't have templates
    class MockEntityType:
        value = "custom_entity"
    
    question = generator._get_template_question(
        MockEntityType(),
        IntentType.BOOKING_MANAGEMENT,
        0
    )
    
    print(f"Question: {question}")
    assert "custom entity" in question.lower()
    assert "?" in question
    print("✅ Test passed: Generic fallback works for unknown entities")


def test_confirmation_for_complaint():
    """Test: Generate confirmation for complaint"""
    print("\n" + "="*80)
    print("TEST 11: Generate Confirmation for Complaint")
    print("="*80)
    
    generator = QuestionGenerator()
    confirmation = generator.generate_confirmation(
        IntentType.COMPLAINT,
        collected_entities={
            "issue_type": "quality",
            "booking_id": "BOOK-12345"
        }
    )
    
    print(f"Confirmation: {confirmation}")
    assert "quality" in confirmation.lower()
    assert "BOOK-12345" in confirmation
    assert "?" in confirmation
    print("✅ Test passed: Complaint confirmation includes issue details")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("QUESTION GENERATOR SERVICE - TEST SUITE")
    print("="*80)
    
    tests = [
        test_generate_question_for_service_type,
        test_generate_question_for_date,
        test_generate_question_with_context,
        test_question_variations,
        test_generate_confirmation_for_booking,
        test_generate_confirmation_for_cancellation,
        test_generate_validation_error_message,
        test_escalation_logic,
        test_context_aware_time_question,
        test_generic_fallback_question,
        test_confirmation_for_complaint,
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

