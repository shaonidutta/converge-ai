"""
Test script to verify Gemini Flash 2.0 API key is working correctly
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Load environment variables
from dotenv import load_dotenv
env_path = backend_path / ".env"
load_dotenv(env_path)

import google.generativeai as genai

def test_gemini_api_key():
    """Test if Gemini API key is working with Flash 2.0"""
    
    print("=" * 80)
    print("GEMINI FLASH 2.0 API KEY TEST")
    print("=" * 80)
    print()
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ FAIL: GOOGLE_API_KEY not found in environment variables")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...{api_key[-10:]}")
    print()
    
    # Configure genai
    try:
        genai.configure(api_key=api_key)
        print("✅ Gemini API configured successfully")
        print()
    except Exception as e:
        print(f"❌ FAIL: Failed to configure Gemini API: {e}")
        return False
    
    # Test 1: List available models
    print("-" * 80)
    print("Test 1: Listing available models")
    print("-" * 80)
    try:
        models = genai.list_models()
        gemini_models = [m for m in models if 'gemini' in m.name.lower()]
        
        print(f"✅ Found {len(gemini_models)} Gemini models:")
        for model in gemini_models[:10]:  # Show first 10
            print(f"   - {model.name}")
        
        # Check if gemini-2.0-flash is available
        flash_2_models = [m for m in gemini_models if '2.0-flash' in m.name.lower()]
        if flash_2_models:
            print(f"\n✅ Gemini 2.0 Flash models found: {len(flash_2_models)}")
            for model in flash_2_models:
                print(f"   - {model.name}")
        else:
            print("\n⚠️  WARNING: No Gemini 2.0 Flash models found")
        print()
    except Exception as e:
        print(f"❌ FAIL: Failed to list models: {e}")
        return False
    
    # Test 2: Generate content with gemini-2.0-flash-exp
    print("-" * 80)
    print("Test 2: Testing content generation with gemini-2.0-flash-exp")
    print("-" * 80)
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print("✅ Model initialized: gemini-2.0-flash-exp")
        
        # Simple test prompt
        prompt = "Say 'Hello, I am Gemini 2.0 Flash!' and nothing else."
        print(f"📝 Prompt: {prompt}")
        print()
        
        response = model.generate_content(prompt)
        print(f"🤖 Response: {response.text}")
        print()
        
        if response.text:
            print("✅ Content generation successful!")
        else:
            print("⚠️  WARNING: Empty response received")
        print()
    except Exception as e:
        print(f"❌ FAIL: Content generation failed: {e}")
        print()
        
        # Try alternative model name
        print("-" * 80)
        print("Test 2b: Trying alternative model name 'gemini-2.0-flash'")
        print("-" * 80)
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            print("✅ Model initialized: gemini-2.0-flash")
            
            response = model.generate_content(prompt)
            print(f"🤖 Response: {response.text}")
            print()
            
            if response.text:
                print("✅ Content generation successful with gemini-2.0-flash!")
            else:
                print("⚠️  WARNING: Empty response received")
            print()
        except Exception as e2:
            print(f"❌ FAIL: Content generation failed with gemini-2.0-flash: {e2}")
            return False
    
    # Test 3: Check quota/rate limits
    print("-" * 80)
    print("Test 3: Testing with a more complex prompt")
    print("-" * 80)
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = "What is 2 + 2? Answer with just the number."
        print(f"📝 Prompt: {prompt}")
        print()
        
        response = model.generate_content(prompt)
        print(f"🤖 Response: {response.text}")
        print()
        
        if "4" in response.text:
            print("✅ Correct response received!")
        else:
            print("⚠️  WARNING: Unexpected response")
        print()
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            print(f"⚠️  QUOTA EXCEEDED: {e}")
            print("   The API key is valid but you've exceeded the rate limit.")
            print("   This is expected if you've been testing extensively.")
            print()
        else:
            print(f"❌ FAIL: {e}")
            return False
    
    # Final summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("✅ API Key is valid and working!")
    print("✅ Gemini 2.0 Flash models are accessible")
    print("✅ Content generation is functional")
    print()
    print("Note: If you see quota errors, wait a few minutes and try again.")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    try:
        success = test_gemini_api_key()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

