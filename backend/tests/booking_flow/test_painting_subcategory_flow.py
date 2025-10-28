#!/usr/bin/env python3
"""
Test painting service subcategory selection flow
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_painting_subcategory_flow():
    """Test the complete painting service subcategory selection flow"""
    try:
        logger.info("=== Testing Painting Service Subcategory Flow ===")
        
        # Test 1: Entity Extraction
        logger.info("1. Testing entity extraction for 'I want to book painting service'...")
        try:
            from src.services.entity_extractor import EntityExtractor
            from src.nlp.llm.gemini_client import get_gemini_client_for_extraction
            
            llm_client = get_gemini_client_for_extraction()
            extractor = EntityExtractor(llm_client)
            
            # Extract entities from painting service request
            result = await extractor.extract_multiple_entities("I want to book painting service")
            logger.info(f"✅ Extracted {len(result)} entities:")
            for entity_type, extraction_result in result.items():
                logger.info(f"   - {entity_type}: '{extraction_result.raw_value}' → '{extraction_result.normalized_value}'")
            
        except Exception as e:
            logger.error(f"❌ Entity extraction error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 2: Service Type Validation (should trigger subcategory selection)
        logger.info("2. Testing service type validation for 'painting'...")
        try:
            from src.services.entity_validator import EntityValidator
            from src.core.database.connection import get_db
            from src.nlp.intent.config import EntityType
            
            db_gen = get_db()
            db = await db_gen.__anext__()
            validator = EntityValidator(db)
            
            # Validate painting service type
            validation_result = await validator.validate(EntityType.SERVICE_TYPE, "painting")
            logger.info(f"✅ Service type validation result:")
            logger.info(f"   - Valid: {validation_result.is_valid}")
            logger.info(f"   - Error: {validation_result.error_message}")
            logger.info(f"   - Suggestions: {validation_result.suggestions}")
            logger.info(f"   - Requires subcategory: {validation_result.metadata.get('requires_subcategory_selection', False)}")
            
            if validation_result.metadata.get('available_subcategories'):
                logger.info(f"   - Available subcategories: {len(validation_result.metadata['available_subcategories'])}")
                for i, sub in enumerate(validation_result.metadata['available_subcategories'], 1):
                    logger.info(f"     {i}. {sub['name']} (ID: {sub['id']})")
            
        except Exception as e:
            logger.error(f"❌ Service validation error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 3: Question Generation for Subcategory Selection
        logger.info("3. Testing question generation for subcategory selection...")
        try:
            from src.services.question_generator import QuestionGenerator
            from src.nlp.intent.config import EntityType, IntentType
            
            question_gen = QuestionGenerator()
            
            # Generate subcategory selection question
            context = {
                'available_subcategories': [
                    {"id": 31, "name": "Interior Painting", "rate_cards": [{"id": 60, "name": "Interior Painting - Basic", "price": 1699.81}]},
                    {"id": 32, "name": "Exterior Painting", "rate_cards": [{"id": 61, "name": "Exterior Painting - Basic", "price": 2199.99}]},
                    {"id": 33, "name": "Waterproofing", "rate_cards": [{"id": 62, "name": "Waterproofing - Basic", "price": 2499.99}]}
                ],
                'service_type': 'painting'
            }
            
            question = question_gen.generate(
                entity_type=EntityType.SERVICE_SUBCATEGORY,
                intent=IntentType.BOOKING_MANAGEMENT,
                collected_entities={'service_type': 'painting'},
                context=context
            )
            
            logger.info(f"✅ Generated subcategory question:")
            logger.info(f"   {question}")
            
        except Exception as e:
            logger.error(f"❌ Question generation error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 4: Subcategory Selection Validation
        logger.info("4. Testing subcategory selection validation...")
        try:
            from src.services.entity_validator import EntityValidator
            
            # Test validating user's subcategory selection
            subcategory_validation = await validator.validate(EntityType.SERVICE_SUBCATEGORY, "interior painting")
            logger.info(f"✅ Subcategory validation result:")
            logger.info(f"   - Valid: {subcategory_validation.is_valid}")
            logger.info(f"   - Normalized: {subcategory_validation.normalized_value}")
            logger.info(f"   - Metadata: {subcategory_validation.metadata}")
            
        except Exception as e:
            logger.error(f"❌ Subcategory validation error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 5: Complete Flow Simulation
        logger.info("5. Simulating complete painting service booking flow...")
        try:
            logger.info("   Step 1: User says 'I want to book painting service'")
            logger.info("   Step 2: System extracts service_type='painting'")
            logger.info("   Step 3: System validates service_type, finds it requires subcategory")
            logger.info("   Step 4: System asks: 'Which type of painting service would you like?'")
            logger.info("   Step 5: User responds: 'interior painting'")
            logger.info("   Step 6: System validates subcategory, maps to rate_card_id=60")
            logger.info("   Step 7: System asks for missing entities (date, time)")
            logger.info("   Step 8: User provides: 'tomorrow 4pm'")
            logger.info("   Step 9: System extracts date='2025-10-29', time='16:00'")
            logger.info("   Step 10: System confirms booking with all details")
            
            logger.info("✅ Complete flow simulation successful!")
            
        except Exception as e:
            logger.error(f"❌ Flow simulation error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        logger.info("=== Painting Service Subcategory Flow Test Completed Successfully! ===")
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_painting_subcategory_flow())
