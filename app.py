from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os
import datetime
import importlib.util
import pandas as pd
import io
import json

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

# Configure file uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_image(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

# Configure MySQL
from flask_mysqldb import MySQL
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'suyash2005')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'aptitude_test_db')
mysql = MySQL(app)

# Initialize extensions
bcrypt = Bcrypt(app)

# Add current year to templates
@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now()}

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        
        # Connect to database
        cur = mysql.connection.cursor()
        
        if user_type == 'admin':
            cur.execute("SELECT * FROM admins WHERE username = %s", [username])
        else:
            cur.execute("SELECT * FROM users WHERE username = %s", [username])
            
        user = cur.fetchone()
        cur.close()
        
        if user and bcrypt.check_password_hash(user[3], password):
            # Set session variables
            session['logged_in'] = True
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['user_type'] = user_type
            
            flash('Login successful', 'success')
            
            if user_type == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Connect to database
        cur = mysql.connection.cursor()
        
        # Check if username already exists
        cur.execute("SELECT * FROM users WHERE username = %s", [username])
        user = cur.fetchone()
        
        if user:
            flash('Username already exists', 'danger')
            cur.close()
            return render_template('register.html')
        
        # Insert new user
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
        mysql.connection.commit()
        cur.close()
        
        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/reset-password')
def reset_password():
    return render_template('reset_password.html')

@app.route('/reset-password-submit', methods=['POST'])
def reset_password_submit():
    username = request.form['username']
    email = request.form['email']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    user_type = request.form['user_type']
    
    # Validation
    if new_password != confirm_password:
        flash('Passwords do not match', 'danger')
        return render_template('reset_password.html')
    
    # Hash password
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    
    # Connect to database
    cur = mysql.connection.cursor()
    
    if user_type == 'admin':
        cur.execute("SELECT * FROM admins WHERE username = %s AND email = %s", [username, email])
    else:
        cur.execute("SELECT * FROM users WHERE username = %s AND email = %s", [username, email])
        
    user = cur.fetchone()
    
    if user:
        if user_type == 'admin':
            cur.execute("UPDATE admins SET password = %s WHERE username = %s", [hashed_password, username])
        else:
            cur.execute("UPDATE users SET password = %s WHERE username = %s", [hashed_password, username])
            
        mysql.connection.commit()
        flash('Password reset successful. You can now log in with your new password.', 'success')
        cur.close()
        return redirect(url_for('login'))
    else:
        flash('Invalid username or email', 'danger')
        cur.close()
        return render_template('reset_password.html')

@app.route('/user-dashboard')
def user_dashboard():
    if 'logged_in' not in session or session['user_type'] != 'user':
        flash('Please log in as a user to access this page', 'danger')
        return redirect(url_for('login'))
    
    # Get available tests
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tests")
    tests_data = cur.fetchall()
    
    # Format the test dates
    tests = []
    for test in tests_data:
        # Format the creation date if it's a datetime object (index 6)
        creation_date = test[6]
        formatted_creation_date = creation_date.strftime('%Y-%m-%d') if hasattr(creation_date, 'strftime') else str(creation_date)
        
        # Create a list with the test data and add the formatted date
        test_with_formatted_date = list(test)
        test_with_formatted_date.append(formatted_creation_date)
        tests.append(test_with_formatted_date)
    
    # Get user's test results
    cur.execute("""SELECT r.id, r.score, r.percentage, r.date_taken, t.name as test_name 
                 FROM results r 
                 JOIN tests t ON r.test_id = t.id 
                 WHERE r.user_id = %s
                 ORDER BY r.date_taken DESC""", [session['user_id']])
    results_tuples = cur.fetchall()
    
    # Convert results to dictionaries
    results = []
    for result in results_tuples:
        # Format the date as a string instead of using strftime in the template
        date_taken = result[3]
        formatted_date = date_taken.strftime('%Y-%m-%d') if hasattr(date_taken, 'strftime') else str(date_taken)
        
        results.append({
            'id': result[0],
            'score': result[1],
            'percentage': result[2],
            'date_taken': date_taken,
            'formatted_date': formatted_date,
            'test_name': result[4]
        })
    
    cur.close()
    
    return render_template('user_dashboard.html', tests=tests, results=results)

@app.route('/admin-dashboard')
def admin_dashboard():
    if 'logged_in' not in session or session['user_type'] != 'admin':
        flash('Please log in as an admin to access this page', 'danger')
        return redirect(url_for('login'))
    
    # Get all tests created by this admin
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tests WHERE admin_id = %s", [session['user_id']])
    tests_data = cur.fetchall()
    
    # Format the test creation dates
    tests = []
    for test in tests_data:
        test_list = list(test)
        # Format the date (index 6 for created_at)
        if test[6] and hasattr(test[6], 'strftime'):
            test_list.append(test[6].strftime('%Y-%m-%d'))
        else:
            test_list.append(str(test[6]) if test[6] else 'N/A')
        tests.append(test_list)
    
    # Get all users
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    
    # Get all results
    cur.execute("SELECT r.*, u.username, t.name FROM results r JOIN users u ON r.user_id = u.id JOIN tests t ON r.test_id = t.id")
    results_data = cur.fetchall()
    
    # Format the result dates
    results = []
    for result in results_data:
        result_dict = {
            'id': result[0],
            'test_id': result[1],
            'user_id': result[2],
            'score': result[3],
            'percentage': result[4],
            'username': result[6],
            'test_name': result[7]
        }
        
        # Format the date taken (assuming it's at index 5)
        date_taken = result[5]
        if date_taken and hasattr(date_taken, 'strftime'):
            result_dict['formatted_date'] = date_taken.strftime('%Y-%m-%d')
        else:
            result_dict['formatted_date'] = str(date_taken) if date_taken else 'N/A'
        
        results.append(result_dict)
    
    # Get all warnings
    cur.execute("SELECT w.*, u.username FROM warnings w JOIN users u ON w.user_id = u.id")
    warnings_data = cur.fetchall()
    
    # Format the warning dates
    warnings = []
    for warning in warnings_data:
        warning_dict = {
            'id': warning[0],
            'user_id': warning[1],
            'warning_text': warning[2],
            'username': warning[4]
        }
        
        # Format the timestamp (assuming it's at index 3)
        timestamp = warning[3]
        if timestamp and hasattr(timestamp, 'strftime'):
            warning_dict['formatted_timestamp'] = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        else:
            warning_dict['formatted_timestamp'] = str(timestamp) if timestamp else 'N/A'
        
        warnings.append(warning_dict)
    
    cur.close()
    
    return render_template('admin_dashboard.html', tests=tests, users=users, results=results, warnings=warnings)

@app.route('/create-test', methods=['GET', 'POST'])
def create_test():
    if 'logged_in' not in session or session['user_type'] != 'admin':
        flash('Please log in as an admin to access this page', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Manual test submission
        if 'test_name' in request.form:
            test_name = request.form['test_name']
            duration = request.form['duration']
            description = ''
            
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO tests (name, duration, admin_id, description) VALUES (%s, %s, %s, %s)", 
                       [test_name, duration, session['user_id'], description])
            mysql.connection.commit()
            test_id = cur.lastrowid
            
            num_questions = int(request.form['question_count'])
            for i in range(1, num_questions + 1):
                question_text = request.form[f'question_{i}']
                option_a = request.form[f'option_{i}_a']
                option_b = request.form[f'option_{i}_b']
                option_c = request.form[f'option_{i}_c']
                option_d = request.form[f'option_{i}_d']
                correct_option = request.form[f'correct_option_{i}']
                
                image_path = None
                file_key = f'question_image_{i}'
                if file_key in request.files:
                    question_image = request.files[file_key]
                    if question_image and question_image.filename != '':
                        filename = secure_filename(question_image.filename)
                        if not allowed_image(filename):
                            flash(f'Invalid image format for question {i}. Allowed: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}', 'danger')
                            cur.close()
                            return render_template('create_test.html')
                        unique_filename = f"{test_id}_{i}_{filename}"
                        save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                        question_image.save(save_path)
                        image_path = unique_filename
                
                if image_path:
                    cur.execute("INSERT INTO questions (test_id, question_text, option_a, option_b, option_c, option_d, correct_option, image_path) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                               [test_id, question_text, option_a, option_b, option_c, option_d, correct_option, image_path])
                else:
                    cur.execute("INSERT INTO questions (test_id, question_text, option_a, option_b, option_c, option_d, correct_option) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                               [test_id, question_text, option_a, option_b, option_c, option_d, correct_option])
            
            flash('Test created successfully', 'success')
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('admin_dashboard'))
    
    return render_template('create_test.html')

@app.route('/available-tests')
def available_tests():
    if 'logged_in' not in session or session['user_type'] != 'user':
        flash('Please log in as a user to access this page', 'danger')
        return redirect(url_for('login'))
    
    # Get available tests
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tests")
    tests = cur.fetchall()
    cur.close()
    
    return render_template('available_tests.html', tests=tests)

@app.route('/take-test/<int:test_id>')
def take_test(test_id):
    if 'logged_in' not in session or session['user_type'] != 'user':
        flash('Please log in as a user to access this page', 'danger')
        return redirect(url_for('login'))
    
    # Get test details
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tests WHERE id = %s", [test_id])
    test = cur.fetchone()
    
    if not test:
        flash('Test not found', 'danger')
        return redirect(url_for('available_tests'))
    
    # Debug: Print test data
    print(f"Test data: {test}")
    print(f"Test duration type: {type(test[3])}, value: {test[3]}")
    
    # Get questions
    cur.execute("SELECT * FROM questions WHERE test_id = %s", [test_id])
    questions = cur.fetchall()
    cur.close()
    
    # Set test start time
    start_time = datetime.datetime.now().timestamp()
    session['test_start_time'] = start_time
    session['test_id'] = test_id
    
    # Handle duration - ensure it's a valid integer, default to 15 minutes if invalid
    try:
        duration = int(test[3]) if test[3] and str(test[3]).strip() else 15
    except (ValueError, TypeError):
        duration = 15
    session['test_duration'] = duration
    
    return render_template('take_test_new.html', test=test, questions=questions, start_time=start_time)

@app.route('/submit-test/<int:test_id>', methods=['POST'])
def submit_test(test_id):
    if 'logged_in' not in session or session['user_type'] != 'user':
        flash('Please log in as a user to access this page', 'danger')
        return redirect(url_for('login'))
    
    # Check if test time is over
    current_time = datetime.datetime.now().timestamp()
    test_start_time = session.get('test_start_time', 0)
    test_duration = session.get('test_duration', 0)
    
    if current_time - test_start_time > test_duration * 60:
        flash('Test time is over. Your answers have been submitted automatically.', 'warning')
    
    # Get questions
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM questions WHERE test_id = %s", [test_id])
    questions = cur.fetchall()
    
    # Calculate score
    score = 0
    for question in questions:
        question_id = question[0]
        correct_option = question[7]  # Correct option (A, B, C, or D)
        
        # Get user's answer
        user_answer = request.form.get(f'answer_{question_id}', '')
        
        if user_answer == correct_option:
            score += 1
    
    # Calculate percentage
    total_questions = len(questions)
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    
    # Get warning count and save warnings to database
    warning_count = int(request.form.get('warning_count', 0))
    
    # Save warnings to database if any
    if warning_count > 0:
        # For now, we'll save a generic warning entry
        # In a full implementation, you'd want to save each specific warning
        cur.execute("INSERT INTO warnings (user_id, test_id, warning_type) VALUES (%s, %s, %s)", 
                   [session['user_id'], test_id, f'Multiple violations ({warning_count} warnings)'])
    
    # Save result
    cur.execute("INSERT INTO results (user_id, test_id, score, percentage) VALUES (%s, %s, %s, %s)", 
               [session['user_id'], test_id, score, percentage])
    mysql.connection.commit()
    
    result_id = cur.lastrowid
    cur.close()
    
    # Clear test session variables
    session.pop('test_start_time', None)
    session.pop('test_id', None)
    session.pop('test_duration', None)
    
    return redirect(url_for('test_result', result_id=result_id))

@app.route('/test-result/<int:result_id>')
def test_result(result_id):
    if 'logged_in' not in session:
        flash('Please log in to access this page', 'danger')
        return redirect(url_for('login'))
    
    # Get result details
    cur = mysql.connection.cursor()
    cur.execute("SELECT r.*, t.name, t.duration FROM results r JOIN tests t ON r.test_id = t.id WHERE r.id = %s", [result_id])
    result = cur.fetchone()
    
    if not result or (session['user_type'] == 'user' and result[1] != session['user_id']):
        flash('Result not found or you do not have permission to view it', 'danger')
        cur.close()
        return redirect(url_for('user_dashboard' if session['user_type'] == 'user' else 'admin_dashboard'))
    
    # Get test questions and user answers
    cur.execute("SELECT q.* FROM questions q WHERE q.test_id = %s", [result[2]])
    questions = cur.fetchall()
    
    # Get warning count
    cur.execute("SELECT COUNT(*) FROM warnings WHERE user_id = %s AND test_id = %s", [result[1], result[2]])
    warning_count = cur.fetchone()[0]
    
    cur.close()
    
    total_questions = len(questions)
    percentage = result[4]
    
    return render_template('test_result.html', result=result, test=result[6:8], questions=questions, total_questions=total_questions, percentage=percentage, warning_count=warning_count)

@app.route('/manage-admins', methods=['GET', 'POST'])
def manage_admins():
    if 'logged_in' not in session or session['user_type'] != 'admin':
        flash('Please log in as an admin to access this page', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        action = request.form['action']
        
        if action == 'create':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            
            # Hash password
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            
            # Connect to database
            cur = mysql.connection.cursor()
            
            # Check if username already exists
            cur.execute("SELECT * FROM admins WHERE username = %s", [username])
            admin = cur.fetchone()
            
            if admin:
                flash('Username already exists', 'danger')
            else:
                # Insert new admin
                cur.execute("INSERT INTO admins (username, email, password) VALUES (%s, %s, %s)", [username, email, hashed_password])
                mysql.connection.commit()
                flash('Admin created successfully', 'success')
            
            cur.close()
        elif action == 'delete':
            admin_id = request.form['admin_id']
            
            # Connect to database
            cur = mysql.connection.cursor()
            
            # Delete admin
            cur.execute("DELETE FROM admins WHERE id = %s", [admin_id])
            mysql.connection.commit()
            cur.close()
            
            flash('Admin deleted successfully', 'success')
    
    # Get all admins
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM admins")
    admin_tuples = cur.fetchall()
    
    # Get column names
    cur.execute("SHOW COLUMNS FROM admins")
    columns = [column[0] for column in cur.fetchall()]
    cur.close()
    
    # Convert tuples to dictionaries with column names as keys
    admins = []
    for admin_tuple in admin_tuples:
        admin_dict = {}
        for i, column in enumerate(columns):
            admin_dict[column] = admin_tuple[i]
        admins.append(admin_dict)
    
    return render_template('manage_admins.html', admins=admins)

@app.route('/delete-test/<int:test_id>', methods=['POST'])
def delete_test(test_id):
    if 'logged_in' not in session or session['user_type'] != 'admin':
        flash('Please log in as an admin to access this page', 'danger')
        return redirect(url_for('login'))
    
    # Connect to database
    cur = mysql.connection.cursor()
    
    # Delete test and related questions (cascade delete will handle this)
    cur.execute("DELETE FROM tests WHERE id = %s AND admin_id = %s", [test_id, session['user_id']])
    mysql.connection.commit()
    cur.close()
    
    flash('Test deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/export-results', methods=['GET'])
def export_results():
    if 'logged_in' not in session or session['user_type'] != 'admin':
        flash('Please log in as an admin to access this page', 'danger')
        return redirect(url_for('login'))
    
    # Connect to database
    cur = mysql.connection.cursor()
    
    # Get all results with user and test information
    cur.execute("""
        SELECT r.id, u.username, t.name, r.score, r.percentage, r.date_taken 
        FROM results r 
        JOIN users u ON r.user_id = u.id 
        JOIN tests t ON r.test_id = t.id
        ORDER BY r.date_taken DESC
    """)
    
    results = cur.fetchall()
    cur.close()
    
    # Create a pandas DataFrame
    df = pd.DataFrame(results, columns=['ID', 'Username', 'Test Name', 'Score', 'Percentage', 'Date Taken'])
    
    # Create an in-memory Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Test Results', index=False)
        
        # Get the openpyxl workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Test Results']
        
        # Add some formatting
        from openpyxl.styles import Font, PatternFill, Alignment
        
        # Format header row
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4CAF50", end_color="4CAF50", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        # Apply formatting to header row
        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
        
        # Set column widths
        worksheet.column_dimensions['A'].width = 5   # ID column
        worksheet.column_dimensions['B'].width = 20  # Username column
        worksheet.column_dimensions['C'].width = 20  # Test Name column
        worksheet.column_dimensions['D'].width = 10  # Score column
        worksheet.column_dimensions['E'].width = 10  # Percentage column
        worksheet.column_dimensions['F'].width = 20  # Date Taken column
    
    # Set up the Http response
    output.seek(0)
    
    # Generate a timestamp for the filename
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'test_results_{timestamp}.xlsx'
    
    return send_file(output, download_name=filename, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/record_warning', methods=['POST'])
def record_warning():
    if 'logged_in' not in session or session['user_type'] != 'user':
        return {'success': False, 'message': 'Unauthorized'}
    
    user_id = session['user_id']
    data = request.get_json()
    test_id = data.get('test_id')
    warning_type = data.get('warning_type')
    warning_count = data.get('warning_count')
    details = str(warning_count) + " warnings recorded"
    
    if not test_id or not warning_type:
        return {'success': False, 'message': 'Invalid request'}
    
    # Connect to database
    cur = mysql.connection.cursor()
    
    # Insert warning
    cur.execute("INSERT INTO warnings (user_id, test_id, warning_type) VALUES (%s, %s, %s)", [user_id, test_id, warning_type])
    mysql.connection.commit()
    cur.close()
    
    return {'success': True, 'message': 'Warning recorded'}

# The create_quiz route has been integrated into the create_test route

if __name__ == '__main__':
    app.run(debug=True)