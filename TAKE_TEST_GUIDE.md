# Take Test Functionality Guide

This document explains how the take test functionality works and how all components are connected.

## Overview

The take test functionality consists of three main components:
1. **HTML Template** (`templates/take_test_new.html`)
2. **JavaScript** (`static/js/take_test.js`)
3. **Backend Routes** (`app.py`)

## Component Connections

### 1. HTML Template (`take_test_new.html`)

**Purpose**: Renders the test interface with questions, navigation, and timer.

**Key Features**:
- Displays test questions one at a time
- Shows timer countdown
- Provides question navigation grid
- Includes anti-cheating warning system
- Supports bookmarking questions

**Data Attributes Passed to JavaScript**:
```html
<form id="test-form" 
      data-duration="{{ test[2] }}" 
      data-total-questions="{{ questions|length }}" 
      data-test-id="{{ test[0] }}">
```

**Form Structure**:
- Hidden inputs for `start_time`, `warning_count`, `current_question`
- Radio buttons for each answer option
- Checkboxes for bookmarking
- Navigation buttons (Previous/Next)
- Submit button

### 2. JavaScript (`take_test.js`)

**Purpose**: Handles all client-side functionality and user interactions.

**Key Functions**:

#### Timer Management
```javascript
function updateTimer() {
    // Countdown timer with visual feedback
    // Auto-submit when time expires
    // Color changes for time warnings
}
```

#### Question Navigation
```javascript
function showQuestion(questionNumber) {
    // Hide all questions, show current one
    // Update navigation buttons
    // Update question status indicators
}
```

#### Anti-Cheating Features
```javascript
// Tab switching detection
document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'hidden') {
        recordWarning('Tab/Application switching detected');
    }
});

// Keyboard shortcut prevention
document.addEventListener('keydown', function (e) {
    if ((e.ctrlKey && (e.key === 'c' || e.key === 'v' || e.key === 'x'))) {
        e.preventDefault();
        recordWarning('Keyboard shortcut detected');
    }
});
```

#### Question Status Tracking
```javascript
function updateQuestionStatus(questionNumber) {
    // Track answered/unanswered questions
    // Handle bookmarking
    // Update legend counts
}
```

### 3. Backend Routes (`app.py`)

#### Route: `/take-test/<int:test_id>`
**Purpose**: Renders the test interface.

**Process**:
1. Verify user authentication
2. Fetch test details and questions from database
3. Set session variables for test tracking
4. Render template with test data

```python
@app.route('/take-test/<int:test_id>')
def take_test(test_id):
    # Authentication check
    # Database queries
    # Session management
    # Template rendering
```

#### Route: `/submit-test/<int:test_id>`
**Purpose**: Processes test submission and calculates results.

**Process**:
1. Verify user authentication
2. Check if test time has expired
3. Calculate score based on correct answers
4. Save warnings to database
5. Save results to database
6. Redirect to results page

```python
@app.route('/submit-test/<int:test_id>', methods=['POST'])
def submit_test(test_id):
    # Time validation
    # Score calculation
    # Warning handling
    # Database saves
    # Redirect to results
```

## Data Flow

### 1. Test Start
```
User clicks "Take Test" 
→ /take-test/<id> route 
→ Database queries 
→ Template rendering 
→ JavaScript initialization
```

### 2. During Test
```
User interactions 
→ JavaScript event handlers 
→ UI updates 
→ Warning tracking 
→ Timer countdown
```

### 3. Test Submission
```
User clicks "Submit" 
→ JavaScript confirmation 
→ Form submission 
→ /submit-test/<id> route 
→ Score calculation 
→ Database saves 
→ Results page
```

## Database Integration

### Tables Used:
1. **tests**: Test information (name, duration, etc.)
2. **questions**: Test questions and answer options
3. **results**: User test results and scores
4. **warnings**: Anti-cheating violation records

### Key Queries:
```sql
-- Get test details
SELECT * FROM tests WHERE id = %s

-- Get test questions
SELECT * FROM questions WHERE test_id = %s

-- Save results
INSERT INTO results (user_id, test_id, score, percentage) VALUES (%s, %s, %s, %s)

-- Save warnings
INSERT INTO warnings (user_id, test_id, warning_type) VALUES (%s, %s, %s)
```

## Security Features

### 1. Anti-Cheating
- Tab switching detection
- Keyboard shortcut prevention
- Right-click prevention
- Print screen prevention
- Maximum warning limit (3 warnings = auto-submit)

### 2. Session Management
- Test start time tracking
- Duration enforcement
- User authentication required

### 3. Data Validation
- Form validation
- Time limit enforcement
- User permission checks

## User Experience Features

### 1. Navigation
- Previous/Next buttons
- Question grid navigation
- Keyboard accessibility

### 2. Visual Feedback
- Timer with color-coded warnings
- Question status indicators
- Legend showing progress
- Bookmarking system

### 3. Accessibility
- ARIA labels
- Keyboard navigation
- Focus management
- Screen reader support

## Testing the Functionality

### 1. Start the Application
```bash
python app.py
```

### 2. Access the Test
1. Navigate to `http://localhost:5000`
2. Login as a user
3. Go to "Available Tests"
4. Click on a test to start

### 3. Test Features
- **Navigation**: Use Previous/Next buttons and question grid
- **Timer**: Watch countdown and color changes
- **Anti-cheating**: Try switching tabs or using Ctrl+C
- **Bookmarking**: Check/uncheck bookmark boxes
- **Submission**: Submit test and view results

## Troubleshooting

### Common Issues:

1. **Questions not showing**: Check JavaScript console for errors
2. **Timer not working**: Verify data attributes are set correctly
3. **Navigation not working**: Check CSS classes and JavaScript selectors
4. **Warnings not saving**: Verify database connection and warnings table

### Debug Steps:
1. Check browser console for JavaScript errors
2. Verify database connections
3. Check Flask application logs
4. Test individual components separately

## File Structure

```
tidu/
├── templates/
│   └── take_test_new.html      # Test interface template
├── static/
│   ├── js/
│   │   └── take_test.js        # Test functionality JavaScript
│   └── css/
│       └── test_interface.css  # Test interface styles
├── app.py                      # Flask routes and backend logic
└── database_schema.sql         # Database structure
```

This functionality provides a complete, secure, and user-friendly test-taking experience with comprehensive anti-cheating measures and accessibility features.
