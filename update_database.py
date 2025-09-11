import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure MySQL connection
config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'suyash2005'),
    'database': os.getenv('MYSQL_DB', 'aptitude_test_db')
}

def update_database_schema():
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        print("Connected to MySQL database.")
        
        # Update tests table - add description and allow_review fields
        try:
            cursor.execute("ALTER TABLE tests ADD COLUMN description TEXT AFTER name")
            print("Added description column to tests table.")
        except mysql.connector.Error as err:
            if err.errno == 1060:  # Duplicate column error
                print("Column 'description' already exists in tests table.")
            else:
                raise
        
        try:
            cursor.execute("ALTER TABLE tests ADD COLUMN allow_review BOOLEAN DEFAULT TRUE AFTER admin_id")
            print("Added allow_review column to tests table.")
        except mysql.connector.Error as err:
            if err.errno == 1060:  # Duplicate column error
                print("Column 'allow_review' already exists in tests table.")
            else:
                raise
        
        # Update questions table - add question_type and points fields
        try:
            cursor.execute("ALTER TABLE questions MODIFY COLUMN option_a TEXT")
            cursor.execute("ALTER TABLE questions MODIFY COLUMN option_b TEXT")
            cursor.execute("ALTER TABLE questions MODIFY COLUMN option_c TEXT")
            cursor.execute("ALTER TABLE questions MODIFY COLUMN option_d TEXT")
            cursor.execute("ALTER TABLE questions MODIFY COLUMN correct_option TEXT")
            print("Modified option columns to allow NULL values.")
        except mysql.connector.Error as err:
            print(f"Error modifying option columns: {err}")
        
        try:
            cursor.execute("ALTER TABLE questions ADD COLUMN question_type VARCHAR(20) DEFAULT 'multiple_choice' AFTER correct_option")
            print("Added question_type column to questions table.")
        except mysql.connector.Error as err:
            if err.errno == 1060:  # Duplicate column error
                print("Column 'question_type' already exists in questions table.")
            else:
                raise
        
        try:
            cursor.execute("ALTER TABLE questions ADD COLUMN points INT DEFAULT 1 AFTER question_type")
            print("Added points column to questions table.")
        except mysql.connector.Error as err:
            if err.errno == 1060:  # Duplicate column error
                print("Column 'points' already exists in questions table.")
            else:
                raise
        
        conn.commit()
        print("Database schema updated successfully.")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    update_database_schema()