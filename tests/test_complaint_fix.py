#!/usr/bin/env python3
"""
Test script to verify the complaint flow fix
Tests the exact scenario that was broken before the fix
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
CHAT_URL = f"{BASE_URL}/api/v1/chat/message"

# Test credentials
CREDENTIALS = {
    "identifier": "agtshaonidutta2k@gmail.com",
    "password": "Shaoni@123"
}

def test_complaint_flow():
    """Test the complete complaint flow that was previously broken"""
    
    print("=" * 80)
    print("COMPLAINT FLOW FIX TEST")
    print("=" * 80)
    
    # Step 1: Login
    print("\nSTEP 1: Login")
    print("-" * 40)
    
    try:
        response = requests.post(LOGIN_URL, json=CREDENTIALS, timeout=10)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
            
        login_data = response.json()
        # Token is nested under 'tokens'
        tokens = login_data.get("tokens", {})
        token = tokens.get("access_token") or login_data.get("access_token")

        user_data = login_data.get("user", {})
        user_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip() or "Unknown"

        print(f"✅ Login successful")
        print(f"   User: {user_name}")
        print(f"   Token: {token[:20] if token else 'None'}...")

        if not token:
            print(f"❌ No access token received: {login_data}")
            return False
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Headers for authenticated requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Start complaint
    print("\nSTEP 2: Start Complaint")
    print("-" * 40)
    
    try:
        message_data = {"message": "I want to file a complaint about the service"}
        response = requests.post(CHAT_URL, json=message_data, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Step 2 failed: {response.status_code} - {response.text}")
            return False
            
        data = response.json()
        session_id = data.get("session_id")
        bot_response = data.get("response", "")
        intent = data.get("intent")
        
        print(f"📤 USER: I want to file a complaint about the service")
        print(f"📥 LISA: {bot_response}")
        print(f"   Intent: {intent}")
        print(f"   Session: {session_id}")
        
        if not session_id:
            print("❌ No session ID received")
            return False
            
    except Exception as e:
        print(f"❌ Step 2 error: {e}")
        return False
    
    # Step 3: Provide issue type
    print("\nSTEP 3: Provide Issue Type")
    print("-" * 40)
    
    try:
        message_data = {
            "message": "no-show",
            "session_id": session_id
        }
        response = requests.post(CHAT_URL, json=message_data, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Step 3 failed: {response.status_code} - {response.text}")
            return False
            
        data = response.json()
        bot_response = data.get("response", "")
        intent = data.get("intent")
        
        print(f"📤 USER: no-show")
        print(f"📥 LISA: {bot_response}")
        print(f"   Intent: {intent}")
        
    except Exception as e:
        print(f"❌ Step 3 error: {e}")
        return False
    
    # Step 4: Provide detailed description (THE CRITICAL TEST)
    print("\nSTEP 4: Provide Detailed Description (CRITICAL TEST)")
    print("-" * 40)
    
    try:
        # This is the exact message that was causing the bug
        critical_message = "The technician didn't show up for my appointment. I waited for 2 hours but no one came. This is very disappointing."
        
        message_data = {
            "message": critical_message,
            "session_id": session_id
        }
        response = requests.post(CHAT_URL, json=message_data, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Step 4 failed: {response.status_code} - {response.text}")
            return False
            
        data = response.json()
        bot_response = data.get("response", "")
        intent = data.get("intent")
        metadata = data.get("metadata", {})
        
        print(f"📤 USER: {critical_message}")
        print(f"📥 LISA: {bot_response}")
        print(f"   Intent: {intent}")
        print(f"   Metadata: {json.dumps(metadata, indent=2)}")
        
        # Check if the fix worked
        if intent == "booking_management":
            print("\n❌ FIX FAILED: Intent was misclassified as 'booking_management'")
            print("   The bug is still present - dialog state was cleared")
            return False
        elif intent == "complaint":
            print("\n✅ FIX WORKING: Intent correctly remained as 'complaint'")
            
            # Check if complaint was created
            if "complaint" in bot_response.lower() and ("COM" in bot_response or "complaint id" in bot_response.lower()):
                print("✅ COMPLAINT CREATED: Response contains complaint details")
                return True
            else:
                print("⚠️  PARTIAL SUCCESS: Intent correct but complaint may not be fully created")
                print("   Response doesn't contain complaint ID - may need further investigation")
                return True
        else:
            print(f"\n⚠️  UNEXPECTED INTENT: {intent}")
            print("   This is neither the bug nor the expected fix")
            return False
            
    except Exception as e:
        print(f"❌ Step 4 error: {e}")
        return False

if __name__ == "__main__":
    success = test_complaint_flow()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 TEST RESULT: COMPLAINT FLOW FIX SUCCESSFUL!")
        print("   The intent misclassification bug has been resolved")
    else:
        print("💥 TEST RESULT: COMPLAINT FLOW STILL BROKEN")
        print("   The fix did not resolve the issue")
    print("=" * 80)
