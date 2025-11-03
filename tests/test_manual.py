import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Login
print("Logging in...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"identifier": "agtshaonidutta2k@gmail.com", "password": "Shaoni@123"}
)
print(f"Login status: {login_response.status_code}")

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["tokens"]["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("Login successful\n")

# Test 1: home cleaning
print("=" * 60)
print("Test 1: 'home cleaning'")
print("=" * 60)
response = requests.post(
    f"{BASE_URL}/chat/message",
    headers=headers,
    json={"message": "home cleaning"}
)
print(f"Status: {response.status_code}")
result = response.json()
print(f"Response keys: {result.keys()}")
print(f"Full response: {json.dumps(result, indent=2)}")

