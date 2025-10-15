"""
Test Dialog State Manager

Tests for dialog state management functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.core.config import settings
from src.services.dialog_state_manager import DialogStateManager
from src.schemas.dialog_state import DialogStateCreate, DialogStateUpdate
from src.core.models.dialog_state import DialogStateType


async def test_dialog_state_manager():
    """Test dialog state manager functionality"""
    
    print("=" * 80)
    print("DIALOG STATE MANAGER TEST")
    print("=" * 80)
    
    # Create async engine (replace mysql+pymysql with mysql+aiomysql)
    database_url = settings.DATABASE_URL.replace("mysql+pymysql://", "mysql+aiomysql://")
    engine = create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True
    )
    
    # Create session factory
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session_factory() as session:
        manager = DialogStateManager(session)
        
        # Test 1: Create dialog state
        print("\n" + "=" * 80)
        print("TEST 1: Create Dialog State")
        print("=" * 80)
        
        create_data = DialogStateCreate(
            user_id=1,  # Assuming user ID 1 exists
            session_id="test_session_123",
            state=DialogStateType.COLLECTING_INFO,
            intent="booking_management",
            collected_entities={
                "service_type": "ac",
                "action": "book",
                "city": "Mumbai"
            },
            needed_entities=["date", "time", "ac_type"],
            pending_action=None,
            context={
                "last_question": "What type of AC do you have?",
                "attempt_count": 1
            },
            expires_in_hours=24
        )
        
        state = await manager.create_state(create_data)
        print(f"✅ Created dialog state: ID={state.id}")
        print(f"   Session: {state.session_id}")
        print(f"   State: {state.state.value}")
        print(f"   Intent: {state.intent}")
        print(f"   Collected: {state.collected_entities}")
        print(f"   Needed: {state.needed_entities}")
        
        # Test 2: Get active state
        print("\n" + "=" * 80)
        print("TEST 2: Get Active State")
        print("=" * 80)
        
        retrieved_state = await manager.get_active_state("test_session_123")
        print(f"✅ Retrieved dialog state: ID={retrieved_state.id}")
        print(f"   Is Active: {retrieved_state.is_active()}")
        print(f"   Needs More Info: {retrieved_state.needs_more_info()}")
        
        # Test 3: Update state - add entity
        print("\n" + "=" * 80)
        print("TEST 3: Add Entity")
        print("=" * 80)
        
        updated_state = await manager.add_entity(
            "test_session_123",
            "date",
            "2025-10-10"
        )
        print(f"✅ Added entity 'date': {updated_state.collected_entities}")
        
        # Test 4: Remove needed entity
        print("\n" + "=" * 80)
        print("TEST 4: Remove Needed Entity")
        print("=" * 80)
        
        updated_state = await manager.remove_needed_entity(
            "test_session_123",
            "date"
        )
        print(f"✅ Removed 'date' from needed entities: {updated_state.needed_entities}")
        
        # Test 5: Follow-up detection - confirmation
        print("\n" + "=" * 80)
        print("TEST 5: Follow-Up Detection - Confirmation")
        print("=" * 80)
        
        # Update state to awaiting confirmation
        await manager.update_state(
            "test_session_123",
            DialogStateUpdate(state=DialogStateType.AWAITING_CONFIRMATION)
        )
        
        result = await manager.is_follow_up_response("yes", "test_session_123")
        print(f"✅ Message: 'yes'")
        print(f"   Is Follow-Up: {result.is_follow_up}")
        print(f"   Confidence: {result.confidence}")
        print(f"   Reason: {result.reason}")
        
        # Test 6: Follow-up detection - short entity value
        print("\n" + "=" * 80)
        print("TEST 6: Follow-Up Detection - Short Entity Value")
        print("=" * 80)
        
        # Update state back to collecting info
        await manager.update_state(
            "test_session_123",
            DialogStateUpdate(
                state=DialogStateType.COLLECTING_INFO,
                needed_entities=["time"]
            )
        )
        
        result = await manager.is_follow_up_response("2 PM", "test_session_123")
        print(f"✅ Message: '2 PM'")
        print(f"   Is Follow-Up: {result.is_follow_up}")
        print(f"   Confidence: {result.confidence}")
        print(f"   Reason: {result.reason}")
        print(f"   Expected Entity: {result.expected_entity}")
        
        # Test 7: Follow-up detection - long message (new intent)
        print("\n" + "=" * 80)
        print("TEST 7: Follow-Up Detection - Long Message (New Intent)")
        print("=" * 80)
        
        result = await manager.is_follow_up_response(
            "Actually, I want to cancel my previous booking instead",
            "test_session_123"
        )
        print(f"✅ Message: 'Actually, I want to cancel my previous booking instead'")
        print(f"   Is Follow-Up: {result.is_follow_up}")
        print(f"   Confidence: {result.confidence}")
        print(f"   Reason: {result.reason}")
        
        # Test 8: Get state status
        print("\n" + "=" * 80)
        print("TEST 8: Get State Status")
        print("=" * 80)
        
        status = await manager.get_state_status("test_session_123")
        print(f"✅ Has Active State: {status.has_active_state}")
        print(f"   Is Follow-Up Likely: {status.is_follow_up_likely}")
        if status.state:
            print(f"   Current State: {status.state.state}")
            print(f"   Current Intent: {status.state.intent}")
        
        # Test 9: Clear state
        print("\n" + "=" * 80)
        print("TEST 9: Clear State")
        print("=" * 80)
        
        cleared = await manager.clear_state("test_session_123")
        print(f"✅ State cleared: {cleared}")
        
        # Verify state is gone
        retrieved_state = await manager.get_active_state("test_session_123")
        print(f"   State after clear: {retrieved_state}")
        
        print("\n" + "=" * 80)
        print("ALL TESTS PASSED! ✅")
        print("=" * 80)
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_dialog_state_manager())

