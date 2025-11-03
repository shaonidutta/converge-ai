"""
Test home cleaning bug
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

print("=" * 80)
print("  TESTING HOME CLEANING BUG")
print("=" * 80)

# Step 1: Login
print("\nStep 1: Login...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "identifier": "agtshaonidutta2k@gmail.com",
        "password": "Shaoni@123"
    }
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["tokens"]["access_token"]
print("✅ Login successful")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Step 2: Ask "what services do u provide?"
print("\n" + "=" * 80)
print("Test 1: What services do u provide?")
print("=" * 80)

response1 = requests.post(
    f"{BASE_URL}/chat/message",
    headers=headers,
    json={"message": "what services do u provide?"}
)

if response1.status_code != 200:
    print(f"❌ Request failed: {response1.status_code}")
    print(response1.text)
    exit(1)

print("Response:")
resp1_data = response1.json()
if "assistant_message" in resp1_data:
    print(resp1_data["assistant_message"]["message"][:500])
else:
    print(json.dumps(resp1_data, indent=2))

# Step 3: Follow up with "home cleaning"
print("\n" + "=" * 80)
print("Test 2: home cleaning (follow-up)")
print("=" * 80)

response2 = requests.post(
    f"{BASE_URL}/chat/message",
    headers=headers,
    json={"message": "home cleaning"}
)

print("Response:")
print(response2.json()["assistant_message"]["message"])

print("\nMetadata:")
print(json.dumps(response2.json().get("metadata", {}), indent=2))

# Check if response contains "No services found"
if "No services found" in response2.json()["assistant_message"]["message"]:
    print("\n❌ BUG CONFIRMED: 'home cleaning' returns 'No services found'")
else:
    print("\n✅ BUG FIXED: 'home cleaning' returns subcategories")

print("\n" + "=" * 80)
print("  TEST COMPLETE")
print("=" * 80)

