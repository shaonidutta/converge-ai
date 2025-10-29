#!/usr/bin/env python3
"""
Debug script to test entity extraction for pest control
"""
import asyncio
import sys
import os
import logging

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.entity_extractor import EntityExtractor
from src.schemas.intent import EntityType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_entity_extraction():
    """Test entity extraction for pest control"""
    logger.info("=== ENTITY EXTRACTION DEBUG ===")
    
    try:
        # Create EntityExtractor (without LLM for pattern testing)
        extractor = EntityExtractor(llm_client=None)
        
        # Test messages
        test_messages = [
            "I want to book pest control service tomorrow 3:30 pm",
            "pest control",
            "pest service",
            "general pest control",
            "pest control service"
        ]
        
        for message in test_messages:
            logger.info(f"\n--- Testing message: '{message}' ---")
            
            # Test pattern-based extraction for service_type
            result = extractor._extract_with_patterns(
                message=message,
                expected_entity=EntityType.SERVICE_TYPE,
                context={}
            )
            
            if result:
                logger.info(f"✅ Pattern extraction successful:")
                logger.info(f"   - Entity type: {result.entity_type}")
                logger.info(f"   - Entity value: {result.entity_value}")
                logger.info(f"   - Confidence: {result.confidence}")
                logger.info(f"   - Normalized: {result.normalized_value}")
                logger.info(f"   - Method: {result.extraction_method}")
            else:
                logger.info(f"❌ Pattern extraction failed")
                
            # Test multiple entity extraction
            logger.info(f"--- Testing multiple entity extraction ---")
            multiple_results = await extractor.extract_multiple_entities(message, context={})
            
            if multiple_results:
                logger.info(f"✅ Multiple extraction found {len(multiple_results)} entities:")
                for i, entity in enumerate(multiple_results, 1):
                    logger.info(f"   {i}. {entity.entity_type}: {entity.entity_value} (confidence: {entity.confidence})")
            else:
                logger.info(f"❌ Multiple extraction found no entities")
        
        logger.info("\n=== TEST COMPLETE ===")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_entity_extraction())
