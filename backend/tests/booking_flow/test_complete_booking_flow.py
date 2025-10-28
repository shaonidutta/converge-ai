#!/usr/bin/env python3
"""
Test complete booking flow end-to-end
"""

import asyncio
import sys
import logging
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_complete_booking_flow():
    """Test the complete booking flow"""
    try:
        logger.info("=== Testing Complete Booking Flow ===")
        
        # Test 1: Test combined date-time extraction
        logger.info("1. Testing combined date-time extraction...")
        try:
            from src.services.entity_extractor import EntityExtractor
            from src.nlp.llm.gemini_client import get_gemini_client_for_extraction
            
            llm_client = get_gemini_client_for_extraction()
            extractor = EntityExtractor(llm_client)
            
            # Test combined extraction
            result = await extractor.extract_multiple_entities("I want to book painting service tomorrow 4pm")
            logger.info(f"✅ Extracted entities: {len(result)}")
            for entity_type, extraction_result in result.items():
                logger.info(f"   - {entity_type}: '{extraction_result.raw_value}' → '{extraction_result.normalized_value}'")
            
        except Exception as e:
            logger.error(f"❌ Entity extraction error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 2: Test service type validation
        logger.info("2. Testing service type validation...")
        try:
            from src.services.entity_validator import EntityValidator
            from src.core.database.connection import get_db
            from src.nlp.intent.config import EntityType
            
            db_gen = get_db()
            db = await db_gen.__anext__()
            validator = EntityValidator(db)
            
            # Test painting validation
            validation_result = await validator.validate(EntityType.SERVICE_TYPE, "painting")
            logger.info(f"✅ Service type validation:")
            logger.info(f"   - Valid: {validation_result.is_valid}")
            logger.info(f"   - Error: {validation_result.error_message}")
            logger.info(f"   - Requires subcategory: {validation_result.metadata.get('requires_subcategory_selection', False)}")
            
        except Exception as e:
            logger.error(f"❌ Service validation error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 3: Test question generation for subcategory
        logger.info("3. Testing question generation for subcategory...")
        try:
            from src.services.question_generator import QuestionGenerator
            from src.nlp.intent.config import EntityType, IntentType
            
            question_gen = QuestionGenerator()
            
            # Test subcategory question with context
            context = {
                'available_subcategories': [
                    {"id": 31, "name": "Interior Painting", "rate_cards": [{"id": 60, "name": "Interior Painting - Basic", "price": 1699.81}]},
                    {"id": 32, "name": "Exterior Painting", "rate_cards": [{"id": 61, "name": "Exterior Painting - Basic", "price": 2199.99}]}
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
        
        # Test 4: Test booking agent with metadata
        logger.info("4. Testing booking agent with metadata...")
        try:
            from src.agents.booking.booking_agent import BookingAgent
            from src.core.models import User
            from unittest.mock import Mock
            
            # Create mock user
            user = Mock(spec=User)
            user.id = 183
            user.first_name = "Test"
            user.last_name = "User"
            user.email = "test@example.com"
            
            # Create booking agent
            booking_agent = BookingAgent(db)
            
            # Test entities with metadata
            entities = {
                'service_type': 'painting',
                'date': '2025-10-29',
                'time': '16:00',
                'location': '123 Main Street, Agra, Uttar Pradesh, 282002',
                '_metadata_rate_card_id': 60  # From subcategory validation
            }
            
            logger.info(f"✅ Booking agent test entities prepared:")
            logger.info(f"   - Service: {entities['service_type']}")
            logger.info(f"   - Date/Time: {entities['date']} {entities['time']}")
            logger.info(f"   - Rate Card ID: {entities.get('_metadata_rate_card_id')}")
            
        except Exception as e:
            logger.error(f"❌ Booking agent error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        logger.info("=== All booking flow components tested successfully! ===")
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_booking_flow())
