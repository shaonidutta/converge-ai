#!/usr/bin/env python3
"""
Test operations login API directly
"""

import requests
import json

def test_ops_login():
    """Test the operations login API"""
    print("\n" + "="*60)
    print("  TESTING OPERATIONS LOGIN API")
    print("="*60)
    
    # API endpoint
    url = "http://localhost:8000/api/v1/ops/auth/login"
    
    # Test credentials
    credentials = {
        "identifier": "ops.admin@convergeai.com",
        "password": "OpsPass123!"
    }
    
    print(f"\n🔗 Testing login at: {url}")
    print(f"📧 Email: {credentials['identifier']}")
    print(f"🔑 Password: {credentials['password']}")
    
    try:
        # Make login request
        response = requests.post(
            url,
            json=credentials,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ LOGIN SUCCESSFUL!")
            print(f"\n👤 Staff Info:")
            user = data.get('user', {})
            print(f"   ID: {user.get('id')}")
            print(f"   Employee ID: {user.get('employee_id')}")
            print(f"   Name: {user.get('first_name')} {user.get('last_name')}")
            print(f"   Email: {user.get('email')}")
            print(f"   Department: {user.get('department')}")
            print(f"   Active: {user.get('is_active')}")
            
            print(f"\n🔑 Tokens:")
            tokens = data.get('tokens', {})
            print(f"   Access Token: {tokens.get('access_token', '')[:50]}...")
            print(f"   Token Type: {tokens.get('token_type')}")
            print(f"   Expires In: {tokens.get('expires_in')} seconds")
            
            print(f"\n🛡️ Permissions:")
            permissions = data.get('permissions', [])
            for perm in permissions[:10]:  # Show first 10 permissions
                print(f"   - {perm}")
            if len(permissions) > 10:
                print(f"   ... and {len(permissions) - 10} more")
                
            print(f"\n🎉 Authentication is working perfectly!")
            print(f"🔗 You can now login at: http://localhost:5174/")
            
        else:
            print(f"❌ LOGIN FAILED!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {e}")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    test_ops_login()
