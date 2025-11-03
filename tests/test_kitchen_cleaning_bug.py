"""
Test kitchen cleaning booking bug
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

print("=" * 80)
print("  TESTING KITCHEN CLEANING BOOKING BUG")
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

# Test the exact flow from the user's report
test_messages = [
    ("home cleaning", "Should show subcategories"),
    ("i want to book kitchen cleaning", "Should start booking flow"),
    ("kitchen cleaning", "Should recognize kitchen cleaning service"),
]

for idx, (message, expected) in enumerate(test_messages, 1):
    print("\n" + "=" * 80)
    print(f"Test {idx}: {message}")
    print(f"Expected: {expected}")
    print("=" * 80)
    
    response = requests.post(
        f"{BASE_URL}/chat/message",
        headers=headers,
        json={"message": message}
    )
    
    if response.status_code != 200:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)
        continue
    
    resp_data = response.json()
    bot_message = resp_data["assistant_message"]["message"]
    
    print(f"\nBot Response:")
    print(bot_message[:500])
    
    # Check metadata
    if "metadata" in resp_data["assistant_message"]:
        metadata = resp_data["assistant_message"]["metadata"]
        print(f"\nMetadata:")
        print(f"  - Intent: {metadata.get('intent')}")
        print(f"  - Agent: {metadata.get('agent_used')}")
        
        if "coordinator_metadata" in metadata:
            coord_meta = metadata["coordinator_metadata"]
            print(f"  - Action: {coord_meta.get('action_taken')}")
            
            # For booking flow, show collected entities
            if "collected_entities" in coord_meta:
                print(f"  - Collected Entities: {coord_meta['collected_entities']}")
            
            # For service agent, show action
            if "action" in coord_meta:
                print(f"  - Service Action: {coord_meta['action']}")

print("\n" + "=" * 80)
print("  TEST COMPLETE")
print("=" * 80)

