"""
Integration test for BookingAgent - Tests actual database operations

This test:
1. Creates real test data in the database
2. Calls BookingAgent._create_booking() with real DB session
3. Verifies Booking and BookingItem records are created properly
4. Checks all required columns have correct values
5. Cleans up test data after execution
"""

import pytest
import asyncio
from decimal import Decimal
from datetime import datetime, date, time
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, delete
import os
from dotenv import load_dotenv

from src.agents.booking.booking_agent import BookingAgent
from src.core.models import (
    User, Address, Cart, CartItem, RateCard, Category, Subcategory,
    Provider, Pincode, ProviderPincode, Booking, BookingItem
)
from src.core.database.base import Base

# Load environment variables
load_dotenv()

# Database URL
DATABASE_URL = os.getenv('DATABASE_URL', '').replace('mysql+pymysql://', 'mysql+aiomysql://')


@pytest.fixture(scope="module")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def db_engine():
    """Create database engine"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    """Create database session for each test"""
    async_session = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
async def test_data(db_session):
    """
    Create test data in database
    Returns dict with all test entities
    """
    # Create test user
    user = User(
        mobile=f"+91999{int(datetime.now().timestamp()) % 1000000}",
        email=f"integration_test_{datetime.now().timestamp()}@example.com",
        first_name="Integration",
        last_name="Test User",
        is_active=True,
        wallet_balance=Decimal('10000.00')
    )
    db_session.add(user)
    await db_session.flush()
    
    # Get existing pincode (assuming 560001 exists from seed data)
    pincode_result = await db_session.execute(
        select(Pincode).where(Pincode.pincode == "560001").limit(1)
    )
    pincode = pincode_result.scalar_one_or_none()
    
    if not pincode:
        # Create pincode if it doesn't exist
        pincode = Pincode(
            pincode="560001",
            city="Bangalore",
            state="Karnataka",
            is_serviceable=True
        )
        db_session.add(pincode)
        await db_session.flush()
    
    # Create test address
    address = Address(
        user_id=user.id,
        address_line1="Test Address Line 1",
        address_line2="Test Address Line 2",
        city="Bangalore",
        state="Karnataka",
        pincode="560001",
        is_default=True
    )
    db_session.add(address)
    await db_session.flush()
    
    # Get existing category and subcategory
    category_result = await db_session.execute(
        select(Category).limit(1)
    )
    category = category_result.scalar_one_or_none()
    
    if not category:
        category = Category(name="Test Category", description="Test")
        db_session.add(category)
        await db_session.flush()
    
    subcategory_result = await db_session.execute(
        select(Subcategory).where(Subcategory.category_id == category.id).limit(1)
    )
    subcategory = subcategory_result.scalar_one_or_none()
    
    if not subcategory:
        subcategory = Subcategory(
            category_id=category.id,
            name="Test Subcategory",
            description="Test"
        )
        db_session.add(subcategory)
        await db_session.flush()
    
    # Get existing provider
    provider_result = await db_session.execute(
        select(Provider).where(
            Provider.is_active == True,
            Provider.is_verified == True
        ).limit(1)
    )
    provider = provider_result.scalar_one_or_none()

    if not provider:
        provider = Provider(
            first_name="Test",
            last_name="Provider",
            mobile="+919999999999",
            email="provider@test.com",
            is_active=True,
            is_verified=True
        )
        db_session.add(provider)
        await db_session.flush()
    else:
        # Ensure the provider is active and verified
        if not provider.is_active or not provider.is_verified:
            provider.is_active = True
            provider.is_verified = True
            await db_session.flush()
    
    # Create provider-pincode association
    provider_pincode_check = await db_session.execute(
        select(ProviderPincode).where(
            ProviderPincode.provider_id == provider.id,
            ProviderPincode.pincode_id == pincode.id
        )
    )
    provider_pincode_assoc = provider_pincode_check.scalar_one_or_none()
    if not provider_pincode_assoc:
        provider_pincode = ProviderPincode(
            provider_id=provider.id,
            pincode_id=pincode.id
        )
        db_session.add(provider_pincode)
        await db_session.flush()
        await db_session.commit()  # Commit so it's visible to other queries
        print(f"[OK] Created provider-pincode association: Provider {provider.id} -> Pincode {pincode.id} ({pincode.pincode})")
    else:
        print(f"[OK] Provider-pincode association already exists: Provider {provider.id} -> Pincode {pincode.id} ({pincode.pincode})")
    
    # Create test rate card
    rate_card = RateCard(
        category_id=category.id,
        subcategory_id=subcategory.id,
        provider_id=provider.id,
        name="Test Service - AC Repair",
        price=Decimal('2500.00'),
        strike_price=Decimal('3000.00'),
        is_active=True
    )
    db_session.add(rate_card)
    await db_session.flush()
    
    # Create cart
    cart = Cart(user_id=user.id)
    db_session.add(cart)
    await db_session.flush()
    
    # Create cart item
    cart_item = CartItem(
        cart_id=cart.id,
        rate_card_id=rate_card.id,
        quantity=2,
        unit_price=Decimal('2500.00'),
        total_price=Decimal('5000.00')
    )
    db_session.add(cart_item)
    await db_session.flush()
    await db_session.commit()  # Commit all test data

    # Debug: Print test data IDs
    print(f"\n=== TEST DATA CREATED ===")
    print(f"User ID: {user.id}")
    print(f"Address ID: {address.id}, Pincode: {address.pincode}")
    print(f"Provider ID: {provider.id}, Name: {provider.first_name} {provider.last_name}")
    print(f"Pincode ID: {pincode.id}, Pincode: {pincode.pincode}, Serviceable: {pincode.is_serviceable}")
    print(f"Rate Card ID: {rate_card.id}, Provider ID: {rate_card.provider_id}")
    print(f"Cart ID: {cart.id}, Cart Items: {len([cart_item])}")

    # Return test data
    test_data = {
        'user': user,
        'address': address,
        'cart': cart,
        'cart_item': cart_item,
        'rate_card': rate_card,
        'provider': provider,
        'pincode': pincode,
        'category': category,
        'subcategory': subcategory
    }
    
    yield test_data
    
    # Cleanup: Delete test data
    try:
        # Delete in reverse order of dependencies
        await db_session.execute(delete(CartItem).where(CartItem.cart_id == cart.id))
        await db_session.execute(delete(Cart).where(Cart.id == cart.id))
        await db_session.execute(delete(RateCard).where(RateCard.id == rate_card.id))
        await db_session.execute(delete(Address).where(Address.id == address.id))
        await db_session.execute(delete(User).where(User.id == user.id))
        await db_session.commit()
    except Exception as e:
        print(f"Cleanup error: {e}")
        await db_session.rollback()


@pytest.mark.asyncio
async def test_booking_creation_integration(db_session, test_data):
    """
    Integration test: Verify BookingAgent creates booking with all required fields
    
    Tests:
    1. Booking record is created
    2. All required Booking columns have values
    3. BookingItem records are created
    4. All required BookingItem columns have values
    5. Relationships are properly set
    """
    # Arrange
    user = test_data['user']
    address = test_data['address']
    pincode = test_data['pincode']
    provider = test_data['provider']

    # Debug: Verify provider-pincode association exists before calling BookingAgent
    # Create a new session to verify data is committed
    from sqlalchemy.ext.asyncio import async_sessionmaker
    from sqlalchemy import text
    from backend.src.core.models.pincode import ProviderPincode

    async_session_maker = async_sessionmaker(db_session.bind, expire_on_commit=False)
    async with async_session_maker() as verify_session:
        # Direct SQL query to check provider_pincodes table
        sql_result = await verify_session.execute(
            text("SELECT * FROM provider_pincodes WHERE pincode_id = :pincode_id"),
            {"pincode_id": pincode.id}
        )
        sql_rows = sql_result.fetchall()
        print(f"\n[DEBUG SQL] Found {len(sql_rows)} rows in provider_pincodes for pincode_id {pincode.id}")
        for row in sql_rows:
            print(f"  - Row: {row}")

        # ORM query
        verify_result = await verify_session.execute(
            select(ProviderPincode)
            .join(Provider, ProviderPincode.provider_id == Provider.id)
            .where(
                ProviderPincode.pincode_id == pincode.id,
                Provider.is_active == True,
                Provider.is_verified == True
            )
        )
        associations = verify_result.all()
        print(f"[DEBUG ORM] Found {len(associations)} provider-pincode associations for pincode {pincode.pincode}")
        for assoc in associations:
            print(f"  - Provider ID: {assoc[0].provider_id}, Pincode ID: {assoc[0].pincode_id}")

    booking_agent = BookingAgent(db_session)

    entities = {
        "action": "book",
        "service_type": "ac_repair",
        "date": "2025-10-20",
        "time": "14:00",
        "location": "560001",
        "payment_method": "card"
    }
    
    # Act
    result = await booking_agent._create_booking(entities, user)
    
    # Assert - Check response
    assert result["action_taken"] == "booking_created", f"Expected booking_created, got {result['action_taken']}: {result.get('response')}"
    assert "booking_id" in result["metadata"]
    assert "order_id" in result["metadata"]
    assert result["metadata"]["total_amount"] > 0

    booking_id = result["metadata"]["booking_id"]
    
    # Verify Booking record in database
    booking_result = await db_session.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = booking_result.scalar_one_or_none()
    
    assert booking is not None, "Booking record not found in database"
    
    # Verify all required Booking columns
    print("\n=== BOOKING RECORD ===")
    print(f"ID: {booking.id}")
    print(f"User ID: {booking.user_id}")
    print(f"Order ID: {booking.order_id}")
    print(f"Payment Status: {booking.payment_status}")
    print(f"Payment Method: {booking.payment_method}")
    print(f"Subtotal: {booking.subtotal}")
    print(f"Total: {booking.total}")
    print(f"Status: {booking.status}")
    print(f"Preferred Date: {booking.preferred_date}")
    print(f"Preferred Time: {booking.preferred_time}")

    assert booking.user_id == user.id
    assert booking.order_id is not None and booking.order_id != ""
    assert booking.payment_status is not None
    assert booking.payment_method is not None
    assert booking.subtotal > 0
    assert booking.total > 0
    assert booking.status is not None
    assert booking.preferred_date is not None
    assert booking.preferred_time is not None
    assert booking.address_id == address.id
    
    # Verify BookingItem records
    booking_items_result = await db_session.execute(
        select(BookingItem).where(BookingItem.booking_id == booking_id)
    )
    booking_items = booking_items_result.scalars().all()
    
    assert len(booking_items) > 0, "No booking items found"
    
    print(f"\n=== BOOKING ITEMS ({len(booking_items)}) ===")
    for idx, item in enumerate(booking_items, 1):
        print(f"\nItem {idx}:")
        print(f"  ID: {item.id}")
        print(f"  Booking ID: {item.booking_id}")
        print(f"  User ID: {item.user_id}")
        print(f"  Rate Card ID: {item.rate_card_id}")
        print(f"  Provider ID: {item.provider_id}")
        print(f"  Address ID: {item.address_id}")
        print(f"  Service Name: {item.service_name}")
        print(f"  Quantity: {item.quantity}")
        print(f"  Price: {item.price}")
        print(f"  Total Amount: {item.total_amount}")
        print(f"  Final Amount: {item.final_amount}")
        print(f"  Scheduled Date: {item.scheduled_date}")
        print(f"  Scheduled Time From: {item.scheduled_time_from}")
        print(f"  Scheduled Time To: {item.scheduled_time_to}")
        print(f"  Payment Status: {item.payment_status}")
        print(f"  Status: {item.status}")
        
        # Verify all required BookingItem columns
        assert item.booking_id == booking_id
        assert item.user_id == user.id
        assert item.rate_card_id is not None
        assert item.address_id == address.id
        assert item.service_name is not None and item.service_name != ""
        assert item.quantity > 0
        assert item.price > 0
        assert item.total_amount > 0
        assert item.final_amount > 0
        assert item.scheduled_date is not None
        assert item.scheduled_time_from is not None
        assert item.scheduled_time_to is not None
        assert item.payment_status is not None
        assert item.status is not None
    
    print("\n[SUCCESS] All assertions passed! Booking created successfully with all required fields.")
    
    # Cleanup: Delete the created booking and items
    await db_session.execute(delete(BookingItem).where(BookingItem.booking_id == booking_id))
    await db_session.execute(delete(Booking).where(Booking.id == booking_id))
    await db_session.commit()

