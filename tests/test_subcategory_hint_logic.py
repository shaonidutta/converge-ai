#!/usr/bin/env python3
"""Test subcategory hint logic"""

message_lower = "kitchen cleaning"

# Map subcategory keywords to their parent categories
subcategory_to_category = {
    "kitchen cleaning": ("cleaning", "Kitchen Cleaning"),
    "bathroom cleaning": ("cleaning", "Bathroom Cleaning"),
    "sofa cleaning": ("cleaning", "Sofa Cleaning"),
    "carpet cleaning": ("cleaning", "Carpet Cleaning"),
    "window cleaning": ("cleaning", "Window Cleaning"),
    "move-in cleaning": ("cleaning", "Move-in/Move-out Cleaning"),
    "move-out cleaning": ("cleaning", "Move-in/Move-out Cleaning"),
    "regular cleaning": ("cleaning", "Regular Cleaning"),
    "deep cleaning": ("cleaning", "Deep Cleaning")
}

print(f"Testing message: '{message_lower}'")
print()

for subcategory, (category, subcategory_name) in subcategory_to_category.items():
    if subcategory in message_lower:
        print(f"✅ MATCH FOUND!")
        print(f"  Subcategory keyword: '{subcategory}'")
        print(f"  Category: '{category}'")
        print(f"  Subcategory name: '{subcategory_name}'")
        break
else:
    print("❌ NO MATCH FOUND")

