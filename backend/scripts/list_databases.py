"""
Script to list all databases on the server
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


def list_databases():
    """
    List all databases on the server
    """
    connection = None
    try:
        # Connect to MySQL server
        print("Connecting to MySQL server...")
        connection = pymysql.connect(**DB_CONFIG)
        
        with connection.cursor() as cursor:
            # List all databases
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            
            print("\nAvailable databases:")
            print("="*60)
            for db in databases:
                print(f"  - {db['Database']}")
            print("="*60)
            print(f"\nTotal: {len(databases)} databases")
            
    except Exception as e:
        print(f"\nError: {e}")
        raise
    finally:
        if connection:
            connection.close()
            print("\nDatabase connection closed.")


if __name__ == "__main__":
    list_databases()

