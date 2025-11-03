#!/usr/bin/env python3
"""Simple test for kitchen cleaning booking"""

import requests
import json

# Login
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"identifier": "agtshaonidutta2k@gmail.com", "password": "Shaoni@123"}
)
login_data = login_response.json()
print(f"Login response: {login_data}")
token = login_data.get("access_token") or login_data.get("token")

headers = {"Authorization": f"Bearer {token}"}

# Test: "i want to book kitchen cleaning"
print("=" * 80)
print("Test: 'i want to book kitchen cleaning'")
print("=" * 80)

response = requests.post(
    "http://localhost:8000/api/v1/chat/message",
    headers=headers,
    json={"message": "i want to book kitchen cleaning"}
)

result = response.json()
print(f"Session ID: {result['session_id']}")
print(f"Agent: {result.get('metadata', {}).get('agent_used', 'unknown')}")
print(f"Bot Response: {result['response'][:200]}...")
print()

