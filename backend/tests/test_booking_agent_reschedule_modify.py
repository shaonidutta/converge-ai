"""
Unit tests for BookingAgent reschedule and modify methods
"""

import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date, time

# Set environment variables before importing anything else
os.environ["DATABASE_URL"] = "mysql+aiomysql://test:test@localhost/test"
os.environ["JWT_SECRET_KEY"] = "test_secret_key_12345678901234567890"
os.environ["PINECONE_API_KEY"] = "test_pinecone_key"
os.environ["GOOGLE_API_KEY"] = "test_google_key"
os.environ["SECRET_KEY"] = "test_secret_key_12345678901234567890"

from backend.src.agents.booking.booking_agent import BookingAgent
from backend.src.core.models import User, Booking, BookingStatus
from backend.src.schemas.customer import BookingResponse, RescheduleBookingRequest


@pytest.fixture
def mock_db():
    """Mock database session"""
    return AsyncMock()


@pytest.fixture
def mock_user():
    """Mock user"""
    user = MagicMock(spec=User)
    user.id = 1
    user.first_name = "John"
    user.last_name = "Doe"
    user.mobile = "9876543210"
    return user


@pytest.fixture
def booking_agent(mock_db):
    """Create BookingAgent instance"""
    return BookingAgent(mock_db)


class TestRescheduleBooking:
    """Tests for _reschedule_booking method"""
    
    @pytest.mark.asyncio
    async def test_reschedule_booking_success(self, booking_agent, mock_user):
        """Test successful booking rescheduling"""
        # Arrange
        entities = {
            "booking_id": "123",
            "date": "2025-10-20",
            "time": "15:00"
        }
        
        mock_booking_response = MagicMock(spec=BookingResponse)
        mock_booking_response.id = 123
        mock_booking_response.booking_number = "BK123456"
        mock_booking_response.preferred_date = "2025-10-20"
        mock_booking_response.preferred_time = "15:00"
        mock_booking_response.status = "PENDING"
        
        # Mock BookingService.reschedule_booking
        booking_agent.booking_service.reschedule_booking = AsyncMock(return_value=mock_booking_response)
        
        # Act
        result = await booking_agent._reschedule_booking(entities, mock_user)
        
        # Assert
        assert result["action_taken"] == "booking_rescheduled"
        assert "BK123456" in result["response"]
        assert "2025-10-20" in result["response"]
        assert "15:00" in result["response"]
        assert result["metadata"]["booking_id"] == 123
        assert result["metadata"]["new_date"] == "2025-10-20"
        assert result["metadata"]["new_time"] == "15:00"
    
    @pytest.mark.asyncio
    async def test_reschedule_booking_missing_booking_id(self, booking_agent, mock_user):
        """Test rescheduling fails when booking_id is missing"""
        # Arrange
        entities = {
            "date": "2025-10-20",
            "time": "15:00"
        }
        
        # Act
        result = await booking_agent._reschedule_booking(entities, mock_user)
        
        # Assert
        assert result["action_taken"] == "missing_entity"
        assert "booking ID" in result["response"]
        assert result["metadata"]["missing"] == "booking_id"
    
    @pytest.mark.asyncio
    async def test_reschedule_booking_missing_date(self, booking_agent, mock_user):
        """Test rescheduling fails when date is missing"""
        # Arrange
        entities = {
            "booking_id": "123",
            "time": "15:00"
        }
        
        # Act
        result = await booking_agent._reschedule_booking(entities, mock_user)
        
        # Assert
        assert result["action_taken"] == "missing_entity"
        assert "date" in result["response"]
        assert result["metadata"]["missing"] == "date"
    
    @pytest.mark.asyncio
    async def test_reschedule_booking_missing_time(self, booking_agent, mock_user):
        """Test rescheduling fails when time is missing"""
        # Arrange
        entities = {
            "booking_id": "123",
            "date": "2025-10-20"
        }
        
        # Act
        result = await booking_agent._reschedule_booking(entities, mock_user)
        
        # Assert
        assert result["action_taken"] == "missing_entity"
        assert "time" in result["response"]
        assert result["metadata"]["missing"] == "time"
    
    @pytest.mark.asyncio
    async def test_reschedule_booking_not_found(self, booking_agent, mock_user):
        """Test rescheduling fails when booking not found"""
        # Arrange
        entities = {
            "booking_id": "999",
            "date": "2025-10-20",
            "time": "15:00"
        }
        
        # Mock BookingService to raise ValueError
        booking_agent.booking_service.reschedule_booking = AsyncMock(
            side_effect=ValueError("Booking not found")
        )
        
        # Act
        result = await booking_agent._reschedule_booking(entities, mock_user)
        
        # Assert
        assert result["action_taken"] == "reschedule_failed"
        assert "Booking not found" in result["response"]
    
    @pytest.mark.asyncio
    async def test_reschedule_booking_invalid_status(self, booking_agent, mock_user):
        """Test rescheduling fails for completed booking"""
        # Arrange
        entities = {
            "booking_id": "123",
            "date": "2025-10-20",
            "time": "15:00"
        }
        
        # Mock BookingService to raise ValueError
        booking_agent.booking_service.reschedule_booking = AsyncMock(
            side_effect=ValueError("Cannot reschedule booking with status: COMPLETED")
        )
        
        # Act
        result = await booking_agent._reschedule_booking(entities, mock_user)
        
        # Assert
        assert result["action_taken"] == "reschedule_failed"
        assert "Cannot reschedule" in result["response"]


class TestModifyBooking:
    """Tests for _modify_booking method"""
    
    @pytest.mark.asyncio
    async def test_modify_booking_special_instructions_success(self, booking_agent, mock_user):
        """Test successful modification of special instructions"""
        # Arrange
        entities = {
            "booking_id": "123",
            "special_instructions": "Please call 30 minutes before arrival"
        }
        
        mock_booking_response = MagicMock(spec=BookingResponse)
        mock_booking_response.id = 123
        mock_booking_response.booking_number = "BK123456"
        mock_booking_response.special_instructions = "Please call 30 minutes before arrival"
        
        # Mock BookingService.get_booking
        booking_agent.booking_service.get_booking = AsyncMock(return_value=mock_booking_response)
        
        # Act
        result = await booking_agent._modify_booking(entities, mock_user)
        
        # Assert
        assert result["action_taken"] == "booking_modified"
        assert "BK123456" in result["response"]
        assert "updated successfully" in result["response"]
        assert result["metadata"]["booking_id"] == 123
        assert result["metadata"]["modifications"]["special_instructions"] == "Please call 30 minutes before arrival"
    
    @pytest.mark.asyncio
    async def test_modify_booking_missing_booking_id(self, booking_agent, mock_user):
        """Test modification fails when booking_id is missing"""
        # Arrange
        entities = {
            "special_instructions": "Please call before arrival"
        }
        
        # Act
        result = await booking_agent._modify_booking(entities, mock_user)
        
        # Assert
        assert result["action_taken"] == "missing_entity"
        assert "booking ID" in result["response"]
        assert result["metadata"]["missing"] == "booking_id"
    
    @pytest.mark.asyncio
    async def test_modify_booking_no_modifications(self, booking_agent, mock_user):
        """Test modification fails when no modifications provided"""
        # Arrange
        entities = {
            "booking_id": "123"
        }
        
        # Act
        result = await booking_agent._modify_booking(entities, mock_user)
        
        # Assert
        assert result["action_taken"] == "missing_entity"
        assert "modifications" in result["response"].lower()
    
    @pytest.mark.asyncio
    async def test_modify_booking_not_found(self, booking_agent, mock_user):
        """Test modification fails when booking not found"""
        # Arrange
        entities = {
            "booking_id": "999",
            "special_instructions": "New instructions"
        }
        
        # Mock BookingService to raise ValueError
        booking_agent.booking_service.get_booking = AsyncMock(
            side_effect=ValueError("Booking not found")
        )
        
        # Act
        result = await booking_agent._modify_booking(entities, mock_user)
        
        # Assert
        assert result["action_taken"] == "modification_failed"
        assert "Booking not found" in result["response"]

