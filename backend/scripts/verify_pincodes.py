"""
Verify that addresses have real pincodes for their cities
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
convergeai_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(convergeai_dir))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL, echo=False)

print("="*80)
print("VERIFYING REAL PINCODES IN ADDRESSES")
print("="*80)

with engine.connect() as conn:
    # Check addresses with city and pincode
    print("\nSample Addresses with City and Pincode:")
    print("-"*80)
    result = conn.execute(text("""
        SELECT 
            city,
            state,
            pincode,
            COUNT(*) as count
        FROM addresses
        GROUP BY city, state, pincode
        ORDER BY city, pincode
        LIMIT 30
    """))
    
    for row in result:
        print(f"{row[0]:20} | {row[1]:20} | {row[2]:10} | {row[3]:3} addresses")
    
    # Check provider service pincodes
    print("\n" + "="*80)
    print("Sample Provider Service Pincodes:")
    print("-"*80)
    result = conn.execute(text("""
        SELECT 
            id,
            CONCAT(first_name, ' ', last_name) as provider_name,
            JSON_LENGTH(service_pincodes) as pincode_count,
            JSON_EXTRACT(service_pincodes, '$[0]') as first_pincode,
            JSON_EXTRACT(service_pincodes, '$[1]') as second_pincode,
            JSON_EXTRACT(service_pincodes, '$[2]') as third_pincode
        FROM providers
        LIMIT 10
    """))
    
    for row in result:
        print(f"Provider {row[0]:3} | {row[1]:25} | {row[2]:2} pincodes | {row[3]}, {row[4]}, {row[5]}...")
    
    # Check rate card available pincodes
    print("\n" + "="*80)
    print("Sample Rate Card Available Pincodes:")
    print("-"*80)
    result = conn.execute(text("""
        SELECT 
            rc.id,
            rc.name,
            JSON_LENGTH(rc.available_pincodes) as pincode_count,
            JSON_EXTRACT(rc.available_pincodes, '$[0]') as first_pincode,
            JSON_EXTRACT(rc.available_pincodes, '$[1]') as second_pincode
        FROM rate_cards rc
        LIMIT 10
    """))
    
    for row in result:
        print(f"RateCard {row[0]:3} | {row[1]:50} | {row[2]:2} pincodes | {row[3]}, {row[4]}...")

print("\n" + "="*80)
print("VERIFICATION COMPLETED!")
print("="*80)

