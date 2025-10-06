"""
Clear all data from database tables
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

print("Clearing all data from database tables...")

with engine.connect() as conn:
    # Disable foreign key checks
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    conn.commit()
    
    # Truncate all tables in reverse order of dependencies
    tables = [
        'complaint_updates',
        'complaints',
        'priority_queue',
        'conversations',
        'booking_items',
        'bookings',
        'providers',
        'addresses',
        'rate_cards',
        'subcategories',
        'categories',
        'users'
    ]
    
    for table in tables:
        try:
            conn.execute(text(f"TRUNCATE TABLE {table}"))
            print(f"  ✓ Cleared {table}")
        except Exception as e:
            print(f"  ✗ Error clearing {table}: {e}")
    
    conn.commit()
    
    # Re-enable foreign key checks
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    conn.commit()

print("\nAll data cleared successfully!")

