"""
Integration test for BookingAgent reschedule and modify methods
Tests actual database operations
"""

import pytest
import asyncio
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from sqlalchemy import select

from backend.src.agents.booking.booking_agent import BookingAgent
from backend.src.core.models import (
    User, Address, Provider, RateCard, Category, Subcategory,
    Booking, BookingItem, BookingStatus, PaymentStatus, PaymentMethod,
    ProviderPincode, Pincode, Cart, CartItem
)
from backend.src.core.database.connection import get_db


@pytest.fixture
async def test_data(db_session):
    """Create test data for integration tests"""
    
    # Create user
    user = User(
        first_name="Test",
        last_name="User",
        mobile="9876543210",
        email="test@example.com",
        password_hash="hashed_password"
    )
    db_session.add(user)
    await db_session.flush()
    
    # Create address
    address = Address(
        user_id=user.id,
        pincode="560001",
        address_line1="123 Test Street",
        city="Bangalore",
        state="Karnataka"
    )
    db_session.add(address)
    await db_session.flush()
    
    # Create pincode
    pincode = Pincode(
        pincode="560001",
        city="Bangalore",
        state="Karnataka",
        is_serviceable=True
    )
    db_session.add(pincode)
    await db_session.flush()
    
    # Create provider
    provider = Provider(
        name="Test Provider",
        mobile="9876543211",
        email="provider@example.com",
        is_active=True,
        is_verified=True
    )
    db_session.add(provider)
    await db_session.flush()
    
    # Link provider to pincode
    provider_pincode = ProviderPincode(
        provider_id=provider.id,
        pincode="560001"
    )
    db_session.add(provider_pincode)
    
    # Create category and subcategory
    category = Category(name="Test Category", is_active=True)
    db_session.add(category)
    await db_session.flush()
    
    subcategory = Subcategory(
        name="Test Subcategory",
        category_id=category.id,
        is_active=True
    )
    db_session.add(subcategory)
    await db_session.flush()
    
    # Create rate card
    rate_card = RateCard(
        name="Test Service - AC Repair",
        description="Test service description",
        price=Decimal("2500.00"),
        category_id=category.id,
        subcategory_id=subcategory.id,
        provider_id=provider.id,
        is_active=True
    )
    db_session.add(rate_card)
    await db_session.flush()
    
    # Create booking
    booking = Booking(
        user_id=user.id,
        address_id=address.id,
        order_id=f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}",
        booking_number=f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}",
        payment_status=PaymentStatus.PENDING,
        payment_method=PaymentMethod.WALLET,
        subtotal=Decimal("5000.00"),
        total=Decimal("5000.00"),
        status=BookingStatus.PENDING,
        preferred_date=date.today() + timedelta(days=5),
        preferred_time=time(14, 0),
        special_instructions="Original instructions"
    )
    db_session.add(booking)
    await db_session.flush()
    
    # Create booking item
    booking_item = BookingItem(
        booking_id=booking.id,
        rate_card_id=rate_card.id,
        service_name="Test Service - AC Repair",
        quantity=2,
        unit_price=Decimal("2500.00"),
        total_price=Decimal("5000.00"),
        scheduled_date=booking.preferred_date,
        scheduled_time=booking.preferred_time
    )
    db_session.add(booking_item)
    
    await db_session.commit()
    
    return {
        "user": user,
        "address": address,
        "provider": provider,
        "rate_card": rate_card,
        "booking": booking,
        "booking_item": booking_item
    }


@pytest.mark.asyncio
async def test_reschedule_booking_integration(db_session, test_data):
    """Integration test: Verify BookingAgent can reschedule booking"""
    
    # Create BookingAgent
    agent = BookingAgent(db_session)
    
    # Prepare entities for rescheduling
    new_date = (date.today() + timedelta(days=10)).strftime("%Y-%m-%d")
    new_time = "16:00"
    
    entities = {
        "booking_id": str(test_data["booking"].id),
        "date": new_date,
        "time": new_time,
        "reason": "Need to change appointment time"
    }
    
    # Execute reschedule
    result = await agent._reschedule_booking(entities, test_data["user"])
    
    # Verify response
    assert result["action_taken"] == "booking_rescheduled"
    assert test_data["booking"].booking_number in result["response"]
    assert new_date in result["response"]
    assert new_time in result["response"]
    assert result["metadata"]["booking_id"] == test_data["booking"].id
    assert result["metadata"]["new_date"] == new_date
    assert result["metadata"]["new_time"] == new_time
    
    # Verify database was updated
    await db_session.refresh(test_data["booking"])
    assert test_data["booking"].preferred_date.strftime("%Y-%m-%d") == new_date
    assert test_data["booking"].preferred_time.strftime("%H:%M") == new_time
    assert "Rescheduled from" in test_data["booking"].special_instructions
    
    print("\n✅ Reschedule Integration Test PASSED")
    print(f"   Booking {test_data['booking'].booking_number} rescheduled to {new_date} at {new_time}")


@pytest.mark.asyncio
async def test_modify_booking_integration(db_session, test_data):
    """Integration test: Verify BookingAgent can modify booking"""
    
    # Create BookingAgent
    agent = BookingAgent(db_session)
    
    # Prepare entities for modification
    new_instructions = "Please call 30 minutes before arrival and use the back entrance"
    
    entities = {
        "booking_id": str(test_data["booking"].id),
        "special_instructions": new_instructions
    }
    
    # Execute modification
    result = await agent._modify_booking(entities, test_data["user"])
    
    # Verify response
    assert result["action_taken"] == "booking_modified"
    assert test_data["booking"].booking_number in result["response"]
    assert "updated successfully" in result["response"]
    assert result["metadata"]["booking_id"] == test_data["booking"].id
    assert result["metadata"]["modifications"]["special_instructions"] == new_instructions
    
    # Verify database was updated
    await db_session.refresh(test_data["booking"])
    assert test_data["booking"].special_instructions == new_instructions
    
    print("\n✅ Modify Integration Test PASSED")
    print(f"   Booking {test_data['booking'].booking_number} instructions updated")


@pytest.mark.asyncio
async def test_reschedule_missing_booking_id(db_session, test_data):
    """Test rescheduling fails when booking_id is missing"""
    
    agent = BookingAgent(db_session)
    
    entities = {
        "date": "2025-10-20",
        "time": "15:00"
    }
    
    result = await agent._reschedule_booking(entities, test_data["user"])
    
    assert result["action_taken"] == "missing_entity"
    assert "booking ID" in result["response"]
    assert result["metadata"]["missing"] == "booking_id"
    
    print("\n✅ Reschedule Missing Booking ID Test PASSED")


@pytest.mark.asyncio
async def test_modify_missing_booking_id(db_session, test_data):
    """Test modification fails when booking_id is missing"""
    
    agent = BookingAgent(db_session)
    
    entities = {
        "special_instructions": "New instructions"
    }
    
    result = await agent._modify_booking(entities, test_data["user"])
    
    assert result["action_taken"] == "missing_entity"
    assert "booking ID" in result["response"]
    assert result["metadata"]["missing"] == "booking_id"
    
    print("\n✅ Modify Missing Booking ID Test PASSED")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])

