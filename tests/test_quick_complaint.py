#!/usr/bin/env python3
"""
Quick test to check if the complaint flow is working
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
CHAT_URL = f"{BASE_URL}/api/v1/chat/message"

# Test credentials
CREDENTIALS = {
    "identifier": "agtshaonidutta2k@gmail.com",
    "password": "Shaoni@123"
}

def quick_test():
    print("Quick Complaint Flow Test")
    print("=" * 50)
    
    # Login
    print("1. Logging in...")
    try:
        response = requests.post(LOGIN_URL, json=CREDENTIALS, timeout=5)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return
            
        login_data = response.json()
        tokens = login_data.get("tokens", {})
        token = tokens.get("access_token")
        
        if not token:
            print("❌ No token received")
            return
            
        print("✅ Login successful")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test complaint start
    print("\n2. Starting complaint...")
    try:
        message_data = {"message": "I want to file a complaint"}
        response = requests.post(CHAT_URL, json=message_data, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
            
        data = response.json()
        print(f"✅ Response received")
        print(f"Intent: {data.get('intent')}")
        print(f"Response: {data.get('response', '')[:100]}...")
        
        if data.get('metadata', {}).get('error'):
            print(f"❌ Error in response: {data['metadata']['error']}")
        
    except Exception as e:
        print(f"❌ Request error: {e}")

if __name__ == "__main__":
    quick_test()
