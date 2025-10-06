"""
Test API Endpoints
Comprehensive tests for user management API
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Test data
test_user_data = {
    "email": f"test_api_{datetime.now().timestamp()}@example.com",
    "mobile": f"+91{int(datetime.now().timestamp()) % 10000000000}",
    "password": "TestPassword123!@#",
    "first_name": "API",
    "last_name": "Test"
}

def print_header(title):
    """Print test section header"""
    print(f"\n{'=' * 80}")
    print(f"{title}")
    print(f"{'=' * 80}\n")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def test_health_check():
    """Test health check endpoint"""
    print_header("TEST 1: HEALTH CHECK")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health Status: {data.get('status')}")
            print_info(f"Database: {data.get('components', {}).get('database')}")
            print_info(f"Redis: {data.get('components', {}).get('redis')}")
            return True
        else:
            print_error(f"Health check failed: {response.text}")
            return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False

def test_user_registration():
    """Test user registration endpoint"""
    print_header("TEST 2: USER REGISTRATION")
    
    try:
        response = requests.post(
            f"{API_V1}/auth/register",
            json=test_user_data
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print_success("User registered successfully")
            print_info(f"User ID: {data['user']['id']}")
            print_info(f"Email: {data['user']['email']}")
            print_info(f"Mobile: {data['user']['mobile']}")
            print_info(f"Access Token: {data['tokens']['access_token'][:50]}...")
            return data
        else:
            print_error(f"Registration failed: {response.text}")
            return None
    except Exception as e:
        print_error(f"Registration error: {e}")
        return None

def test_user_login(identifier):
    """Test user login endpoint"""
    print_header("TEST 3: USER LOGIN")
    
    try:
        response = requests.post(
            f"{API_V1}/auth/login",
            json={
                "identifier": identifier,
                "password": test_user_data["password"]
            }
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("User logged in successfully")
            print_info(f"User ID: {data['user']['id']}")
            print_info(f"Access Token: {data['tokens']['access_token'][:50]}...")
            return data
        else:
            print_error(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print_error(f"Login error: {e}")
        return None

def test_get_profile(access_token):
    """Test get user profile endpoint"""
    print_header("TEST 4: GET USER PROFILE")
    
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{API_V1}/users/me", headers=headers)
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Profile retrieved successfully")
            print_info(f"User ID: {data['id']}")
            print_info(f"Name: {data['first_name']} {data['last_name']}")
            print_info(f"Email: {data['email']}")
            print_info(f"Wallet Balance: ₹{data['wallet_balance']}")
            return True
        else:
            print_error(f"Get profile failed: {response.text}")
            return False
    except Exception as e:
        print_error(f"Get profile error: {e}")
        return False

def test_update_profile(access_token):
    """Test update user profile endpoint"""
    print_header("TEST 5: UPDATE USER PROFILE")
    
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        update_data = {
            "first_name": "Updated",
            "last_name": "Name"
        }
        response = requests.put(
            f"{API_V1}/users/me",
            headers=headers,
            json=update_data
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Profile updated successfully")
            print_info(f"New Name: {data['first_name']} {data['last_name']}")
            return True
        else:
            print_error(f"Update profile failed: {response.text}")
            return False
    except Exception as e:
        print_error(f"Update profile error: {e}")
        return False

def test_change_password(access_token):
    """Test change password endpoint"""
    print_header("TEST 6: CHANGE PASSWORD")
    
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        password_data = {
            "current_password": test_user_data["password"],
            "new_password": "NewPassword123!@#"
        }
        response = requests.patch(
            f"{API_V1}/users/me/password",
            headers=headers,
            json=password_data
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Password changed: {data['message']}")
            return True
        else:
            print_error(f"Change password failed: {response.text}")
            return False
    except Exception as e:
        print_error(f"Change password error: {e}")
        return False

def test_refresh_token(refresh_token):
    """Test refresh token endpoint"""
    print_header("TEST 7: REFRESH TOKEN")
    
    try:
        response = requests.post(
            f"{API_V1}/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Token refreshed successfully")
            print_info(f"New Access Token: {data['access_token'][:50]}...")
            return data
        else:
            print_error(f"Refresh token failed: {response.text}")
            return None
    except Exception as e:
        print_error(f"Refresh token error: {e}")
        return None

def test_invalid_login():
    """Test login with invalid credentials"""
    print_header("TEST 8: INVALID LOGIN (Should Fail)")
    
    try:
        response = requests.post(
            f"{API_V1}/auth/login",
            json={
                "identifier": "nonexistent@example.com",
                "password": "WrongPassword123!"
            }
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print_success("Invalid login correctly rejected")
            return True
        else:
            print_error(f"Invalid login should have been rejected")
            return False
    except Exception as e:
        print_error(f"Invalid login test error: {e}")
        return False

def test_unauthorized_access():
    """Test accessing protected endpoint without token"""
    print_header("TEST 9: UNAUTHORIZED ACCESS (Should Fail)")
    
    try:
        response = requests.get(f"{API_V1}/users/me")
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 401 or response.status_code == 403:
            print_success("Unauthorized access correctly rejected")
            return True
        else:
            print_error(f"Unauthorized access should have been rejected")
            return False
    except Exception as e:
        print_error(f"Unauthorized access test error: {e}")
        return False

def main():
    """Run all API tests"""
    print("\n" + "=" * 80)
    print("API ENDPOINTS - COMPREHENSIVE TESTS")
    print("=" * 80)
    
    results = []
    
    # Test 1: Health Check
    results.append(("Health Check", test_health_check()))
    
    # Test 2: User Registration
    registration_data = test_user_registration()
    results.append(("User Registration", registration_data is not None))
    
    if not registration_data:
        print_error("Cannot continue tests without successful registration")
        return
    
    access_token = registration_data['tokens']['access_token']
    refresh_token = registration_data['tokens']['refresh_token']
    user_email = registration_data['user']['email']
    
    # Test 3: User Login
    login_data = test_user_login(user_email)
    results.append(("User Login", login_data is not None))
    
    # Test 4: Get Profile
    results.append(("Get User Profile", test_get_profile(access_token)))
    
    # Test 5: Update Profile
    results.append(("Update User Profile", test_update_profile(access_token)))
    
    # Test 6: Change Password
    results.append(("Change Password", test_change_password(access_token)))
    
    # Test 7: Refresh Token
    refresh_data = test_refresh_token(refresh_token)
    results.append(("Refresh Token", refresh_data is not None))
    
    # Test 8: Invalid Login
    results.append(("Invalid Login", test_invalid_login()))
    
    # Test 9: Unauthorized Access
    results.append(("Unauthorized Access", test_unauthorized_access()))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'=' * 80}")
    print(f"TOTAL: {passed}/{total} tests passed")
    print(f"{'=' * 80}\n")
    
    if passed == total:
        print("🎉 All API tests passed successfully!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")

if __name__ == "__main__":
    main()

