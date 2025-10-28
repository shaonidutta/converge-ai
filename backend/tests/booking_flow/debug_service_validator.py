#!/usr/bin/env python3
"""
Debug script for ServiceCategoryValidator
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

async def test_service_validator():
    """Test ServiceCategoryValidator step by step"""
    try:
        logger.info("=== Testing ServiceCategoryValidator ===")
        
        # Test 1: Import check
        logger.info("1. Testing imports...")
        try:
            from src.utils.entity_normalizer import normalize_service_type
            logger.info("✅ normalize_service_type imported successfully")
            
            # Test normalization
            result = normalize_service_type("painting")
            logger.info(f"✅ normalize_service_type('painting') = '{result}'")
            
        except Exception as e:
            logger.error(f"❌ Import error: {e}")
            return
        
        # Test 2: Database connection
        logger.info("2. Testing database connection...")
        try:
            from src.core.database.connection import get_db

            # Get database session using the dependency
            db_gen = get_db()
            db = await db_gen.__anext__()
            logger.info("✅ Database session created successfully")

            # Test 3: Simple query
            logger.info("3. Testing simple database query...")
            from sqlalchemy import select, text

            # Test basic connectivity
            result = await db.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            logger.info(f"✅ Basic query result: {test_value}")

            # Test 4: Category table query
            logger.info("4. Testing Category table query...")
            from src.core.models.category import Category

            category_result = await db.execute(
                select(Category.id, Category.name)
                .where(Category.is_active == True)
                .limit(5)
            )
            categories = category_result.all()
            logger.info(f"✅ Found {len(categories)} active categories")
            for cat_id, cat_name in categories:
                logger.info(f"   - {cat_name} (ID: {cat_id})")

            # Test 5: Painting category specific query
            logger.info("5. Testing painting category query...")
            from sqlalchemy import func

            painting_result = await db.execute(
                select(Category.id, Category.name)
                .where(
                    func.lower(Category.name).like("%paint%"),
                    Category.is_active == True
                )
            )
            painting_categories = painting_result.all()
            logger.info(f"✅ Found {len(painting_categories)} painting categories")
            for cat_id, cat_name in painting_categories:
                logger.info(f"   - {cat_name} (ID: {cat_id})")

        except Exception as e:
            logger.error(f"❌ Database error: {e}")
            import traceback
            traceback.print_exc()
            return

        # Test 6: ServiceCategoryValidator
        logger.info("6. Testing ServiceCategoryValidator...")
        try:
            from src.services.service_category_validator import ServiceCategoryValidator

            db_gen = get_db()
            db = await db_gen.__anext__()
            validator = ServiceCategoryValidator(db)
            logger.info("✅ ServiceCategoryValidator created successfully")

            # Test with timeout
            logger.info("7. Testing painting validation with timeout...")
            try:
                result = await asyncio.wait_for(
                    validator.validate_service_type("painting"),
                    timeout=10.0  # 10 second timeout
                )
                logger.info(f"✅ Validation result: valid={result.is_valid}, requires_subcategory={result.requires_subcategory_selection}")
                if result.available_subcategories:
                    logger.info(f"   Available subcategories: {len(result.available_subcategories)}")
                    for sub in result.available_subcategories[:3]:
                        logger.info(f"     - {sub.get('name', 'Unknown')}")

            except asyncio.TimeoutError:
                logger.error("❌ ServiceCategoryValidator.validate_service_type() timed out after 10 seconds")
                return

        except Exception as e:
            logger.error(f"❌ ServiceCategoryValidator error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        logger.info("=== All tests completed successfully! ===")
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_service_validator())
