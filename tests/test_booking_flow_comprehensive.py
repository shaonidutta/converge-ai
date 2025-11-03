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

# Test 1: Kitchen cleaning booking (specific subcategory)
print("=" * 80)
print("Test 1: 'i want to book kitchen cleaning' - should skip subcategory selection")
print("=" * 80)
response = requests.post(
    f"{BASE_URL}/chat/message",
    headers=headers,
    json={"message": "i want to book kitchen cleaning"}
)
result = response.json()
session_id_1 = result['session_id']
agent_1 = result['metadata'].get('agent_used', 'unknown')
bot_response_1 = result['assistant_message']['message']
print(f"Session ID: {session_id_1}")
print(f"Agent: {agent_1}")
print(f"Bot Response: {bot_response_1[:200]}...")

# Check if it's asking for subcategory selection
if "specify which type" in bot_response_1.lower() or "which one would you like" in bot_response_1.lower():
    print("❌ FAIL: System is asking for subcategory selection (should skip this step)")
elif "date" in bot_response_1.lower() or "when" in bot_response_1.lower() or "time" in bot_response_1.lower() or "pincode" in bot_response_1.lower() or "location" in bot_response_1.lower():
    print("✅ PASS: System skipped subcategory selection and is asking for next entity")
else:
    print(f"⚠️  UNKNOWN: Bot response doesn't match expected patterns")
print()

# Test 2: Deep cleaning booking (specific subcategory)
print("=" * 80)
print("Test 2: 'i want to book deep cleaning' - should skip subcategory selection")
print("=" * 80)
response = requests.post(
    f"{BASE_URL}/chat/message",
    headers=headers,
    json={"message": "i want to book deep cleaning"}
)
result = response.json()
session_id_2 = result['session_id']
agent_2 = result['metadata'].get('agent_used', 'unknown')
bot_response_2 = result['assistant_message']['message']
print(f"Session ID: {session_id_2}")
print(f"Agent: {agent_2}")
print(f"Bot Response: {bot_response_2[:200]}...")

# Check if it's asking for subcategory selection
if "specify which type" in bot_response_2.lower() or "which one would you like" in bot_response_2.lower():
    print("❌ FAIL: System is asking for subcategory selection (should skip this step)")
elif "date" in bot_response_2.lower() or "when" in bot_response_2.lower() or "time" in bot_response_2.lower() or "pincode" in bot_response_2.lower() or "location" in bot_response_2.lower():
    print("✅ PASS: System skipped subcategory selection and is asking for next entity")
else:
    print(f"⚠️  UNKNOWN: Bot response doesn't match expected patterns")
print()

# Test 3: Generic cleaning booking (should ask for subcategory)
print("=" * 80)
print("Test 3: 'i want to book cleaning' - should ask for subcategory selection")
print("=" * 80)
response = requests.post(
    f"{BASE_URL}/chat/message",
    headers=headers,
    json={"message": "i want to book cleaning"}
)
result = response.json()
session_id_3 = result['session_id']
agent_3 = result['metadata'].get('agent_used', 'unknown')
bot_response_3 = result['assistant_message']['message']
print(f"Session ID: {session_id_3}")
print(f"Agent: {agent_3}")
print(f"Bot Response: {bot_response_3[:200]}...")

# Check if it's asking for subcategory selection
if "specify which type" in bot_response_3.lower() or "which one would you like" in bot_response_3.lower() or "cleaning service" in bot_response_3.lower():
    print("✅ PASS: System is correctly asking for subcategory selection")
else:
    print(f"❌ FAIL: System should ask for subcategory selection but didn't")
print()

# Test 4: Follow-up with specific subcategory
print("=" * 80)
print("Test 4: Follow-up 'kitchen cleaning' in same session")
print("=" * 80)
response = requests.post(
    f"{BASE_URL}/chat/message",
    headers=headers,
    json={"message": "kitchen cleaning", "session_id": session_id_3}
)
result = response.json()
agent_4 = result['metadata'].get('agent_used', 'unknown')
bot_response_4 = result['assistant_message']['message']
print(f"Session ID: {result['session_id']}")
print(f"Agent: {agent_4}")
print(f"Bot Response: {bot_response_4[:200]}...")

# Check if it moved to next entity
if "date" in bot_response_4.lower() or "when" in bot_response_4.lower() or "time" in bot_response_4.lower() or "pincode" in bot_response_4.lower() or "location" in bot_response_4.lower():
    print("✅ PASS: System accepted subcategory and moved to next entity")
else:
    print(f"❌ FAIL: System should move to next entity but didn't")
print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print("All tests completed. Review results above.")

