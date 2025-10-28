#!/usr/bin/env python3
"""
Test script for the complete booking flow with service subcategory selection
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_service_category_validator():
    """Test the ServiceCategoryValidator"""
    print("=" * 80)
    print("TESTING SERVICE CATEGORY VALIDATOR")
    print("=" * 80)
    
    try:
        from src.services.service_category_validator import ServiceCategoryValidator
        from src.core.database.session import get_db_session
        
        async with get_db_session() as db:
            validator = ServiceCategoryValidator(db)
            
            # Test 1: Painting service (should require subcategory selection)
            print("\n1. Testing 'painting' service type:")
            result = await validator.validate_service_type("painting")
            print(f"   Valid: {result.is_valid}")
            print(f"   Requires subcategory: {result.requires_subcategory_selection}")
            if result.available_subcategories:
                print(f"   Available subcategories: {len(result.available_subcategories)}")
                for i, sub in enumerate(result.available_subcategories[:3], 1):
                    print(f"     {i}. {sub['name']} - {len(sub['rate_cards'])} options")
            
            # Test 2: Plumbing service (check if single or multiple options)
            print("\n2. Testing 'plumbing' service type:")
            result = await validator.validate_service_type("plumbing")
            print(f"   Valid: {result.is_valid}")
            print(f"   Requires subcategory: {result.requires_subcategory_selection}")
            if result.default_rate_card_id:
                print(f"   Default rate card ID: {result.default_rate_card_id}")
            
            # Test 3: Invalid service type
            print("\n3. Testing 'invalid_service' service type:")
            result = await validator.validate_service_type("invalid_service")
            print(f"   Valid: {result.is_valid}")
            print(f"   Error: {result.error_message}")
            
            # Test 4: Subcategory selection for painting
            if result.is_valid and result.requires_subcategory_selection:
                print("\n4. Testing subcategory selection for painting:")
                sub_result = await validator.validate_subcategory_selection("painting", "interior painting")
                print(f"   Valid: {sub_result.is_valid}")
                if sub_result.is_valid:
                    print(f"   Rate card ID: {sub_result.default_rate_card_id}")
                else:
                    print(f"   Error: {sub_result.error_message}")
        
        print("\n✅ ServiceCategoryValidator tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ ServiceCategoryValidator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_entity_extractor():
    """Test the EntityExtractor combined date-time extraction"""
    print("\n" + "=" * 80)
    print("TESTING ENTITY EXTRACTOR - COMBINED DATE-TIME")
    print("=" * 80)
    
    try:
        from src.services.entity_extractor import EntityExtractor
        from src.nlp.intent.config import EntityType
        
        extractor = EntityExtractor()
        
        # Test combined date-time patterns
        test_cases = [
            "tomorrow 4pm",
            "today at 3pm",
            "next Monday 2:30pm",
            "31st October at 5pm"
        ]
        
        for i, test_message in enumerate(test_cases, 1):
            print(f"\n{i}. Testing: '{test_message}'")
            
            # Test multiple entity extraction
            results = await extractor.extract_multiple_entities(
                message=test_message,
                expected_entities=[EntityType.DATE, EntityType.TIME],
                context={}
            )
            
            if results:
                print(f"   Found {len(results)} entities:")
                for entity_type, result in results.items():
                    print(f"     {entity_type}: '{result.entity_value}' → '{result.normalized_value}'")
            else:
                print("   No entities extracted")
        
        print("\n✅ EntityExtractor tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ EntityExtractor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_question_generator():
    """Test the QuestionGenerator for service subcategory questions"""
    print("\n" + "=" * 80)
    print("TESTING QUESTION GENERATOR - SERVICE SUBCATEGORY")
    print("=" * 80)
    
    try:
        from src.services.question_generator import QuestionGenerator
        from src.nlp.intent.config import EntityType, IntentType
        
        generator = QuestionGenerator()
        
        # Mock available subcategories data
        mock_subcategories = [
            {
                "id": 31,
                "name": "Interior Painting",
                "description": "Interior wall painting",
                "rate_cards": [
                    {"id": 60, "name": "Interior Painting - Basic", "price": 1699.81, "description": "Basic interior painting"}
                ]
            },
            {
                "id": 32,
                "name": "Exterior Painting", 
                "description": "Exterior wall painting",
                "rate_cards": [
                    {"id": 61, "name": "Exterior Painting - Basic", "price": 2199.99, "description": "Basic exterior painting"}
                ]
            }
        ]
        
        # Test service subcategory question generation
        print("\n1. Testing service subcategory question:")
        context = {
            "available_subcategories": mock_subcategories,
            "service_type": "painting"
        }
        
        question = generator.generate(
            entity_type=EntityType.SERVICE_SUBCATEGORY,
            intent=IntentType.BOOKING_MANAGEMENT,
            collected_entities={"service_type": "painting"},
            context=context
        )
        
        print(f"Generated question:\n{question}")
        
        print("\n✅ QuestionGenerator tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ QuestionGenerator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🚀 STARTING BOOKING FLOW TESTS")
    print("=" * 80)
    
    results = []
    
    # Test 1: Service Category Validator
    results.append(await test_service_category_validator())
    
    # Test 2: Entity Extractor
    results.append(await test_entity_extractor())
    
    # Test 3: Question Generator
    results.append(await test_question_generator())
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The booking flow should work correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
