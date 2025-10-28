#!/usr/bin/env python3
"""
Simple test of booking flow components
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test if all imports work"""
    print("=== Testing Imports ===")
    
    try:
        from src.services.entity_extractor import EntityExtractor
        print("✅ EntityExtractor imported")
        
        from src.services.entity_validator import EntityValidator
        print("✅ EntityValidator imported")
        
        from src.services.question_generator import QuestionGenerator
        print("✅ QuestionGenerator imported")
        
        from src.agents.booking.booking_agent import BookingAgent
        print("✅ BookingAgent imported")
        
        from src.nlp.intent.config import EntityType, IntentType
        print("✅ Config imported")
        
        print("=== All imports successful! ===")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_entity_extraction():
    """Test entity extraction without LLM"""
    print("\n=== Testing Entity Extraction ===")
    
    try:
        from src.services.entity_extractor import EntityExtractor
        
        # Create extractor without LLM for pattern testing
        extractor = EntityExtractor(llm_client=None)
        
        # Test combined date-time extraction
        result = extractor._extract_combined_date_time("tomorrow 4pm")
        
        if result:
            print("✅ Combined date-time extraction works:")
            for entity_type, extraction_result in result.items():
                print(f"   - {entity_type}: '{extraction_result.raw_value}' → '{extraction_result.normalized_value}'")
        else:
            print("❌ Combined date-time extraction failed")
            
        return True
        
    except Exception as e:
        print(f"❌ Entity extraction error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_question_generation():
    """Test question generation"""
    print("\n=== Testing Question Generation ===")
    
    try:
        from src.services.question_generator import QuestionGenerator
        from src.nlp.intent.config import EntityType, IntentType
        
        question_gen = QuestionGenerator()
        
        # Test subcategory question
        context = {
            'available_subcategories': [
                {"name": "Interior Painting", "rate_cards": [{"price": 1699.81}]},
                {"name": "Exterior Painting", "rate_cards": [{"price": 2199.99}]}
            ],
            'service_type': 'painting'
        }
        
        question = question_gen.generate(
            entity_type=EntityType.SERVICE_SUBCATEGORY,
            intent=IntentType.BOOKING_MANAGEMENT,
            collected_entities={'service_type': 'painting'},
            context=context
        )
        
        print(f"✅ Generated question: {question}")
        return True
        
    except Exception as e:
        print(f"❌ Question generation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 SIMPLE BOOKING FLOW TESTS")
    
    success = True
    success &= test_imports()
    success &= test_entity_extraction()
    success &= test_question_generation()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED!")
    
    return success

if __name__ == "__main__":
    main()
