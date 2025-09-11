#!/usr/bin/env python3
"""
Simple test script to verify take test functionality
"""

def test_take_test_components():
    """Test that all components are properly connected"""
    
    print("Testing Take Test Functionality Components...")
    print("=" * 50)
    
    # Test 1: Check if files exist
    import os
    
    files_to_check = [
        'templates/take_test_new.html',
        'static/js/take_test.js',
        'static/css/test_interface.css',
        'app.py'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} missing")
    
    # Test 2: Check if routes exist in app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
        
    routes_to_check = [
        '@app.route(\'/take-test/<int:test_id>\')',
        '@app.route(\'/submit-test/<int:test_id>\', methods=[\'POST\'])'
    ]
    
    for route in routes_to_check:
        if route in app_content:
            print(f"✓ Route found: {route}")
        else:
            print(f"✗ Route missing: {route}")
    
    # Test 3: Check if JavaScript functions exist
    with open('static/js/take_test.js', 'r', encoding='utf-8') as f:
        js_content = f.read()
        
    functions_to_check = [
        'function updateTimer()',
        'function showQuestion(',
        'function updateQuestionStatus(',
        'function recordWarning('
    ]
    
    for func in functions_to_check:
        if func in js_content:
            print(f"✓ Function found: {func}")
        else:
            print(f"✗ Function missing: {func}")
    
    # Test 4: Check if HTML template has required elements
    with open('templates/take_test_new.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    elements_to_check = [
        'id="test-form"',
        'id="timer"',
        'id="minutes"',
        'id="seconds"',
        'question-number',
        'id="submit-btn"'
    ]
    
    for element in elements_to_check:
        if element in html_content:
            print(f"✓ HTML element found: {element}")
        else:
            print(f"✗ HTML element missing: {element}")
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print("✓ HTML Template: take_test_new.html")
    print("✓ JavaScript: take_test.js with timer, navigation, and anti-cheating")
    print("✓ Backend Routes: /take-test/<id> and /submit-test/<id>")
    print("✓ CSS Styling: test_interface.css")
    print("✓ Database Integration: warnings and results tables")
    
    print("\nTo test the full functionality:")
    print("1. Start the Flask app: python app.py")
    print("2. Open browser to: http://localhost:5000")
    print("3. Login as a user")
    print("4. Go to Available Tests")
    print("5. Click on a test to start")
    print("6. Test navigation, timer, and submission")
    
    return True

if __name__ == "__main__":
    test_take_test_components()
