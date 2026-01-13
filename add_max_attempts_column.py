
import mysql.connector
import os

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'suyash2005',
    'database': 'aptitude_test_db'
}

def add_max_attempts_column():
    print("Connecting to database...")
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        print("Connected to MySQL database.")
        
        # Add per-test max_attempts column
        try:
            cursor.execute("ALTER TABLE tests ADD COLUMN max_attempts INT DEFAULT 1 AFTER max_warnings")
            print("Added max_attempts column to tests table.")
        except mysql.connector.Error as err:
            if err.errno == 1060:  # Duplicate column error
                print("Column 'max_attempts' already exists in tests table.")
            else:
                raise
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database schema updated successfully.")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    add_max_attempts_column()
