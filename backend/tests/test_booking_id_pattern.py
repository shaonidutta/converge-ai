"""Test booking ID pattern matching"""
import re

# Test messages
test_messages = [
    "Cancel booking BK66A80A35",
    "I want to cancel BK66A80A35",
    "Please cancel my booking number BK66A80A35",
    "Cancel booking BK123456",
    "I want to cancel BOOK12345",
]

# Updated patterns
booking_id_patterns = [
    r"\bBK[A-Z0-9]{8}\b",  # BK66A80A35 (BK + 8 alphanumeric) - PRIMARY FORMAT
    r"\b(BK)[-_]?(\d{6})\b",  # BK123456, BK-123456, BK_123456
    r"\b(BOOK)[-_]?([A-Z0-9]{4,8})\b",  # BOOK12345, BOOK-12345
    r"\b(BKG)[-_]?([A-Z0-9]{4,8})\b",  # BKG12345, BKG-12345
    r"\b(ORD)[-_]?([A-Z0-9]{4,8})\b",  # ORD12345, ORD-12345
    r"#([A-Z0-9]{6,8})\b",  # #123456, #66A80A35
]

print("="*60)
print("BOOKING ID PATTERN MATCHING TEST")
print("="*60)

for message in test_messages:
    print(f"\nMessage: {message}")
    found = False
    
    for pattern in booking_id_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            booking_id = match.group(0).upper()
            print(f"  ✅ FOUND: {booking_id} (pattern: {pattern})")
            found = True
            break
    
    if not found:
        print(f"  ❌ NOT FOUND")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)

