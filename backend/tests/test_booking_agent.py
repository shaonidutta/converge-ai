"""
Tests for BookingAgent

Tests cover:
- Booking creation with provider validation
- Provider availability validation
- Booking cancellation
- Error handling for missing entities
- Error handling for unavailable providers
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date, time

from backend.src.agents.booking.booking_agent import BookingAgent
from backend.src.core.models import User, Address, Pincode, Provider, ProviderPincode


@pytest.fixture
def mock_db():
    """Mock database session"""
    return AsyncMock()


@pytest.fixture
def mock_user():
    """Mock user object"""
    user = MagicMock(spec=User)
    user.id = 1
    user.name = "Test User"
    user.email = "test@example.com"
    user.wallet_balance = 5000.00
    return user


@pytest.fixture
def booking_agent(mock_db):
    """Create BookingAgent instance"""
    return BookingAgent(mock_db)


@pytest.mark.asyncio
async def test_execute_book_action(booking_agent, mock_user):
    """Test execute method routes to _create_booking for 'book' action"""
    entities = {
        "action": "book",
        "service_type": "ac",
        "date": "2025-10-15",
        "time": "14:00",
        "location": "560001"
    }
    
    with patch.object(booking_agent, '_create_booking', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = {"response": "Booking created", "action_taken": "booking_created"}
        
        result = await booking_agent.execute("booking_management", entities, mock_user, "session123")
        
        assert result["action_taken"] == "booking_created"
        mock_create.assert_called_once_with(entities, mock_user)


@pytest.mark.asyncio
async def test_execute_cancel_action(booking_agent, mock_user):
    """Test execute method routes to _cancel_booking for 'cancel' action"""
    entities = {
        "action": "cancel",
        "booking_id": "12345",
        "reason": "Changed plans"
    }
    
    with patch.object(booking_agent, '_cancel_booking', new_callable=AsyncMock) as mock_cancel:
        mock_cancel.return_value = {"response": "Booking cancelled", "action_taken": "booking_cancelled"}
        
        result = await booking_agent.execute("booking_management", entities, mock_user, "session123")
        
        assert result["action_taken"] == "booking_cancelled"
        mock_cancel.assert_called_once_with(entities, mock_user)


@pytest.mark.asyncio
async def test_execute_unknown_action(booking_agent, mock_user):
    """Test execute method handles unknown action"""
    entities = {"action": "unknown_action"}
    
    result = await booking_agent.execute("booking_management", entities, mock_user, "session123")
    
    assert result["action_taken"] == "error"
    assert "not sure what you want to do" in result["response"].lower()


@pytest.mark.asyncio
async def test_create_booking_missing_location(booking_agent, mock_user):
    """Test _create_booking returns error when location is missing"""
    entities = {
        "action": "book",
        "service_type": "ac",
        "date": "2025-10-15",
        "time": "14:00"
        # Missing location
    }
    
    result = await booking_agent._create_booking(entities, mock_user)
    
    assert result["action_taken"] == "missing_entity"
    assert result["metadata"]["missing"] == "location"
    assert "location" in result["response"].lower()


@pytest.mark.asyncio
async def test_create_booking_address_not_found(booking_agent, mock_user, mock_db):
    """Test _create_booking returns error when address not found"""
    entities = {
        "action": "book",
        "service_type": "ac",
        "date": "2025-10-15",
        "time": "14:00",
        "location": "560001"
    }

    # Mock address query returning None
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await booking_agent._create_booking(entities, mock_user)

    assert result["action_taken"] == "address_not_found"
    assert "560001" in result["response"]


@pytest.mark.asyncio
async def test_validate_provider_availability_success(booking_agent, mock_db):
    """Test _validate_provider_availability succeeds when providers are available"""
    # Mock pincode exists and is serviceable
    mock_pincode = MagicMock(spec=Pincode)
    mock_pincode.id = 1
    mock_pincode.pincode = "560001"
    mock_pincode.is_serviceable = True

    pincode_result = MagicMock()
    pincode_result.scalar_one_or_none.return_value = mock_pincode

    # Mock provider associations exist
    provider_result = MagicMock()
    provider_result.all.return_value = [MagicMock(), MagicMock()]  # 2 providers

    mock_db.execute = AsyncMock(side_effect=[pincode_result, provider_result])

    result = await booking_agent._validate_provider_availability("560001")

    assert result["is_valid"] is True
    assert result["available_providers"] == 2
    assert result["pincode_id"] == 1


@pytest.mark.asyncio
async def test_validate_provider_availability_pincode_not_found(booking_agent, mock_db):
    """Test _validate_provider_availability fails when pincode doesn't exist"""
    # Mock pincode not found
    pincode_result = MagicMock()
    pincode_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=pincode_result)

    result = await booking_agent._validate_provider_availability("999999")

    assert result["is_valid"] is False
    assert "not in our service area" in result["message"]
    assert result["available_providers"] == 0


@pytest.mark.asyncio
async def test_validate_provider_availability_not_serviceable(booking_agent, mock_db):
    """Test _validate_provider_availability fails when pincode is not serviceable"""
    # Mock pincode exists but not serviceable
    mock_pincode = MagicMock(spec=Pincode)
    mock_pincode.id = 1
    mock_pincode.pincode = "560001"
    mock_pincode.is_serviceable = False

    pincode_result = MagicMock()
    pincode_result.scalar_one_or_none.return_value = mock_pincode
    mock_db.execute = AsyncMock(return_value=pincode_result)

    result = await booking_agent._validate_provider_availability("560001")

    assert result["is_valid"] is False
    assert "don't service" in result["message"]
    assert result["pincode_id"] == 1


@pytest.mark.asyncio
async def test_validate_provider_availability_no_providers(booking_agent, mock_db):
    """Test _validate_provider_availability fails when no providers available"""
    # Mock pincode exists and is serviceable
    mock_pincode = MagicMock(spec=Pincode)
    mock_pincode.id = 1
    mock_pincode.pincode = "560001"
    mock_pincode.is_serviceable = True

    pincode_result = MagicMock()
    pincode_result.scalar_one_or_none.return_value = mock_pincode

    # Mock no provider associations
    provider_result = MagicMock()
    provider_result.all.return_value = []

    mock_db.execute = AsyncMock(side_effect=[pincode_result, provider_result])

    result = await booking_agent._validate_provider_availability("560001")

    assert result["is_valid"] is False
    assert "no service providers are available" in result["message"]


@pytest.mark.asyncio
async def test_cancel_booking_missing_booking_id(booking_agent, mock_user):
    """Test _cancel_booking returns error when booking_id is missing"""
    entities = {
        "action": "cancel",
        "reason": "Changed plans"
        # Missing booking_id
    }
    
    result = await booking_agent._cancel_booking(entities, mock_user)
    
    assert result["action_taken"] == "missing_entity"
    assert result["metadata"]["missing"] == "booking_id"


@pytest.mark.asyncio
async def test_cancel_booking_success(booking_agent, mock_user):
    """Test _cancel_booking succeeds"""
    entities = {
        "action": "cancel",
        "booking_id": "12345",
        "reason": "Changed plans"
    }
    
    # Mock successful cancellation
    mock_booking_response = MagicMock()
    mock_booking_response.id = 12345
    mock_booking_response.booking_number = "BK12345"
    mock_booking_response.total = 2500.00
    mock_booking_response.status = "cancelled"
    
    with patch.object(booking_agent.booking_service, 'cancel_booking', new_callable=AsyncMock) as mock_cancel:
        mock_cancel.return_value = mock_booking_response
        
        result = await booking_agent._cancel_booking(entities, mock_user)
        
        assert result["action_taken"] == "booking_cancelled"
        assert "BK12345" in result["response"]
        assert result["metadata"]["refund_amount"] == 2500.00


@pytest.mark.asyncio
async def test_reschedule_booking_not_implemented(booking_agent, mock_user):
    """Test _reschedule_booking returns not_implemented"""
    entities = {
        "action": "reschedule",
        "booking_id": "12345",
        "date": "2025-10-20",
        "time": "16:00"
    }
    
    result = await booking_agent._reschedule_booking(entities, mock_user)
    
    assert result["action_taken"] == "not_implemented"
    assert "coming soon" in result["response"].lower()


@pytest.mark.asyncio
async def test_modify_booking_not_implemented(booking_agent, mock_user):
    """Test _modify_booking returns not_implemented"""
    entities = {
        "action": "modify",
        "booking_id": "12345"
    }
    
    result = await booking_agent._modify_booking(entities, mock_user)
    
    assert result["action_taken"] == "not_implemented"
    assert "coming soon" in result["response"].lower()

