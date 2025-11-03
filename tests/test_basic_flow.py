import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Step 1: Login
print("Step 1: Login...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"identifier": "agtshaonidutta2k@gmail.com", "password": "Shaoni@123"}
)
if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)
token = login_response.json()["tokens"]["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"✅ Login successful\n")

# Step 2: Test bare category name "home cleaning"
print("=" * 80)
print("Test 1: Bare category name 'home cleaning'")
print("=" * 80)
response = requests.post(
    f"{BASE_URL}/chat/message",
    headers=headers,
    json={"message": "home cleaning"}
)
result = response.json()
print(f"Agent: {result.get('agent_used', 'unknown')}")
print(f"Bot Response: {result.get('response', result)[:200]}...")
print()

# Step 3: Test booking flow with "i want to book kitchen cleaning"
print("=" * 80)
print("Test 2: Booking flow 'i want to book kitchen cleaning'")
print("=" * 80)
response = requests.post(
    f"{BASE_URL}/chat/message",
    headers=headers,
    json={"message": "i want to book kitchen cleaning"}
)
result = response.json()
print(f"Agent: {result.get('agent_used', 'unknown')}")
bot_response = result.get('response', result)
print(f"Bot Response: {bot_response[:200]}...")
print()

# Check if it's asking for subcategory selection
if "specify which type" in bot_response.lower() or "which one would you like" in bot_response.lower():
    print("⚠️  ISSUE: System is asking for subcategory selection (should skip this step)")

    # Step 4: Try responding with "kitchen cleaning"
    print("\n" + "=" * 80)
    print("Test 3: Follow-up 'kitchen cleaning'")
    print("=" * 80)
    response = requests.post(
        f"{BASE_URL}/chat/message",
        headers=headers,
        json={"message": "kitchen cleaning"}
    )
    result = response.json()
    print(f"Agent: {result.get('agent_used', 'unknown')}")
    print(f"Bot Response: {result.get('response', result)[:200]}...")
    print()
else:
    print("✅ SUCCESS: System skipped subcategory selection")

