"""
Unit Tests for Intent Classifier

Tests the multi-intent classification system.
"""

import asyncio
import os
import sys
from pathlib import Path
import pytest

# Add backend/src to Python path
backend_path = Path(__file__).parent.parent.parent.parent
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


@pytest.fixture
def intent_service():
    """Create intent service fixture"""
    return IntentService()


@pytest.mark.asyncio
async def test_single_intent_booking(intent_service):
    """Test single intent - booking"""
    result = await intent_service.classify_message("I want to book AC service")
    
    assert result.primary_intent == "booking_management"
    assert len(result.intents) >= 1
    assert result.intents[0].confidence >= 0.7


@pytest.mark.asyncio
async def test_single_intent_pricing(intent_service):
    """Test single intent - pricing"""
    result = await intent_service.classify_message("How much does plumbing cost?")
    
    assert result.primary_intent == "pricing_inquiry"
    assert len(result.intents) >= 1
    assert result.intents[0].confidence >= 0.7


@pytest.mark.asyncio
async def test_multi_intent_booking_pricing(intent_service):
    """Test multi-intent - booking + pricing"""
    result = await intent_service.classify_message("I want to book AC service and know the price")
    
    assert result.primary_intent == "booking_management"
    assert len(result.intents) >= 2
    
    detected_intents = [intent.intent for intent in result.intents]
    assert "booking_management" in detected_intents
    assert "pricing_inquiry" in detected_intents


@pytest.mark.asyncio
async def test_multi_intent_cancel_refund(intent_service):
    """Test multi-intent - cancel + refund"""
    result = await intent_service.classify_message("Cancel my booking and give me a refund")
    
    assert result.primary_intent == "booking_management"
    assert len(result.intents) >= 2
    
    detected_intents = [intent.intent for intent in result.intents]
    assert "booking_management" in detected_intents
    assert "refund_request" in detected_intents


@pytest.mark.asyncio
async def test_classification_method(intent_service):
    """Test that classification method is returned"""
    result = await intent_service.classify_message("I want to book AC service")
    
    assert result.classification_method in ["pattern_match", "llm", "fallback"]


@pytest.mark.asyncio
async def test_confidence_scores(intent_service):
    """Test that confidence scores are valid"""
    result = await intent_service.classify_message("I want to book AC service")
    
    for intent in result.intents:
        assert 0.0 <= intent.confidence <= 1.0


@pytest.mark.asyncio
async def test_entity_extraction(intent_service):
    """Test entity extraction"""
    result = await intent_service.classify_message("I want to book AC service")
    
    # Should have at least one intent
    assert len(result.intents) >= 1
    
    # Entities should be a dict
    assert isinstance(result.intents[0].entities, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

