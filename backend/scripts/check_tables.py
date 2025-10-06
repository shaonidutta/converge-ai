"""
Script to check tables in eassy databases
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


def check_tables_in_database(database_name):
    """
    Check tables in a specific database
    """
    connection = None
    try:
        # Connect to MySQL server
        print(f"\nChecking database: {database_name}")
        print("="*60)
        connection = pymysql.connect(**DB_CONFIG, database=database_name)
        
        with connection.cursor() as cursor:
            # List all tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            table_key = f'Tables_in_{database_name}'
            table_names = [table[table_key] for table in tables]
            
            # Check for categories and subcategories
            has_categories = 'categories' in table_names
            has_subcategories = 'subcategories' in table_names
            
            print(f"Total tables: {len(tables)}")
            print(f"Has 'categories' table: {has_categories}")
            print(f"Has 'subcategories' table: {has_subcategories}")
            
            if has_categories or has_subcategories:
                print("\nRelevant tables found:")
                if has_categories:
                    print("  - categories")
                if has_subcategories:
                    print("  - subcategories")
            
            return has_categories and has_subcategories
            
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    # Check eassy databases
    eassy_databases = ['eassy_new', 'eassy_new_2', 'eassy_new_backup', 'eassydb']
    
    print("Checking eassy databases for categories and subcategories tables...")
    print("="*60)
    
    found_database = None
    for db_name in eassy_databases:
        if check_tables_in_database(db_name):
            found_database = db_name
            print(f"\n✓ Found both tables in: {db_name}")
            break
    
    if found_database:
        print(f"\n{'='*60}")
        print(f"Use database: {found_database}")
        print("="*60)
    else:
        print("\n✗ Could not find both categories and subcategories tables in any eassy database")

