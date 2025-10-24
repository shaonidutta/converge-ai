"""
Simple test to verify routing fixes
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Get token
print("Getting token...")
response = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    json={
        "identifier": "agtshaonidutta2k@gmail.com",
        "password": "Shaoni@123"
    }
)

if response.status_code != 200:
    print(f"Failed to login: {response.status_code}")
    print(response.text)
    exit(1)

token = response.json()["tokens"]["access_token"]
print(f"✅ Token obtained\n")

# Test 1: Greeting
print("=" * 80)
print("TEST 1: GREETING - 'Hello'")
print("=" * 80)

response = requests.post(
    f"{BASE_URL}/api/v1/chat/message",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "session_id": "test_greeting_1",
        "message": "Hello"
    }
)

print(f"Status: {response.status_code}")
print(f"Response JSON:")
print(json.dumps(response.json(), indent=2))

# Test 2: Cancellation
print("\n" + "=" * 80)
print("TEST 2: CANCELLATION - 'Cancel booking BK123456'")
print("=" * 80)

response = requests.post(
    f"{BASE_URL}/api/v1/chat/message",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "session_id": "test_cancel_1",
        "message": "Cancel booking BK123456"
    }
)

print(f"Status: {response.status_code}")
print(f"Response JSON:")
print(json.dumps(response.json(), indent=2))

