"""
Test pattern extraction for kitchen cleaning
"""
from dotenv import load_dotenv
load_dotenv('backend/.env')

import sys
sys.path.insert(0, 'backend')

from src.services.entity_extractor import EntityExtractor

# Create extractor
extractor = EntityExtractor()

# Test extraction
test_cases = [
    "kitchen cleaning",
    "i want to book kitchen cleaning",
    "cleaning"
]

print("\n=== Testing Pattern Extraction ===\n")

for test_input in test_cases:
    print(f"Input: '{test_input}'")
    
    # Clean the message
    cleaned = extractor._clean_conversational_prefixes(test_input)
    print(f"Cleaned: '{cleaned}'")
    
    # Extract service type
    result = extractor._extract_service_type(cleaned.lower())
    
    if result:
        print(f"  Extracted: {result.entity_value}")
        print(f"  Confidence: {result.confidence}")
        print(f"  Method: {result.extraction_method}")
        if result.metadata:
            print(f"  Metadata: {result.metadata}")
    else:
        print(f"  No match")
    print()

