#!/usr/bin/env python3
"""
Test script to check if subcategory validation is working correctly
"""
import asyncio
import sys
import os
import logging

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_subcategory_validation():
    """Test if services requiring subcategory selection return is_valid=False"""
    logger.info("=== SUBCATEGORY VALIDATION TEST ===")
    
    try:
        # Import after setting up path
        from src.services.entity_validator import EntityValidator
        from src.core.database import get_db
        
        # Get database session
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            # Create EntityValidator with database
            validator = EntityValidator(db)
            
            # Test services that should require subcategory selection
            test_cases = [
                ("pest_control", True),  # Should require subcategory
                ("painting", True),      # Should require subcategory  
                ("ac", False),          # Should NOT require subcategory
                ("cleaning", False)     # Should NOT require subcategory
            ]
            
            for service, should_require_subcategory in test_cases:
                logger.info(f"\n--- Testing service: '{service}' ---")
                logger.info(f"Expected to require subcategory: {should_require_subcategory}")
                
                # Test service validation
                result = await validator.validate_entity(
                    entity_type="service_type",
                    entity_value=service,
                    context={
                        "session_id": "test_session",
                        "user_id": 123,
                        "collected_entities": {}
                    }
                )
                
                logger.info(f"Validation result:")
                logger.info(f"   - is_valid: {result.is_valid}")
                logger.info(f"   - error_message: {result.error_message}")
                logger.info(f"   - suggestions: {result.suggestions}")
                
                # Check if result matches expectation
                if should_require_subcategory:
                    if not result.is_valid and result.metadata and result.metadata.get('requires_subcategory_selection'):
                        logger.info(f"   ✅ CORRECT: Service requires subcategory selection")
                        subcategories = result.metadata.get('available_subcategories', [])
                        logger.info(f"   - Available subcategories: {len(subcategories)}")
                        for i, subcat in enumerate(subcategories, 1):
                            name = subcat.get('name', 'Unknown')
                            rate_cards = subcat.get('rate_cards', [])
                            logger.info(f"     {i}. {name} ({len(rate_cards)} rate cards)")
                    else:
                        logger.error(f"   ❌ INCORRECT: Service should require subcategory but doesn't")
                        logger.error(f"       is_valid={result.is_valid}, metadata={result.metadata}")
                else:
                    if result.is_valid:
                        logger.info(f"   ✅ CORRECT: Service does not require subcategory")
                        logger.info(f"   - normalized_value: {result.normalized_value}")
                    else:
                        logger.error(f"   ❌ INCORRECT: Service should be valid but isn't")
                        logger.error(f"       error_message={result.error_message}")
            
            logger.info("\n=== TEST COMPLETE ===")
            
        finally:
            # Close database session
            if hasattr(db, 'close'):
                await db.close()
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_subcategory_validation())
