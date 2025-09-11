import mysql.connector
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
        password=password
    )
    
    cursor = conn.cursor()
    
    # Create database if it doesn't exist
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    print(f"Database '{db_name}' created or already exists.")
    
    # Use the database
    cursor.execute(f"USE {db_name}")
    
    # Read SQL schema from file
    with open('database_schema.sql', 'r') as f:
        sql_schema = f.read()
    
    # Split SQL commands
    sql_commands = sql_schema.split(';')
    
    # Execute each SQL command
    for command in sql_commands:
        command = command.strip()
        if command:
            cursor.execute(command)
    
    conn.commit()
    print("Database schema created successfully.")
    
    # Insert default admin if not exists
    cursor.execute("SELECT * FROM admins WHERE username = 'admin'")
    admin = cursor.fetchone()
    
    if not admin:
        from flask_bcrypt import Bcrypt
        bcrypt = Bcrypt()
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        
        cursor.execute("INSERT INTO admins (username, email, password) VALUES (%s, %s, %s)", 
                      ('admin', 'admin@example.com', hashed_password))
        conn.commit()
        print("Default admin created.")
    
    # Insert demo user if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'user'")
    user_record = cursor.fetchone()
    
    if not user_record:
        from flask_bcrypt import Bcrypt
        bcrypt = Bcrypt()
        hashed_password = bcrypt.generate_password_hash('user123').decode('utf-8')
        
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                      ('user', 'user@example.com', hashed_password))
        conn.commit()
        print("Demo user created.")
    
    cursor.close()
    conn.close()
    
    print("Database setup completed successfully.")
    
except mysql.connector.Error as err:
    print(f"Error: {err}")