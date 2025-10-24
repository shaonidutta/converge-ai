"""
Test script to verify greeting and cancellation routing fixes
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def get_auth_token():
    """Get authentication token"""
    print("🔐 Getting authentication token...")
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "identifier": "agtshaonidutta2k@gmail.com",
            "password": "Shaoni@123"
        }
    )
    
    if response.status_code == 200:
        token = response.json()["tokens"]["access_token"]
        print("✅ Token obtained successfully\n")
        return token
    else:
        print(f"❌ Failed to get token: {response.status_code}")
        print(response.text)
        return None

def test_greeting_flow(token):
    """Test greeting routing - should be handled by CoordinatorAgent"""
    print("=" * 80)
    print("TEST 1: GREETING FLOW")
    print("=" * 80)
    
    test_messages = [
        "Hello",
        "Hi",
        "Good morning",
        "Hey there"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Test {i}: '{message}'")
        print("-" * 80)
        
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/message",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "session_id": f"greeting_test_{i}_{int(time.time())}",
                "message": message
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📤 Response: {data.get('response', 'N/A')}")
            print(f"🤖 Agent Used: {data.get('agent_used', 'N/A')}")
            print(f"⚙️  Action Taken: {data.get('action_taken', 'N/A')}")
            
            # Verify it's handled by coordinator
            if data.get('agent_used') == 'coordinator':
                print("✅ PASS: Greeting handled by CoordinatorAgent")
            else:
                print(f"❌ FAIL: Expected 'coordinator', got '{data.get('agent_used')}'")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
        
        time.sleep(1)

def test_cancellation_flow(token):
    """Test cancellation routing - should use CancellationAgent"""
    print("\n" + "=" * 80)
    print("TEST 2: CANCELLATION FLOW")
    print("=" * 80)
    
    # First, get a booking to cancel
    print("\n📋 Getting user bookings...")
    response = requests.get(
        f"{BASE_URL}/api/v1/bookings?skip=0&limit=5",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        bookings = response.json()
        if bookings and len(bookings) > 0:
            # Find a confirmed booking
            confirmed_booking = None
            for booking in bookings:
                if booking.get('status') == 'confirmed':
                    confirmed_booking = booking
                    break
            
            if confirmed_booking:
                booking_number = confirmed_booking['booking_number']
                print(f"✅ Found confirmed booking: {booking_number}")
                print(f"   Service: {confirmed_booking.get('service_name', 'N/A')}")
                print(f"   Scheduled: {confirmed_booking.get('scheduled_datetime', 'N/A')}")
                
                # Test cancellation
                print(f"\n📝 Testing cancellation of booking {booking_number}")
                print("-" * 80)
                
                cancel_response = requests.post(
                    f"{BASE_URL}/api/v1/chat/message",
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "session_id": f"cancel_test_{int(time.time())}",
                        "message": f"Cancel booking {booking_number}"
                    }
                )
                
                if cancel_response.status_code == 200:
                    data = cancel_response.json()
                    print(f"✅ Status: {cancel_response.status_code}")
                    print(f"📤 Response: {data.get('response', 'N/A')}")
                    print(f"🤖 Agent Used: {data.get('agent_used', 'N/A')}")
                    print(f"⚙️  Action Taken: {data.get('action_taken', 'N/A')}")
                    
                    # Check if CancellationAgent was used
                    metadata = data.get('metadata', {})
                    if 'refund_percentage' in metadata:
                        print(f"💰 Refund Percentage: {metadata['refund_percentage']}%")
                        print(f"💵 Refund Amount: ₹{metadata.get('refund_amount', 'N/A')}")
                        print("✅ PASS: Cancellation handled with policy enforcement")
                    else:
                        print("⚠️  WARNING: No refund information in response")
                else:
                    print(f"❌ Failed: {cancel_response.status_code}")
                    print(cancel_response.text)
            else:
                print("⚠️  No confirmed bookings found to test cancellation")
                print("   Testing with a hypothetical booking number...")
                
                # Test with a fake booking number to see the flow
                print(f"\n📝 Testing cancellation with booking BK123456")
                print("-" * 80)
                
                cancel_response = requests.post(
                    f"{BASE_URL}/api/v1/chat/message",
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "session_id": f"cancel_test_{int(time.time())}",
                        "message": "Cancel booking BK123456"
                    }
                )
                
                if cancel_response.status_code == 200:
                    data = cancel_response.json()
                    print(f"✅ Status: {cancel_response.status_code}")
                    print(f"📤 Response: {data.get('response', 'N/A')}")
                    print(f"🤖 Agent Used: {data.get('agent_used', 'N/A')}")
                    print(f"⚙️  Action Taken: {data.get('action_taken', 'N/A')}")
        else:
            print("⚠️  No bookings found")
    else:
        print(f"❌ Failed to get bookings: {response.status_code}")

def main():
    """Main test function"""
    print("\n" + "=" * 80)
    print("🧪 TESTING ROUTING FIXES")
    print("=" * 80)
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    # Test greeting flow
    test_greeting_flow(token)
    
    # Test cancellation flow
    test_cancellation_flow(token)
    
    # Summary
    print("\n" + "=" * 80)
    print("✅ TESTING COMPLETE")
    print("=" * 80)
    print("\n📊 SUMMARY:")
    print("   1. Greeting Flow: Check if greetings are handled by CoordinatorAgent")
    print("   2. Cancellation Flow: Check if cancellations enforce policies via CancellationAgent")
    print("\n💡 Review the output above to verify both fixes are working correctly.")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()

