#!/usr/bin/env python3
"""
Test out-of-scope query handling
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def get_token():
    """Get authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"identifier": "agtshaonidutta2k@gmail.com", "password": "Shaoni@123"}
    )
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    return response.json()["tokens"]["access_token"]

def test_query(token, session_id, message, test_name):
    """Test a single query"""
    print(f"\n{'='*80}")
    print(f"{test_name}")
    print(f"{'='*80}")
    print(f"Query: {message}")
    print()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "session_id": session_id,
        "message": message
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/message",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Response received:")
            print(f"Intent: {result['assistant_message']['intent']}")
            print(f"Confidence: {result['assistant_message']['intent_confidence']}")
            print(f"Agent Used: {result['assistant_message'].get('agent_used', 'N/A')}")
            print(f"\nAssistant Message:")
            print(result['assistant_message']['message'])
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("🔐 Getting authentication token...")
    token = get_token()
    print("✅ Token obtained\n")
    
    # Test cases
    tests = [
        ("test_oos_weather", "What's the weather today?", "TEST 1: Weather Query (Out-of-Scope)"),
        ("test_oos_sports", "Who won the cricket match?", "TEST 2: Sports Query (Out-of-Scope)"),
        ("test_oos_joke", "Tell me a joke", "TEST 3: Joke Request (Out-of-Scope)"),
        ("test_oos_flight", "Book a flight to Mumbai", "TEST 4: Flight Booking (Out-of-Scope)"),
        ("test_greeting", "Hello", "TEST 5: Greeting (Should Work)"),
        ("test_booking", "I want to book AC repair", "TEST 6: Booking Query (Should Work)"),
    ]
    
    results = []
    for session_id, message, test_name in tests:
        success = test_query(token, session_id, message, test_name)
        results.append((test_name, success))
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")

if __name__ == "__main__":
    main()

