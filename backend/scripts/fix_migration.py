"""
Fix migration state - drop pincode tables if they exist
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
engine = create_engine(DATABASE_URL, echo=True)

print("="*80)
print("FIXING MIGRATION STATE")
print("="*80)

with engine.connect() as conn:
    # Drop pincode tables if they exist
    try:
        print("\nDropping provider_pincodes table...")
        conn.execute(text("DROP TABLE IF EXISTS provider_pincodes"))
        conn.commit()
        print("✓ Dropped provider_pincodes")
    except Exception as e:
        print(f"✗ Error dropping provider_pincodes: {e}")
    
    try:
        print("\nDropping rate_card_pincodes table...")
        conn.execute(text("DROP TABLE IF EXISTS rate_card_pincodes"))
        conn.commit()
        print("✓ Dropped rate_card_pincodes")
    except Exception as e:
        print(f"✗ Error dropping rate_card_pincodes: {e}")
    
    try:
        print("\nDropping pincodes table...")
        conn.execute(text("DROP TABLE IF EXISTS pincodes"))
        conn.commit()
        print("✓ Dropped pincodes")
    except Exception as e:
        print(f"✗ Error dropping pincodes: {e}")
    
    # Reset alembic version to previous migration
    try:
        print("\nResetting alembic version...")
        conn.execute(text("UPDATE alembic_version SET version_num = 'c69d77625ee9'"))
        conn.commit()
        print("✓ Reset alembic version to c69d77625ee9")
    except Exception as e:
        print(f"✗ Error resetting alembic version: {e}")

print("\n" + "="*80)
print("MIGRATION STATE FIXED!")
print("="*80)
print("\nNow run: alembic upgrade head")

