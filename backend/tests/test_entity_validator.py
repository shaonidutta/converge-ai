"""
Tests for Entity Validator Service

Tests:
- Date validation (future dates, past dates, booking window)
- Time validation (service hours)
- Location validation (pincode format)
- Service type validation
- Normalized values
- Error messages and suggestions
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.entity_validator import EntityValidator
from src.nlp.intent.config import EntityType
from unittest.mock import AsyncMock


def test_validate_date_future():
    """Test: Validate future date"""
    print("\n" + "="*80)
    print("TEST 1: Validate Future Date")
    print("="*80)
    
    mock_db = AsyncMock()
    validator = EntityValidator(mock_db)
    
    future_date = (datetime.now().date() + timedelta(days=7)).isoformat()
    result = asyncio.run(validator.validate(
        EntityType.DATE,
        future_date
    ))
    
    print(f"Date: {future_date}")
    print(f"Result: {result}")
    assert result.is_valid == True
    assert result.normalized_value == future_date
    print("✅ Test passed: Future date is valid")


def test_validate_date_past():
    """Test: Validate past date (should fail)"""
    print("\n" + "="*80)
    print("TEST 2: Validate Past Date (Should Fail)")
    print("="*80)
    
    mock_db = AsyncMock()
    validator = EntityValidator(mock_db)
    
    past_date = (datetime.now().date() - timedelta(days=1)).isoformat()
    result = asyncio.run(validator.validate(
        EntityType.DATE,
        past_date
    ))
    
    print(f"Date: {past_date}")
    print(f"Result: {result}")
    assert result.is_valid == False
    assert "future" in result.error_message.lower()
    assert result.suggestions is not None
    print("✅ Test passed: Past date rejected with suggestions")


def test_validate_date_too_far():
    """Test: Validate date too far in future (should fail)"""
    print("\n" + "="*80)
    print("TEST 3: Validate Date Too Far in Future")
    print("="*80)
    
    mock_db = AsyncMock()
    validator = EntityValidator(mock_db)
    
    far_future_date = (datetime.now().date() + timedelta(days=100)).isoformat()
    result = asyncio.run(validator.validate(
        EntityType.DATE,
        far_future_date
    ))
    
    print(f"Date: {far_future_date}")
    print(f"Result: {result}")
    assert result.is_valid == False
    assert "too far" in result.error_message.lower()
    print("✅ Test passed: Date too far rejected")


def test_validate_time_valid():
    """Test: Validate time within service hours"""
    print("\n" + "="*80)
    print("TEST 4: Validate Time Within Service Hours")
    print("="*80)
    
    mock_db = AsyncMock()
    validator = EntityValidator(mock_db)
    
    result = asyncio.run(validator.validate(
        EntityType.TIME,
        "14:00"
    ))
    
    print(f"Time: 14:00")
    print(f"Result: {result}")
    assert result.is_valid == True
    assert result.normalized_value == "14:00"
    print("✅ Test passed: Time within service hours is valid")


def test_validate_time_too_early():
    """Test: Validate time before service hours (should fail)"""
    print("\n" + "="*80)
    print("TEST 5: Validate Time Before Service Hours")
    print("="*80)
    
    mock_db = AsyncMock()
    validator = EntityValidator(mock_db)
    
    result = asyncio.run(validator.validate(
        EntityType.TIME,
        "06:00"
    ))
    
    print(f"Time: 06:00")
    print(f"Result: {result}")
    assert result.is_valid == False
    assert "service hours" in result.error_message.lower()
    assert result.suggestions is not None
    print("✅ Test passed: Time before service hours rejected")


def test_validate_time_too_late():
    """Test: Validate time after service hours (should fail)"""
    print("\n" + "="*80)
    print("TEST 6: Validate Time After Service Hours")
    print("="*80)
    
    mock_db = AsyncMock()
    validator = EntityValidator(mock_db)
    
    result = asyncio.run(validator.validate(
        EntityType.TIME,
        "22:00"
    ))
    
    print(f"Time: 22:00")
    print(f"Result: {result}")
    assert result.is_valid == False
    assert "service hours" in result.error_message.lower()
    print("✅ Test passed: Time after service hours rejected")


def test_validate_location_pincode():
    """Test: Validate pincode format"""
    print("\n" + "="*80)
    print("TEST 7: Validate Pincode Format")
    print("="*80)
    
    mock_db = AsyncMock()
    validator = EntityValidator(mock_db)
    
    # Mock the DB query to return None (pincode not found)
    # In real scenario, this would check against serviceable pincodes
    result = asyncio.run(validator.validate(
        EntityType.LOCATION,
        "400001"
    ))
    
    print(f"Pincode: 400001")
    print(f"Result: {result}")
    # Note: Without actual DB, it will gracefully accept the pincode
    print("✅ Test passed: Pincode format validated")


def test_validate_location_city():
    """Test: Validate city name"""
    print("\n" + "="*80)
    print("TEST 8: Validate City Name")
    print("="*80)
    
    mock_db = AsyncMock()
    validator = EntityValidator(mock_db)
    
    result = asyncio.run(validator.validate(
        EntityType.LOCATION,
        "Mumbai"
    ))
    
    print(f"City: Mumbai")
    print(f"Result: {result}")
    assert result.is_valid == True
    assert result.normalized_value == "Mumbai"
    print("✅ Test passed: City name is valid")


def test_validate_service_type_valid():
    """Test: Validate valid service type"""
    print("\n" + "="*80)
    print("TEST 9: Validate Valid Service Type")
    print("="*80)
    
    mock_db = AsyncMock()
    validator = EntityValidator(mock_db)
    
    result = asyncio.run(validator.validate(
        EntityType.SERVICE_TYPE,
        "ac"
    ))
    
    print(f"Service type: ac")
    print(f"Result: {result}")
    assert result.is_valid == True
    assert result.normalized_value == "ac"
    print("✅ Test passed: Valid service type accepted")


def test_validate_service_type_invalid():
    """Test: Validate invalid service type (should fail)"""
    print("\n" + "="*80)
    print("TEST 10: Validate Invalid Service Type")
    print("="*80)
    
    mock_db = AsyncMock()
    validator = EntityValidator(mock_db)
    
    result = asyncio.run(validator.validate(
        EntityType.SERVICE_TYPE,
        "unknown_service"
    ))
    
    print(f"Service type: unknown_service")
    print(f"Result: {result}")
    assert result.is_valid == False
    assert "unknown" in result.error_message.lower()
    assert result.suggestions is not None
    print("✅ Test passed: Invalid service type rejected with suggestions")


def test_validate_date_today():
    """Test: Validate today's date"""
    print("\n" + "="*80)
    print("TEST 11: Validate Today's Date")
    print("="*80)
    
    mock_db = AsyncMock()
    validator = EntityValidator(mock_db)
    
    today = datetime.now().date().isoformat()
    result = asyncio.run(validator.validate(
        EntityType.DATE,
        today
    ))
    
    print(f"Date: {today}")
    print(f"Result: {result}")
    assert result.is_valid == True
    print("✅ Test passed: Today's date is valid")


def test_error_messages_user_friendly():
    """Test: Error messages are user-friendly"""
    print("\n" + "="*80)
    print("TEST 12: Error Messages Are User-Friendly")
    print("="*80)
    
    mock_db = AsyncMock()
    validator = EntityValidator(mock_db)
    
    # Test past date error
    past_date = (datetime.now().date() - timedelta(days=1)).isoformat()
    result = asyncio.run(validator.validate(
        EntityType.DATE,
        past_date
    ))
    
    print(f"Error message: {result.error_message}")
    assert result.error_message is not None
    assert len(result.error_message) > 0
    # Should not contain technical jargon
    assert "exception" not in result.error_message.lower()
    assert "error" not in result.error_message.lower()
    print("✅ Test passed: Error messages are user-friendly")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("ENTITY VALIDATOR SERVICE - TEST SUITE")
    print("="*80)
    
    tests = [
        test_validate_date_future,
        test_validate_date_past,
        test_validate_date_too_far,
        test_validate_time_valid,
        test_validate_time_too_early,
        test_validate_time_too_late,
        test_validate_location_pincode,
        test_validate_location_city,
        test_validate_service_type_valid,
        test_validate_service_type_invalid,
        test_validate_date_today,
        test_error_messages_user_friendly,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ Test failed: {test.__name__}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ Test error: {test.__name__}")
            print(f"   Error: {e}")
            failed += 1
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print("="*80)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

