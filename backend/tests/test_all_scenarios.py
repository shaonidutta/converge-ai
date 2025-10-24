"""
Comprehensive Chat Integration Test - All Scenarios
Tests: Booking, Policies, Cancellations, Refunds, Service Discovery, Edge Cases
"""
import asyncio
import sys
import os
from datetime import datetime

# Load .env file FIRST
from dotenv import load_dotenv
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test scenarios
TEST_SCENARIOS = [
    # Basic Flow
    {
        "category": "BASIC FLOW",
        "scenarios": [
            {"name": "Greeting", "message": "Hello"},
            {"name": "Help Request", "message": "What can you help me with?"},
        ]
    },
    
    # Booking Flow
    {
        "category": "BOOKING",
        "scenarios": [
            {"name": "Book AC Service", "message": "I want to book AC service"},
            {"name": "Book Plumbing", "message": "I need a plumber"},
            {"name": "Book Cleaning", "message": "Book home cleaning service"},
            {"name": "Check Booking Status", "message": "What is my booking status?"},
            {"name": "Reschedule Booking", "message": "I want to reschedule my booking"},
        ]
    },
    
    # Service Discovery
    {
        "category": "SERVICE DISCOVERY",
        "scenarios": [
            {"name": "List Services", "message": "What services do you offer?"},
            {"name": "AC Service Details", "message": "Tell me about AC services"},
            {"name": "Pricing Query", "message": "How much does AC service cost?"},
        ]
    },
    
    # Policy Queries
    {
        "category": "POLICIES",
        "scenarios": [
            {"name": "Cancellation Policy", "message": "What is your cancellation policy?"},
            {"name": "Refund Policy", "message": "How do refunds work?"},
            {"name": "Payment Policy", "message": "What payment methods do you accept?"},
            {"name": "Service Guarantee", "message": "Do you provide service guarantee?"},
        ]
    },
    
    # Cancellation & Refund
    {
        "category": "CANCELLATION & REFUND",
        "scenarios": [
            {"name": "Cancel Booking", "message": "I want to cancel my booking"},
            {"name": "Request Refund", "message": "I want a refund"},
            {"name": "Refund Status", "message": "What is my refund status?"},
        ]
    },
    
    # Complaints
    {
        "category": "COMPLAINTS",
        "scenarios": [
            {"name": "Service Complaint", "message": "The service was not good"},
            {"name": "Staff Complaint", "message": "The technician was rude"},
            {"name": "Quality Issue", "message": "The work quality is poor"},
        ]
    },
    
    # Edge Cases
    {
        "category": "EDGE CASES",
        "scenarios": [
            {"name": "Empty Message", "message": ""},
            {"name": "Very Long Message", "message": "I want to book " + "AC service " * 50},
            {"name": "Special Characters", "message": "Book @#$% service!!!"},
            {"name": "Multiple Intents", "message": "I want to book AC service and also know about refund policy"},
            {"name": "Unclear Intent", "message": "asdfghjkl"},
            {"name": "Number Only", "message": "123456"},
        ]
    },
]

async def test_scenario(coordinator, user, scenario_name, message, session_id):
    """Test a single scenario"""
    try:
        result = await coordinator.execute(
            message=message,
            user=user,
            session_id=session_id,
            conversation_history=[]
        )
        
        return {
            "status": "✅ PASS",
            "response": result.get('response', 'N/A')[:100],  # First 100 chars
            "intent": result.get('intent', 'N/A'),
            "agent": result.get('agent_used', 'N/A'),
            "confidence": result.get('intent_confidence', 'N/A'),
        }
    except Exception as e:
        return {
            "status": "❌ FAIL",
            "error": str(e)[:100],  # First 100 chars
            "response": None,
            "intent": None,
            "agent": None,
        }

async def run_all_tests():
    """Run all test scenarios"""
    from src.core.database.connection import get_db
    from src.agents.coordinator.coordinator_agent import CoordinatorAgent
    from src.core.models import User
    from sqlalchemy import select
    
    print("\n" + "="*100)
    print("COMPREHENSIVE CHAT INTEGRATION TEST - ALL SCENARIOS")
    print("="*100)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100)
    
    # Get database session
    async for db in get_db():
        try:
            # Get test user
            result = await db.execute(select(User).where(User.email == "testchat@convergeai.com"))
            user = result.scalar_one_or_none()
            
            if not user:
                print("❌ Test user not found!")
                return
            
            print(f"\n✅ Test User: {user.email} (ID: {user.id})")
            
            # Initialize CoordinatorAgent
            print("\n📋 Initializing CoordinatorAgent...")
            try:
                coordinator = CoordinatorAgent(db=db)
                print("✅ CoordinatorAgent initialized\n")
            except Exception as e:
                print(f"❌ Failed to initialize CoordinatorAgent: {e}")
                return
            
            # Run all test scenarios
            all_results = []
            total_tests = sum(len(cat["scenarios"]) for cat in TEST_SCENARIOS)
            current_test = 0
            
            for category_data in TEST_SCENARIOS:
                category = category_data["category"]
                scenarios = category_data["scenarios"]
                
                print("\n" + "="*100)
                print(f"CATEGORY: {category}")
                print("="*100)
                
                category_results = []
                
                for scenario in scenarios:
                    current_test += 1
                    scenario_name = scenario["name"]
                    message = scenario["message"]
                    session_id = f"test_{category.lower().replace(' ', '_')}_{current_test}"
                    
                    print(f"\n[{current_test}/{total_tests}] Testing: {scenario_name}")
                    print(f"Message: '{message[:80]}{'...' if len(message) > 80 else ''}'")
                    
                    result = await test_scenario(coordinator, user, scenario_name, message, session_id)
                    
                    print(f"Status: {result['status']}")
                    if result['status'] == "✅ PASS":
                        print(f"Intent: {result['intent']}")
                        print(f"Agent: {result['agent']}")
                        print(f"Response: {result['response']}...")
                    else:
                        print(f"Error: {result['error']}")
                    
                    category_results.append({
                        "scenario": scenario_name,
                        "message": message[:50],
                        **result
                    })
                
                all_results.append({
                    "category": category,
                    "results": category_results
                })
            
            # Generate Summary Report
            print("\n\n" + "="*100)
            print("SUMMARY REPORT")
            print("="*100)
            
            total_pass = 0
            total_fail = 0
            issues = []
            
            for category_data in all_results:
                category = category_data["category"]
                results = category_data["results"]
                
                pass_count = sum(1 for r in results if r['status'] == "✅ PASS")
                fail_count = sum(1 for r in results if r['status'] == "❌ FAIL")
                
                total_pass += pass_count
                total_fail += fail_count
                
                print(f"\n{category}:")
                print(f"  ✅ Passed: {pass_count}/{len(results)}")
                print(f"  ❌ Failed: {fail_count}/{len(results)}")
                
                # Collect failed scenarios
                for result in results:
                    if result['status'] == "❌ FAIL":
                        issues.append({
                            "category": category,
                            "scenario": result['scenario'],
                            "message": result['message'],
                            "error": result.get('error', 'Unknown error')
                        })
            
            print(f"\n{'='*100}")
            print(f"OVERALL: {total_pass} PASSED, {total_fail} FAILED out of {total_tests} tests")
            print(f"Success Rate: {(total_pass/total_tests)*100:.1f}%")
            print(f"{'='*100}")
            
            # Detailed Issues Report
            if issues:
                print("\n\n" + "="*100)
                print("ISSUES FOUND - DETAILED REPORT")
                print("="*100)
                
                for i, issue in enumerate(issues, 1):
                    print(f"\n{i}. [{issue['category']}] {issue['scenario']}")
                    print(f"   Message: {issue['message']}")
                    print(f"   Error: {issue['error']}")
            else:
                print("\n\n🎉 ALL TESTS PASSED! No issues found.")
            
            print("\n" + "="*100)
            print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*100)
            
        except Exception as e:
            print(f"❌ Test execution error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            break

if __name__ == "__main__":
    asyncio.run(run_all_tests())

