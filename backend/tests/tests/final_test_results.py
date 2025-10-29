#!/usr/bin/env python3
"""
Final ServiceAgent Test Results - Quick Manual Tests
"""

import requests
import json
import time

# Test Configuration
BASE_URL = "http://127.0.0.1:8000/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZ3RzaGFvbmlkdXR0YTJrQGdtYWlsLmNvbSIsInVzZXJfaWQiOjE4MywidXNlcl90eXBlIjoiY3VzdG9tZXIiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYxNzQ0MzExLCJpYXQiOjE3NjE3NDI1MTF9.9iYi0z0SriT1CZqNrEDwuZ_ocYS8Xp4jORJnE7edDgw"

def test_single_query(message, expected_keywords):
    """Test a single query"""
    try:
        response = requests.post(
            f"{BASE_URL}/chat/message",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {TOKEN}"
            },
            json={"message": message},
            timeout=8
        )
        if response.status_code == 200:
            data = response.json()
            assistant_message = data.get("assistant_message", {}).get("message", "")
            
            # Check for expected keywords
            found = []
            for keyword in expected_keywords:
                if keyword.lower() in assistant_message.lower():
                    found.append(keyword)
            
            success = len(found) >= len(expected_keywords) * 0.7
            status = "✅ PASSED" if success else "❌ FAILED"
            
            print(f"{status} | {message}")
            if not success:
                print(f"   Expected: {expected_keywords}")
                print(f"   Found: {found}")
                print(f"   Response: {assistant_message[:100]}...")
            
            return success
        else:
            print(f"❌ FAILED | {message} - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ERROR | {message} - {str(e)}")
        return False

def main():
    print("🎯 FINAL SERVICEAGENT TEST RESULTS")
    print("=" * 60)
    
    # Test the key issues that were identified
    tests = [
        # Fixed Issues
        ("Show me all service categories", ["categories"]),  # Issue 1 - FIXED
        ("subcategories for house cleaning", ["Home Cleaning"]),  # Previously failed - FIXED
        
        # Remaining Issues to Test
        ("subcategories for barber shop", ["Salon for Men"]),  # Issue 2
        ("subcategories for water filter", ["Water Purifier"]),  # Issue 3
        ("subcategories for women salon", ["Salon for Women"]),  # Issue 4
        
        # Core Functionality Tests
        ("subcategories for cleaning", ["Home Cleaning"]),
        ("subcategories for packers", ["Packers and Movers"]),
        ("subcategories for electrical", ["Electrical"]),
        ("subcategories for plumbing", ["Plumbing"]),
        
        # NLP Tests
        ("subcategories for pakkers", ["Packers and Movers"]),  # Spell correction
        ("subcategories for moving company", ["Packers and Movers"]),  # Semantic
        ("subcategories for beauty salon", ["Salon for Women"]),  # Semantic
        
        # Advanced Patterns
        ("What types of cleaning do you offer?", ["cleaning"]),
        ("Can you show me salon options?", ["salon"]),
        
        # Error Handling
        ("subcategories for xyz", ["couldn't find"]),
        ("subcategories for repair", ["repair"])
    ]
    
    passed = 0
    total = len(tests)
    
    print(f"\nTesting {total} key scenarios...\n")
    
    for message, keywords in tests:
        if test_single_query(message, keywords):
            passed += 1
        time.sleep(0.3)  # Rate limiting
    
    # Results
    success_rate = (passed / total) * 100
    
    print("\n" + "=" * 60)
    print("🎯 FINAL RESULTS")
    print("=" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 95:
        print("\n🎉 EXCELLENT! ServiceAgent is production-ready!")
    elif success_rate >= 85:
        print("\n✅ VERY GOOD! ServiceAgent is highly functional.")
    elif success_rate >= 75:
        print("\n👍 GOOD! ServiceAgent is functional with minor issues.")
    else:
        print("\n⚠️ NEEDS IMPROVEMENT! Several issues remain.")

if __name__ == "__main__":
    main()
