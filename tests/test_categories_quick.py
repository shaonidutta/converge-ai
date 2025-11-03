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

# Test categories
categories = [
    "home cleaning",
    "plumbing",
    "electrical",
    "ac services",
    "appliance repair",
    "carpentry",
    "painting",
    "pest control"
]

print("Testing all 8 categories...")
print("=" * 80)

passed = 0
failed = 0

for category in categories:
    response = requests.post(
        f"{BASE_URL}/chat/message",
        headers=headers,
        json={"message": category}
    )
    result = response.json()
    agent = result['metadata'].get('agent_used', 'unknown')
    bot_response = result['assistant_message']['message']
    
    # Check if response contains subcategories or services
    if "subcategor" in bot_response.lower() or "service" in bot_response.lower():
        print(f"✅ {category.upper()}: PASS (agent={agent})")
        passed += 1
    else:
        print(f"❌ {category.upper()}: FAIL (agent={agent})")
        print(f"   Response: {bot_response[:100]}...")
        failed += 1

print("=" * 80)
print(f"\nResults: {passed} passed, {failed} failed out of {len(categories)} tests")

