#!/usr/bin/env python3
"""
Debug script to test ServiceCategoryValidator for pest control service
"""
import asyncio
import sys
import os
import logging

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.database import get_db
from src.services.service_category_validator import ServiceCategoryValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_pest_control_validation():
    """Test pest control service validation"""
    logger.info("=== PEST CONTROL SERVICE VALIDATION DEBUG ===")
    
    try:
        # Get database session
        db_gen = get_db()
        db = await anext(db_gen)

        logger.info("✅ Database connection successful")
        
        # Create ServiceCategoryValidator
        service_validator = ServiceCategoryValidator(db)
        
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
                result = await asyncio.wait_for(
                    service_validator.validate_service_type(service),
                    timeout=10.0
                )
                
                logger.info(f"✅ Validation successful for '{service}'")
                logger.info(f"   - Valid: {result.is_valid}")
                logger.info(f"   - Normalized: {result.normalized_service_type}")
                logger.info(f"   - Requires subcategory: {result.requires_subcategory_selection}")
                
                if result.requires_subcategory_selection and result.available_subcategories:
                    logger.info(f"   - Available subcategories ({len(result.available_subcategories)}):")
                    for i, sub in enumerate(result.available_subcategories[:5], 1):
                        rate_cards = sub.get('rate_cards', [])
                        if rate_cards:
                            price = rate_cards[0].get('price', 'N/A')
                            logger.info(f"     {i}. {sub['name']} - ₹{price}")
                        else:
                            logger.info(f"     {i}. {sub['name']} - No pricing")
                
                if result.default_rate_card_id:
                    logger.info(f"   - Default rate card ID: {result.default_rate_card_id}")
                
                if not result.is_valid:
                    logger.info(f"   - Error: {result.error_message}")
                    
            except asyncio.TimeoutError:
                logger.error(f"❌ Timeout for '{service}'")
            except Exception as e:
                logger.error(f"❌ Error for '{service}': {e}")
        
        # Close database session
        await anext(db_gen, None)
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_pest_control_validation())
