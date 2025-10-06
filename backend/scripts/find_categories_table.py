"""
Script to find which database contains the categories table
"""

import pymysql

# Database connection details
DB_CONFIG = {
    'host': 'ls-d157091fb9608cc702c3b9a33dec25bca625f14b.cstb7bwkbg8x.ap-south-1.rds.amazonaws.com',
    'user': 'dbmasteruser',
    'password': 'R8AR9z^_y|AP3+jABss?GN8<!|ta4<,f',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# Databases to check
DATABASES_TO_CHECK = ['eassy_new', 'eassy_new_2', 'eassy_new_backup', 'eassydb']


def find_categories_table():
    """
    Find which database contains the categories table
    """
    connection = None
    try:
        # Connect to MySQL server
        print("Connecting to MySQL server...")
        connection = pymysql.connect(**DB_CONFIG)
        
        print("\nChecking databases for 'categories' table...")
        print("="*60)
        
        for db_name in DATABASES_TO_CHECK:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"USE {db_name}")
                    cursor.execute("SHOW TABLES LIKE 'categories'")
                    result = cursor.fetchone()
                    
                    if result:
                        print(f"\n✓ Found 'categories' table in: {db_name}")
                        
                        # Get table structure
                        cursor.execute("DESCRIBE categories")
                        columns = cursor.fetchall()
                        print(f"\n  Table structure:")
                        for col in columns:
                            print(f"    - {col['Field']}: {col['Type']}")
                        
                        # Get row count
                        cursor.execute("SELECT COUNT(*) as count FROM categories")
                        count = cursor.fetchone()
                        print(f"\n  Row count: {count['count']}")
                        
                        # Check for subcategories table
                        cursor.execute("SHOW TABLES LIKE 'subcategories'")
                        subcat_result = cursor.fetchone()
                        if subcat_result:
                            print(f"\n✓ Found 'subcategories' table in: {db_name}")
                            cursor.execute("SELECT COUNT(*) as count FROM subcategories")
                            subcat_count = cursor.fetchone()
                            print(f"  Row count: {subcat_count['count']}")
                        else:
                            print(f"\n✗ No 'subcategories' table in: {db_name}")
                        
                        print("="*60)
                    else:
                        print(f"✗ No 'categories' table in: {db_name}")
            except Exception as e:
                print(f"✗ Error checking {db_name}: {e}")
        
    except Exception as e:
        print(f"\nError: {e}")
        raise
    finally:
        if connection:
            connection.close()
            print("\nDatabase connection closed.")


if __name__ == "__main__":
    find_categories_table()

