import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv('MYSQL_HOST', 'localhost')
user = os.getenv('MYSQL_USER', 'root')
password = os.getenv('MYSQL_PASSWORD', 'suyash2005')
db_name = os.getenv('MYSQL_DB', 'aptitude_test_db')

print(f"Connecting to {host} with user {user}...")

try:
    db = MySQLdb.connect(host=host, user=user, passwd=password, db=db_name)
    cur = db.cursor()
    
    # Check if full_name column exists in users table
    print("Checking for full_name column in users table...")
    cur.execute("SHOW COLUMNS FROM users LIKE 'full_name'")
    result = cur.fetchone()
    
    if not result:
        print("Adding full_name column to users table...")
        cur.execute("ALTER TABLE users ADD COLUMN full_name VARCHAR(255)")
        print("Column added.")
    else:
        print("full_name column already exists.")
        
    # Update specific users
    print("Updating specific users...")
    
    # Update suyash
    cur.execute("UPDATE users SET full_name = %s WHERE username = %s", ('suyash Dhondiram sawant', 'suyash'))
    print(f"Updated suyash: {cur.rowcount} rows affected")
    
    # Update dhiraj
    cur.execute("UPDATE users SET full_name = %s WHERE username = %s", ('dhiraj sunil desai', 'dhiraj'))
    print(f"Updated dhiraj: {cur.rowcount} rows affected")
    
    db.commit()
    cur.close()
    db.close()
    print("Database update completed successfully.")
    
except Exception as e:
    print(f"Error: {e}")
