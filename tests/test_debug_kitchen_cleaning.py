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

# Test: "i want to book kitchen cleaning"
print("=" * 80)
print("Test: 'i want to book kitchen cleaning'")
print("=" * 80)
response = requests.post(
    f"{BASE_URL}/chat/message",
    headers=headers,
    json={"message": "i want to book kitchen cleaning"}
)
result = response.json()

print(f"\nAgent: {result['metadata'].get('agent_used', 'unknown')}")
print(f"Intent: {result['assistant_message'].get('intent', 'unknown')}")
print(f"\nBot Response:\n{result['assistant_message']['message']}\n")

# Print full metadata
print("=" * 80)
print("Full Metadata:")
print("=" * 80)
print(json.dumps(result['metadata'], indent=2))

