"""
Integration Tests for Chat Service with Slot-Filling

Tests end-to-end chat flow with slot-filling system integration.
Uses mocked LLM calls for deterministic testing.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import json

from src.services.chat_service import ChatService
from src.schemas.chat import ChatMessageRequest
from src.core.models import User
from src.core.models.conversation import MessageRole, Channel


# ============================================
# Fixtures
# ============================================

@pytest.fixture
def mock_db():
    """Mock database session with proper refresh behavior"""
    from datetime import datetime, timezone

    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()

    # Mock refresh to set id and created_at on Conversation objects
    async def mock_refresh(obj):
        if not hasattr(obj, 'id') or obj.id is None:
            obj.id = 1
        if not hasattr(obj, 'created_at') or obj.created_at is None:
            obj.created_at = datetime.now(timezone.utc)

    db.refresh = AsyncMock(side_effect=mock_refresh)
    db.execute = AsyncMock()
    db.scalar = AsyncMock()
    return db


@pytest.fixture
def test_user():
    """Create test user"""
    user = User(
        id=1,
        first_name="Test",
        last_name="User",
        email="test@example.com",
        mobile="1234567890",
        is_active=True
    )
    return user


@pytest.fixture
def mock_slot_filling_service():
    """Mock slot-filling service"""
    service = AsyncMock()
    return service


# ============================================
# Test Cases
# ============================================

def test_chat_service_initialization(mock_db):
    """Test 1: Chat service initializes correctly"""
    service = ChatService(mock_db)
    assert service.db == mock_db


@patch('src.core.config.settings')
@patch('src.services.service_factory.SlotFillingServiceFactory')
def test_send_message_with_slot_filling_question(
    mock_factory,
    mock_settings,
    mock_db,
    test_user
):
    """
    Test 2: Send message and get question response

    Scenario: User says "I want to book AC service"
    Expected: System asks for date
    """
    # Setup mocks
    mock_settings.ENABLE_SLOT_FILLING = True
    
    mock_slot_filling = AsyncMock()
    mock_slot_filling.process_message = AsyncMock(return_value=MagicMock(
        final_response="What date would you like to book the service?",
        response_type="question",
        collected_entities={"service_type": "AC"},
        needed_entities=["date", "time", "location"],
        should_trigger_agent=False,
        metadata={
            "primary_intent": "BOOKING_MANAGEMENT",
            "intent_confidence": 0.95,
            "classification_method": "pattern",
            "nodes_executed": ["classify_intent", "determine_needed_entities", "generate_question"]
        }
    ))
    
    mock_factory.create = AsyncMock(return_value=mock_slot_filling)
    
    # Mock database operations
    mock_db.execute = AsyncMock()
    mock_db.scalar = AsyncMock(return_value=0)
    
    # Create request
    request = ChatMessageRequest(
        message="I want to book AC service",
        session_id="test_session_1",
        channel="web"
    )
    
    # Execute
    service = ChatService(mock_db)
    result = asyncio.run(service.send_message(test_user, request))
    
    # Assert
    assert result.session_id == "test_session_1"
    assert "date" in result.assistant_message.message.lower()
    assert mock_slot_filling.process_message.called


@patch('src.core.config.settings')
@patch('src.services.service_factory.SlotFillingServiceFactory')
def test_send_message_with_confirmation(
    mock_factory,
    mock_settings,
    mock_db,
    test_user
):
    """
    Test 3: Multi-turn conversation leads to confirmation
    
    Scenario: All entities collected
    Expected: System generates confirmation
    """
    # Setup mocks
    mock_settings.ENABLE_SLOT_FILLING = True
    
    mock_slot_filling = AsyncMock()
    mock_slot_filling.process_message = AsyncMock(return_value=MagicMock(
        final_response="Let me confirm: You want to book AC service on 2025-10-10 at 14:00 in Mumbai. Should I proceed?",
        response_type="confirmation",
        collected_entities={
            "service_type": "AC",
            "date": "2025-10-10",
            "time": "14:00",
            "location": "Mumbai"
        },
        needed_entities=[],
        should_trigger_agent=True,
        metadata={
            "primary_intent": "BOOKING_MANAGEMENT",
            "intent_confidence": 0.95,
            "classification_method": "pattern",
            "nodes_executed": ["classify_intent", "extract_entity", "validate_entity", "update_dialog_state", "generate_question"]
        }
    ))
    
    mock_factory.create = AsyncMock(return_value=mock_slot_filling)
    
    # Mock database operations
    mock_db.execute = AsyncMock()
    mock_db.scalar = AsyncMock(return_value=0)
    
    # Create request
    request = ChatMessageRequest(
        message="Mumbai",
        session_id="test_session_1",
        channel="web"
    )
    
    # Execute
    service = ChatService(mock_db)
    result = asyncio.run(service.send_message(test_user, request))
    
    # Assert
    assert result.session_id == "test_session_1"
    assert "confirm" in result.assistant_message.message.lower()
    assert "mumbai" in result.assistant_message.message.lower()


@patch('src.core.config.settings')
@patch('src.services.service_factory.SlotFillingServiceFactory')
def test_send_message_with_error_handling(
    mock_factory,
    mock_settings,
    mock_db,
    test_user
):
    """
    Test 4: Error handling returns fallback response
    
    Scenario: Slot-filling service raises exception
    Expected: Fallback response with error metadata
    """
    # Setup mocks
    mock_settings.ENABLE_SLOT_FILLING = True
    
    mock_slot_filling = AsyncMock()
    mock_slot_filling.process_message = AsyncMock(side_effect=Exception("Test error"))
    
    mock_factory.create = AsyncMock(return_value=mock_slot_filling)
    
    # Mock database operations
    mock_db.execute = AsyncMock()
    mock_db.scalar = AsyncMock(return_value=0)
    
    # Create request
    request = ChatMessageRequest(
        message="I want to book AC service",
        session_id="test_session_1",
        channel="web"
    )
    
    # Execute
    service = ChatService(mock_db)
    result = asyncio.run(service.send_message(test_user, request))
    
    # Assert
    assert result.session_id == "test_session_1"
    assert "apologize" in result.assistant_message.message.lower() or "trouble" in result.assistant_message.message.lower()


@patch('src.core.config.settings')
def test_send_message_with_slot_filling_disabled(
    mock_settings,
    mock_db,
    test_user
):
    """
    Test 5: Fallback response when slot-filling is disabled
    
    Scenario: ENABLE_SLOT_FILLING = False
    Expected: Fallback response
    """
    # Setup mocks
    mock_settings.ENABLE_SLOT_FILLING = False
    
    # Mock database operations
    mock_db.execute = AsyncMock()
    mock_db.scalar = AsyncMock(return_value=0)
    
    # Create request
    request = ChatMessageRequest(
        message="I want to book AC service",
        session_id="test_session_1",
        channel="web"
    )
    
    # Execute
    service = ChatService(mock_db)
    result = asyncio.run(service.send_message(test_user, request))
    
    # Assert
    assert result.session_id == "test_session_1"
    assert "ConvergeAI assistant" in result.assistant_message.message


def test_delete_session_success(mock_db, test_user):
    """
    Test 6: Delete session successfully
    
    Scenario: Session exists and belongs to user
    Expected: Session deleted
    """
    # Mock database operations
    mock_db.scalar = AsyncMock(return_value=5)  # 5 messages in session
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()
    
    # Execute
    service = ChatService(mock_db)
    asyncio.run(service.delete_session(test_user, "test_session_1"))
    
    # Assert
    assert mock_db.execute.called
    assert mock_db.commit.called


def test_delete_session_not_found(mock_db, test_user):
    """
    Test 7: Delete session that doesn't exist
    
    Scenario: Session not found
    Expected: ValueError raised
    """
    # Mock database operations
    mock_db.scalar = AsyncMock(return_value=0)  # No messages found
    
    # Execute and assert
    service = ChatService(mock_db)
    with pytest.raises(ValueError, match="not found"):
        asyncio.run(service.delete_session(test_user, "nonexistent_session"))


# ============================================
# Run Tests
# ============================================

if __name__ == "__main__":
    print("Running Chat Service Integration Tests...")
    print("=" * 60)
    print("\nNote: Use 'pytest tests/test_chat_service_integration.py' for proper test execution")
    print("This script provides basic test validation only.\n")
    print("=" * 60)

