"""
Integration Tests for Intent Classification

Automated tests for the multi-intent classification system.
Run with: pytest tests/integration/test_intent_classification.py -v
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
import pytest

# Add backend/src to Python path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from src.services.intent_service import IntentService


# Test queries with expected results
TEST_CASES = [
    {
        "query": "I want to book AC service",
        "expected_primary": "booking_management",
        "expected_entities": ["action", "service_type"],
        "description": "Single intent - booking"
    },
    {
        "query": "How much does plumbing cost?",
        "expected_primary": "pricing_inquiry",
        "expected_entities": ["service_type"],
        "description": "Single intent - pricing"
    },
    {
        "query": "I want to book AC service and know the price",
        "expected_primary": "booking_management",
        "expected_intents": ["booking_management", "pricing_inquiry"],
        "description": "Multi-intent - booking + pricing"
    },
    {
        "query": "Cancel my booking and give me a refund",
        "expected_primary": "booking_management",
        "expected_intents": ["booking_management", "refund_request"],
        "description": "Multi-intent - cancel + refund"
    },
    {
        "query": "What's the price and when are you available?",
        "expected_primary": "pricing_inquiry",
        "expected_intents": ["pricing_inquiry", "availability_check"],
        "description": "Multi-intent - pricing + availability"
    },
    {
        "query": "The technician was rude and service was poor",
        "expected_primary": "complaint",
        "expected_entities": ["issue_type"],
        "description": "Single intent - complaint"
    },
    {
        "query": "My payment failed",
        "expected_primary": "payment_issue",
        "expected_entities": ["payment_type"],
        "description": "Single intent - payment issue"
    },
    {
        "query": "Hello",
        "expected_primary": "greeting",
        "description": "Single intent - greeting"
    },
]


@pytest.fixture(scope="module")
def intent_service():
    """Create intent service fixture"""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check if API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY not set")
    
    return IntentService()


@pytest.mark.asyncio
@pytest.mark.parametrize("test_case", TEST_CASES, ids=[tc["description"] for tc in TEST_CASES])
async def test_intent_classification(intent_service, test_case):
    """Test intent classification for each test case"""
    
    # Classify intent
    result = await intent_service.classify_message(test_case['query'])
    
    # Validate primary intent
    assert result.primary_intent == test_case['expected_primary'], \
        f"Expected primary intent '{test_case['expected_primary']}', got '{result.primary_intent}'"
    
    # Validate multiple intents if expected
    if 'expected_intents' in test_case:
        detected_intents = [intent.intent for intent in result.intents]
        for expected_intent in test_case['expected_intents']:
            assert expected_intent in detected_intents, \
                f"Expected intent '{expected_intent}' not detected. Got: {detected_intents}"
    
    # Validate confidence scores
    for intent in result.intents:
        assert 0.0 <= intent.confidence <= 1.0, \
            f"Invalid confidence score: {intent.confidence}"
    
    # Validate classification method
    assert result.classification_method in ["pattern_match", "llm", "fallback"], \
        f"Invalid classification method: {result.classification_method}"


@pytest.mark.asyncio
async def test_performance_pattern_match(intent_service):
    """Test that pattern matching is fast"""
    result = await intent_service.classify_message("I want to book AC service")
    
    # Pattern matching should be very fast
    if result.classification_method == "pattern_match":
        assert result.processing_time_ms < 100, \
            f"Pattern matching too slow: {result.processing_time_ms}ms"


@pytest.mark.asyncio
async def test_performance_llm(intent_service):
    """Test that LLM classification completes in reasonable time"""
    result = await intent_service.classify_message("I want to book AC service and know the price")
    
    # LLM should complete within 5 seconds
    assert result.processing_time_ms < 5000, \
        f"LLM classification too slow: {result.processing_time_ms}ms"


@pytest.mark.asyncio
async def test_multi_intent_detection(intent_service):
    """Test that multi-intent queries are detected correctly"""
    
    multi_intent_queries = [
        "I want to book AC service and know the price",
        "Cancel my booking and give me a refund",
        "What's the price and when are you available?"
    ]
    
    for query in multi_intent_queries:
        result = await intent_service.classify_message(query)
        
        # Should detect at least 2 intents
        assert len(result.intents) >= 2, \
            f"Expected multiple intents for '{query}', got {len(result.intents)}"


@pytest.mark.asyncio
async def test_entity_extraction(intent_service):
    """Test entity extraction"""
    result = await intent_service.classify_message("I want to book AC service")
    
    # Should have entities
    assert len(result.intents) >= 1
    assert isinstance(result.intents[0].entities, dict)


@pytest.mark.asyncio
async def test_clarification_flag(intent_service):
    """Test that unclear queries are flagged for clarification"""
    result = await intent_service.classify_message("xyz abc random text")
    
    # Should either detect an intent or flag for clarification
    if result.primary_intent == "unclear_intent":
        assert result.requires_clarification == True
        assert result.clarification_reason is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

