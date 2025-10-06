"""
Verify seeded data in database
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
print("VERIFYING SEEDED DATA")
print("="*80)

with engine.connect() as conn:
    # Check all tables
    tables = [
        'users',
        'categories',
        'subcategories',
        'rate_cards',
        'addresses',
        'providers',
        'bookings',
        'booking_items',
        'conversations',
        'priority_queue',
        'complaints',
        'complaint_updates'
    ]
    
    print("\nTable Record Counts:")
    print("-"*80)
    for table in tables:
        result = conn.execute(text(f"SELECT COUNT(*) as count FROM {table}"))
        count = result.fetchone()[0]
        print(f"{table:25} {count:>10} records")
    
    # Check categories with subcategory counts
    print("\n" + "="*80)
    print("Categories with Subcategory Counts:")
    print("-"*80)
    result = conn.execute(text("""
        SELECT 
            c.id,
            c.name,
            c.slug,
            COUNT(s.id) as subcategory_count
        FROM categories c
        LEFT JOIN subcategories s ON c.id = s.category_id
        GROUP BY c.id, c.name, c.slug
        ORDER BY c.display_order
    """))
    
    for row in result:
        print(f"{row[0]:3} | {row[1]:30} | {row[2]:35} | {row[3]:2} subcategories")
    
    # Check sample subcategories for first category
    print("\n" + "="*80)
    print("Sample Subcategories (Home Cleaning):")
    print("-"*80)
    result = conn.execute(text("""
        SELECT 
            s.id,
            s.name,
            s.slug,
            c.name as category_name
        FROM subcategories s
        JOIN categories c ON s.category_id = c.id
        WHERE c.slug = 'home-cleaning'
        ORDER BY s.display_order
        LIMIT 10
    """))
    
    for row in result:
        print(f"{row[0]:3} | {row[1]:30} | {row[2]:50} | Category: {row[3]}")
    
    # Check user types
    print("\n" + "="*80)
    print("User Statistics:")
    print("-"*80)
    result = conn.execute(text("""
        SELECT 
            CASE 
                WHEN email LIKE '%@convergeai.com' THEN 'Ops Staff'
                ELSE 'Customer'
            END as user_type,
            COUNT(*) as count
        FROM users
        GROUP BY user_type
    """))
    
    for row in result:
        print(f"{row[0]:15} {row[1]:>10} users")
    
    # Check booking statistics
    print("\n" + "="*80)
    print("Booking Statistics:")
    print("-"*80)
    result = conn.execute(text("""
        SELECT 
            status,
            COUNT(*) as count,
            SUM(total) as total_amount
        FROM bookings
        GROUP BY status
    """))
    
    for row in result:
        print(f"{row[0]:15} {row[1]:>10} bookings | Total: ₹{float(row[2]):,.2f}")
    
    # Check provider statistics
    print("\n" + "="*80)
    print("Provider Statistics:")
    print("-"*80)
    result = conn.execute(text("""
        SELECT 
            COUNT(*) as total_providers,
            SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_providers,
            SUM(CASE WHEN is_verified = 1 THEN 1 ELSE 0 END) as verified_providers,
            AVG(avg_rating) as avg_rating
        FROM providers
    """))
    
    row = result.fetchone()
    print(f"Total Providers:    {row[0]:>10}")
    print(f"Active Providers:   {row[1]:>10}")
    print(f"Verified Providers: {row[2]:>10}")
    print(f"Average Rating:     {float(row[3]):>10.2f}")
    
    # Check complaint statistics
    print("\n" + "="*80)
    print("Complaint Statistics:")
    print("-"*80)
    result = conn.execute(text("""
        SELECT 
            status,
            COUNT(*) as count
        FROM complaints
        GROUP BY status
    """))
    
    for row in result:
        print(f"{row[0]:15} {row[1]:>10} complaints")

print("\n" + "="*80)
print("VERIFICATION COMPLETED!")
print("="*80)

