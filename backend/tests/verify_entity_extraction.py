#!/usr/bin/env python3
"""
Verify Entity Extraction Tests
Tests all 4 entity extraction scenarios to confirm fixes are working
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def login():
    """Login and get access token"""
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "identifier": "agtshaonidutta2k@gmail.com",
            "password": "Shaoni@123"
        }
    )
    response.raise_for_status()
    return response.json()["tokens"]["access_token"]

def test_message(token, session_id, message, test_name):
    """Send a test message and verify response"""
    print(f"\n{'='*100}")
    print(f"TEST: {test_name}")
    print(f"Message: {message}")
    print(f"{'='*100}")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/chat/message",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "session_id": session_id,
            "message": message
        }
    )
    response.raise_for_status()
    result = response.json()
    
    print(f"\n✅ Response: {result.get('response', 'N/A')[:200]}...")
    print(f"Intent: {result.get('intent', 'N/A')}")
    print(f"Confidence: {result.get('confidence', 'N/A')}")
    print(f"Agent: {result.get('agent_used', 'N/A')}")
    print(f"Classification Method: {result.get('classification_method', 'N/A')}")
    
    # Check if all entities were collected (no follow-up questions for missing entities)
    response_text = result.get('response', '').lower()
    if 'what service' in response_text or 'which service' in response_text:
        print("⚠️  WARNING: System is asking for service type (should be extracted)")
    elif 'when would you like' in response_text or 'what date' in response_text:
        print("⚠️  WARNING: System is asking for date/time (should be extracted)")
    elif 'where would you like' in response_text or 'what is your location' in response_text:
        print("⚠️  WARNING: System is asking for location (should be auto-filled)")
    elif 'let me confirm' in response_text or 'confirm:' in response_text:
        print("✅ SUCCESS: All entities extracted, showing confirmation")
    else:
        print(f"ℹ️  Response type: {response_text[:100]}")
    
    return result

def main():
    print("="*100)
    print("ENTITY EXTRACTION VERIFICATION TESTS")
    print("="*100)
    
    print("\nLogging in...")
    token = login()
    print("✅ Login successful")
    
    # Test 1: "I want to book AC service for day after tomorrow at 2 PM"
    test_message(
        token, 
        "verify_test_1", 
        "I want to book AC service for day after tomorrow at 2 PM",
        "Test 1: Pattern matching with 'I want to book'"
    )
    time.sleep(2)
    
    # Test 2: "book plumbing service tomorrow morning"
    test_message(
        token,
        "verify_test_2",
        "book plumbing service tomorrow morning",
        "Test 2: Date-time splitting (tomorrow morning)"
    )
    time.sleep(2)
    
    # Test 3: "I need AC repair on 26/10/2025 at 14:00"
    test_message(
        token,
        "verify_test_3",
        "I need AC repair on 26/10/2025 at 14:00",
        "Test 3: Fallback action extraction from 'I need'"
    )
    time.sleep(2)
    
    # Test 4: "I want AC service today at 3 PM"
    test_message(
        token,
        "verify_test_4",
        "I want AC service today at 3 PM",
        "Test 4: Fallback action extraction from 'I want'"
    )
    
    print("\n" + "="*100)
    print("✅ ALL VERIFICATION TESTS COMPLETED")
    print("="*100)
    print("\nCheck backend logs for detailed entity extraction information:")
    print("- Look for '[_normalize_llm_entities] Fallback extracted action' messages")
    print("- Verify 'Collected' entities include: action, service_type, date, time, location")
    print("- Confirm 'Needed: []' (no missing entities)")

if __name__ == "__main__":
    main()

