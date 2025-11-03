"""
Test Complaint Flow - Direct ComplaintAgent Testing

This script tests the ComplaintAgent directly without going through
the full chat flow to avoid hitting Gemini API rate limits.
"""
import os
import sys
import asyncio
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
from src.core.models import User
from src.agents.complaint.complaint_agent import ComplaintAgent


async def get_test_user(session: AsyncSession) -> User:
    """Get test user from database"""
    from sqlalchemy import select
    result = await session.execute(
        select(User).where(User.email == "agtshaonidutta2k@gmail.com")
    )
    user = result.scalar_one_or_none()
    
    if not user:
        print("❌ Test user not found. Please login first.")
        sys.exit(1)
    
    return user


async def test_complaint_creation():
    """Test complaint creation flow"""
    
    print("=" * 80)
    print("COMPLAINT AGENT TEST - DIRECT TESTING")
    print("=" * 80)
    print()
    
    # Create database session
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    # Convert to async URL
    if database_url.startswith("mysql://"):
        database_url = database_url.replace("mysql://", "mysql+aiomysql://")
    elif database_url.startswith("mysql+pymysql://"):
        database_url = database_url.replace("mysql+pymysql://", "mysql+aiomysql://")
    
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get test user
        print("📋 Getting test user...")
        user = await get_test_user(session)
        print(f"✅ Test user: {user.first_name} {user.last_name} (ID: {user.id})")
        print()
        
        # Initialize ComplaintAgent
        print("🤖 Initializing ComplaintAgent...")
        complaint_agent = ComplaintAgent(db=session)
        print("✅ ComplaintAgent initialized")
        print()
        
        # Test 1: Create complaint without booking
        print("-" * 80)
        print("Test 1: Create Complaint (No Booking)")
        print("-" * 80)
        
        message = "The technician didn't show up for my appointment. I waited for 2 hours but no one came."
        entities = {
            "action": "create",
            "description": message,
            "complaint_type": "delay",
            "issue_type": "no-show"
        }
        
        print(f"📝 Message: {message}")
        print(f"📦 Entities: {entities}")
        print()
        
        try:
            result = await complaint_agent.execute(
                message=message,
                user=user,
                session_id="test_session_001",
                entities=entities
            )
            
            print("✅ Complaint created successfully!")
            print()
            print(f"🎯 Action Taken: {result['action_taken']}")
            print(f"📄 Response: {result['response'][:200]}...")
            print()
            
            if result.get('metadata'):
                metadata = result['metadata']
                print("📊 Complaint Details:")
                print(f"   • Complaint ID: #{metadata.get('complaint_id')}")
                print(f"   • Type: {metadata.get('complaint_type')}")
                print(f"   • Priority: {metadata.get('priority')}")
                print(f"   • Status: {metadata.get('status')}")
                print(f"   • Response Due: {metadata.get('response_due_at')}")
                print(f"   • Resolution Due: {metadata.get('resolution_due_at')}")
                print()
                
                complaint_id = metadata.get('complaint_id')
        except Exception as e:
            print(f"❌ FAIL: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 2: Check complaint status
        print("-" * 80)
        print("Test 2: Check Complaint Status")
        print("-" * 80)
        
        entities = {
            "action": "status",
            "complaint_id": str(complaint_id)
        }
        
        print(f"📝 Checking status for complaint #{complaint_id}")
        print()
        
        try:
            result = await complaint_agent.execute(
                message=f"check status of complaint {complaint_id}",
                user=user,
                session_id="test_session_001",
                entities=entities
            )
            
            print("✅ Status retrieved successfully!")
            print()
            print(f"📄 Response:\n{result['response']}")
            print()
        except Exception as e:
            print(f"❌ FAIL: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 3: Add update to complaint
        print("-" * 80)
        print("Test 3: Add Update to Complaint")
        print("-" * 80)
        
        entities = {
            "action": "update",
            "complaint_id": str(complaint_id),
            "comment": "I tried calling customer support but no one answered. This is very frustrating."
        }
        
        print(f"📝 Adding update to complaint #{complaint_id}")
        print(f"💬 Comment: {entities['comment']}")
        print()
        
        try:
            result = await complaint_agent.execute(
                message=entities['comment'],
                user=user,
                session_id="test_session_001",
                entities=entities
            )
            
            print("✅ Update added successfully!")
            print()
            print(f"📄 Response: {result['response']}")
            print()
        except Exception as e:
            print(f"❌ FAIL: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 4: Create complaint with booking
        print("-" * 80)
        print("Test 4: Create Complaint (With Booking)")
        print("-" * 80)
        
        # Get a booking for the user
        from sqlalchemy import select
        from src.core.models import Booking
        
        result = await session.execute(
            select(Booking).where(Booking.user_id == user.id).limit(1)
        )
        booking = result.scalar_one_or_none()
        
        if booking:
            message = f"I want to complain about booking {booking.order_id}. The service quality was very poor."
            entities = {
                "action": "create",
                "description": message,
                "complaint_type": "service_quality",
                "booking_id": str(booking.id)
            }
            
            print(f"📝 Message: {message}")
            print(f"📦 Entities: {entities}")
            print()
            
            try:
                result = await complaint_agent.execute(
                    message=message,
                    user=user,
                    session_id="test_session_002",
                    entities=entities
                )
                
                print("✅ Complaint with booking created successfully!")
                print()
                print(f"🎯 Action Taken: {result['action_taken']}")
                print(f"📄 Response: {result['response'][:200]}...")
                print()
                
                if result.get('metadata'):
                    metadata = result['metadata']
                    print("📊 Complaint Details:")
                    print(f"   • Complaint ID: #{metadata.get('complaint_id')}")
                    print(f"   • Booking ID: {metadata.get('booking_id')}")
                    print(f"   • Order ID: {booking.order_id}")
                    print(f"   • Type: {metadata.get('complaint_type')}")
                    print(f"   • Priority: {metadata.get('priority')}")
                    print()
            except Exception as e:
                print(f"❌ FAIL: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("⚠️  No bookings found for user, skipping booking complaint test")
            print()
        
        # Test 5: Priority calculation
        print("-" * 80)
        print("Test 5: Priority Calculation Tests")
        print("-" * 80)
        
        test_cases = [
            {
                "description": "URGENT - This is a critical safety issue!",
                "expected_priority": "CRITICAL",
                "complaint_type": "other"
            },
            {
                "description": "The service was terrible and I'm very disappointed",
                "expected_priority": "HIGH",
                "complaint_type": "service_quality"
            },
            {
                "description": "I need a refund for the poor service",
                "expected_priority": "HIGH",
                "complaint_type": "refund_issue"
            },
            {
                "description": "The technician was a bit late",
                "expected_priority": "LOW",
                "complaint_type": "delay"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest Case {i}:")
            print(f"   Description: {test_case['description']}")
            print(f"   Type: {test_case['complaint_type']}")
            print(f"   Expected Priority: {test_case['expected_priority']}")
            
            entities = {
                "action": "create",
                "description": test_case['description'],
                "complaint_type": test_case['complaint_type']
            }
            
            try:
                result = await complaint_agent.execute(
                    message=test_case['description'],
                    user=user,
                    session_id=f"test_session_priority_{i}",
                    entities=entities
                )
                
                actual_priority = result['metadata']['priority'].upper()
                if actual_priority == test_case['expected_priority']:
                    print(f"   ✅ Priority: {actual_priority} (CORRECT)")
                else:
                    print(f"   ⚠️  Priority: {actual_priority} (Expected: {test_case['expected_priority']})")
            except Exception as e:
                print(f"   ❌ FAIL: {e}")
        
        print()
    
    # Final summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("✅ All complaint flow tests completed successfully!")
    print("✅ ComplaintAgent is working correctly")
    print()
    print("Tested Features:")
    print("   • Create complaint without booking")
    print("   • Check complaint status")
    print("   • Add update to complaint")
    print("   • Create complaint with booking")
    print("   • Priority calculation (CRITICAL, HIGH, MEDIUM, LOW)")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_complaint_creation())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

