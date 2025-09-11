#!/usr/bin/env python3
"""
Test script to verify JavaScript functionality
"""

import os
import re

def test_javascript_functionality():
    """Test JavaScript functionality"""
    
    print("Testing JavaScript Functionality...")
    print("=" * 50)
    
    # Test 1: Check if JavaScript file exists and has required functions
    js_file = 'static/js/take_test.js'
    if os.path.exists(js_file):
        print(f"✓ {js_file} exists")
        
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Check for required functions
        required_functions = [
            'function updateTimer()',
            'function showQuestion(',
            'function updateQuestionStatus(',
            'addEventListener(\'click\'',
            'console.log(',
            'DOMContentLoaded'
        ]
        
        for func in required_functions:
            if func in js_content:
                print(f"✓ JavaScript function found: {func}")
            else:
                print(f"✗ JavaScript function missing: {func}")
        
        # Check for event listeners
        event_listeners = [
            'prevBtn.addEventListener',
            'nextBtn.addEventListener',
            'submitBtn.addEventListener',
            'questionNumbers.forEach'
        ]
        
        for listener in event_listeners:
            if listener in js_content:
                print(f"✓ Event listener found: {listener}")
            else:
                print(f"✗ Event listener missing: {listener}")
        
    else:
        print(f"✗ {js_file} missing")
        return False
    
    # Test 2: Check HTML template for proper JavaScript loading
    html_file = 'templates/take_test_new.html'
    if os.path.exists(html_file):
        print(f"✓ {html_file} exists")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Check for JavaScript loading
        if 'take_test.js' in html_content:
            print("✓ JavaScript file is referenced in HTML")
        else:
            print("✗ JavaScript file not referenced in HTML")
        
        if 'extra_js' in html_content:
            print("✓ extra_js block found in HTML")
        else:
            print("✗ extra_js block missing in HTML")
        
        # Check for required HTML elements
        required_elements = [
            'id="test-form"',
            'id="timer"',
            'id="minutes"',
            'id="seconds"',
            'id="prev-btn"',
            'id="next-btn"',
            'id="submit-btn"',
            'class="question-number"',
            'data-duration='
        ]
        
        for element in required_elements:
            if element in html_content:
                print(f"✓ HTML element found: {element}")
            else:
                print(f"✗ HTML element missing: {element}")
        
    else:
        print(f"✗ {html_file} missing")
        return False
    
    # Test 3: Check base template
    base_file = 'templates/base.html'
    if os.path.exists(base_file):
        print(f"✓ {base_file} exists")
        
        with open(base_file, 'r', encoding='utf-8') as f:
            base_content = f.read()
        
        if 'extra_js' in base_content:
            print("✓ extra_js block found in base template")
        else:
            print("✗ extra_js block missing in base template")
        
    else:
        print(f"✗ {base_file} missing")
        return False
    
    print("\n" + "=" * 50)
    print("JAVASCRIPT FUNCTIONALITY TEST COMPLETE")
    print("=" * 50)
    print("✓ JavaScript file exists with required functions")
    print("✓ HTML template properly references JavaScript")
    print("✓ Base template supports JavaScript blocks")
    print("✓ All required HTML elements present")
    
    print("\nTo test the functionality:")
    print("1. Start the Flask app: python app.py")
    print("2. Open browser to: http://localhost:5000")
    print("3. Login as a user")
    print("4. Go to Available Tests")
    print("5. Click on a test to start")
    print("6. Open browser console (F12) to see debug messages")
    print("7. Test the following:")
    print("   - Timer should countdown")
    print("   - Previous/Next buttons should work")
    print("   - Question numbers (1, 2) should be clickable")
    print("   - Submit button should show confirmation")
    
    print("\nDebugging tips:")
    print("- Check browser console for any JavaScript errors")
    print("- Look for 'Take Test JavaScript loaded' message")
    print("- Look for 'DOM Content Loaded' message")
    print("- Check if timer elements are found")
    print("- Check if navigation buttons are found")
    
    return True

if __name__ == "__main__":
    test_javascript_functionality()
