"""
Unit Test for Context-Aware Intent Classification

Tests the context-aware prompt building and helper functions without requiring LLM API calls.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from src.llm.gemini.prompts import build_context_aware_intent_prompt
from src.core.models.dialog_state import DialogState, DialogStateType
from datetime import datetime, timezone, timedelta


def test_context_aware_prompt_building():
    """Test context-aware prompt building"""
    
    print("=" * 80)
    print("CONTEXT-AWARE PROMPT BUILDING TEST")
    print("=" * 80)
    
    # Test 1: Prompt with conversation history only
    print("\n" + "=" * 80)
    print("TEST 1: Prompt with Conversation History Only")
    print("=" * 80)
    
    conversation_history = [
        {"role": "user", "content": "I want to book AC servicing"},
        {"role": "assistant", "content": "What date would you like to schedule the service?"}
    ]
    
    prompt = build_context_aware_intent_prompt(
        user_message="tomorrow",
        conversation_history=conversation_history
    )
    
    print("✅ Prompt generated successfully")
    print(f"   Prompt length: {len(prompt)} characters")
    assert "Conversation History:" in prompt
    assert "I want to book AC servicing" in prompt
    assert "What date would you like to schedule the service?" in prompt
    assert "tomorrow" in prompt
    print("   ✓ Contains conversation history")
    print("   ✓ Contains user message")
    
    # Test 2: Prompt with dialog state only
    print("\n" + "=" * 80)
    print("TEST 2: Prompt with Dialog State Only")
    print("=" * 80)
    
    # Create a mock dialog state
    dialog_state = DialogState(
        id=1,
        user_id=1,
        session_id="test_session",
        state=DialogStateType.COLLECTING_INFO,
        intent="booking_management",
        collected_entities={"service_type": "ac", "action": "book"},
        needed_entities=["date", "time"],
        pending_action=None,
        context={"last_question": "What date would you like?"},
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
    )
    
    prompt = build_context_aware_intent_prompt(
        user_message="2 PM",
        dialog_state=dialog_state
    )
    
    print("✅ Prompt generated successfully")
    print(f"   Prompt length: {len(prompt)} characters")
    assert "Active Dialog State:" in prompt
    assert "collecting_info" in prompt
    assert "booking_management" in prompt
    assert "date, time" in prompt
    assert "What date would you like?" in prompt
    print("   ✓ Contains dialog state information")
    print("   ✓ Contains state type")
    print("   ✓ Contains intent")
    print("   ✓ Contains needed entities")
    print("   ✓ Contains last question")
    
    # Test 3: Prompt with both conversation history and dialog state
    print("\n" + "=" * 80)
    print("TEST 3: Prompt with Both History and Dialog State")
    print("=" * 80)
    
    conversation_history = [
        {"role": "user", "content": "I want to book AC servicing"},
        {"role": "assistant", "content": "What date would you like to schedule the service?"},
        {"role": "user", "content": "tomorrow"},
        {"role": "assistant", "content": "What time works best for you?"}
    ]
    
    dialog_state.needed_entities = ["time"]
    dialog_state.collected_entities = {"service_type": "ac", "action": "book", "date": "tomorrow"}
    dialog_state.context = {"last_question": "What time works best for you?"}
    
    prompt = build_context_aware_intent_prompt(
        user_message="2 PM",
        conversation_history=conversation_history,
        dialog_state=dialog_state
    )
    
    print("✅ Prompt generated successfully")
    print(f"   Prompt length: {len(prompt)} characters")
    assert "Conversation History:" in prompt
    assert "Active Dialog State:" in prompt
    assert "IMPORTANT - Context-Aware Classification:" in prompt
    assert "follow-up response" in prompt.lower()
    print("   ✓ Contains both conversation history and dialog state")
    print("   ✓ Contains context-aware instructions")
    print("   ✓ Contains follow-up detection guidance")
    
    # Test 4: Prompt without any context (standard prompt)
    print("\n" + "=" * 80)
    print("TEST 4: Verify Context-Aware Prompt Structure")
    print("=" * 80)
    
    prompt = build_context_aware_intent_prompt(
        user_message="yes",
        conversation_history=conversation_history,
        dialog_state=dialog_state
    )
    
    # Verify key sections exist
    required_sections = [
        "Context-Aware Classification:",
        "Conversation History:",
        "Active Dialog State:",
        "Current User Message:",
        "Instructions:",
        "If it's a follow-up response:",
        "If it's a NEW intent:",
        "Entity Extraction:"
    ]
    
    for section in required_sections:
        assert section in prompt, f"Missing section: {section}"
        print(f"   ✓ Contains section: {section}")
    
    print("\n" + "=" * 80)
    print("ALL UNIT TESTS PASSED! ✅")
    print("=" * 80)
    print("\n📊 Summary:")
    print("   - Context-aware prompt builder works correctly")
    print("   - Conversation history properly formatted")
    print("   - Dialog state information included")
    print("   - Follow-up detection instructions present")
    print("   - All required sections included in prompt")


def test_context_summary_building():
    """Test context summary building"""
    
    print("\n" + "=" * 80)
    print("CONTEXT SUMMARY BUILDING TEST")
    print("=" * 80)
    
    from src.nlp.intent.classifier import IntentClassifier
    
    classifier = IntentClassifier.__new__(IntentClassifier)  # Create instance without __init__
    
    # Test 1: Summary with history only
    print("\n--- Test 1: History Only ---")
    conversation_history = [
        {"role": "user", "content": "message 1"},
        {"role": "assistant", "content": "response 1"},
        {"role": "user", "content": "message 2"}
    ]
    
    summary = classifier._build_context_summary(conversation_history, None)
    print(f"Summary: {summary}")
    assert "3 previous messages" in summary
    print("✅ Correct message count")
    
    # Test 2: Summary with dialog state only
    print("\n--- Test 2: Dialog State Only ---")
    dialog_state = DialogState(
        id=1,
        user_id=1,
        session_id="test",
        state=DialogStateType.AWAITING_CONFIRMATION,
        intent="booking_management",
        collected_entities={},
        needed_entities=[],
        pending_action=None,
        context={},
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
    )
    
    summary = classifier._build_context_summary(None, dialog_state)
    print(f"Summary: {summary}")
    assert "awaiting_confirmation" in summary
    assert "booking_management" in summary
    print("✅ Contains state and intent")
    
    # Test 3: Summary with both
    print("\n--- Test 3: Both History and State ---")
    summary = classifier._build_context_summary(conversation_history, dialog_state)
    print(f"Summary: {summary}")
    assert "3 previous messages" in summary
    assert "awaiting_confirmation" in summary
    print("✅ Contains both elements")
    
    print("\n✅ All context summary tests passed!")


if __name__ == "__main__":
    test_context_aware_prompt_building()
    test_context_summary_building()
    
    print("\n" + "=" * 80)
    print("🎉 ALL UNIT TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)

