"""
Test conversational prefix cleaning
"""
from dotenv import load_dotenv
load_dotenv('backend/.env')

import sys
sys.path.insert(0, 'backend')

from src.services.entity_extractor import EntityExtractor

# Create extractor
extractor = EntityExtractor()

# Test cleaning
test_cases = [
    "i want to book kitchen cleaning",
    "book kitchen cleaning",
    "kitchen cleaning",
    "i want to book cleaning",
    "cleaning"
]

print("\n=== Testing Conversational Prefix Cleaning ===\n")

for test_input in test_cases:
    cleaned = extractor._clean_conversational_prefixes(test_input)
    print(f"Input:   '{test_input}'")
    print(f"Cleaned: '{cleaned}'")
    print()

