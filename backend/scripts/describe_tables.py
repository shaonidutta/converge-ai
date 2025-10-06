"""
Script to describe table structures
"""

import pymysql

# Database connection details
DB_CONFIG = {
    'host': 'ls-d157091fb9608cc702c3b9a33dec25bca625f14b.cstb7bwkbg8x.ap-south-1.rds.amazonaws.com',
    'user': 'dbmasteruser',
    'password': 'R8AR9z^_y|AP3+jABss?GN8<!|ta4<,f',
    'database': 'eassy_new_backup',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}


def describe_table(table_name):
    """
    Describe table structure
    """
    connection = None
    try:
        # Connect to database
        connection = pymysql.connect(**DB_CONFIG)
        
        with connection.cursor() as cursor:
            # Describe table
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            
            print(f"\nTable: {table_name}")
            print("="*80)
            print(f"{'Field':<30} {'Type':<20} {'Null':<6} {'Key':<6} {'Default':<15}")
            print("-"*80)
            for col in columns:
                field = col['Field']
                type_val = col['Type']
                null_val = col['Null']
                key_val = col['Key']
                default_val = str(col['Default']) if col['Default'] is not None else 'NULL'
                print(f"{field:<30} {type_val:<20} {null_val:<6} {key_val:<6} {default_val:<15}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    # Describe categories and subcategories tables
    describe_table('eassy_categories')
    describe_table('eassy_subcategories')

