import MySQLdb

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'suyash2005',
    'db': 'aptitude_test_db'
}

def verify_data():
    try:
        conn = MySQLdb.connect(**db_config)
        cursor = conn.cursor()
        
        # Check column existence
        cursor.execute("SHOW COLUMNS FROM users LIKE 'full_name'")
        column = cursor.fetchone()
        if column:
            print("SUCCESS: 'full_name' column exists.")
        else:
            print("FAILURE: 'full_name' column does NOT exist.")
            
        # Check data
        cursor.execute("SELECT username, full_name FROM users WHERE username IN ('suyash', 'dhiraj')")
        users = cursor.fetchall()
        for user in users:
            print(f"User: {user[0]}, Full Name: {user[1]}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_data()
