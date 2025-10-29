#!/usr/bin/env python3
"""
Debug script to test entity validation for subcategory selection
"""
import asyncio
import sys
import os
import logging

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from src.services.entity_validator import EntityValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_service_validation():
    """Test service validation for subcategory selection"""
    logger.info("=== SERVICE VALIDATION DEBUG ===")
    
    try:
        # Create EntityValidator
        validator = EntityValidator()
        
        # Test services that should require subcategory selection
        test_services = [
            "pest_control",
            "painting", 
            "ac",  # Should NOT require subcategory
            "cleaning"  # Should NOT require subcategory
        ]
        
        for service in test_services:
            logger.info(f"\n--- Testing service: '{service}' ---")
            
            # Test service validation
            result = await validator._validate_service_type(service)
            
            logger.info(f"Validation result:")
            logger.info(f"   - is_valid: {result.is_valid}")
            logger.info(f"   - error_message: {result.error_message}")
            logger.info(f"   - suggestions: {result.suggestions}")
            
            if result.metadata:
                logger.info(f"   - metadata: {result.metadata}")
                if result.metadata.get('requires_subcategory_selection'):
                    logger.info(f"   ✅ REQUIRES SUBCATEGORY SELECTION")
                    subcategories = result.metadata.get('available_subcategories', [])
                    logger.info(f"   - Available subcategories: {len(subcategories)}")
                    for i, subcat in enumerate(subcategories, 1):
                        name = subcat.get('name', 'Unknown')
                        rate_cards = subcat.get('rate_cards', [])
                        logger.info(f"     {i}. {name} ({len(rate_cards)} rate cards)")
                else:
                    logger.info(f"   ✅ NO SUBCATEGORY REQUIRED")
            else:
                logger.info(f"   ✅ NO SUBCATEGORY REQUIRED")
        
        logger.info("\n=== TEST COMPLETE ===")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_service_validation())
