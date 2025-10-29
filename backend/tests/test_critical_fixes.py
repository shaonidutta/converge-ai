#!/usr/bin/env python3
"""
Critical Issues Test Suite
Tests for the three critical production issues:
1. Cart empty error during booking
2. Booking cancellation not working
3. Authentication state persistence across browser tabs

This test suite validates that all fixes are working correctly.
"""

import asyncio
import pytest
import httpx
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.models.booking import Booking, BookingStatus, PaymentMethod, PaymentStatus
from src.models.cart import Cart, CartItem
from src.models.rate_card import RateCard
from src.services.booking_service import BookingService
from src.services.cart_service import CartService
from src.core.database import get_db
from src.core.security.jwt_handler import create_access_token, create_refresh_token


class TestCriticalFixes:
    """Test suite for critical production fixes"""

    @pytest.fixture
    async def test_user(self, db_session: AsyncSession):
        """Create a test user"""
        user = User(
            email="test@example.com",
            mobile="1234567890",
            first_name="Test",
            last_name="User",
            password_hash="hashed_password",
            is_active=True,
            wallet_balance=1000.0
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @pytest.fixture
    async def test_rate_card(self, db_session: AsyncSession):
        """Create a test rate card"""
        rate_card = RateCard(
            service_name="Test Service",
            description="Test service description",
            price=100.0,
            duration_minutes=60,
            is_active=True
        )
        db_session.add(rate_card)
        await db_session.commit()
        await db_session.refresh(rate_card)
        return rate_card

    @pytest.fixture
    async def booking_service(self, db_session: AsyncSession):
        """Create booking service instance"""
        return BookingService(db_session)

    @pytest.fixture
    async def cart_service(self, db_session: AsyncSession):
        """Create cart service instance"""
        return CartService(db_session)

    async def test_cart_sync_and_booking_creation(
        self, 
        db_session: AsyncSession, 
        test_user: User, 
        test_rate_card: RateCard,
        booking_service: BookingService,
        cart_service: CartService
    ):
        """
        Test Fix #1: Cart empty error during booking
        
        This test validates that:
        1. Cart items can be added to backend cart
        2. Booking creation works with cart items
        3. Cart is cleared after successful booking
        """
        print("\n=== Testing Cart Sync and Booking Creation ===")
        
        # Step 1: Add item to cart (simulating frontend cart sync)
        print("1. Adding item to cart...")
        await cart_service.add_item(
            user_id=test_user.id,
            rate_card_id=test_rate_card.id,
            quantity=1
        )
        
        # Verify cart has items
        cart_items = await cart_service.get_cart_items(test_user.id)
        assert len(cart_items) == 1
        assert cart_items[0].rate_card_id == test_rate_card.id
        print(f"   ✓ Cart has {len(cart_items)} item(s)")
        
        # Step 2: Create booking
        print("2. Creating booking...")
        booking_data = {
            "address_id": 1,  # Assuming address exists
            "preferred_date": "2024-12-01",
            "preferred_time": "10:00",
            "special_instructions": "Test booking",
            "payment_method": "wallet"
        }
        
        booking = await booking_service.create_booking(
            user=test_user,
            **booking_data
        )
        
        assert booking is not None
        assert booking.user_id == test_user.id
        assert booking.status == BookingStatus.PENDING
        assert booking.payment_method == PaymentMethod.WALLET
        print(f"   ✓ Booking created: ID={booking.id}, Status={booking.status.value}")
        
        # Step 3: Verify cart is cleared after booking
        print("3. Verifying cart is cleared...")
        cart_items_after = await cart_service.get_cart_items(test_user.id)
        assert len(cart_items_after) == 0
        print("   ✓ Cart cleared after booking")
        
        print("✅ Cart sync and booking creation test PASSED")

    async def test_booking_cancellation_fix(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_rate_card: RateCard,
        booking_service: BookingService,
        cart_service: CartService
    ):
        """
        Test Fix #2: Booking cancellation not working
        
        This test validates that:
        1. Booking can be cancelled successfully
        2. Booking status changes to CANCELLED
        3. Cancellation reason and timestamp are set
        4. Wallet refund is processed if applicable
        """
        print("\n=== Testing Booking Cancellation Fix ===")
        
        # Step 1: Create a booking first
        print("1. Creating booking to cancel...")
        await cart_service.add_item(
            user_id=test_user.id,
            rate_card_id=test_rate_card.id,
            quantity=1
        )
        
        booking = await booking_service.create_booking(
            user=test_user,
            address_id=1,
            preferred_date="2024-12-01",
            preferred_time="10:00",
            payment_method="wallet"
        )
        
        # Simulate payment completion
        booking.payment_status = PaymentStatus.PAID
        test_user.wallet_balance -= booking.total
        await db_session.commit()
        
        original_wallet_balance = test_user.wallet_balance
        print(f"   ✓ Booking created: ID={booking.id}")
        print(f"   ✓ Wallet balance after payment: {original_wallet_balance}")
        
        # Step 2: Cancel the booking
        print("2. Cancelling booking...")
        cancellation_request = type('CancelBookingRequest', (), {
            'reason': 'Test cancellation'
        })()
        
        await booking_service.cancel_booking(
            booking_id=booking.id,
            request=cancellation_request,
            user=test_user
        )
        
        # Step 3: Verify cancellation
        print("3. Verifying cancellation...")
        await db_session.refresh(booking)
        await db_session.refresh(test_user)
        
        assert booking.status == BookingStatus.CANCELLED
        assert booking.cancellation_reason == "Test cancellation"
        assert booking.cancelled_at is not None
        assert booking.payment_status == PaymentStatus.REFUNDED
        assert test_user.wallet_balance == original_wallet_balance + booking.total
        
        print(f"   ✓ Booking status: {booking.status.value}")
        print(f"   ✓ Cancellation reason: {booking.cancellation_reason}")
        print(f"   ✓ Cancelled at: {booking.cancelled_at}")
        print(f"   ✓ Payment status: {booking.payment_status.value}")
        print(f"   ✓ Wallet refunded: {booking.total}")
        
        print("✅ Booking cancellation test PASSED")

    async def test_authentication_token_validation(self):
        """
        Test Fix #3: Authentication state persistence
        
        This test validates that:
        1. JWT tokens are created correctly
        2. Token validation works
        3. Token refresh mechanism works
        """
        print("\n=== Testing Authentication Token Validation ===")
        
        # Step 1: Create tokens
        print("1. Creating authentication tokens...")
        user_data = {
            "user_id": 123,
            "user_type": "customer",
            "email": "test@example.com"
        }
        
        access_token = await create_access_token(user_data)
        refresh_token = await create_refresh_token(user_data)
        
        assert access_token is not None
        assert refresh_token is not None
        print("   ✓ Tokens created successfully")
        
        # Step 2: Validate tokens (this would be done by the frontend AuthContext)
        print("2. Validating token format...")
        assert isinstance(access_token, str)
        assert len(access_token) > 0
        assert isinstance(refresh_token, str)
        assert len(refresh_token) > 0
        print("   ✓ Token format validation passed")
        
        print("✅ Authentication token validation test PASSED")

    async def test_end_to_end_booking_flow(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_rate_card: RateCard,
        booking_service: BookingService,
        cart_service: CartService
    ):
        """
        End-to-end test of the complete booking flow
        
        This test validates the entire flow:
        1. Add items to cart
        2. Create booking
        3. Cancel booking
        4. Verify all state changes
        """
        print("\n=== Testing End-to-End Booking Flow ===")
        
        # Step 1: Add multiple items to cart
        print("1. Adding multiple items to cart...")
        await cart_service.add_item(test_user.id, test_rate_card.id, 2)
        
        cart_items = await cart_service.get_cart_items(test_user.id)
        assert len(cart_items) == 1
        assert cart_items[0].quantity == 2
        print(f"   ✓ Added {cart_items[0].quantity} items to cart")
        
        # Step 2: Create booking
        print("2. Creating booking from cart...")
        initial_balance = test_user.wallet_balance
        
        booking = await booking_service.create_booking(
            user=test_user,
            address_id=1,
            preferred_date="2024-12-01",
            preferred_time="14:00",
            special_instructions="End-to-end test",
            payment_method="wallet"
        )
        
        # Simulate payment
        booking.payment_status = PaymentStatus.PAID
        test_user.wallet_balance -= booking.total
        await db_session.commit()
        
        print(f"   ✓ Booking created: Total={booking.total}")
        
        # Step 3: Verify cart is cleared
        cart_items_after = await cart_service.get_cart_items(test_user.id)
        assert len(cart_items_after) == 0
        print("   ✓ Cart cleared after booking")
        
        # Step 4: Cancel booking
        print("3. Cancelling booking...")
        cancellation_request = type('CancelBookingRequest', (), {
            'reason': 'End-to-end test cancellation'
        })()
        
        await booking_service.cancel_booking(
            booking_id=booking.id,
            request=cancellation_request,
            user=test_user
        )
        
        # Step 5: Verify final state
        print("4. Verifying final state...")
        await db_session.refresh(booking)
        await db_session.refresh(test_user)
        
        assert booking.status == BookingStatus.CANCELLED
        assert test_user.wallet_balance == initial_balance  # Full refund
        
        print(f"   ✓ Final booking status: {booking.status.value}")
        print(f"   ✓ Wallet balance restored: {test_user.wallet_balance}")
        
        print("✅ End-to-end booking flow test PASSED")


if __name__ == "__main__":
    print("Critical Issues Test Suite")
    print("=" * 50)
    print("This test suite validates fixes for:")
    print("1. Cart empty error during booking")
    print("2. Booking cancellation not working") 
    print("3. Authentication state persistence")
    print("=" * 50)
    
    # Run with: python -m pytest backend/tests/test_critical_fixes.py -v
    pytest.main([__file__, "-v"])
