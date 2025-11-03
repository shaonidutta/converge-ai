#!/usr/bin/env python
"""Test entity extraction for status filter"""

import sys
sys.path.insert(0, 'backend')

from src.nlp.intent.patterns import IntentPatterns

# Test messages
test_messages = [
    "show pending bookings",
    "give me list of my bookings",
    "show my pending bookings",
    "list pending bookings",
    "show cancelled bookings",
    "show completed bookings"
]

print("=" * 60)
print("Testing Entity Extraction")
print("=" * 60)

for message in test_messages:
    print(f"\nMessage: '{message}'")
    entities = IntentPatterns.extract_entities_from_patterns(message)
    print(f"Extracted entities: {entities}")
    print(f"  - Action: {entities.get('action', 'NOT FOUND')}")
    print(f"  - Status Filter: {entities.get('status_filter', 'NOT FOUND')}")

