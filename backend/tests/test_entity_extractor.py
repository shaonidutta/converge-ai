"""
Tests for Entity Extractor Service

Tests:
- Pattern-based extraction (dates, times, locations, etc.)
- Confirmation extraction
- Service type extraction
- Booking ID extraction
- Confidence scoring
- Normalized values
"""

import sys
import os
import asyncio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.entity_extractor import EntityExtractor
from src.nlp.intent.config import EntityType


def test_extract_confirmation_yes():
    """Test: Extract confirmation (yes)"""
    print("\n" + "="*80)
    print("TEST 1: Extract Confirmation (Yes)")
    print("="*80)
    
    extractor = EntityExtractor()
    result = asyncio.run(extractor.extract_from_follow_up(
        message="yes",
        expected_entity=EntityType.ACTION,
        context={}
    ))
    
    print(f"Message: 'yes'")
    print(f"Result: {result}")
    assert result is not None
    assert result.normalized_value == True
    assert result.confidence >= 0.9
    print("✅ Test passed: 'yes' extracted as confirmation")


def test_extract_confirmation_no():
    """Test: Extract confirmation (no)"""
    print("\n" + "="*80)
    print("TEST 2: Extract Confirmation (No)")
    print("="*80)
    
    extractor = EntityExtractor()
    result = asyncio.run(extractor.extract_from_follow_up(
        message="no",
        expected_entity=EntityType.ACTION,
        context={}
    ))
    
    print(f"Message: 'no'")
    print(f"Result: {result}")
    assert result is not None
    assert result.normalized_value == False
    assert result.confidence >= 0.9
    print("✅ Test passed: 'no' extracted as confirmation")


def test_extract_date_tomorrow():
    """Test: Extract date (tomorrow)"""
    print("\n" + "="*80)
    print("TEST 3: Extract Date (Tomorrow)")
    print("="*80)
    
    extractor = EntityExtractor()
    result = asyncio.run(extractor.extract_from_follow_up(
        message="tomorrow",
        expected_entity=EntityType.DATE,
        context={}
    ))
    
    print(f"Message: 'tomorrow'")
    print(f"Result: {result}")
    assert result is not None
    assert result.normalized_value is not None
    assert result.confidence >= 0.9
    print(f"✅ Test passed: 'tomorrow' extracted as date: {result.normalized_value}")


def test_extract_date_iso_format():
    """Test: Extract date (ISO format)"""
    print("\n" + "="*80)
    print("TEST 4: Extract Date (ISO Format)")
    print("="*80)
    
    extractor = EntityExtractor()
    result = asyncio.run(extractor.extract_from_follow_up(
        message="2025-10-15",
        expected_entity=EntityType.DATE,
        context={}
    ))
    
    print(f"Message: '2025-10-15'")
    print(f"Result: {result}")
    assert result is not None
    assert result.normalized_value == "2025-10-15"
    assert result.confidence >= 0.9
    print("✅ Test passed: ISO date extracted correctly")


def test_extract_time_12hour():
    """Test: Extract time (12-hour format)"""
    print("\n" + "="*80)
    print("TEST 5: Extract Time (12-Hour Format)")
    print("="*80)
    
    extractor = EntityExtractor()
    result = asyncio.run(extractor.extract_from_follow_up(
        message="2 PM",
        expected_entity=EntityType.TIME,
        context={}
    ))
    
    print(f"Message: '2 PM'")
    print(f"Result: {result}")
    assert result is not None
    assert result.normalized_value == "14:00"
    assert result.confidence >= 0.9
    print("✅ Test passed: '2 PM' converted to 24-hour format: 14:00")


def test_extract_time_24hour():
    """Test: Extract time (24-hour format)"""
    print("\n" + "="*80)
    print("TEST 6: Extract Time (24-Hour Format)")
    print("="*80)
    
    extractor = EntityExtractor()
    result = asyncio.run(extractor.extract_from_follow_up(
        message="14:30",
        expected_entity=EntityType.TIME,
        context={}
    ))
    
    print(f"Message: '14:30'")
    print(f"Result: {result}")
    assert result is not None
    assert result.normalized_value == "14:30"
    assert result.confidence >= 0.9
    print("✅ Test passed: 24-hour time extracted correctly")


def test_extract_time_morning():
    """Test: Extract time (morning)"""
    print("\n" + "="*80)
    print("TEST 7: Extract Time (Morning)")
    print("="*80)
    
    extractor = EntityExtractor()
    result = asyncio.run(extractor.extract_from_follow_up(
        message="morning",
        expected_entity=EntityType.TIME,
        context={}
    ))
    
    print(f"Message: 'morning'")
    print(f"Result: {result}")
    assert result is not None
    assert result.normalized_value == "10:00"
    assert result.confidence >= 0.6
    print("✅ Test passed: 'morning' mapped to 10:00")


def test_extract_location_pincode():
    """Test: Extract location (pincode)"""
    print("\n" + "="*80)
    print("TEST 8: Extract Location (Pincode)")
    print("="*80)
    
    extractor = EntityExtractor()
    result = asyncio.run(extractor.extract_from_follow_up(
        message="400001",
        expected_entity=EntityType.LOCATION,
        context={}
    ))
    
    print(f"Message: '400001'")
    print(f"Result: {result}")
    assert result is not None
    assert result.normalized_value == "400001"
    assert result.confidence >= 0.9
    print("✅ Test passed: Pincode extracted correctly")


def test_extract_location_city():
    """Test: Extract location (city name)"""
    print("\n" + "="*80)
    print("TEST 9: Extract Location (City Name)")
    print("="*80)
    
    extractor = EntityExtractor()
    result = asyncio.run(extractor.extract_from_follow_up(
        message="Mumbai",
        expected_entity=EntityType.LOCATION,
        context={}
    ))
    
    print(f"Message: 'Mumbai'")
    print(f"Result: {result}")
    assert result is not None
    assert "Mumbai" in result.normalized_value
    assert result.confidence >= 0.8
    print("✅ Test passed: City name extracted correctly")


def test_extract_booking_id():
    """Test: Extract booking ID"""
    print("\n" + "="*80)
    print("TEST 10: Extract Booking ID")
    print("="*80)
    
    extractor = EntityExtractor()
    result = asyncio.run(extractor.extract_from_follow_up(
        message="BOOK-12345",
        expected_entity=EntityType.BOOKING_ID,
        context={}
    ))
    
    print(f"Message: 'BOOK-12345'")
    print(f"Result: {result}")
    assert result is not None
    assert "BOOK-12345" in result.normalized_value.upper()
    assert result.confidence >= 0.9
    print("✅ Test passed: Booking ID extracted correctly")


def test_extract_service_type():
    """Test: Extract service type"""
    print("\n" + "="*80)
    print("TEST 11: Extract Service Type")
    print("="*80)
    
    extractor = EntityExtractor()
    result = asyncio.run(extractor.extract_from_follow_up(
        message="AC repair",
        expected_entity=EntityType.SERVICE_TYPE,
        context={}
    ))
    
    print(f"Message: 'AC repair'")
    print(f"Result: {result}")
    assert result is not None
    assert result.normalized_value == "ac"
    assert result.confidence >= 0.8
    print("✅ Test passed: Service type extracted correctly")


def test_extraction_method_tracking():
    """Test: Extraction method tracking"""
    print("\n" + "="*80)
    print("TEST 12: Extraction Method Tracking")
    print("="*80)
    
    extractor = EntityExtractor()
    
    # Pattern match
    result1 = asyncio.run(extractor.extract_from_follow_up(
        message="2025-10-15",
        expected_entity=EntityType.DATE,
        context={}
    ))
    
    # Heuristic
    result2 = asyncio.run(extractor.extract_from_follow_up(
        message="morning",
        expected_entity=EntityType.TIME,
        context={}
    ))
    
    print(f"Date extraction method: {result1.extraction_method}")
    print(f"Time extraction method: {result2.extraction_method}")
    
    assert result1.extraction_method == "pattern"
    assert result2.extraction_method == "heuristic"
    print("✅ Test passed: Extraction methods tracked correctly")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("ENTITY EXTRACTOR SERVICE - TEST SUITE")
    print("="*80)
    
    tests = [
        test_extract_confirmation_yes,
        test_extract_confirmation_no,
        test_extract_date_tomorrow,
        test_extract_date_iso_format,
        test_extract_time_12hour,
        test_extract_time_24hour,
        test_extract_time_morning,
        test_extract_location_pincode,
        test_extract_location_city,
        test_extract_booking_id,
        test_extract_service_type,
        test_extraction_method_tracking,
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

