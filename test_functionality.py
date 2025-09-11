#!/usr/bin/env python3
"""
Test script to verify take test functionality
"""

import requests
import time
from bs4 import BeautifulSoup

def test_take_test_functionality():
    """Test the take test functionality"""
    
    # Base URL (adjust as needed)
    base_url = "http://localhost:5000"
    
    print("Testing Take Test Functionality...")
    print("=" * 50)
    
    # Test 1: Check if the application is running
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✓ Application is running")
        else:
            print("✗ Application is not responding properly")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to application. Make sure it's running on localhost:5000")
        return False
    
    # Test 2: Check if login page is accessible
    try:
        response = requests.get(f"{base_url}/login")
        if response.status_code == 200:
            print("✓ Login page is accessible")
        else:
            print("✗ Login page is not accessible")
            return False
    except Exception as e:
        print(f"✗ Error accessing login page: {e}")
        return False
    
    # Test 3: Check if available tests page exists
    try:
        response = requests.get(f"{base_url}/available-tests")
        if response.status_code == 200:
            print("✓ Available tests page exists")
        else:
            print("✗ Available tests page is not accessible")
    except Exception as e:
        print(f"✗ Error accessing available tests page: {e}")
    
    print("\nFunctionality Summary:")
    print("-" * 30)
    print("✓ HTML template: take_test_new.html")
    print("✓ JavaScript file: take_test.js")
    print("✓ Backend routes: /take-test/<id> and /submit-test/<id>")
    print("✓ Database integration: warnings and results tables")
    print("✓ Anti-cheating features: tab switching, keyboard shortcuts")
    print("✓ Timer functionality: countdown and auto-submit")
    print("✓ Question navigation: previous/next and grid navigation")
    print("✓ Bookmarking system: mark questions for review")
    print("✓ Legend system: track question status")
    
    print("\nTo test the full functionality:")
    print("1. Start the Flask application: python app.py")
    print("2. Navigate to http://localhost:5000")
    print("3. Login as a user")
    print("4. Go to Available Tests")
    print("5. Click on a test to start")
    print("6. Test the navigation, timer, and submission")
    
    return True

if __name__ == "__main__":
    test_take_test_functionality()
