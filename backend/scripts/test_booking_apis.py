# -*- coding: utf-8 -*-
"""
Booking APIs Testing Script
Tests all booking-related endpoints
"""

import requests
import json
import sys
import io
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

# Store tokens
auth_tokens = {
    "user": None,
    "user_refresh": None
}

# Test results
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0
}


def test_endpoint(
    module: str,
    endpoint: str,
    method: str,
    expected_status: int,
    headers: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
    description: str = ""
) -> Optional[Any]:
    """Test an API endpoint"""
    test_results["total"] += 1
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=json_data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=json_data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, json=json_data)
        
        if response.status_code == expected_status:
            test_results["passed"] += 1
            print(f"{Colors.GREEN}✅ [{module}] {method} {endpoint} - PASS{Colors.RESET}")
            if description:
                print(f"   {description}")
            return response.json() if response.text else None
        else:
            test_results["failed"] += 1
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response"
            print(f"{Colors.RED}❌ [{module}] {method} {endpoint} - FAIL{Colors.RESET}")
            print(f"   Expected {expected_status}, got {response.status_code}. Error: {error_detail}")
            return None
            
    except Exception as e:
        test_results["failed"] += 1
        print(f"{Colors.RED}❌ [{module}] {method} {endpoint} - FAIL{Colors.RESET}")
        print(f"   Exception: {str(e)}")
        return None


def get_auth_header(token_type: str = "user") -> Dict[str, str]:
    """Get authorization header"""
    token = auth_tokens.get(token_type)
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def setup_test_user():
    """Register and login a test user"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("SETUP: Creating Test User")
    print(f"{'='*60}{Colors.RESET}\n")
    
    # Register
    timestamp = datetime.now().timestamp()
    register_data = {
        "email": f"booking_test_{timestamp}@example.com",
        "mobile": f"+91{int(timestamp) % 10000000000}",
        "password": "TestPass123!",
        "first_name": "Booking",
        "last_name": "Tester"
    }
    
    response = test_endpoint(
        "SETUP",
        "/auth/register",
        "POST",
        201,
        json_data=register_data,
        description="Register test user"
    )
    
    if response:
        tokens = response.get("tokens", {})
        auth_tokens["user"] = tokens.get("access_token")
        auth_tokens["user_refresh"] = tokens.get("refresh_token")
        print(f"{Colors.GREEN}✅ Test user created and logged in{Colors.RESET}\n")
        return True
    
    return False


def setup_test_data():
    """Setup required test data (address and cart item)"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("SETUP: Creating Test Data")
    print(f"{'='*60}{Colors.RESET}\n")
    
    # Create address
    address_data = {
        "address_line1": "123 Test Street",
        "address_line2": "Apt 4B",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400001",
        "is_default": True
    }
    
    address_response = test_endpoint(
        "SETUP",
        "/addresses",
        "POST",
        201,
        headers=get_auth_header("user"),
        json_data=address_data,
        description="Create test address"
    )
    
    if not address_response:
        print(f"{Colors.RED}❌ Failed to create address{Colors.RESET}")
        return None, None
    
    address_id = address_response.get("id")
    print(f"{Colors.GREEN}✅ Address created: ID={address_id}{Colors.RESET}\n")
    
    # Get rate cards
    rate_cards_response = test_endpoint(
        "SETUP",
        "/categories/subcategories/1/rate-cards",
        "GET",
        200,
        headers=get_auth_header("user"),
        description="Get rate cards"
    )
    
    if not rate_cards_response or len(rate_cards_response) == 0:
        print(f"{Colors.RED}❌ No rate cards found{Colors.RESET}")
        return address_id, None
    
    rate_card_id = rate_cards_response[0].get("id")
    print(f"{Colors.GREEN}✅ Rate card found: ID={rate_card_id}{Colors.RESET}\n")
    
    # Add to cart
    cart_data = {
        "rate_card_id": rate_card_id,
        "quantity": 1
    }
    
    cart_response = test_endpoint(
        "SETUP",
        "/cart/items",
        "POST",
        201,
        headers=get_auth_header("user"),
        json_data=cart_data,
        description="Add item to cart"
    )
    
    if cart_response:
        print(f"{Colors.GREEN}✅ Item added to cart{Colors.RESET}\n")
    
    return address_id, rate_card_id


def test_booking_apis(address_id: int):
    """Test all booking endpoints"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("BOOKING APIs TESTING")
    print(f"{'='*60}{Colors.RESET}\n")
    
    booking_id = None
    
    # 1. Create Booking
    future_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    booking_data = {
        "address_id": address_id,
        "preferred_date": future_date,
        "preferred_time": "10:00",
        "special_instructions": "Test booking - automated test",
        "payment_method": "cash"  # Valid values: card, upi, wallet, cash
    }
    
    booking_response = test_endpoint(
        "BOOKINGS",
        "/bookings",
        "POST",
        201,
        headers=get_auth_header("user"),
        json_data=booking_data,
        description="Create new booking"
    )
    
    if booking_response:
        booking_id = booking_response.get("id")
        print(f"{Colors.GREEN}✅ Booking created: ID={booking_id}{Colors.RESET}\n")
    else:
        print(f"{Colors.RED}❌ Failed to create booking - skipping remaining tests{Colors.RESET}")
        return
    
    # 2. List Bookings
    test_endpoint(
        "BOOKINGS",
        "/bookings",
        "GET",
        200,
        headers=get_auth_header("user"),
        description="List user bookings"
    )
    
    # 3. Get Booking Details
    test_endpoint(
        "BOOKINGS",
        f"/bookings/{booking_id}",
        "GET",
        200,
        headers=get_auth_header("user"),
        description=f"Get booking {booking_id} details"
    )
    
    # 4. Reschedule Booking
    reschedule_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
    reschedule_data = {
        "preferred_date": reschedule_date,
        "preferred_time": "14:00",
        "reason": "Testing reschedule functionality"
    }
    
    test_endpoint(
        "BOOKINGS",
        f"/bookings/{booking_id}/reschedule",
        "POST",
        200,
        headers=get_auth_header("user"),
        json_data=reschedule_data,
        description=f"Reschedule booking {booking_id}"
    )
    
    # 5. Cancel Booking
    cancel_data = {
        "reason": "Testing cancellation - automated test cleanup"
    }
    
    test_endpoint(
        "BOOKINGS",
        f"/bookings/{booking_id}/cancel",
        "POST",
        200,
        headers=get_auth_header("user"),
        json_data=cancel_data,
        description=f"Cancel booking {booking_id}"
    )


def print_summary():
    """Print test summary"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}{Colors.RESET}\n")
    
    print(f"Total Tests: {test_results['total']}")
    print(f"Passed: {Colors.GREEN}{test_results['passed']}{Colors.RESET}")
    print(f"Failed: {Colors.RED}{test_results['failed']}{Colors.RESET}")
    print(f"Skipped: {Colors.YELLOW}{test_results['skipped']}{Colors.RESET}")
    
    if test_results['total'] > 0:
        success_rate = (test_results['passed'] / test_results['total']) * 100
        print(f"Success Rate: {success_rate:.1f}%\n")


def main():
    """Run all booking API tests"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("BOOKING APIs COMPREHENSIVE TESTING")
    print(f"{'='*60}{Colors.RESET}\n")
    print(f"Base URL: {BASE_URL}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Setup
    if not setup_test_user():
        print(f"{Colors.RED}Failed to setup test user - aborting{Colors.RESET}")
        return
    
    address_id, rate_card_id = setup_test_data()
    
    if not address_id:
        print(f"{Colors.RED}Failed to setup test data - aborting{Colors.RESET}")
        return
    
    # Run booking tests
    test_booking_apis(address_id)
    
    # Print summary
    print_summary()


if __name__ == "__main__":
    main()

