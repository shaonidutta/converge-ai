"""
Test Out-of-Scope Query Handling

This script tests what happens when queries don't belong to any intent.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend/src to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from src.services.intent_service import IntentService


# Out-of-scope test queries
OUT_OF_SCOPE_QUERIES = [
    # Weather queries
    "What's the weather today?",
    "Will it rain tomorrow?",
    
    # News/Politics
    "Who won the election?",
    "What's the latest news?",
    
    # Sports
    "Who won the cricket match?",
    "What's the football score?",
    
    # Entertainment
    "What movies are playing?",
    "Recommend a good restaurant",
    
    # Random/Gibberish
    "xyz abc random text",
    "asdfghjkl qwerty",
    
    # Other services
    "Book a flight to Mumbai",
    "Order pizza",
    "Call me a taxi",
    
    # Personal questions
    "How old are you?",
    "What's your name?",
]


async def test_out_of_scope_queries():
    """Test out-of-scope query handling"""
    
    print("=" * 100)
    print("OUT-OF-SCOPE QUERY HANDLING TEST")
    print("=" * 100)
    print()
    
    # Check if API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ ERROR: GOOGLE_API_KEY environment variable not set!")
        return
    
    # Initialize intent service
    print("Initializing Intent Service...")
    intent_service = IntentService()
    print("✅ Intent Service initialized")
    print()
    
    # Test each query
    for i, query in enumerate(OUT_OF_SCOPE_QUERIES, 1):
        print(f"\n{'=' * 100}")
        print(f"TEST {i}/{len(OUT_OF_SCOPE_QUERIES)}")
        print(f"{'=' * 100}")
        print(f"Query: \"{query}\"")
        print()
        
        try:
            # Classify intent
            result = await intent_service.classify_message(query)
            
            # Display results
            print(f"✅ Classification Method: {result.classification_method}")
            print(f"⏱️  Processing Time: {result.processing_time_ms}ms")
            print()
            
            print(f"🎯 Primary Intent: {result.primary_intent}")
            print(f"   Confidence: {result.intents[0].confidence:.2f}")
            print()
            
            if result.requires_clarification:
                print(f"⚠️  Requires Clarification: YES")
                print(f"   Reason: {result.clarification_reason}")
            else:
                print(f"✅ No Clarification Needed")
            print()
            
            # Analyze result
            if result.primary_intent == "out_of_scope":
                print("✅ Correctly identified as OUT OF SCOPE")
            elif result.primary_intent == "unclear_intent":
                print("⚠️  Identified as UNCLEAR INTENT (needs clarification)")
            else:
                print(f"⚠️  Classified as: {result.primary_intent}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 100)
    print("TEST COMPLETED")
    print("=" * 100)


def main():
    """Main function"""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run tests
    asyncio.run(test_out_of_scope_queries())


if __name__ == "__main__":
    main()

