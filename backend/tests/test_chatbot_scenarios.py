"""
Test script to validate all chatbot scenarios without frontend
Tests:
1. Service information query
2. Booking flow with slot-filling
3. Context awareness
"""

import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.session import get_db
from agents.coordinator.coordinator_agent import CoordinatorAgent
from models.user import User


async def get_test_user(db: AsyncSession) -> User:
    """Get or create a test user"""
    result = await db.execute(
        select(User).where(User.email == "test@example.com")
    )
    user = result.scalar_one_or_none()
    
    if not user:
        print("❌ Test user not found. Please create a user with email: test@example.com")
        sys.exit(1)
    
    return user


async def test_scenario_1_service_information():
    """Test 1: Service information query"""
    print("\n" + "="*80)
    print("TEST 1: Service Information Query")
    print("="*80)
    
    async for db in get_db():
        try:
            user = await get_test_user(db)
            coordinator = CoordinatorAgent(db)
            
            session_id = "test_session_service_info"
            message = "can u help with services?"
            
            print(f"\n📤 User: {message}")
            print(f"🔄 Processing...")
            
            result = await coordinator.execute(
                user=user,
                session_id=session_id,
                message=message
            )
            
            print(f"\n📥 Lisa: {result['response']}")
            print(f"🎯 Intent: {result['intent']}")
            print(f"🤖 Agent: {result['agent_used']}")
            print(f"📊 Confidence: {result['confidence']}")
            
            # Validation
            if result['agent_used'] == 'service':
                print("\n✅ TEST PASSED: Correctly routed to ServiceAgent")
            else:
                print(f"\n❌ TEST FAILED: Expected 'service' agent, got '{result['agent_used']}'")
                
            if 'policy' in result['response'].lower():
                print("❌ TEST FAILED: Response mentions 'policy' (should be about services)")
            else:
                print("✅ TEST PASSED: Response does not mention 'policy'")
                
        except Exception as e:
            print(f"\n❌ TEST FAILED with error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            await db.close()
            break


async def test_scenario_2_booking_slot_filling():
    """Test 2: Booking flow with slot-filling"""
    print("\n" + "="*80)
    print("TEST 2: Booking Flow with Slot-Filling")
    print("="*80)
    
    async for db in get_db():
        try:
            user = await get_test_user(db)
            coordinator = CoordinatorAgent(db)
            
            session_id = "test_session_booking"
            
            # Turn 1: Initial booking request
            print("\n--- Turn 1 ---")
            message1 = "I want to book a service"
            print(f"📤 User: {message1}")
            
            result1 = await coordinator.execute(
                user=user,
                session_id=session_id,
                message=message1
            )
            
            print(f"📥 Lisa: {result1['response']}")
            print(f"🎯 Intent: {result1['intent']}")
            print(f"🤖 Agent: {result1['agent_used']}")
            
            # Validation: Should ask for location
            if 'location' in result1['response'].lower() or 'pincode' in result1['response'].lower():
                print("✅ Lisa asks for location/pincode")
            else:
                print(f"❌ Lisa should ask for location/pincode, but said: {result1['response']}")
            
            # Turn 2: Provide location
            print("\n--- Turn 2 ---")
            message2 = "282002"
            print(f"📤 User: {message2}")
            
            result2 = await coordinator.execute(
                user=user,
                session_id=session_id,
                message=message2
            )
            
            print(f"📥 Lisa: {result2['response']}")
            print(f"🎯 Intent: {result2['intent']}")
            print(f"🤖 Agent: {result2['agent_used']}")
            
            # Validation: Should NOT repeat location question
            if 'location' in result2['response'].lower() or 'pincode' in result2['response'].lower():
                print("❌ TEST FAILED: Lisa repeated the location question (no context awareness!)")
            else:
                print("✅ TEST PASSED: Lisa did NOT repeat the location question")
            
            # Should ask for next piece of information
            if any(word in result2['response'].lower() for word in ['date', 'time', 'service', 'what']):
                print("✅ Lisa asks for next piece of information")
            else:
                print(f"⚠️  Lisa's response unclear: {result2['response']}")
            
            # Turn 3: Provide more information
            print("\n--- Turn 3 ---")
            message3 = "tomorrow at 2 PM, I need AC service"
            print(f"📤 User: {message3}")
            
            result3 = await coordinator.execute(
                user=user,
                session_id=session_id,
                message=message3
            )
            
            print(f"📥 Lisa: {result3['response']}")
            print(f"🎯 Intent: {result3['intent']}")
            print(f"🤖 Agent: {result3['agent_used']}")
            
            # Validation: Should proceed with booking or ask for confirmation
            if 'error' in result3['response'].lower() or 'apologize' in result3['response'].lower():
                print("❌ TEST FAILED: Got error response")
            else:
                print("✅ TEST PASSED: No error response")
                
        except Exception as e:
            print(f"\n❌ TEST FAILED with error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            await db.close()
            break


async def test_scenario_3_context_awareness():
    """Test 3: Context awareness across messages"""
    print("\n" + "="*80)
    print("TEST 3: Context Awareness")
    print("="*80)
    
    async for db in get_db():
        try:
            user = await get_test_user(db)
            coordinator = CoordinatorAgent(db)
            
            session_id = "test_session_context"
            
            # Turn 1: Greeting
            print("\n--- Turn 1 ---")
            message1 = "hi"
            print(f"📤 User: {message1}")
            
            result1 = await coordinator.execute(
                user=user,
                session_id=session_id,
                message=message1
            )
            
            print(f"📥 Lisa: {result1['response']}")
            
            # Turn 2: Ask about services (should understand context)
            print("\n--- Turn 2 ---")
            message2 = "what services do you offer?"
            print(f"📤 User: {message2}")
            
            result2 = await coordinator.execute(
                user=user,
                session_id=session_id,
                message=message2
            )
            
            print(f"📥 Lisa: {result2['response']}")
            print(f"🎯 Intent: {result2['intent']}")
            print(f"🤖 Agent: {result2['agent_used']}")
            
            # Validation
            if result2['agent_used'] == 'service':
                print("✅ TEST PASSED: Correctly routed to ServiceAgent")
            else:
                print(f"❌ TEST FAILED: Expected 'service' agent, got '{result2['agent_used']}'")
                
        except Exception as e:
            print(f"\n❌ TEST FAILED with error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            await db.close()
            break


async def main():
    """Run all test scenarios"""
    print("\n" + "="*80)
    print("🧪 CHATBOT SCENARIO TESTING")
    print("="*80)
    print("\nTesting all scenarios without frontend...")
    
    # Test 1: Service information query
    await test_scenario_1_service_information()
    
    # Test 2: Booking flow with slot-filling
    await test_scenario_2_booking_slot_filling()
    
    # Test 3: Context awareness
    await test_scenario_3_context_awareness()
    
    print("\n" + "="*80)
    print("🏁 ALL TESTS COMPLETED")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())

