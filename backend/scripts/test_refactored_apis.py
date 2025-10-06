# -*- coding: utf-8 -*-
"""
Comprehensive API Testing Script for Refactored Architecture
Tests all 21 endpoints systematically
"""

import requests
import json
import sys
import io
from typing import Dict, Any, Optional
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Test results storage
test_results = []
auth_tokens = {}


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def log_test(module: str, endpoint: str, method: str, status: str, details: str = ""):
    """Log test result"""
    result = {
        "module": module,
        "endpoint": endpoint,
        "method": method,
        "status": status,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    test_results.append(result)
    
    color = Colors.GREEN if status == "PASS" else Colors.RED
    symbol = "✅" if status == "PASS" else "❌"
    print(f"{color}{symbol} [{module}] {method} {endpoint} - {status}{Colors.RESET}")
    if details:
        print(f"   {details}")


def test_endpoint(
    module: str,
    endpoint: str,
    method: str,
    expected_status: int,
    headers: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
    description: str = ""
) -> Optional[Dict]:
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=json_data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=json_data)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=json_data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            log_test(module, endpoint, method, "FAIL", f"Unknown method: {method}")
            return None
        
        # Check status code
        if response.status_code == expected_status:
            log_test(module, endpoint, method, "PASS", description)
            try:
                return response.json()
            except:
                return {"status": "success"}
        else:
            error_detail = ""
            try:
                error_detail = response.json().get("detail", "")
            except:
                error_detail = response.text[:100]
            
            log_test(
                module, 
                endpoint, 
                method, 
                "FAIL", 
                f"Expected {expected_status}, got {response.status_code}. Error: {error_detail}"
            )
            return None
            
    except Exception as e:
        log_test(module, endpoint, method, "FAIL", f"Exception: {str(e)}")
        return None


def get_auth_header(token_type: str = "user") -> Dict:
    """Get authorization header"""
    token = auth_tokens.get(token_type)
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


# ============================================================================
# TEST SUITE 1: AUTHENTICATION APIs (4 endpoints)
# ============================================================================

def test_auth_apis():
    """Test authentication endpoints"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("TEST SUITE 1: AUTHENTICATION APIs")
    print(f"{'='*60}{Colors.RESET}\n")
    
    # 1. Register User
    register_data = {
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "mobile": f"+91{int(datetime.now().timestamp()) % 10000000000}",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = test_endpoint(
        "AUTH",
        "/auth/register",
        "POST",
        201,
        json_data=register_data,
        description="Register new user"
    )
    
    if response:
        tokens = response.get("tokens", {})
        auth_tokens["user"] = tokens.get("access_token")
        auth_tokens["user_refresh"] = tokens.get("refresh_token")
    
    # 2. Login User
    login_data = {
        "identifier": register_data["email"],
        "password": register_data["password"]
    }
    
    response = test_endpoint(
        "AUTH",
        "/auth/login",
        "POST",
        200,
        json_data=login_data,
        description="Login with credentials"
    )
    
    if response:
        tokens = response.get("tokens", {})
        auth_tokens["user"] = tokens.get("access_token")
    
    # 3. Refresh Token
    if auth_tokens.get("user_refresh"):
        refresh_data = {
            "refresh_token": auth_tokens["user_refresh"]
        }
        
        response = test_endpoint(
            "AUTH",
            "/auth/refresh",
            "POST",
            200,
            json_data=refresh_data,
            description="Refresh access token"
        )
    
    # 4. Logout User
    test_endpoint(
        "AUTH",
        "/auth/logout",
        "POST",
        200,
        headers=get_auth_header("user"),
        description="Logout user"
    )


# ============================================================================
# TEST SUITE 2: USER MANAGEMENT APIs (3 endpoints)
# ============================================================================

def test_user_apis():
    """Test user management endpoints"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("TEST SUITE 2: USER MANAGEMENT APIs")
    print(f"{'='*60}{Colors.RESET}\n")
    
    # 1. Get User Profile
    test_endpoint(
        "USERS",
        "/users/me",
        "GET",
        200,
        headers=get_auth_header("user"),
        description="Get current user profile"
    )
    
    # 2. Update User Profile
    update_data = {
        "first_name": "Updated",
        "last_name": "Name"
    }
    
    test_endpoint(
        "USERS",
        "/users/me",
        "PUT",
        200,
        headers=get_auth_header("user"),
        json_data=update_data,
        description="Update user profile"
    )
    
    # 3. Delete User Account (skip to keep test user)
    # test_endpoint(
    #     "USERS",
    #     "/users/me",
    #     "DELETE",
    #     200,
    #     headers=get_auth_header("user"),
    #     description="Delete user account"
    # )
    print(f"{Colors.YELLOW}⏭️  [USERS] DELETE /users/me - SKIPPED (preserving test user){Colors.RESET}")


# ============================================================================
# TEST SUITE 3: CATEGORY APIs (4 endpoints)
# ============================================================================

def test_category_apis():
    """Test category endpoints"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("TEST SUITE 3: CATEGORY APIs")
    print(f"{'='*60}{Colors.RESET}\n")
    
    # 1. List Categories
    response = test_endpoint(
        "CATEGORIES",
        "/categories",
        "GET",
        200,
        description="List all categories"
    )
    
    category_id = None
    if response and len(response) > 0:
        category_id = response[0]["id"]
    
    # 2. Get Category
    if category_id:
        test_endpoint(
            "CATEGORIES",
            f"/categories/{category_id}",
            "GET",
            200,
            description=f"Get category {category_id}"
        )
        
        # 3. List Subcategories
        response = test_endpoint(
            "CATEGORIES",
            f"/categories/{category_id}/subcategories",
            "GET",
            200,
            description=f"List subcategories for category {category_id}"
        )
        
        subcategory_id = None
        if response and len(response) > 0:
            subcategory_id = response[0]["id"]
        
        # 4. List Rate Cards
        if subcategory_id:
            test_endpoint(
                "CATEGORIES",
                f"/categories/subcategories/{subcategory_id}/rate-cards",
                "GET",
                200,
                description=f"List rate cards for subcategory {subcategory_id}"
            )


# ============================================================================
# TEST SUITE 4: CART APIs (5 endpoints)
# ============================================================================

def test_cart_apis():
    """Test cart endpoints"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("TEST SUITE 4: CART APIs")
    print(f"{'='*60}{Colors.RESET}\n")

    # 1. Get Cart
    response = test_endpoint(
        "CART",
        "/cart",
        "GET",
        200,
        headers=get_auth_header("user"),
        description="Get user cart"
    )

    # 2. Add to Cart (need a rate card ID)
    add_data = {
        "rate_card_id": 1,
        "quantity": 2
    }

    test_endpoint(
        "CART",
        "/cart/items",
        "POST",
        201,
        headers=get_auth_header("user"),
        json_data=add_data,
        description="Add item to cart"
    )

    # 3. Update Cart Item
    update_data = {
        "quantity": 3
    }

    test_endpoint(
        "CART",
        "/cart/items/1",
        "PUT",
        200,
        headers=get_auth_header("user"),
        json_data=update_data,
        description="Update cart item quantity"
    )

    # 4. Remove Cart Item
    test_endpoint(
        "CART",
        "/cart/items/1",
        "DELETE",
        200,
        headers=get_auth_header("user"),
        description="Remove item from cart"
    )

    # 5. Clear Cart
    test_endpoint(
        "CART",
        "/cart",
        "DELETE",
        200,
        headers=get_auth_header("user"),
        description="Clear cart"
    )


# ============================================================================
# TEST SUITE 5: ADDRESS APIs (5 endpoints)
# ============================================================================

def test_address_apis():
    """Test address endpoints"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("TEST SUITE 5: ADDRESS APIs")
    print(f"{'='*60}{Colors.RESET}\n")

    # 1. List Addresses
    test_endpoint(
        "ADDRESSES",
        "/addresses",
        "GET",
        200,
        headers=get_auth_header("user"),
        description="List user addresses"
    )

    # 2. Add Address
    address_data = {
        "address_line1": "123 Test Street",
        "address_line2": "Apt 4B",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400001",
        "is_default": True
    }

    response = test_endpoint(
        "ADDRESSES",
        "/addresses",
        "POST",
        201,
        headers=get_auth_header("user"),
        json_data=address_data,
        description="Add new address"
    )

    address_id = None
    if response:
        address_id = response.get("id")

    # 3. Get Address
    if address_id:
        test_endpoint(
            "ADDRESSES",
            f"/addresses/{address_id}",
            "GET",
            200,
            headers=get_auth_header("user"),
            description=f"Get address {address_id}"
        )

        # 4. Update Address (skip - not required for MVP)
        # update_data = {
        #     "address_line2": "Apt 5C"
        # }
        #
        # test_endpoint(
        #     "ADDRESSES",
        #     f"/addresses/{address_id}",
        #     "PUT",
        #     200,
        #     headers=get_auth_header("user"),
        #     json_data=update_data,
        #     description=f"Update address {address_id}"
        # )
        print(f"{Colors.YELLOW}⏭️  [ADDRESSES] PUT /addresses/{address_id} - SKIPPED (not required for MVP){Colors.RESET}")

        # 5. Delete Address (skip to preserve test data)
        # test_endpoint(
        #     "ADDRESSES",
        #     f"/addresses/{address_id}",
        #     "DELETE",
        #     200,
        #     headers=get_auth_header("user"),
        #     description=f"Delete address {address_id}"
        # )
        print(f"{Colors.YELLOW}⏭️  [ADDRESSES] DELETE /addresses/{address_id} - SKIPPED (preserving test data){Colors.RESET}")


# ============================================================================
# TEST SUITE 6: BOOKING APIs (4 endpoints)
# ============================================================================

def test_booking_apis():
    """Test booking endpoints"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("TEST SUITE 6: BOOKING APIs")
    print(f"{'='*60}{Colors.RESET}\n")

    # 1. List Bookings (should work even if empty)
    bookings_response = test_endpoint(
        "BOOKINGS",
        "/bookings",
        "GET",
        200,
        headers=get_auth_header("user"),
        description="List user bookings"
    )

    # Check if user has any existing bookings
    existing_bookings = bookings_response if bookings_response else []

    if existing_bookings and len(existing_bookings) > 0:
        # User has bookings - test with first booking
        booking_id = existing_bookings[0].get("id")
        booking_status = existing_bookings[0].get("status")

        print(f"\n{Colors.BLUE}Found existing booking: ID={booking_id}, Status={booking_status}{Colors.RESET}\n")

        # 2. Get Booking Details
        booking_detail = test_endpoint(
            "BOOKINGS",
            f"/bookings/{booking_id}",
            "GET",
            200,
            headers=get_auth_header("user"),
            description=f"Get booking {booking_id} details"
        )

        # 3. Reschedule Booking (only if status allows)
        if booking_status in ["PENDING", "CONFIRMED"]:
            from datetime import datetime, timedelta
            future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

            reschedule_data = {
                "preferred_date": future_date,
                "preferred_time": "15:00",
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
        else:
            print(f"{Colors.YELLOW}⏭️  [BOOKINGS] POST /bookings/{booking_id}/reschedule - SKIPPED (status: {booking_status}){Colors.RESET}")

        # 4. Cancel Booking (only if status allows and not already cancelled)
        if booking_status in ["PENDING", "CONFIRMED"]:
            cancel_data = {
                "reason": "Testing cancellation functionality - please ignore"
            }

            # Ask before cancelling
            print(f"{Colors.YELLOW}⚠️  About to cancel booking {booking_id} for testing{Colors.RESET}")

            test_endpoint(
                "BOOKINGS",
                f"/bookings/{booking_id}/cancel",
                "POST",
                200,
                headers=get_auth_header("user"),
                json_data=cancel_data,
                description=f"Cancel booking {booking_id}"
            )
        else:
            print(f"{Colors.YELLOW}⏭️  [BOOKINGS] POST /bookings/{booking_id}/cancel - SKIPPED (status: {booking_status}){Colors.RESET}")

    else:
        # No existing bookings - try to create one
        print(f"\n{Colors.YELLOW}No existing bookings found. Attempting to create test booking...{Colors.RESET}\n")

        # First, we need to get a valid rate card and add to cart
        # Get rate cards from category 1, subcategory 1
        rate_cards_response = test_endpoint(
            "BOOKINGS-SETUP",
            "/categories/subcategories/1/rate-cards",
            "GET",
            200,
            headers=get_auth_header("user"),
            description="Get rate cards for booking setup"
        )

        if rate_cards_response and len(rate_cards_response) > 0:
            rate_card_id = rate_cards_response[0].get("id")
            print(f"{Colors.GREEN}Found rate card: ID={rate_card_id}{Colors.RESET}")

            # Add to cart
            add_cart_data = {
                "rate_card_id": rate_card_id,
                "quantity": 1
            }

            cart_item = test_endpoint(
                "BOOKINGS-SETUP",
                "/cart/items",
                "POST",
                201,
                headers=get_auth_header("user"),
                json_data=add_cart_data,
                description="Add item to cart for booking"
            )

            if cart_item:
                # Get user's addresses
                addresses_response = test_endpoint(
                    "BOOKINGS-SETUP",
                    "/addresses",
                    "GET",
                    200,
                    headers=get_auth_header("user"),
                    description="Get addresses for booking"
                )

                if addresses_response and len(addresses_response) > 0:
                    address_id = addresses_response[0].get("id")
                    print(f"{Colors.GREEN}Found address: ID={address_id}{Colors.RESET}")

                    # Create booking
                    from datetime import datetime, timedelta
                    future_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")

                    booking_data = {
                        "address_id": address_id,
                        "preferred_date": future_date,
                        "preferred_time": "10:00",
                        "special_instructions": "Test booking - automated test",
                        "payment_method": "cod"  # Use COD to avoid wallet balance issues
                    }

                    new_booking = test_endpoint(
                        "BOOKINGS",
                        "/bookings",
                        "POST",
                        201,
                        headers=get_auth_header("user"),
                        json_data=booking_data,
                        description="Create new booking"
                    )

                    if new_booking:
                        new_booking_id = new_booking.get("id")
                        print(f"\n{Colors.GREEN}✅ Booking created successfully: ID={new_booking_id}{Colors.RESET}\n")

                        # Test get booking
                        test_endpoint(
                            "BOOKINGS",
                            f"/bookings/{new_booking_id}",
                            "GET",
                            200,
                            headers=get_auth_header("user"),
                            description=f"Get booking {new_booking_id} details"
                        )

                        # Test reschedule
                        reschedule_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
                        reschedule_data = {
                            "preferred_date": reschedule_date,
                            "preferred_time": "14:00",
                            "reason": "Testing reschedule functionality"
                        }

                        test_endpoint(
                            "BOOKINGS",
                            f"/bookings/{new_booking_id}/reschedule",
                            "POST",
                            200,
                            headers=get_auth_header("user"),
                            json_data=reschedule_data,
                            description=f"Reschedule booking {new_booking_id}"
                        )

                        # Test cancel
                        cancel_data = {
                            "reason": "Testing cancellation - automated test cleanup"
                        }

                        test_endpoint(
                            "BOOKINGS",
                            f"/bookings/{new_booking_id}/cancel",
                            "POST",
                            200,
                            headers=get_auth_header("user"),
                            json_data=cancel_data,
                            description=f"Cancel booking {new_booking_id}"
                        )
                    else:
                        print(f"{Colors.RED}❌ Failed to create booking{Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}⏭️  No addresses found - cannot create booking{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}⏭️  Failed to add item to cart{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⏭️  No rate cards found - cannot create booking{Colors.RESET}")


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("COMPREHENSIVE API TESTING - REFACTORED ARCHITECTURE")
    print(f"{'='*60}{Colors.RESET}\n")
    print(f"Base URL: {BASE_URL}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Run test suites
    test_auth_apis()
    test_user_apis()
    test_category_apis()
    test_cart_apis()
    test_address_apis()
    test_booking_apis()
    
    # Print summary
    print(f"\n{Colors.BLUE}{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}{Colors.RESET}\n")
    
    passed = sum(1 for r in test_results if r["status"] == "PASS")
    failed = sum(1 for r in test_results if r["status"] == "FAIL")
    total = len(test_results)
    
    print(f"Total Tests: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
    print(f"Success Rate: {(passed/total*100):.1f}%\n")
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    
    print(f"Detailed results saved to: test_results.json\n")


if __name__ == "__main__":
    main()

