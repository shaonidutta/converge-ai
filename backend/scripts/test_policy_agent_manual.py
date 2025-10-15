"""
Manual test script for PolicyAgent

Tests the PolicyAgent with various policy-related queries
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.agents.policy.policy_agent import PolicyAgent
from src.core.models import User
from src.core.config.settings import settings


async def create_test_user(db: AsyncSession) -> User:
    """Create a test user for testing"""
    # For testing, we'll create a mock user object
    user = User(
        id=1,
        mobile="9876543210",
        email="test@example.com",
        first_name="Test",
        last_name="User"
    )
    return user


async def test_policy_agent():
    """Test PolicyAgent with various queries"""
    print("=" * 70)
    print("PolicyAgent Manual Test")
    print("=" * 70)
    
    # Create database session
    print("\n1. Setting up database connection...")
    DATABASE_URL = settings.DATABASE_URL.replace("pymysql", "aiomysql")
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        print("   ✅ Database connected")
        
        # Create test user
        user = await create_test_user(db)
        print(f"   ✅ Test user created: {user.first_name} {user.last_name}")
        
        # Initialize PolicyAgent
        print("\n2. Initializing PolicyAgent...")
        try:
            agent = PolicyAgent(db)
            print("   ✅ PolicyAgent initialized")
        except Exception as e:
            print(f"   ❌ Error initializing PolicyAgent: {e}")
            return
        
        # Test queries
        test_queries = [
            {
                "name": "Cancellation Refund Query",
                "query": "What is your cancellation policy? Can I get a refund if I cancel 2 hours before?"
            },
            {
                "name": "Full Refund Query",
                "query": "When can I get a full refund for my booking?"
            },
            {
                "name": "Refund Processing Time",
                "query": "How long does it take to process a refund?"
            },
            {
                "name": "Rescheduling Query",
                "query": "Can I reschedule my booking instead of canceling?"
            },
            {
                "name": "Multi-Service Cancellation",
                "query": "What happens if I cancel only one service from a multi-service booking?"
            }
        ]
        
        print("\n3. Testing PolicyAgent with queries...")
        print("=" * 70)
        
        for idx, test in enumerate(test_queries, 1):
            print(f"\n📝 Test {idx}: {test['name']}")
            print(f"   Query: {test['query']}")
            print("-" * 70)
            
            try:
                # Execute agent
                result = await agent.execute(
                    intent="policy_inquiry",
                    entities={"query": test['query']},
                    user=user,
                    session_id=f"test_session_{idx}"
                )
                
                # Display results
                print(f"\n   ✅ Response:")
                print(f"   {result['response']}\n")
                
                print(f"   📊 Metadata:")
                print(f"   - Action: {result['action_taken']}")
                
                metadata = result.get('metadata', {})
                if 'grounding_score' in metadata:
                    print(f"   - Grounding Score: {metadata['grounding_score']:.2f}")
                if 'confidence' in metadata:
                    print(f"   - Confidence: {metadata['confidence']}")
                
                if 'sources' in metadata:
                    print(f"\n   📚 Sources:")
                    for source in metadata['sources']:
                        policy_type = source.get('policy_type', 'Unknown')
                        section = source.get('section', 'Unknown')
                        score = source.get('relevance_score') or source.get('score', 0.0)
                        print(f"   - {policy_type} / {section} (Score: {score})")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            print("=" * 70)
        
        # Test with no relevant query
        print(f"\n📝 Test {len(test_queries) + 1}: Irrelevant Query")
        print(f"   Query: What is the weather today?")
        print("-" * 70)
        
        try:
            result = await agent.execute(
                intent="policy_inquiry",
                entities={"query": "What is the weather today?"},
                user=user,
                session_id="test_session_irrelevant"
            )
            
            print(f"\n   ✅ Response:")
            print(f"   {result['response']}\n")
            print(f"   📊 Action: {result['action_taken']}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("=" * 70)
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(test_policy_agent())

