#!/usr/bin/env python3
"""
Script to check test data in the database
"""

import pymysql
from flask import Flask
from flask_mysqldb import MySQL

# Initialize Flask app
app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'suyash2005'
app.config['MYSQL_DB'] = 'aptitude_test_db'

mysql = MySQL(app)

def check_test_data():
    """Check the test data in the database"""
    
    print("Checking test data in database...")
    print("=" * 50)
    
    try:
        with app.app_context():
            cur = mysql.connection.cursor()
            
            # Check all tests
            cur.execute("SELECT * FROM tests")
            tests = cur.fetchall()
            
            print(f"Total tests found: {len(tests)}")
            print("\nTest details:")
            print("-" * 30)
            
            for test in tests:
                print(f"ID: {test[0]}")
                print(f"Name: {test[1]}")
                print(f"Description: {test[2]}")
                print(f"Duration: '{test[3]}' (type: {type(test[3])})")
                print(f"Admin ID: {test[4]}")
                print(f"Allow Review: {test[5]}")
                print(f"Created At: {test[6]}")
                print("-" * 30)
            
            # Check specific test ID 4
            print(f"\nChecking test ID 4 specifically:")
            cur.execute("SELECT * FROM tests WHERE id = 4")
            test_4 = cur.fetchone()
            
            if test_4:
                print(f"Test 4 found:")
                print(f"ID: {test_4[0]}")
                print(f"Name: {test_4[1]}")
                print(f"Description: {test_4[2]}")
                print(f"Duration: '{test_4[3]}' (type: {type(test_4[3])})")
                print(f"Admin ID: {test_4[4]}")
                print(f"Allow Review: {test_4[5]}")
                print(f"Created At: {test_4[6]}")
            else:
                print("Test ID 4 not found!")
            
            cur.close()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_test_data()
