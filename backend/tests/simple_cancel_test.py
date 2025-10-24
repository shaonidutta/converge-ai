"""Simple cancellation test"""
import requests
import json

# Login
print("Logging in...")
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"identifier": "agtshaonidutta2k@gmail.com", "password": "Shaoni@123"}
)
print(f"Login status: {response.status_code}")
token = response.json()["tokens"]["access_token"]
print(f"Token: {token[:50]}...")

# Get bookings
print("\nGetting bookings...")
response = requests.get(
    "http://localhost:8000/api/v1/bookings?skip=0&limit=5",
    headers={"Authorization": f"Bearer {token}"}
)
print(f"Bookings status: {response.status_code}")
bookings = response.json()
print(f"Found {len(bookings)} bookings")

if bookings:
    for b in bookings:
        print(f"  - {b['booking_number']}: {b['status']}")
    
    # Test cancellation with first booking
    booking_number = bookings[0]['booking_number']
    print(f"\nTesting cancellation with: {booking_number}")
    
    response = requests.post(
        "http://localhost:8000/api/v1/chat/message",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "session_id": "simple_test_1",
            "message": f"Cancel booking {booking_number}"
        }
    )
    print(f"Chat status: {response.status_code}")
    result = response.json()
    print(f"Bot: {result['assistant_message']['message']}")
    print(f"Intent: {result['assistant_message']['intent']}")
else:
    print("No bookings found!")

