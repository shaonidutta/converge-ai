"""
Test all category names to ensure they work
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

print("=" * 80)
print("  TESTING ALL CATEGORY NAMES")
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

# Test categories
test_categories = [
    "home cleaning",
    "plumbing",
    "electrical",
    "ac services",
    "appliance repair",
    "carpentry",
    "painting",
    "pest control"
]

results = []

for category in test_categories:
    print("\n" + "=" * 80)
    print(f"Testing: {category}")
    print("=" * 80)
    
    response = requests.post(
        f"{BASE_URL}/chat/message",
        headers=headers,
        json={"message": category}
    )
    
    if response.status_code != 200:
        print(f"❌ Request failed: {response.status_code}")
        results.append({"category": category, "status": "FAILED", "reason": f"HTTP {response.status_code}"})
        continue
    
    resp_data = response.json()
    message = resp_data["assistant_message"]["message"]
    
    # Check if response contains subcategories
    if "subcategories" in message.lower() or "subcategory" in message.lower():
        print(f"✅ SUCCESS: Got subcategories")
        results.append({"category": category, "status": "SUCCESS"})
    elif "no services found" in message.lower():
        print(f"❌ FAILED: 'No services found'")
        results.append({"category": category, "status": "FAILED", "reason": "No services found"})
    else:
        print(f"⚠️  UNCLEAR: {message[:100]}")
        results.append({"category": category, "status": "UNCLEAR", "message": message[:100]})

# Summary
print("\n" + "=" * 80)
print("  SUMMARY")
print("=" * 80)

success_count = sum(1 for r in results if r["status"] == "SUCCESS")
failed_count = sum(1 for r in results if r["status"] == "FAILED")
unclear_count = sum(1 for r in results if r["status"] == "UNCLEAR")

print(f"\n✅ SUCCESS: {success_count}/{len(test_categories)}")
print(f"❌ FAILED: {failed_count}/{len(test_categories)}")
print(f"⚠️  UNCLEAR: {unclear_count}/{len(test_categories)}")

if failed_count > 0:
    print("\nFailed categories:")
    for r in results:
        if r["status"] == "FAILED":
            print(f"  - {r['category']}: {r.get('reason', 'Unknown')}")

print("\n" + "=" * 80)

