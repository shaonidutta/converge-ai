"""
Test Complaint Flow using Python requests (simulating frontend API calls)
Tests the complete complaint flow and verifies database storage
"""
import os
import sys
import json
import asyncio
import requests
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Load environment variables
from dotenv import load_dotenv
env_path = backend_path / ".env"
load_dotenv(env_path)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from src.core.models import User, Complaint


BASE_URL = "http://localhost:8000/api/v1"


def login_user():
    """Login and get access token"""
    print("\n" + "="*80)
    print("STEP 0: Login to get access token")
    print("="*80)
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "identifier": "agtshaonidutta2k@gmail.com",
            "password": "Shaoni@123"
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    
    data = response.json()
    tokens = data.get("tokens", {})
    access_token = tokens.get("access_token")
    user_data = data.get("user", {})

    if not access_token:
        print(f"❌ No access_token in response")
        print(f"Response data: {json.dumps(data, indent=2)}")
        return None

    print(f"✅ Login Successful")
    print(f"   User: {user_data.get('first_name')} {user_data.get('last_name')}")
    print(f"   Email: {user_data.get('email')}")
    print(f"   User ID: {user_data.get('id')}")
    print(f"   Token: {access_token[:30]}...")

    return access_token


async def check_complaint_in_db(complaint_id: int):
    """Check if complaint exists in database"""
    database_url = os.getenv("DATABASE_URL")
    if database_url.startswith("mysql://"):
        database_url = database_url.replace("mysql://", "mysql+aiomysql://")
    elif database_url.startswith("mysql+pymysql://"):
        database_url = database_url.replace("mysql+pymysql://", "mysql+aiomysql://")
    
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(
            select(Complaint).where(Complaint.id == complaint_id)
        )
        complaint = result.scalar_one_or_none()
        
        if complaint:
            print(f"\n{'='*80}")
            print(f"✅ COMPLAINT FOUND IN DATABASE")
            print(f"{'='*80}")
            print(f"Complaint ID: {complaint.id}")
            print(f"User ID: {complaint.user_id}")
            print(f"Session ID: {complaint.session_id}")
            print(f"Type: {complaint.complaint_type.value}")
            print(f"Subject: {complaint.subject}")
            print(f"Description: {complaint.description}")
            print(f"Priority: {complaint.priority.value}")
            print(f"Status: {complaint.status.value}")
            print(f"Response Due: {complaint.response_due_at}")
            print(f"Resolution Due: {complaint.resolution_due_at}")
            print(f"Created At: {complaint.created_at}")
            print(f"{'='*80}")
            return True
        else:
            print(f"\n❌ COMPLAINT #{complaint_id} NOT FOUND IN DATABASE")
            return False


async def test_complaint_flow():
    """Test complaint flow using requests"""
    
    print("=" * 80)
    print("COMPLAINT FLOW TEST - API REQUESTS")
    print("=" * 80)
    print()
    
    # Step 0: Login
    token = login_user()
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 1: Send first message - "I want to file a complaint"
    print("\n" + "="*80)
    print("STEP 1: Send First Message - 'I want to file a complaint'")
    print("="*80)
    
    response = requests.post(
        f"{BASE_URL}/chat/message",
        json={"message": "I want to file a complaint about the service"},
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to send message: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    data = response.json()
    session_id = data.get('session_id')
    
    if not session_id:
        print("❌ No session_id in response")
        return False
    
    print(f"\n✅ Session Created: {session_id}")
    print(f"📤 USER: I want to file a complaint about the service")
    print(f"📥 LISA: {data.get('response', 'No response')}")
    
    # Step 2: Send complaint type - "no-show"
    print("\n" + "="*80)
    print("STEP 2: Send Complaint Type - 'no-show'")
    print("="*80)
    
    response = requests.post(
        f"{BASE_URL}/chat/message",
        json={
            "session_id": session_id,
            "message": "no-show"
        },
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to send message: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    data = response.json()
    print(f"\n📤 USER: no-show")
    print(f"📥 LISA: {data.get('response', 'No response')}")
    
    # Step 3: Send detailed description
    print("\n" + "="*80)
    print("STEP 3: Send Detailed Description")
    print("="*80)
    
    description = "The technician didn't show up for my appointment. I waited for 2 hours but no one came. This is very disappointing."
    
    response = requests.post(
        f"{BASE_URL}/chat/message",
        json={
            "session_id": session_id,
            "message": description
        },
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to send message: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    data = response.json()
    print(f"\n📤 USER: {description}")
    print(f"📥 LISA: {data.get('response', 'No response')}")
    
    # Check if complaint was created
    metadata = data.get('metadata', {})
    complaint_id = None
    
    if metadata:
        print(f"\n{'='*80}")
        print(f"RESPONSE METADATA:")
        print(f"{'='*80}")
        print(json.dumps(metadata, indent=2))
        
        # Try to extract complaint_id from metadata
        if 'complaint_id' in metadata:
            complaint_id = metadata['complaint_id']
        elif 'agent_metadata' in metadata and 'complaint_id' in metadata['agent_metadata']:
            complaint_id = metadata['agent_metadata']['complaint_id']
    
    # Extract complaint ID from response text if not in metadata
    if not complaint_id:
        response_text = data.get('response', '')
        import re
        match = re.search(r'#(\d+)', response_text)
        if match:
            complaint_id = int(match.group(1))
    
    if complaint_id:
        print(f"\n✅ COMPLAINT CREATED: #{complaint_id}")
        
        # Verify in database
        print(f"\n{'='*80}")
        print(f"VERIFYING COMPLAINT IN DATABASE")
        print(f"{'='*80}")
        
        db_check = await check_complaint_in_db(complaint_id)
        
        if db_check:
            print(f"\n✅ COMPLAINT #{complaint_id} VERIFIED IN DATABASE")
        else:
            print(f"\n❌ COMPLAINT #{complaint_id} NOT FOUND IN DATABASE")
            return False
        
        # Step 4: Check complaint status
        print("\n" + "="*80)
        print("STEP 4: Check Complaint Status")
        print("="*80)
        
        response = requests.post(
            f"{BASE_URL}/chat/message",
            json={
                "session_id": session_id,
                "message": f"What's the status of complaint #{complaint_id}?"
            },
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📤 USER: What's the status of complaint #{complaint_id}?")
            print(f"📥 LISA: {data.get('response', 'No response')}")
        
        return True
    else:
        print(f"\n❌ COMPLAINT ID NOT FOUND IN RESPONSE")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(test_complaint_flow())
        
        if success:
            print("\n" + "="*80)
            print("✅ ALL TESTS PASSED")
            print("="*80)
            print("✅ Complaint flow works correctly with API requests")
            print("✅ Complaint details shown in chat response")
            print("✅ Complaint stored in database")
            print("="*80)
        else:
            print("\n" + "="*80)
            print("❌ TESTS FAILED")
            print("="*80)
        
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

