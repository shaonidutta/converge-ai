"""
Script to extract categories and subcategories from easylife database
"""

import pymysql
import json
from datetime import datetime

# EasyLife database connection details
EASYLIFE_DB_CONFIG = {
    'host': 'ls-d157091fb9608cc702c3b9a33dec25bca625f14b.cstb7bwkbg8x.ap-south-1.rds.amazonaws.com',
    'user': 'dbmasteruser',
    'password': 'R8AR9z^_y|AP3+jABss?GN8<!|ta4<,f',
    'database': 'eassy_new_backup',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}


def extract_categories_and_subcategories():
    """
    Extract categories and subcategories from easylife database
    """
    connection = None
    try:
        # Connect to easylife database
        print("Connecting to easylife database...")
        connection = pymysql.connect(**EASYLIFE_DB_CONFIG)
        
        with connection.cursor() as cursor:
            # Extract categories
            print("\nExtracting categories...")
            cursor.execute("""
                SELECT
                    id,
                    name,
                    slug,
                    meta_description as description,
                    image,
                    weight as display_order,
                    active as is_active,
                    FROM_UNIXTIME(created_at) as created_at,
                    FROM_UNIXTIME(updated_at) as updated_at
                FROM eassy_categories
                WHERE deleted_at IS NULL
                ORDER BY weight, id
            """)
            categories = cursor.fetchall()
            print(f"Found {len(categories)} categories")

            # Extract subcategories
            print("\nExtracting subcategories...")
            cursor.execute("""
                SELECT
                    id,
                    category_id,
                    name,
                    slug,
                    description,
                    image,
                    weightage as display_order,
                    active as is_active,
                    FROM_UNIXTIME(created_at) as created_at,
                    FROM_UNIXTIME(updated_at) as updated_at
                FROM eassy_subcategories
                WHERE deleted_at IS NULL
                ORDER BY category_id, weightage, id
            """)
            subcategories = cursor.fetchall()
            print(f"Found {len(subcategories)} subcategories")
            
            # Convert datetime objects to strings for JSON serialization
            for cat in categories:
                if cat.get('created_at'):
                    cat['created_at'] = cat['created_at'].isoformat()
                if cat.get('updated_at'):
                    cat['updated_at'] = cat['updated_at'].isoformat()
            
            for subcat in subcategories:
                if subcat.get('created_at'):
                    subcat['created_at'] = subcat['created_at'].isoformat()
                if subcat.get('updated_at'):
                    subcat['updated_at'] = subcat['updated_at'].isoformat()
            
            # Save to JSON files
            print("\nSaving data to JSON files...")
            with open('backend/scripts/seed_data/categories.json', 'w', encoding='utf-8') as f:
                json.dump(categories, f, indent=2, ensure_ascii=False)
            print(f"Saved categories to backend/scripts/seed_data/categories.json")
            
            with open('backend/scripts/seed_data/subcategories.json', 'w', encoding='utf-8') as f:
                json.dump(subcategories, f, indent=2, ensure_ascii=False)
            print(f"Saved subcategories to backend/scripts/seed_data/subcategories.json")
            
            # Print summary
            print("\n" + "="*60)
            print("EXTRACTION SUMMARY")
            print("="*60)
            print(f"Total Categories: {len(categories)}")
            print(f"Total Subcategories: {len(subcategories)}")
            
            # Group subcategories by category
            subcat_by_cat = {}
            for subcat in subcategories:
                cat_id = subcat['category_id']
                if cat_id not in subcat_by_cat:
                    subcat_by_cat[cat_id] = []
                subcat_by_cat[cat_id].append(subcat)
            
            print("\nCategories with subcategory counts:")
            for cat in categories:
                cat_id = cat['id']
                subcat_count = len(subcat_by_cat.get(cat_id, []))
                print(f"  - {cat['name']} (ID: {cat_id}): {subcat_count} subcategories")
            
            print("="*60)
            print("\nData extraction completed successfully!")
            
            return categories, subcategories
            
    except Exception as e:
        print(f"\nError: {e}")
        raise
    finally:
        if connection:
            connection.close()
            print("\nDatabase connection closed.")


if __name__ == "__main__":
    # Create seed_data directory if it doesn't exist
    import os
    os.makedirs('backend/scripts/seed_data', exist_ok=True)
    
    # Extract data
    extract_categories_and_subcategories()

