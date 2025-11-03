#!/usr/bin/env python3
"""
Detailed test for kitchen cleaning booking bug with session tracking
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Login
print("Step 1: Login...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"identifier": "agtshaonidutta2k@gmail.com", "password": "Shaoni@123"}
)
if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["tokens"]["access_token"]
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
print("[OK] Login successful\n")

# Test 1: Start booking flow
print("="*80)
print("Test 1: i want to book kitchen cleaning")
print("="*80)
response1 = requests.post(
    f"{BASE_URL}/chat/message",
    headers=headers,
    json={"message": "i want to book kitchen cleaning"}
)
data1 = response1.json()
print(f"Full Response: {json.dumps(data1, indent=2)}\n")
print(f"Bot Response: {data1.get('response', 'N/A')}\n")
print(f"Intent: {data1.get('intent')}")
print(f"Agent: {data1.get('agent_used')}")
print(f"Metadata: {json.dumps(data1.get('metadata', {}), indent=2)}\n")

# Get session ID from response
session_id = data1.get('session_id')
print(f"Session ID: {session_id}\n")

# Test 2: Follow-up with "kitchen cleaning"
print("="*80)
print("Test 2: kitchen cleaning (follow-up)")
print("="*80)
response2 = requests.post(
    f"{BASE_URL}/chat/message",
    headers=headers,
    json={"message": "kitchen cleaning", "session_id": session_id}
)
data2 = response2.json()
print(f"Full Response: {json.dumps(data2, indent=2)}\n")
print(f"Bot Response: {data2.get('response', 'N/A')}\n")
print(f"Intent: {data2.get('intent')}")
print(f"Agent: {data2.get('agent_used')}")
print(f"Metadata: {json.dumps(data2.get('metadata', {}), indent=2)}\n")

