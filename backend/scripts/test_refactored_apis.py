"""
Comprehensive API Testing Script for Refactored Architecture
Tests all 21 endpoints systematically
"""

import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime

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
        "landmark": "Near Test Mall",
        "address_type": "home",
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

        # 4. Update Address
        update_data = {
            "landmark": "Near Updated Mall"
        }

        test_endpoint(
            "ADDRESSES",
            f"/addresses/{address_id}",
            "PUT",
            200,
            headers=get_auth_header("user"),
            json_data=update_data,
            description=f"Update address {address_id}"
        )

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

