#!/usr/bin/env python3
"""
Test EntityValidator with ServiceCategoryValidator
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

async def test_entity_validator():
    """Test EntityValidator with painting service"""
    try:
        logger.info("=== Testing EntityValidator with ServiceCategoryValidator ===")
        
        # Test 1: Import EntityValidator
        logger.info("1. Testing EntityValidator import...")
        try:
            from src.services.entity_validator import EntityValidator
            from src.core.database.connection import get_db
            
            logger.info("✅ EntityValidator imported successfully")
            
        except Exception as e:
            logger.error(f"❌ Import error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 2: Create EntityValidator
        logger.info("2. Creating EntityValidator...")
        try:
            db_gen = get_db()
            db = await db_gen.__anext__()
            
            validator = EntityValidator(db)
            logger.info("✅ EntityValidator created successfully")
            
        except Exception as e:
            logger.error(f"❌ EntityValidator creation error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 3: Test service type validation
        logger.info("3. Testing service type validation...")
        try:
            from src.nlp.intent.config import EntityType
            
            # Test with timeout
            result = await asyncio.wait_for(
                validator.validate(EntityType.SERVICE_TYPE, "painting"),
                timeout=15.0
            )
            
            logger.info(f"✅ Validation result:")
            logger.info(f"   - Valid: {result.is_valid}")
            logger.info(f"   - Error: {result.error_message}")
            logger.info(f"   - Suggestions: {result.suggestions}")
            logger.info(f"   - Metadata: {result.metadata}")
            
        except asyncio.TimeoutError:
            logger.error("❌ EntityValidator.validate() timed out after 15 seconds")
            return
        except Exception as e:
            logger.error(f"❌ Validation error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        logger.info("=== EntityValidator test completed successfully! ===")
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_entity_validator())
