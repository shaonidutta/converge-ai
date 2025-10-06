"""
Script to list all tables in eassy databases
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


def list_tables_in_database(database_name):
    """
    List all tables in a specific database
    """
    connection = None
    try:
        # Connect to MySQL server
        print(f"\nDatabase: {database_name}")
        print("="*60)
        connection = pymysql.connect(**DB_CONFIG, database=database_name)
        
        with connection.cursor() as cursor:
            # List all tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            table_key = f'Tables_in_{database_name}'
            table_names = [table[table_key] for table in tables]
            
            # Filter tables that might contain category/service data
            relevant_keywords = ['category', 'categor', 'service', 'sub']
            relevant_tables = [t for t in table_names if any(keyword in t.lower() for keyword in relevant_keywords)]
            
            print(f"Total tables: {len(tables)}")
            
            if relevant_tables:
                print(f"\nTables with category/service keywords ({len(relevant_tables)}):")
                for table in sorted(relevant_tables):
                    print(f"  - {table}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    # Check eassy databases
    eassy_databases = ['eassydb', 'eassy_new', 'eassy_new_backup']
    
    print("Listing tables in eassy databases...")
    print("="*60)
    
    for db_name in eassy_databases:
        list_tables_in_database(db_name)

