"""
Simple test to debug registration endpoint
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# Test registration
register_data = {
    "email": f"test_{int(datetime.now().timestamp())}@example.com",
    "mobile": f"+91{int(datetime.now().timestamp()) % 10000000000}",
    "password": "TestPass123!",
    "first_name": "Test",
    "last_name": "User"
}

print("Testing registration endpoint...")
print(f"URL: {BASE_URL}/auth/register")
print(f"Data: {json.dumps(register_data, indent=2)}")
print()

try:
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=register_data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
except Exception as e:
    print(f"Error: {e}")
    print(f"Response text: {response.text if 'response' in locals() else 'N/A'}")

