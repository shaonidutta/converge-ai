"""
Test chatbot scenarios using direct API calls
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def print_separator(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_result(response_data):
    """Pretty print API response"""
    if 'user_message' in response_data:
        print(f"\n📤 User: {response_data['user_message']['message']}")
    if 'assistant_message' in response_data:
        print(f"📥 Lisa: {response_data['assistant_message']['message']}")
        print(f"🎯 Intent: {response_data['assistant_message']['intent']}")
    if 'response_time_ms' in response_data:
        print(f"⏱️  Response Time: {response_data['response_time_ms']}ms")

def login():
    """Login and get JWT token"""
    print_separator("LOGIN")

    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "identifier": "agtshaonidutta2k@gmail.com",
            "password": "Shaoni@123"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful")
        print(f"📦 Response data: {json.dumps(data, indent=2)}")

        # Try different possible token field names
        token = data.get('access_token') or data.get('token') or data.get('accessToken')

        if token:
            print(f"🔑 Token: {token[:50]}...")
            return token
        else:
            print(f"❌ No token found in response")
            return None
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def send_message(token, message, session_id=None):
    """Send a chat message"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {"message": message}
    if session_id:
        payload["session_id"] = session_id
    
    response = requests.post(
        f"{BASE_URL}/chat/message",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)
        return None

def test_scenario_1_service_information(token):
    """Test 1: Service information query"""
    print_separator("TEST 1: Service Information Query")
    
    session_id = f"test_service_info_{int(time.time())}"
    
    result = send_message(token, "can u help with services?", session_id)
    
    if result:
        print_result(result)
        
        # Validation
        intent = result['assistant_message']['intent']
        response = result['assistant_message']['message']
        
        print("\n📊 Validation:")
        
        # Check if routed to service agent
        if intent in ['service_information', 'service_inquiry', 'service_discovery']:
            print("✅ Intent correctly classified as service-related")
        else:
            print(f"❌ Intent is '{intent}', expected service-related intent")
        
        # Check if response mentions policy
        if 'policy' in response.lower():
            print("❌ Response mentions 'policy' (should be about services)")
        else:
            print("✅ Response does not mention 'policy'")
        
        # Check if response is about services
        if any(word in response.lower() for word in ['service', 'category', 'categories', 'help']):
            print("✅ Response is about services")
        else:
            print("⚠️  Response may not be about services")
        
        return True
    return False

def test_scenario_2_booking_slot_filling(token):
    """Test 2: Booking flow with slot-filling"""
    print_separator("TEST 2: Booking Flow with Slot-Filling")
    
    session_id = f"test_booking_{int(time.time())}"
    
    # Turn 1: Initial booking request
    print("\n--- Turn 1: Initial Booking Request ---")
    result1 = send_message(token, "I want to book a service", session_id)
    
    if not result1:
        return False
    
    print_result(result1)
    response1 = result1['assistant_message']['message']
    
    print("\n📊 Validation:")
    if any(word in response1.lower() for word in ['location', 'pincode', 'where', 'address']):
        print("✅ Lisa asks for location/pincode")
    else:
        print(f"⚠️  Lisa should ask for location, but said: {response1[:100]}")
    
    time.sleep(1)  # Small delay between requests
    
    # Turn 2: Provide location
    print("\n--- Turn 2: Provide Location ---")
    result2 = send_message(token, "282002", session_id)
    
    if not result2:
        return False
    
    print_result(result2)
    response2 = result2['assistant_message']['message']
    
    print("\n📊 Validation:")
    
    # Check if location question is repeated (context awareness test)
    if 'location' in response2.lower() or 'pincode' in response2.lower():
        print("❌ CRITICAL: Lisa repeated the location question (NO CONTEXT AWARENESS!)")
        print("   This means slot-filling is not maintaining context properly")
    else:
        print("✅ PASS: Lisa did NOT repeat location question (context maintained)")
    
    # Check if asks for next piece of information
    if any(word in response2.lower() for word in ['date', 'time', 'when', 'service', 'what']):
        print("✅ Lisa asks for next piece of information")
    else:
        print(f"⚠️  Lisa's response: {response2[:100]}")
    
    # Check for error messages
    if 'error' in response2.lower() or 'apologize' in response2.lower() or 'sorry' in response2.lower():
        print("❌ Got error response")
    else:
        print("✅ No error response")
    
    time.sleep(1)
    
    # Turn 3: Provide more information
    print("\n--- Turn 3: Provide Date, Time, and Service ---")
    result3 = send_message(token, "tomorrow at 2 PM, I need AC service", session_id)
    
    if not result3:
        return False
    
    print_result(result3)
    response3 = result3['assistant_message']['message']
    
    print("\n📊 Validation:")
    if 'error' in response3.lower() or 'apologize' in response3.lower():
        print("❌ Got error response")
    else:
        print("✅ No error response")
    
    return True

def test_scenario_3_context_awareness(token):
    """Test 3: Context awareness across messages"""
    print_separator("TEST 3: Context Awareness")
    
    session_id = f"test_context_{int(time.time())}"
    
    # Turn 1: Greeting
    print("\n--- Turn 1: Greeting ---")
    result1 = send_message(token, "hi", session_id)
    
    if not result1:
        return False
    
    print_result(result1)
    
    time.sleep(1)
    
    # Turn 2: Ask about services
    print("\n--- Turn 2: Ask About Services ---")
    result2 = send_message(token, "what services do you offer?", session_id)
    
    if not result2:
        return False
    
    print_result(result2)
    
    intent = result2['assistant_message']['intent']
    response = result2['assistant_message']['message']
    
    print("\n📊 Validation:")
    if intent in ['service_information', 'service_inquiry', 'service_discovery']:
        print("✅ Intent correctly classified as service-related")
    else:
        print(f"⚠️  Intent is '{intent}', expected service-related")
    
    if 'policy' in response.lower():
        print("❌ Response mentions 'policy' (should be about services)")
    else:
        print("✅ Response does not mention 'policy'")
    
    return True

def main():
    """Run all tests"""
    print_separator("🧪 CHATBOT API TESTING")
    print("\nTesting all scenarios using direct API calls...")
    
    # Login
    token = login()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return
    
    # Run tests
    test_scenario_1_service_information(token)
    test_scenario_2_booking_slot_filling(token)
    test_scenario_3_context_awareness(token)
    
    print_separator("🏁 ALL TESTS COMPLETED")

if __name__ == "__main__":
    main()

