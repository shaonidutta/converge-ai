import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZ3RzaGFvbmlkdXR0YTJrQGdtYWlsLmNvbSIsInVzZXJfaWQiOjE4MywidXNlcl90eXBlIjoiY3VzdG9tZXIiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYxMjE3MzEzLCJpYXQiOjE3NjEyMTU1MTN9.WJfwFLeu3bfBWhIXQW7ae3qeyH_ZOlXVx1ljwzymPyg"

def send_message(message, session_id):
    """Send a chat message"""
    url = f"{BASE_URL}/chat/message"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    data = {
        "message": message,
        "session_id": session_id
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def print_response(response, test_name):
    """Print formatted response"""
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print(f"{'='*80}")
    print(f"User Message: {response['user_message']['message']}")
    print(f"Intent: {response['assistant_message']['intent']}")
    print(f"Confidence: {response['assistant_message']['intent_confidence']}")
    print(f"Lisa's Response: {response['assistant_message']['message']}")
    print(f"Response Time: {response['response_time_ms']}ms")
    print(f"{'='*80}\n")

# TEST 2: Booking Flow - Turn 2 (Context Awareness)
print("\n🧪 TEST 2 - TURN 2: Provide AC service and location")
print("CRITICAL: Should ask for date/time, NOT repeat service type or location!")
time.sleep(1)

response = send_message("AC service in 282002", "test_booking_flow")
print_response(response, "Booking Flow - Turn 2 (Context Awareness)")

# Check if context is maintained
lisa_response = response['assistant_message']['message'].lower()
if "service" in lisa_response and "type" in lisa_response:
    print("❌ FAILED: Lisa is asking for service type again (context lost!)")
elif "location" in lisa_response or "pincode" in lisa_response:
    print("❌ FAILED: Lisa is asking for location again (context lost!)")
elif "date" in lisa_response or "time" in lisa_response or "when" in lisa_response:
    print("✅ PASSED: Lisa is asking for date/time (context maintained!)")
else:
    print("⚠️ UNCLEAR: Check the response manually")

# TEST 2: Booking Flow - Turn 3
print("\n🧪 TEST 2 - TURN 3: Provide date and time")
time.sleep(2)

response = send_message("tomorrow at 2 PM", "test_booking_flow")
print_response(response, "Booking Flow - Turn 3")

# Check if booking proceeds
lisa_response = response['assistant_message']['message'].lower()
if "error" in lisa_response or "missing" in lisa_response:
    print("❌ FAILED: Error in booking process")
else:
    print("✅ PASSED: Booking proceeding")

