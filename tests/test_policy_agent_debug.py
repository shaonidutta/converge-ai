"""
Test script to debug PolicyAgent issues
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from src.rag.vector_store.pinecone_service import PineconeService
from src.agents.policy.policy_agent import PolicyAgent
from src.core.database.connection import get_db


async def check_pinecone_documents():
    """Check if there are documents in Pinecone"""
    print("\n" + "="*80)
    print("CHECKING PINECONE DOCUMENTS")
    print("="*80)
    
    pinecone_service = PineconeService()
    
    # Check both namespaces
    for namespace in ["policies", "documents", ""]:
        print(f"\n📦 Checking namespace: '{namespace or 'default'}'")
        print("-" * 80)
        
        try:
            # Query with a generic term to get any documents
            results = pinecone_service.query_by_text(
                query_text="policy",
                top_k=5,
                namespace=namespace,
                include_metadata=True
            )
            
            if results:
                print(f"✅ Found {len(results)} documents in '{namespace or 'default'}' namespace")
                for i, result in enumerate(results[:3], 1):
                    print(f"\n  Document {i}:")
                    print(f"    Score: {result.get('score', 0):.4f}")
                    metadata = result.get('metadata', {})
                    print(f"    Document Name: {metadata.get('document_name', 'N/A')}")
                    print(f"    Category: {metadata.get('category', 'N/A')}")
                    print(f"    Text Preview: {metadata.get('text_preview', 'N/A')[:100]}...")
            else:
                print(f"❌ No documents found in '{namespace or 'default'}' namespace")
                
        except Exception as e:
            print(f"❌ Error querying namespace '{namespace or 'default'}': {e}")
    
    # Get index stats
    print(f"\n📊 Index Statistics:")
    print("-" * 80)
    try:
        stats = pinecone_service.index.describe_index_stats()
        print(f"Total vectors: {stats.get('total_vector_count', 0)}")
        print(f"Namespaces: {list(stats.get('namespaces', {}).keys())}")
        for ns, ns_stats in stats.get('namespaces', {}).items():
            print(f"  - {ns or 'default'}: {ns_stats.get('vector_count', 0)} vectors")
    except Exception as e:
        print(f"❌ Error getting index stats: {e}")


async def test_policy_agent():
    """Test PolicyAgent with various queries"""
    print("\n" + "="*80)
    print("TESTING POLICY AGENT")
    print("="*80)

    async for db in get_db():
        policy_agent = PolicyAgent(db)

        # Create a mock user
        from src.core.models import User
        mock_user = User(
            id=183,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            mobile="1234567890"
        )

        test_queries = [
            "can u tell me about policies?",
            "what is your refund policy?",
            "how do I cancel a booking?",
            "what are your terms and conditions?",
        ]

        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            print("-" * 80)

            try:
                result = await policy_agent.execute(
                    intent="policy_inquiry",
                    entities={},
                    user=mock_user,
                    session_id="test_session",
                    message=query
                )

                print(f"✅ Response: {result.get('response', 'N/A')[:200]}...")
                print(f"   Action: {result.get('action_taken', 'N/A')}")

                metadata = result.get('metadata', {})
                print(f"   Grounding Score: {metadata.get('grounding_score', 0):.4f}")
                print(f"   Confidence: {metadata.get('confidence', 'N/A')}")

                if 'sources' in metadata:
                    print(f"   Sources: {len(metadata['sources'])} documents")

            except Exception as e:
                print(f"❌ Error: {e}")


async def main():
    """Main test function"""
    print("\n" + "="*80)
    print("POLICY AGENT DEBUG TEST")
    print("="*80)
    
    # Check Pinecone documents
    await check_pinecone_documents()
    
    # Test PolicyAgent
    await test_policy_agent()
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())

