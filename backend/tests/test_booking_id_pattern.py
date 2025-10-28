"""Test order ID pattern matching"""
import re

# Test messages
test_messages = [
    "Cancel booking ORD12345678",
    "I want to cancel ORD12345678",
    "Please cancel my order number ORD12345678",
    "Cancel booking ORD123456",
    "I want to cancel ORDER12345",
]

# Updated patterns
order_id_patterns = [
    r"\bORD[A-Z0-9]{8}\b",  # ORD12345678 (ORD + 8 alphanumeric) - PRIMARY FORMAT
    r"\b(ORD)[-_]?([A-Z0-9]{6,8})\b",  # ORD123456, ORD-123456, ORD_123456
    r"\b(ORDER)[-_]?([A-Z0-9]{4,8})\b",  # ORDER12345, ORDER-12345
    r"#([A-Z0-9]{6,8})\b",  # #123456, #12345678
]

print("="*60)
print("ORDER ID PATTERN MATCHING TEST")
print("="*60)

for message in test_messages:
    print(f"\nMessage: {message}")
    found = False

    for pattern in order_id_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            order_id = match.group(0).upper()
            print(f"  ✅ FOUND: {order_id} (pattern: {pattern})")
            found = True
            break

    if not found:
        print(f"  ❌ NOT FOUND")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)

