"""
Test kitchen cleaning booking flow with detailed logging
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def print_section(title):
    print("\n" + "="*80)
    print(title)
    print("="*80)

# Step 1: Login
print_section("Step 1: Login...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"identifier": "agtshaonidutta2k@gmail.com", "password": "Shaoni@123"}
)

if login_response.status_code != 200:
    print(f"[ERROR] Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["tokens"]["access_token"]
print("[OK] Login successful")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Test 1: Start booking flow
print_section("Test 1: i want to book kitchen cleaning")
response1 = requests.post(
    f"{BASE_URL}/chat/message",
    headers=headers,
    json={"message": "i want to book kitchen cleaning"}
)

data1 = response1.json()
print(f"Bot Response: {data1['assistant_message']['message']}")
print(f"\nIntent: {data1['metadata']['intent']}")
print(f"Agent: {data1['metadata']['agent_used']}")
print(f"Classification Method: {data1['metadata']['classification_method']}")

# Get session ID from response
session_id = data1.get('session_id')
print(f"\nSession ID: {session_id}")

# Check if available_subcategories are in metadata
metadata = data1.get('metadata', {})
coordinator_metadata = metadata.get('coordinator_metadata', {})
print(f"\nCoordinator Metadata Keys: {list(coordinator_metadata.keys())}")

# Test 2: Follow-up with "kitchen cleaning"
print_section("Test 2: kitchen cleaning (follow-up)")
response2 = requests.post(
    f"{BASE_URL}/chat/message",
    headers=headers,
    json={"message": "kitchen cleaning", "session_id": session_id}
)

data2 = response2.json()
print(f"Bot Response: {data2['assistant_message']['message']}")
print(f"\nIntent: {data2['metadata']['intent']}")
print(f"Agent: {data2['metadata']['agent_used']}")
print(f"Classification Method: {data2['metadata']['classification_method']}")
print(f"Is Follow-up: {data2['metadata']['coordinator_metadata'].get('is_follow_up')}")

# Check if it's still in booking flow
if data2['metadata']['agent_used'] == 'slot_filling':
    print("\n✅ Still in booking flow (slot_filling)")
else:
    print(f"\n❌ Switched to {data2['metadata']['agent_used']} agent")

# Test 3: Try "3" (selecting option 3 from the list)
print_section("Test 3: 3 (selecting option 3)")
response3 = requests.post(
    f"{BASE_URL}/chat/message",
    headers=headers,
    json={"message": "3", "session_id": session_id}
)

data3 = response3.json()
print(f"Bot Response: {data3['assistant_message']['message']}")
print(f"\nIntent: {data3['metadata']['intent']}")
print(f"Agent: {data3['metadata']['agent_used']}")
print(f"Classification Method: {data3['metadata']['classification_method']}")

# Check if it progressed to next step
if "date" in data3['assistant_message']['message'].lower() or "when" in data3['assistant_message']['message'].lower():
    print("\n✅ Progressed to date/time collection")
else:
    print("\n⚠️ Still asking for service type")

