#!/usr/bin/env python3
"""
Debug script to test pattern matcher for pest control
"""
import sys
import os
import logging

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.nlp.intent.patterns import IntentPatterns

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pattern_matcher():
    """Test pattern matcher for pest control"""
    logger.info("=== PATTERN MATCHER DEBUG ===")
    
    try:
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
            
            # Test entity extraction
            entities = IntentPatterns.extract_entities_from_patterns(message)
            
            if entities:
                logger.info(f"✅ Entities extracted:")
                for entity_type, entity_value in entities.items():
                    logger.info(f"   - {entity_type}: {entity_value}")
            else:
                logger.info(f"❌ No entities extracted")
        
        logger.info("\n=== TEST COMPLETE ===")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pattern_matcher()
