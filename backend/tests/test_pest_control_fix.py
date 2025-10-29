#!/usr/bin/env python3
"""
Test script to verify pest control service validation fixes
"""
import asyncio
import sys
import os
import logging

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.entity_validator import EntityValidator
from src.schemas.intent import EntityType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_pest_control_validation():
    """Test pest control service validation"""
    logger.info("=== PEST CONTROL VALIDATION TEST ===")
    
    try:
        # Create EntityValidator (without database for this test)
        validator = EntityValidator(db=None)
        
        # Test pest control variations
        test_services = [
            "pest control",
            "pest",
            "general pest control",
            "pest control service"
        ]
        
        for service in test_services:
            logger.info(f"\n--- Testing service: '{service}' ---")
            
            try:
                result = await validator._validate_service_type(service)
                
                logger.info(f"✅ Validation result for '{service}':")
                logger.info(f"   - Valid: {result.is_valid}")
                logger.info(f"   - Normalized: {result.normalized_value}")
                logger.info(f"   - Error message: {result.error_message}")
                logger.info(f"   - Suggestions: {result.suggestions}")
                
                if result.metadata:
                    logger.info(f"   - Requires subcategory: {result.metadata.get('requires_subcategory_selection', False)}")
                    if result.metadata.get('available_subcategories'):
                        logger.info(f"   - Available subcategories: {len(result.metadata['available_subcategories'])}")
                        for sub in result.metadata['available_subcategories']:
                            logger.info(f"     • {sub['name']}")
                            if sub.get('rate_cards'):
                                for card in sub['rate_cards']:
                                    logger.info(f"       - {card['name']}: ₹{card['price']}")
                    
            except Exception as e:
                logger.error(f"❌ Error for '{service}': {e}")
        
        logger.info("\n=== TEST COMPLETE ===")
        
    except Exception as e:
        logger.error(f"❌ Test setup failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_pest_control_validation())
