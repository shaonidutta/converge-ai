import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Login
print("Logging in...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"identifier": "agtshaonidutta2k@gmail.com", "password": "Shaoni@123"}
)
token = login_response.json()["tokens"]["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("Login successful\n")

# Test 1: "home cleaning" - should show subcategories
print("=" * 80)
print("Test 1: 'home cleaning' - should show subcategories")
print("=" * 80)
response = requests.post(
    f"{BASE_URL}/chat/message",
    headers=headers,
    json={"message": "home cleaning"}
)
result = response.json()
session_id_1 = result['session_id']
print(f"Session ID: {session_id_1}")
print(f"Agent: {result['metadata'].get('agent_used', 'unknown')}")
print(f"Bot Response: {result['assistant_message']['message'][:150]}...")
print()

# Test 2: "i want to book kitchen cleaning" - should skip subcategory selection
# Use a NEW session for this test
print("=" * 80)
print("Test 2: 'i want to book kitchen cleaning' - should skip subcategory selection")
print("=" * 80)
response = requests.post(
    f"{BASE_URL}/chat/message",
    headers=headers,
    json={"message": "i want to book kitchen cleaning"}
)
result = response.json()
session_id_2 = result['session_id']
print(f"Session ID: {session_id_2}")
print(f"Agent: {result['metadata'].get('agent_used', 'unknown')}")
bot_response = result['assistant_message']['message']
print(f"Bot Response: {bot_response[:200]}...")
print()

# Check if it's asking for subcategory selection
if "specify which type" in bot_response.lower() or "which one would you like" in bot_response.lower():
    print("ISSUE: System is asking for subcategory selection (should skip this step)")
    print()

    # Test 3: Try responding with "kitchen cleaning" in the SAME session
    print("=" * 80)
    print("Test 3: Follow-up 'kitchen cleaning' (same session)")
    print("=" * 80)
    response = requests.post(
        f"{BASE_URL}/chat/message",
        headers=headers,
        json={"message": "kitchen cleaning", "session_id": session_id_2}
    )
    result = response.json()
    print(f"Session ID: {result['session_id']}")
    print(f"Agent: {result['metadata'].get('agent_used', 'unknown')}")
    print(f"Bot Response: {result['assistant_message']['message'][:200]}...")
    print()
elif "pincode" in bot_response.lower() or "location" in bot_response.lower() or "where" in bot_response.lower() or "date" in bot_response.lower() or "when" in bot_response.lower() or "time" in bot_response.lower():
    print("SUCCESS: System skipped subcategory selection and is asking for next entity (location/date/time)")
    print()
else:
    print(f"UNEXPECTED: Bot response doesn't match expected patterns")
    print(f"Full response: {bot_response}")
    print()

