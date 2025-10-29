#!/usr/bin/env python3
"""
Test the validation logic directly without database
"""
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_validation_logic():
    """Test the hardcoded validation logic for subcategory selection"""
    logger.info("=== VALIDATION LOGIC TEST ===")
    
    # This is the hardcoded logic from entity_validator.py
    services_with_subcategories = {
        "painting": {
            "subcategories": [
                {"id": 31, "name": "Interior Painting", "rate_cards": [{"id": 60, "name": "Interior Painting - Basic", "price": 1699.81}]},
                {"id": 32, "name": "Exterior Painting", "rate_cards": [{"id": 61, "name": "Exterior Painting - Basic", "price": 2199.99}]},
                {"id": 33, "name": "Waterproofing", "rate_cards": [{"id": 62, "name": "Waterproofing - Basic", "price": 2499.99}]}
            ],
            "suggestions": ["interior painting", "exterior painting", "waterproofing"]
        },
        "pest_control": {
            "subcategories": [
                {"id": 34, "name": "General Pest Control", "rate_cards": [
                    {"id": 63, "name": "General Pest Control - Basic", "price": 2054.35},
                    {"id": 64, "name": "General Pest Control - Standard", "price": 3815.94}
                ]}
            ],
            "suggestions": ["general pest control basic", "general pest control standard"]
        }
    }
    
    # Service normalizations from entity_validator.py
    service_normalizations = {
        "pest": "pest_control",
        "general pest control": "pest_control",
        "pest control service": "pest_control",
        "paint": "painting",
        "painter": "painting",
        "wall painting": "painting",
        "interior painting": "painting",
        "exterior painting": "painting",
        "waterproofing": "painting"
    }
    
    # Test cases
    test_cases = [
        ("pest_control", True),
        ("pest", True),  # Should normalize to pest_control
        ("painting", True),
        ("paint", True),  # Should normalize to painting
        ("ac", False),
        ("cleaning", False)
    ]
    
    for service_input, should_require_subcategory in test_cases:
        logger.info(f"\n--- Testing service: '{service_input}' ---")
        
        # Apply normalization
        normalized_service = service_normalizations.get(service_input.lower(), service_input.lower())
        logger.info(f"Normalized to: '{normalized_service}'")
        
        # Check if service requires subcategory selection
        requires_subcategory = normalized_service in services_with_subcategories
        
        logger.info(f"Expected to require subcategory: {should_require_subcategory}")
        logger.info(f"Actually requires subcategory: {requires_subcategory}")
        
        if should_require_subcategory == requires_subcategory:
            logger.info(f"✅ CORRECT")
            if requires_subcategory:
                service_data = services_with_subcategories[normalized_service]
                subcategories = service_data["subcategories"]
                suggestions = service_data["suggestions"]
                logger.info(f"   - Available subcategories: {len(subcategories)}")
                logger.info(f"   - Suggestions: {suggestions}")
                for i, subcat in enumerate(subcategories, 1):
                    name = subcat.get('name', 'Unknown')
                    rate_cards = subcat.get('rate_cards', [])
                    logger.info(f"     {i}. {name} ({len(rate_cards)} rate cards)")
                    for j, rate_card in enumerate(rate_cards, 1):
                        rc_name = rate_card.get('name', 'Unknown')
                        rc_price = rate_card.get('price', 0)
                        logger.info(f"        {j}. {rc_name} - ₹{rc_price}")
        else:
            logger.error(f"❌ INCORRECT")
    
    logger.info("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_validation_logic()
