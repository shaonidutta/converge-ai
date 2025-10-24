#!/usr/bin/env python3
"""
Booking Cancellation Flow Tests
Tests all cancellation scenarios to verify entity extraction, intent classification, and agent routing
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def login():
    """Login and get access token"""
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "identifier": "agtshaonidutta2k@gmail.com",
            "password": "Shaoni@123"
        }
    )
    response.raise_for_status()
    return response.json()["tokens"]["access_token"]

def get_user_bookings(token):
    """Get user's bookings to find a valid booking ID"""
    response = requests.get(
        f"{BASE_URL}/api/v1/bookings",
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    bookings = response.json()
    
    # Find a confirmed booking
    for booking in bookings:
        if booking.get("status") == "confirmed":
            return booking.get("booking_number")
    
    return None

def test_message(token, session_id, message, test_name, expected_intent="booking_management", expected_action="cancel"):
    """Send a test message and verify response"""
    print(f"\n{'='*100}")
    print(f"TEST: {test_name}")
    print(f"Message: {message}")
    print(f"Expected Intent: {expected_intent}, Expected Action: {expected_action}")
    print(f"{'='*100}")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/chat/message",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "session_id": session_id,
            "message": message
        }
    )
    
    if response.status_code != 200:
        print(f"❌ ERROR: HTTP {response.status_code}")
        print(f"Response: {response.text}")
        return None
    
    result = response.json()
    
    print(f"\n✅ Response: {result.get('response', 'N/A')[:300]}...")
    print(f"Intent: {result.get('intent', 'N/A')}")
    print(f"Confidence: {result.get('confidence', 'N/A')}")
    print(f"Agent: {result.get('agent_used', 'N/A')}")
    print(f"Classification Method: {result.get('classification_method', 'N/A')}")
    
    # Verify intent and action
    intent = result.get('intent', '')
    response_text = result.get('response', '').lower()
    
    if intent == expected_intent:
        print(f"✅ Intent matches: {intent}")
    else:
        print(f"⚠️  Intent mismatch: Expected '{expected_intent}', Got '{intent}'")
    
    # Check if cancellation-related keywords are in response
    cancellation_keywords = ['cancel', 'cancellation', 'cancelled', 'confirm']
    if any(keyword in response_text for keyword in cancellation_keywords):
        print(f"✅ Response contains cancellation-related keywords")
    else:
        print(f"⚠️  Response doesn't contain expected cancellation keywords")
    
    return result

def main():
    print("="*100)
    print("BOOKING CANCELLATION FLOW TESTS")
    print("="*100)
    
    print("\nLogging in...")
    token = login()
    print("✅ Login successful")
    
    print("\nFetching user bookings to get a valid booking ID...")
    booking_id = get_user_bookings(token)
    if booking_id:
        print(f"✅ Found booking: {booking_id}")
    else:
        print("⚠️  No confirmed bookings found. Some tests may fail.")
        booking_id = "BK123456"  # Use dummy ID for testing
    
    # Test 1: Cancel by booking number (explicit)
    test_message(
        token,
        "cancel_test_1",
        f"Cancel booking {booking_id}",
        "Test 1: Cancel by booking number (explicit)"
    )
    time.sleep(2)
    
    # Test 2: Cancel by booking number (with "I want to")
    test_message(
        token,
        "cancel_test_2",
        f"I want to cancel {booking_id}",
        "Test 2: Cancel by booking number (with 'I want to')"
    )
    time.sleep(2)
    
    # Test 3: Cancel by booking number (with "please")
    test_message(
        token,
        "cancel_test_3",
        f"Please cancel my booking number {booking_id}",
        "Test 3: Cancel by booking number (with 'please')"
    )
    time.sleep(2)
    
    # Test 4: Cancel by service type
    test_message(
        token,
        "cancel_test_4",
        "Cancel my AC service",
        "Test 4: Cancel by service type"
    )
    time.sleep(2)
    
    # Test 5: Cancel by description (service + time)
    test_message(
        token,
        "cancel_test_5",
        "I want to cancel my plumbing appointment tomorrow",
        "Test 5: Cancel by description (service + time)"
    )
    time.sleep(2)
    
    # Test 6: Cancel latest booking
    test_message(
        token,
        "cancel_test_6",
        "Cancel my booking",
        "Test 6: Cancel latest booking (ambiguous)"
    )
    time.sleep(2)
    
    # Test 7: Cancel with "I need to"
    test_message(
        token,
        "cancel_test_7",
        "I need to cancel my last booking",
        "Test 7: Cancel with 'I need to'"
    )
    time.sleep(2)
    
    # Test 8: Cancel non-existent booking
    test_message(
        token,
        "cancel_test_8",
        "Cancel booking BK999999",
        "Test 8: Cancel non-existent booking"
    )
    time.sleep(2)
    
    # Test 9: Cancel with date reference
    test_message(
        token,
        "cancel_test_9",
        "Cancel my booking for tomorrow at 2 PM",
        "Test 9: Cancel with date/time reference"
    )
    time.sleep(2)
    
    # Test 10: Cancel recent booking
    test_message(
        token,
        "cancel_test_10",
        "Cancel my recent booking",
        "Test 10: Cancel recent booking"
    )
    
    print("\n" + "="*100)
    print("✅ ALL CANCELLATION TESTS COMPLETED")
    print("="*100)
    print("\nCheck backend logs for detailed information:")
    print("- Intent classification (should be 'booking_management')")
    print("- Action extraction (should be 'cancel')")
    print("- Entity extraction (booking_id, service_type, date, time)")
    print("- Agent routing (should route to CancellationAgent)")
    print("- Confirmation requests")
    print("- Error handling for invalid bookings")

if __name__ == "__main__":
    main()

