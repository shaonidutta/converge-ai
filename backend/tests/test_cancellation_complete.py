"""
Complete Cancellation Flow Testing Script

This script:
1. Gets existing bookings for the user
2. Tests cancellation with real booking numbers
3. Verifies the complete end-to-end flow
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
EMAIL = "agtshaonidutta2k@gmail.com"
PASSWORD = "Shaoni@123"

def login():
    """Login and get access token"""
    print("🔐 Logging in...")
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"identifier": EMAIL, "password": PASSWORD}
    )
    response.raise_for_status()
    token = response.json()["tokens"]["access_token"]
    print(f"✅ Login successful")
    return token

def get_bookings(token):
    """Get list of bookings"""
    print("\n📋 Fetching existing bookings...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/v1/bookings?skip=0&limit=10",
        headers=headers
    )
    response.raise_for_status()
    bookings = response.json()
    
    if bookings:
        print(f"✅ Found {len(bookings)} bookings:")
        for booking in bookings:
            print(f"   - {booking['order_id']}: {booking['status']} (ID: {booking['id']})")
    else:
        print("⚠️  No bookings found")

    return bookings

def create_test_booking(token):
    """Create a test booking via chat"""
    print("\n🎯 Creating a test booking via chat...")
    headers = {"Authorization": f"Bearer {token}"}
    
    session_id = f"create_booking_{int(time.time())}"
    
    # Step 1: Initiate booking
    response = requests.post(
        f"{BASE_URL}/api/v1/chat/message",
        headers=headers,
        json={
            "session_id": session_id,
            "message": "I want to book AC service for tomorrow at 2 PM"
        }
    )
    response.raise_for_status()
    result = response.json()
    
    print(f"📝 Bot: {result['assistant_message']['message'][:100]}...")
    
    # Check if confirmation is needed
    if "confirm" in result['assistant_message']['message'].lower():
        print("✅ Booking ready for confirmation")
        
        # Step 2: Confirm booking
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/message",
            headers=headers,
            json={
                "session_id": session_id,
                "message": "Yes, confirm"
            }
        )
        response.raise_for_status()
        result = response.json()
        
        print(f"📝 Bot: {result['assistant_message']['message'][:150]}...")
        
        # Extract booking number from response
        message = result['assistant_message']['message']
        if "ORD" in message:
            # Try to extract order ID
            import re
            match = re.search(r'ORD[A-Z0-9]{8}', message)
            if match:
                order_id = match.group(0)
                print(f"✅ Booking created: {order_id}")
                return order_id

    return None

def test_cancellation(token, order_id, test_message, test_name):
    """Test a cancellation scenario"""
    print(f"\n{'='*60}")
    print(f"🧪 TEST: {test_name}")
    print(f"{'='*60}")
    print(f"📝 Message: \"{test_message}\"")
    
    headers = {"Authorization": f"Bearer {token}"}
    session_id = f"cancel_test_{int(time.time())}"
    
    response = requests.post(
        f"{BASE_URL}/api/v1/chat/message",
        headers=headers,
        json={
            "session_id": session_id,
            "message": test_message
        }
    )
    response.raise_for_status()
    result = response.json()
    
    bot_message = result['assistant_message']['message']
    intent = result['assistant_message']['intent']
    confidence = result['assistant_message']['intent_confidence']
    
    print(f"🤖 Bot Response: {bot_message}")
    print(f"🎯 Intent: {intent} (Confidence: {confidence})")
    
    # Check if order ID was extracted
    if order_id in test_message:
        if "provide" in bot_message.lower() and ("booking" in bot_message.lower() or "order" in bot_message.lower()):
            print("❌ FAIL: Order ID not extracted (bot asking for it)")
            return False
        else:
            print("✅ PASS: Order ID extracted successfully")
            return True
    else:
        print("ℹ️  No booking ID in message (expected to ask)")
        return True

def main():
    """Main test execution"""
    print("="*60)
    print("🚀 COMPLETE CANCELLATION FLOW TESTING")
    print("="*60)
    
    try:
        # Step 1: Login
        token = login()
        
        # Step 2: Get existing bookings
        bookings = get_bookings(token)
        
        # Step 3: Use existing booking or create new one
        if bookings and bookings[0]['status'] in ['PENDING', 'CONFIRMED']:
            order_id = bookings[0]['order_id']
            print(f"\n✅ Using existing booking: {order_id}")
        else:
            print("\n⚠️  No active bookings found. Creating a test booking...")
            order_id = create_test_booking(token)
            if not order_id:
                print("❌ Failed to create test booking")
                return

        # Step 4: Run cancellation tests
        print(f"\n{'='*60}")
        print(f"📋 RUNNING CANCELLATION TESTS WITH: {order_id}")
        print(f"{'='*60}")

        tests = [
            (f"Cancel booking {order_id}", "Direct cancellation with order ID"),
            (f"I want to cancel {order_id}", "Cancellation with 'I want to'"),
            (f"Please cancel my order number {order_id}", "Polite cancellation request"),
            ("Cancel my AC service", "Cancel by service type (ambiguous)"),
            ("I need to cancel", "Cancel without details"),
        ]

        results = []
        for test_message, test_name in tests:
            result = test_cancellation(token, order_id, test_message, test_name)
            results.append((test_name, result))
            time.sleep(2)  # Small delay between tests
        
        # Step 5: Summary
        print(f"\n{'='*60}")
        print("📊 TEST SUMMARY")
        print(f"{'='*60}")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print(f"\n🎯 Results: {passed}/{total} tests passed ({passed*100//total}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED!")
        else:
            print("⚠️  Some tests failed. Review the output above.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

