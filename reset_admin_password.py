import mysql.connector
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get MySQL credentials from .env file
host = os.getenv('MYSQL_HOST', 'localhost')
user = os.getenv('MYSQL_USER', 'root')
password = os.getenv('MYSQL_PASSWORD', 'suyash2005')
db_name = os.getenv('MYSQL_DB', 'aptitude_test_db')

try:
    # Connect to MySQL server
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )
    
    cursor = conn.cursor()
    
    # Create a new Bcrypt instance
    bcrypt = Bcrypt()
    
    # Generate hashed password
    admin_password = 'admin123'
    hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')
    
    # Update admin password
    cursor.execute("UPDATE admins SET password = %s WHERE username = %s", 
                  (hashed_password, 'admin'))
    
    conn.commit()
    
    # Verify the update
    cursor.execute("SELECT * FROM admins WHERE username = %s", ['admin'])
    admin = cursor.fetchone()
    
    if admin:
        print(f"Admin password reset successfully.")
        print(f"Username: admin")
        print(f"Password: {admin_password}")
    else:
        print("Admin user not found.")
    
    cursor.close()
    conn.close()
    
except mysql.connector.Error as err:
    print(f"Error: {err}")