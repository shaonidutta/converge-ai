#!/usr/bin/env python3
"""
Test conversational responses to verify natural, context-aware interactions
"""
import requests
import json
import sys
import time

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

def send_message(token, session_id, message):
    """Send a message and get response"""
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
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_greeting_variations(token):
    """Test different greeting variations"""
    print(f"\n{'='*80}")
    print("TEST 1: GREETING VARIATIONS (Should be natural and varied)")
    print(f"{'='*80}\n")
    
    greetings = [
        ("test_greeting_1", "Hello"),
        ("test_greeting_2", "Hi"),
        ("test_greeting_3", "Hey there"),
        ("test_greeting_4", "Good morning"),
    ]
    
    for session_id, message in greetings:
        print(f"User: {message}")
        result = send_message(token, session_id, message)
        if result:
            print(f"Lisa: {result['assistant_message']['message']}")
            print(f"Intent: {result['assistant_message']['intent']}")
            print()
        time.sleep(2)

def test_general_query_variations(token):
    """Test different general query variations"""
    print(f"\n{'='*80}")
    print("TEST 2: GENERAL QUERY VARIATIONS (Should be natural and helpful)")
    print(f"{'='*80}\n")
    
    queries = [
        ("test_general_1", "What can you do?"),
        ("test_general_2", "How can you help me?"),
        ("test_general_3", "What services do you offer?"),
    ]
    
    for session_id, message in queries:
        print(f"User: {message}")
        result = send_message(token, session_id, message)
        if result:
            print(f"Lisa: {result['assistant_message']['message']}")
            print(f"Intent: {result['assistant_message']['intent']}")
            print()
        time.sleep(2)

def test_out_of_scope_variations(token):
    """Test different out-of-scope query variations"""
    print(f"\n{'='*80}")
    print("TEST 3: OUT-OF-SCOPE VARIATIONS (Should gracefully decline)")
    print(f"{'='*80}\n")
    
    queries = [
        ("test_oos_1", "What's the weather?"),
        ("test_oos_2", "Tell me a joke"),
        ("test_oos_3", "Book a flight"),
    ]
    
    for session_id, message in queries:
        print(f"User: {message}")
        result = send_message(token, session_id, message)
        if result:
            print(f"Lisa: {result['assistant_message']['message']}")
            print(f"Intent: {result['assistant_message']['intent']}")
            print()
        time.sleep(2)

def test_multi_turn_conversation(token):
    """Test multi-turn conversation to verify context awareness"""
    print(f"\n{'='*80}")
    print("TEST 4: MULTI-TURN CONVERSATION (Should be context-aware)")
    print(f"{'='*80}\n")
    
    session_id = "test_multi_turn"
    
    conversation = [
        "Hello",
        "I want to book AC repair",
        "Mumbai 400001",
        "Tomorrow at 2 PM",
    ]
    
    for message in conversation:
        print(f"User: {message}")
        result = send_message(token, session_id, message)
        if result:
            print(f"Lisa: {result['assistant_message']['message']}")
            print(f"Intent: {result['assistant_message']['intent']}")
            print()
        time.sleep(3)

def main():
    print("🔐 Getting authentication token...")
    token = get_token()
    print("✅ Token obtained\n")
    
    # Run all tests
    test_greeting_variations(token)
    test_general_query_variations(token)
    test_out_of_scope_variations(token)
    test_multi_turn_conversation(token)
    
    print(f"\n{'='*80}")
    print("✅ ALL TESTS COMPLETED")
    print(f"{'='*80}\n")
    print("Review the responses above to verify:")
    print("1. Greetings are natural and varied (not the same every time)")
    print("2. General queries are helpful and conversational")
    print("3. Out-of-scope queries are gracefully declined")
    print("4. Multi-turn conversations maintain context")

if __name__ == "__main__":
    main()

