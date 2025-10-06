"""
Migrate pincode data from JSON columns to relational tables
This script:
1. Extracts unique pincodes from addresses table
2. Populates pincodes master table
3. Migrates rate_cards.available_pincodes JSON to rate_card_pincodes table
4. Migrates providers.service_pincodes JSON to provider_pincodes table
"""

import sys
import os
from pathlib import Path
import json

# Add parent directory to path
convergeai_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(convergeai_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)

print("="*80)
print("MIGRATING PINCODE DATA TO RELATIONAL TABLES")
print("="*80)

session = Session()

try:
    # Step 1: Extract unique pincodes from addresses and populate pincodes table
    print("\n1. Extracting unique pincodes from addresses...")
    result = session.execute(text("""
        SELECT DISTINCT pincode, city, state
        FROM addresses
        ORDER BY city, pincode
    """))
    
    unique_pincodes = []
    for row in result:
        unique_pincodes.append({
            'pincode': row[0],
            'city': row[1],
            'state': row[2]
        })
    
    print(f"   Found {len(unique_pincodes)} unique pincodes")
    
    # Insert into pincodes table
    print("\n2. Populating pincodes master table...")
    for pincode_data in unique_pincodes:
        session.execute(text("""
            INSERT IGNORE INTO pincodes (pincode, city, state, is_serviceable)
            VALUES (:pincode, :city, :state, TRUE)
        """), pincode_data)
    
    session.commit()
    print(f"   ✓ Inserted {len(unique_pincodes)} pincodes")
    
    # Step 2: Migrate rate_cards.available_pincodes to rate_card_pincodes
    print("\n3. Migrating rate_cards.available_pincodes to rate_card_pincodes...")
    result = session.execute(text("""
        SELECT id, available_pincodes
        FROM rate_cards
        WHERE available_pincodes IS NOT NULL
    """))
    
    rate_card_count = 0
    pincode_link_count = 0
    
    for row in result:
        rate_card_id = row[0]
        available_pincodes = json.loads(row[1]) if row[1] else []
        
        for pincode in available_pincodes:
            try:
                session.execute(text("""
                    INSERT IGNORE INTO rate_card_pincodes (rate_card_id, pincode_id)
                    SELECT :rate_card_id, id
                    FROM pincodes
                    WHERE pincode = :pincode
                """), {'rate_card_id': rate_card_id, 'pincode': pincode})
                pincode_link_count += 1
            except Exception as e:
                print(f"   Warning: Could not link rate_card {rate_card_id} to pincode {pincode}: {e}")
        
        rate_card_count += 1
    
    session.commit()
    print(f"   ✓ Migrated {rate_card_count} rate cards with {pincode_link_count} pincode links")
    
    # Step 3: Migrate providers.service_pincodes to provider_pincodes
    print("\n4. Migrating providers.service_pincodes to provider_pincodes...")
    result = session.execute(text("""
        SELECT id, service_pincodes
        FROM providers
        WHERE service_pincodes IS NOT NULL
    """))
    
    provider_count = 0
    pincode_link_count = 0
    
    for row in result:
        provider_id = row[0]
        service_pincodes = json.loads(row[1]) if row[1] else []
        
        for pincode in service_pincodes:
            try:
                session.execute(text("""
                    INSERT IGNORE INTO provider_pincodes (provider_id, pincode_id)
                    SELECT :provider_id, id
                    FROM pincodes
                    WHERE pincode = :pincode
                """), {'provider_id': provider_id, 'pincode': pincode})
                pincode_link_count += 1
            except Exception as e:
                print(f"   Warning: Could not link provider {provider_id} to pincode {pincode}: {e}")
        
        provider_count += 1
    
    session.commit()
    print(f"   ✓ Migrated {provider_count} providers with {pincode_link_count} pincode links")
    
    # Step 4: Verify migration
    print("\n5. Verifying migration...")
    
    # Count pincodes
    result = session.execute(text("SELECT COUNT(*) FROM pincodes"))
    pincode_count = result.scalar()
    print(f"   Total pincodes in master table: {pincode_count}")
    
    # Count rate_card_pincodes
    result = session.execute(text("SELECT COUNT(*) FROM rate_card_pincodes"))
    rcp_count = result.scalar()
    print(f"   Total rate_card_pincode links: {rcp_count}")
    
    # Count provider_pincodes
    result = session.execute(text("SELECT COUNT(*) FROM provider_pincodes"))
    pp_count = result.scalar()
    print(f"   Total provider_pincode links: {pp_count}")
    
    # Sample queries
    print("\n6. Sample queries:")
    print("\n   Rate cards available in pincode 400001:")
    result = session.execute(text("""
        SELECT rc.id, rc.name
        FROM rate_cards rc
        JOIN rate_card_pincodes rcp ON rc.id = rcp.rate_card_id
        JOIN pincodes p ON rcp.pincode_id = p.id
        WHERE p.pincode = '400001'
        LIMIT 5
    """))
    for row in result:
        print(f"      - RateCard {row[0]}: {row[1]}")
    
    print("\n   Providers serving pincode 400001:")
    result = session.execute(text("""
        SELECT pr.id, CONCAT(pr.first_name, ' ', pr.last_name) as name
        FROM providers pr
        JOIN provider_pincodes pp ON pr.id = pp.provider_id
        JOIN pincodes p ON pp.pincode_id = p.id
        WHERE p.pincode = '400001'
        LIMIT 5
    """))
    for row in result:
        print(f"      - Provider {row[0]}: {row[1]}")
    
    print("\n" + "="*80)
    print("MIGRATION COMPLETED SUCCESSFULLY!")
    print("="*80)
    print("\nNext steps:")
    print("1. Test the new queries in your application")
    print("2. Once verified, you can drop the JSON columns:")
    print("   - ALTER TABLE rate_cards DROP COLUMN available_pincodes;")
    print("   - ALTER TABLE providers DROP COLUMN service_pincodes;")
    
except Exception as e:
    session.rollback()
    print(f"\n✗ Error during migration: {e}")
    import traceback
    traceback.print_exc()
finally:
    session.close()

