"""
Simple Complaint Flow Test - Tests the complete complaint flow via API
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_complaint_flow():
    """Test complete complaint flow"""
    
    print("\n" + "="*80)
    print("COMPLAINT FLOW TEST - SIMPLE VERSION")
    print("="*80)
    
    # Step 1: Login
    print("\n" + "="*80)
    print("STEP 1: Login")
    print("="*80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "identifier": "agtshaonidutta2k@gmail.com",
                "password": "Shaoni@123"
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        data = response.json()
        access_token = data.get("tokens", {}).get("access_token")
        user_data = data.get("user", {})
        
        if not access_token:
            print(f"❌ No access_token in response")
            return
        
        print(f"✅ Login Successful")
        print(f"   User: {user_data.get('first_name')} {user_data.get('last_name')}")
        print(f"   Token: {access_token[:30]}...")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 2: Start complaint
    print("\n" + "="*80)
    print("STEP 2: Start Complaint")
    print("="*80)
    print("📤 USER: I want to file a complaint about the service")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/message",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"message": "I want to file a complaint about the service"},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        data = response.json()
        print(f"📥 LISA: {data.get('response', 'No response')}")
        print(f"\nMETADATA:")
        print(f"   Intent: {data.get('intent')}")
        print(f"   Agent: {data.get('agent_used')}")
        
        session_id = data.get("session_id")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    time.sleep(1)
    
    # Step 3: Provide issue type
    print("\n" + "="*80)
    print("STEP 3: Provide Issue Type")
    print("="*80)
    print("📤 USER: no-show")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/message",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "message": "no-show",
                "session_id": session_id
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        data = response.json()
        print(f"📥 LISA: {data.get('response', 'No response')}")
        print(f"\nMETADATA:")
        print(f"   Intent: {data.get('intent')}")
        print(f"   Agent: {data.get('agent_used')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    time.sleep(1)
    
    # Step 4: Provide description
    print("\n" + "="*80)
    print("STEP 4: Provide Detailed Description")
    print("="*80)
    print("📤 USER: The technician didn't show up for my appointment. I waited for 2 hours but no one came. This is very disappointing.")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/message",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "message": "The technician didn't show up for my appointment. I waited for 2 hours but no one came. This is very disappointing.",
                "session_id": session_id
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        data = response.json()
        response_text = data.get('response', 'No response')
        print(f"📥 LISA: {response_text}")
        print(f"\nMETADATA:")
        print(f"   Intent: {data.get('intent')}")
        print(f"   Agent: {data.get('agent_used')}")
        
        metadata = data.get('metadata', {})
        if metadata:
            print(f"\nCOMPLAINT DETAILS:")
            print(f"   Complaint ID: {metadata.get('complaint_id')}")
            print(f"   Type: {metadata.get('complaint_type')}")
            print(f"   Priority: {metadata.get('priority')}")
            print(f"   Status: {metadata.get('status')}")
            print(f"   Response Due: {metadata.get('response_due_at')}")
            print(f"   Resolution Due: {metadata.get('resolution_due_at')}")
            
            # Check if complaint ID is in response
            complaint_id = metadata.get('complaint_id')
            if complaint_id and str(complaint_id) in response_text:
                print(f"\n✅ COMPLAINT ID #{complaint_id} FOUND IN RESPONSE")
            else:
                print(f"\n⚠️ Complaint ID not found in response text")
        else:
            print(f"\n❌ NO METADATA IN RESPONSE")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    test_complaint_flow()

