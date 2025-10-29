#!/usr/bin/env python3
"""
Quick ServiceAgent Testing Script - Focused on finding issues
"""

import requests
import json
import time

# Test Configuration
BASE_URL = "http://127.0.0.1:8000/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZ3RzaGFvbmlkdXR0YTJrQGdtYWlsLmNvbSIsInVzZXJfaWQiOjE4MywidXNlcl90eXBlIjoiY3VzdG9tZXIiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYxNzQ0MzExLCJpYXQiOjE3NjE3NDI1MTF9.9iYi0z0SriT1CZqNrEDwuZ_ocYS8Xp4jORJnE7edDgw"

def send_message(message):
    """Send message to ServiceAgent"""
    try:
        response = requests.post(
            f"{BASE_URL}/chat/message",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {TOKEN}"
            },
            json={"message": message},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def check_response(response, expected_keywords, test_name):
    """Check if response contains expected keywords"""
    if "error" in response:
        print(f"❌ {test_name}: API Error - {response['error']}")
        return False
    
    assistant_message = response.get("assistant_message", {}).get("message", "")
    
    # Check for expected keywords
    found_keywords = []
    for keyword in expected_keywords:
        if keyword.lower() in assistant_message.lower():
            found_keywords.append(keyword)
    
    if len(found_keywords) >= len(expected_keywords) * 0.7:  # 70% match threshold
        print(f"✅ {test_name}: PASSED")
        return True
    else:
        print(f"❌ {test_name}: FAILED")
        print(f"   Expected: {expected_keywords}")
        print(f"   Found: {found_keywords}")
        print(f"   Response: {assistant_message[:150]}...")
        return False

def main():
    print("🚀 QUICK SERVICEAGENT TESTING - FINDING ISSUES")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    
    # Test 1: Category Browsing
    print("\n🔍 TESTING CATEGORY BROWSING")
    tests = [
        ("What categories do you have?", ["categories"]),
        ("Show me all service categories", ["categories"]),
        ("List all categories", ["categories"])
    ]
    
    for message, keywords in tests:
        response = send_message(message)
        if check_response(response, keywords, f"Category: {message}"):
            passed_tests += 1
        total_tests += 1
        time.sleep(0.5)
    
    # Test 2: Core Subcategory Browsing
    print("\n🔍 TESTING CORE SUBCATEGORY BROWSING")
    tests = [
        ("subcategories for cleaning", ["Home Cleaning", "subcategories"]),
        ("subcategories for packers", ["Packers and Movers"]),
        ("subcategories for electrical", ["Electrical"]),
        ("subcategories for plumbing", ["Plumbing"]),
        ("subcategories for salon", ["Salon"]),
        ("subcategories for car care", ["Car Care"]),
        ("subcategories for painting", ["Painting"]),
        ("subcategories for pest control", ["Pest Control"])
    ]
    
    for message, keywords in tests:
        response = send_message(message)
        if check_response(response, keywords, f"Subcategory: {message}"):
            passed_tests += 1
        total_tests += 1
        time.sleep(0.5)
    
    # Test 3: NLP Capabilities - Fixed Issues
    print("\n🔍 TESTING NLP CAPABILITIES (FIXED ISSUES)")
    tests = [
        ("subcategories for house cleaning", ["Home Cleaning"]),  # Previously failed
        ("subcategories for pakkers", ["Packers and Movers"]),   # Spell correction
        ("subcategories for eletrician", ["Electrical"]),        # Spell correction
        ("subcategories for moving company", ["Packers and Movers"]),  # Semantic
        ("subcategories for beauty salon", ["Salon for Women"]), # Semantic
        ("subcategories for barber shop", ["Salon for Men"]),    # Semantic
        ("subcategories for water filter", ["Water Purifier"])   # Semantic
    ]
    
    for message, keywords in tests:
        response = send_message(message)
        if check_response(response, keywords, f"NLP: {message}"):
            passed_tests += 1
        total_tests += 1
        time.sleep(0.5)
    
    # Test 4: Advanced Query Patterns
    print("\n🔍 TESTING ADVANCED QUERY PATTERNS")
    tests = [
        ("What types of cleaning do you offer?", ["cleaning"]),
        ("Can you show me salon options?", ["salon"]),
        ("I'm looking for electrical services", ["electrical"]),
        ("Do you have plumbing available?", ["plumbing"]),
        ("What painting services are there?", ["painting"])
    ]
    
    for message, keywords in tests:
        response = send_message(message)
        if check_response(response, keywords, f"Advanced: {message}"):
            passed_tests += 1
        total_tests += 1
        time.sleep(0.5)
    
    # Test 5: Service Search
    print("\n🔍 TESTING SERVICE SEARCH")
    tests = [
        ("search for cleaning", ["cleaning"]),
        ("find plumbing services", ["plumbing"]),
        ("look for electrical work", ["electrical"]),
        ("I need painting services", ["painting"]),
        ("cleaning services", ["cleaning"])
    ]
    
    for message, keywords in tests:
        response = send_message(message)
        if check_response(response, keywords, f"Search: {message}"):
            passed_tests += 1
        total_tests += 1
        time.sleep(0.5)
    
    # Test 6: Error Handling
    print("\n🔍 TESTING ERROR HANDLING")
    tests = [
        ("subcategories for xyz", ["couldn't find", "try"]),
        ("subcategories for", ["try"]),
        ("random gibberish query", ["help"]),
        ("subcategories for repair", ["repair"])  # Should match Appliance Repair
    ]
    
    for message, keywords in tests:
        response = send_message(message)
        if check_response(response, keywords, f"Error: {message}"):
            passed_tests += 1
        total_tests += 1
        time.sleep(0.5)
    
    # Test 7: Edge Cases
    print("\n🔍 TESTING EDGE CASES")
    tests = [
        ("subcategories for ac", ["AC"]),  # Short form
        ("subcategories for men salon", ["Salon for Men"]),  # Gender specific
        ("subcategories for women salon", ["Salon for Women"]),  # Gender specific
        ("subcategories for home cleaning", ["Home Cleaning"]),  # Alternative phrasing
        ("subcategories for appliance repair", ["Appliance Repair"])  # Multi-word
    ]
    
    for message, keywords in tests:
        response = send_message(message)
        if check_response(response, keywords, f"Edge: {message}"):
            passed_tests += 1
        total_tests += 1
        time.sleep(0.5)
    
    # Final Results
    print("\n" + "=" * 60)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 60)
    
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("\n🎉 EXCELLENT! ServiceAgent is production-ready!")
    elif success_rate >= 80:
        print("\n✅ GOOD! ServiceAgent is functional with minor issues.")
    elif success_rate >= 70:
        print("\n⚠️ ACCEPTABLE! Some issues need attention.")
    else:
        print("\n❌ NEEDS WORK! Several critical issues found.")

if __name__ == "__main__":
    main()
