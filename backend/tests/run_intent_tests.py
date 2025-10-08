"""
Test Runner for Intent Classification

Standalone script to run intent classification tests with detailed output.
This is for manual testing and debugging.

Usage:
    python tests/run_intent_tests.py
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Add backend/src to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from src.services.intent_service import IntentService


# Test queries with expected results
TEST_CASES = [
    {
        "query": "I want to book AC service",
        "expected_primary": "booking_management",
        "expected_entities": ["action", "service_type"],
        "description": "Single intent - booking"
    },
    {
        "query": "How much does plumbing cost?",
        "expected_primary": "pricing_inquiry",
        "expected_entities": ["service_type"],
        "description": "Single intent - pricing"
    },
    {
        "query": "I want to book AC service and know the price",
        "expected_primary": "booking_management",
        "expected_intents": ["booking_management", "pricing_inquiry"],
        "description": "Multi-intent - booking + pricing"
    },
    {
        "query": "Cancel my booking and give me a refund",
        "expected_primary": "booking_management",
        "expected_intents": ["booking_management", "refund_request"],
        "description": "Multi-intent - cancel + refund"
    },
    {
        "query": "What's the price and when are you available?",
        "expected_primary": "pricing_inquiry",
        "expected_intents": ["pricing_inquiry", "availability_check"],
        "description": "Multi-intent - pricing + availability"
    },
    {
        "query": "The technician was rude and service was poor",
        "expected_primary": "complaint",
        "expected_entities": ["issue_type"],
        "description": "Single intent - complaint"
    },
    {
        "query": "My payment failed",
        "expected_primary": "payment_issue",
        "expected_entities": ["payment_type"],
        "description": "Single intent - payment issue"
    },
    {
        "query": "Hello",
        "expected_primary": "greeting",
        "description": "Single intent - greeting"
    },
]


async def run_automated_tests():
    """Run automated tests"""
    
    print("=" * 100)
    print("AUTOMATED MULTI-INTENT CLASSIFICATION TESTS")
    print("=" * 100)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ ERROR: GOOGLE_API_KEY environment variable not set!")
        print("Please set it in your .env file")
        return
    
    # Initialize intent service
    print("Initializing Intent Service...")
    intent_service = IntentService()
    print("✅ Intent Service initialized")
    print()
    
    # Track results
    total_tests = len(TEST_CASES)
    passed_tests = 0
    failed_tests = 0
    results = []
    
    # Run each test
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n{'=' * 100}")
        print(f"TEST {i}/{total_tests}: {test_case['description']}")
        print(f"{'=' * 100}")
        print(f"Query: \"{test_case['query']}\"")
        print()
        
        try:
            # Classify intent
            result = await intent_service.classify_message(test_case['query'])
            
            # Display results
            print(f"✅ Classification Method: {result.classification_method}")
            print(f"⏱️  Processing Time: {result.processing_time_ms}ms")
            print()
            
            print(f"🎯 Primary Intent: {result.primary_intent}")
            print(f"📋 All Detected Intents ({len(result.intents)}):")
            for j, intent in enumerate(result.intents, 1):
                print(f"  {j}. {intent.intent} (confidence: {intent.confidence:.2f})")
                if intent.entities:
                    print(f"     Entities: {intent.entities}")
            print()
            
            # Validate results
            test_passed = True
            validation_messages = []
            
            # Check primary intent
            if result.primary_intent == test_case['expected_primary']:
                validation_messages.append(f"✅ Primary intent matches: {result.primary_intent}")
            else:
                validation_messages.append(
                    f"❌ Primary intent mismatch: "
                    f"expected '{test_case['expected_primary']}', "
                    f"got '{result.primary_intent}'"
                )
                test_passed = False
            
            # Check multiple intents if expected
            if 'expected_intents' in test_case:
                detected_intents = [intent.intent for intent in result.intents]
                for expected_intent in test_case['expected_intents']:
                    if expected_intent in detected_intents:
                        validation_messages.append(f"✅ Intent detected: {expected_intent}")
                    else:
                        validation_messages.append(f"❌ Intent missing: {expected_intent}")
                        test_passed = False
            
            # Check entities if expected
            if 'expected_entities' in test_case and result.intents:
                primary_entities = result.intents[0].entities
                for expected_entity in test_case['expected_entities']:
                    if expected_entity in primary_entities:
                        validation_messages.append(
                            f"✅ Entity extracted: {expected_entity} = {primary_entities[expected_entity]}"
                        )
                    else:
                        validation_messages.append(f"⚠️  Entity not extracted: {expected_entity}")
                        # Don't fail test for missing entities, just warn
            
            # Print validation results
            print("VALIDATION:")
            for msg in validation_messages:
                print(f"  {msg}")
            print()
            
            if test_passed:
                print("✅ TEST PASSED")
                passed_tests += 1
            else:
                print("❌ TEST FAILED")
                failed_tests += 1
            
            # Store result
            results.append({
                "test_case": test_case,
                "result": result,
                "passed": test_passed,
                "validation": validation_messages
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            failed_tests += 1
            results.append({
                "test_case": test_case,
                "error": str(e),
                "passed": False
            })
    
    # Print summary
    print("\n" + "=" * 100)
    print("TEST SUMMARY")
    print("=" * 100)
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print()
    
    # Print detailed results
    print("DETAILED RESULTS:")
    print()
    for i, res in enumerate(results, 1):
        status = "✅ PASS" if res['passed'] else "❌ FAIL"
        print(f"{i}. {status} - {res['test_case']['description']}")
        if 'result' in res:
            print(f"   Query: \"{res['test_case']['query']}\"")
            print(f"   Primary Intent: {res['result'].primary_intent}")
            print(f"   Method: {res['result'].classification_method}")
            print(f"   Time: {res['result'].processing_time_ms}ms")
        print()
    
    print("=" * 100)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)


def main():
    """Main function"""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run tests
    asyncio.run(run_automated_tests())


if __name__ == "__main__":
    main()

