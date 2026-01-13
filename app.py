from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os
import random
import datetime
import importlib.util
import pandas as pd
import io
import json

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Enable Jinja2 extensions
app.jinja_env.add_extension('jinja2.ext.do')

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
import MySQLdb
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'suyash2005')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'aptitude_test_db')
mysql = MySQL(app)

def ensure_schema():
    try:
        cur = mysql.connection.cursor()
        
        # Create categories table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE
            )
        """)
        
        # Populate categories
        default_categories = [
            'Quantitative', 
            'Logical Reasoning', 
            'Verbal Ability', 
            'General Awareness/Technical/Computer Basics'
        ]
        
        for category in default_categories:
            try:
                cur.execute("INSERT INTO categories (name) VALUES (%s)", [category])
            except Exception:
                pass # Already exists
                
        # Add category_id to questions if not exists
        try:
            cur.execute("SELECT category_id FROM questions LIMIT 1")
        except Exception:
            try:
                cur.execute("ALTER TABLE questions ADD COLUMN category_id INT")
                cur.execute("ALTER TABLE questions ADD CONSTRAINT fk_question_category FOREIGN KEY (category_id) REFERENCES categories(id)")
            except Exception:
                pass
                
        # Add shuffle_questions to tests if not exists
        try:
            cur.execute("SELECT shuffle_questions FROM tests LIMIT 1")
        except Exception:
            try:
                cur.execute("ALTER TABLE tests ADD COLUMN shuffle_questions BOOLEAN DEFAULT FALSE")
            except Exception:
                pass
        
        # Make test_id nullable in questions table for Question Bank
        try:
            cur.execute("""
                SELECT IS_NULLABLE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'questions' AND COLUMN_NAME = 'test_id'
            """, [app.config['MYSQL_DB']])
            is_nullable = cur.fetchone()
            if is_nullable and is_nullable[0] == 'NO':
                cur.execute("ALTER TABLE questions MODIFY test_id INT NULL")
        except Exception as e:
            print(f"Error modifying test_id: {e}")
                
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        print(f"Schema update error: {e}")

# Initialize extensions
bcrypt = Bcrypt(app)

# Add current year to templates
@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now()}

# Settings helper
def get_setting(key: str, default: str) -> str:
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT value FROM settings WHERE `key` = %s", [key])
        row = cur.fetchone()
        cur.close()
        if row and row[0] is not None:
            return str(row[0])
    except Exception:
        pass
    return default

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
        full_name = request.form['full_name']
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
        cur.execute("INSERT INTO users (username, email, password, full_name) VALUES (%s, %s, %s, %s)", (username, email, hashed_password, full_name))
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
    
    # Ensure schema is up to date
    ensure_schema()
    
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Get all tests created by this admin
    cur.execute("SELECT * FROM tests WHERE admin_id = %s", [session['user_id']])
    tests = cur.fetchall()
    
    # Format dates for tests
    for test in tests:
        if test.get('created_at'):
             test['formatted_date'] = test['created_at'].strftime('%Y-%m-%d')
        else:
             test['formatted_date'] = 'N/A'

    # Get all users
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    
    # Get all results
    cur.execute("""
        SELECT r.*, u.username, u.full_name, u.email, t.name as test_name 
        FROM results r 
        JOIN users u ON r.user_id = u.id 
        JOIN tests t ON r.test_id = t.id
        ORDER BY r.date_taken DESC
    """)
    results = cur.fetchall()
    
    # Group results by student
    student_performance = {}
    for result in results:
        uid = result['user_id']
        if uid not in student_performance:
            student_performance[uid] = {
                'username': result['username'],
                'full_name': result.get('full_name', ''),
                'email': result.get('email', 'N/A'),
                'results': [],
                'average_score': 0,
                'total_tests': 0
            }
        
        # Format date
        if result.get('date_taken'):
            result['formatted_date'] = result['date_taken'].strftime('%Y-%m-%d')
        else:
            result['formatted_date'] = 'N/A'
            
        student_performance[uid]['results'].append(result)
        student_performance[uid]['total_tests'] += 1
        
    # Calculate averages
    for uid in student_performance:
        total_score = sum(r['percentage'] for r in student_performance[uid]['results'])
        student_performance[uid]['average_score'] = total_score / student_performance[uid]['total_tests']

    # Get all warnings
    cur.execute("""
        SELECT w.*, u.username, u.full_name, t.name as test_name 
        FROM warnings w 
        JOIN users u ON w.user_id = u.id 
        LEFT JOIN tests t ON w.test_id = t.id 
        ORDER BY w.timestamp DESC
    """)
    warnings = cur.fetchall()
    
    # Format warning timestamps
    for warning in warnings:
        warning['message'] = warning.get('warning_type', 'Unknown Warning')
        if warning.get('timestamp'):
            warning['formatted_timestamp'] = warning['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        else:
            warning['formatted_timestamp'] = 'N/A'
            
    # Get current warnings limit from settings
    max_warnings = get_setting('max_warnings', '3')
    
    # Calculate warning counts per student
    warning_counts = {}
    for warning in warnings:
        uid = warning['user_id']
        warning_counts[uid] = warning_counts.get(uid, 0) + 1
        
    # Add warning counts to student_performance
    for uid in student_performance:
        student_performance[uid]['warning_count'] = warning_counts.get(uid, 0)

    # Calculate participation stats
    total_students = len(users)
    participating_students = len(student_performance)
    non_participating_students = total_students - participating_students
    
    participation = {
        'total': total_students,
        'participating': participating_students,
        'not_participating': non_participating_students
    }
    
    # Calculate category performance stats (Global)
    category_performance = {}
    try:
        cur.execute("""
            SELECT c.name, AVG(ua.is_correct) * 100 as average_percentage
            FROM user_answers ua
            JOIN questions q ON ua.question_id = q.id
            JOIN categories c ON q.category_id = c.id
            GROUP BY c.id, c.name
        """)
        cat_stats = cur.fetchall()
        for stat in cat_stats:
            category_performance[stat['name']] = float(round(stat['average_percentage'], 1))
            
        # Ensure all 4 sections are present even if no data
        default_categories = ['Quantitative', 'Logical Reasoning', 'Verbal Ability', 'General Awareness/Technical/Computer Basics']
        for cat in default_categories:
            if cat not in category_performance:
                category_performance[cat] = 0
                
    except Exception as e:
        # Fallback if table doesn't exist or other error
        print(f"Error calculating category stats: {e}")
        default_categories = ['Quantitative', 'Logical Reasoning', 'Verbal Ability', 'General Awareness/Technical/Computer Basics']
        for cat in default_categories:
            category_performance[cat] = 0
            
    # Calculate category performance stats per student
    try:
        cur.execute("""
            SELECT u.id as user_id, c.name, AVG(ua.is_correct) * 100 as average_percentage
            FROM user_answers ua
            JOIN questions q ON ua.question_id = q.id
            JOIN categories c ON q.category_id = c.id
            JOIN users u ON ua.user_id = u.id
            GROUP BY u.id, c.id, c.name
        """)
        user_cat_stats = cur.fetchall()
        
        # Initialize category stats for all students in performance dict
        default_categories = ['Quantitative', 'Logical Reasoning', 'Verbal Ability', 'General Awareness/Technical/Computer Basics']
        for uid in student_performance:
            student_performance[uid]['category_performance'] = {cat: 0 for cat in default_categories}
            
        for stat in user_cat_stats:
            uid = stat['user_id']
            cat_name = stat['name']
            percentage = float(round(stat['average_percentage'], 1))
            
            if uid in student_performance:
                student_performance[uid]['category_performance'][cat_name] = percentage
                
    except Exception as e:
        print(f"Error calculating user category stats: {e}")
        # Initialize empty if error
        default_categories = ['Quantitative', 'Logical Reasoning', 'Verbal Ability', 'General Awareness/Technical/Computer Basics']
        for uid in student_performance:
            student_performance[uid]['category_performance'] = {cat: 0 for cat in default_categories}
    
    # Calculate test performance stats (Average score per test)
    test_performance = {}
    try:
        cur.execute("""
            SELECT t.name, AVG(r.percentage) as average_percentage
            FROM results r
            JOIN tests t ON r.test_id = t.id
            GROUP BY t.id, t.name
            ORDER BY t.created_at DESC
            LIMIT 10
        """)
        test_stats = cur.fetchall()
        # Reverse to show chronological order (Oldest -> Newest) on graph
        for stat in reversed(test_stats):
            test_performance[stat['name']] = float(round(stat['average_percentage'], 1))
    except Exception as e:
        print(f"Error calculating test stats: {e}")

    cur.close()
    
    return render_template('admin_dashboard.html', tests=tests, users=users, results=results, 
                           student_performance=student_performance, warnings=warnings, max_warnings=int(max_warnings),
                           participation=participation, warning_counts=warning_counts, category_performance=category_performance,
                           test_performance=test_performance)

@app.route('/download-template')
def download_template():
    return send_file('static/files/question_template.xlsx', as_attachment=True)

@app.route('/edit-test/<int:test_id>', methods=['GET', 'POST'])
def edit_test(test_id):
    if 'logged_in' not in session or session['user_type'] != 'admin':
        flash('Please log in as an admin to access this page', 'danger')
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Get categories
    cur.execute("SELECT * FROM categories")
    categories = cur.fetchall()
    
    if request.method == 'POST':
        # Get test details
        test_name = request.form['test_name']
        duration = request.form['duration']
        try:
             max_warnings = int(request.form.get('max_warnings', get_setting('max_warnings', '3')))
        except (ValueError, TypeError):
             max_warnings = int(get_setting('max_warnings', '3'))
        
        try:
             max_attempts = int(request.form.get('max_attempts', 1))
        except (ValueError, TypeError):
             max_attempts = 1
        
        shuffle_questions = 1 if 'shuffle_questions' in request.form else 0
        
        # Update test
        try:
            cur.execute("""
                UPDATE tests 
                SET name = %s, duration = %s, max_warnings = %s, max_attempts = %s, shuffle_questions = %s 
                WHERE id = %s AND admin_id = %s
            """, (test_name, duration, max_warnings, max_attempts, shuffle_questions, test_id, session['user_id']))
        except:
             try:
                 cur.execute("""
                    UPDATE tests 
                    SET name = %s, duration = %s, max_warnings = %s, max_attempts = %s
                    WHERE id = %s AND admin_id = %s
                """, (test_name, duration, max_warnings, max_attempts, test_id, session['user_id']))
             except:
                 cur.execute("""
                    UPDATE tests 
                    SET name = %s, duration = %s, max_warnings = %s 
                    WHERE id = %s AND admin_id = %s
                """, (test_name, duration, max_warnings, test_id, session['user_id']))
        
        # Get existing question IDs to track deletions
        cur.execute("SELECT id FROM questions WHERE test_id = %s", [test_id])
        existing_ids = [row['id'] for row in cur.fetchall()]
        updated_ids = []
        
        question_count = int(request.form['question_count'])
        
        import time
        
        for i in range(1, question_count + 1):
            question_text = request.form.get(f'question_{i}')
            # Skip if for some reason question text is missing
            if not question_text:
                continue
                
            option_a = request.form[f'option_{i}_a']
            option_b = request.form[f'option_{i}_b']
            option_c = request.form[f'option_{i}_c']
            option_d = request.form[f'option_{i}_d']
            correct_option = request.form[f'correct_option_{i}']
            category_id = request.form.get(f'category_{i}')
            if category_id == '': category_id = None
            
            # Check if it's an existing question
            question_id_field = f'question_id_{i}'
            question_id = request.form.get(question_id_field)
            
            # Handle image
            image_path = None
            file_key = f'question_image_{i}'
            if file_key in request.files:
                file = request.files[file_key]
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    if allowed_image(filename):
                        # Generate unique filename
                        ext = filename.rsplit('.', 1)[1].lower()
                        timestamp = int(time.time())
                        new_filename = f"test_{test_id}_q{i}_{timestamp}.{ext}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
                        image_path = new_filename
            
            if question_id:
                # Update existing
                try:
                    qid = int(question_id)
                    updated_ids.append(qid)
                    
                    if image_path:
                        try:
                            cur.execute("""
                                UPDATE questions 
                                SET question_text=%s, option_a=%s, option_b=%s, option_c=%s, option_d=%s, correct_option=%s, image_path=%s, category_id=%s 
                                WHERE id=%s AND test_id=%s
                            """, (question_text, option_a, option_b, option_c, option_d, correct_option, image_path, category_id, qid, test_id))
                        except:
                            cur.execute("""
                                UPDATE questions 
                                SET question_text=%s, option_a=%s, option_b=%s, option_c=%s, option_d=%s, correct_option=%s, image_path=%s 
                                WHERE id=%s AND test_id=%s
                            """, (question_text, option_a, option_b, option_c, option_d, correct_option, image_path, qid, test_id))
                    else:
                        try:
                            cur.execute("""
                                UPDATE questions 
                                SET question_text=%s, option_a=%s, option_b=%s, option_c=%s, option_d=%s, correct_option=%s, category_id=%s 
                                WHERE id=%s AND test_id=%s
                            """, (question_text, option_a, option_b, option_c, option_d, correct_option, category_id, qid, test_id))
                        except:
                            cur.execute("""
                                UPDATE questions 
                                SET question_text=%s, option_a=%s, option_b=%s, option_c=%s, option_d=%s, correct_option=%s 
                                WHERE id=%s AND test_id=%s
                            """, (question_text, option_a, option_b, option_c, option_d, correct_option, qid, test_id))
                except ValueError:
                    pass
            else:
                # Insert new
                try:
                    cur.execute("""
                        INSERT INTO questions (test_id, question_text, option_a, option_b, option_c, option_d, correct_option, image_path, category_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (test_id, question_text, option_a, option_b, option_c, option_d, correct_option, image_path, category_id))
                except:
                     cur.execute("""
                        INSERT INTO questions (test_id, question_text, option_a, option_b, option_c, option_d, correct_option, image_path)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (test_id, question_text, option_a, option_b, option_c, option_d, correct_option, image_path))
        
        # Delete removed questions
        for qid in existing_ids:
            if qid not in updated_ids:
                cur.execute("DELETE FROM questions WHERE id = %s AND test_id = %s", (qid, test_id))
                
        mysql.connection.commit()
        cur.close()
        flash('Test updated successfully', 'success')
        return redirect(url_for('admin_dashboard'))

    # GET request
    cur.execute("SELECT * FROM tests WHERE id = %s AND admin_id = %s", [test_id, session['user_id']])
    test = cur.fetchone()
    
    if not test:
        cur.close()
        flash('Test not found or access denied', 'danger')
        return redirect(url_for('admin_dashboard'))
        
    cur.execute("SELECT * FROM questions WHERE test_id = %s ORDER BY id", [test_id])
    questions = cur.fetchall()
    
    cur.close()
    return render_template('edit_test.html', test=test, questions=questions, categories=categories)

@app.route('/view-test-results/<int:test_id>')
def view_test_results(test_id):
    if 'logged_in' not in session or session['user_type'] != 'admin':
        flash('Please log in as an admin to access this page', 'danger')
        return redirect(url_for('login'))
        
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Get test details
    cur.execute("SELECT * FROM tests WHERE id = %s AND admin_id = %s", [test_id, session['user_id']])
    test = cur.fetchone()
    
    if not test:
        cur.close()
        flash('Test not found or access denied', 'danger')
        return redirect(url_for('admin_dashboard'))
        
    # Get results for this test
    cur.execute("""
        SELECT r.*, u.username, u.full_name, u.email 
        FROM results r 
        JOIN users u ON r.user_id = u.id 
        WHERE r.test_id = %s 
        ORDER BY r.date_taken DESC
    """, [test_id])
    results = cur.fetchall()
    
    # Format dates
    for result in results:
        if result.get('date_taken'):
            result['formatted_date'] = result['date_taken'].strftime('%Y-%m-%d %H:%M')
        else:
            result['formatted_date'] = 'N/A'
            
    cur.close()
    return render_template('view_test_results.html', test=test, results=results)

@app.route('/question-bank')
def question_bank():
    if 'logged_in' not in session or session['user_type'] != 'admin':
        flash('Please log in as an admin to access this page', 'danger')
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Get categories
    cur.execute("SELECT * FROM categories")
    categories = cur.fetchall()
    
    # Get bank stats (count per category)
    bank_stats = {}
    for cat in categories:
        cur.execute("SELECT COUNT(*) as count FROM questions WHERE test_id IS NULL AND category_id = %s", [cat['id']])
        result = cur.fetchone()
        bank_stats[cat['id']] = result['count']
        cat['count'] = result['count']
        
    # Get recent questions
    cur.execute("""
        SELECT q.*, c.name as category_name 
        FROM questions q 
        LEFT JOIN categories c ON q.category_id = c.id 
        WHERE q.test_id IS NULL 
        ORDER BY q.id DESC LIMIT 50
    """)
    recent_questions = cur.fetchall()
    
    cur.close()
    return render_template('question_bank.html', categories=categories, recent_questions=recent_questions)

@app.route('/add-bank-question', methods=['POST'])
def add_bank_question():
    if 'logged_in' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
        
    category_id = request.form.get('category_id')
    question_text = request.form.get('question_text')
    option_a = request.form.get('option_a')
    option_b = request.form.get('option_b')
    option_c = request.form.get('option_c')
    option_d = request.form.get('option_d')
    correct_option = request.form.get('correct_option')
    
    if not all([category_id, question_text, option_a, option_b, option_c, option_d, correct_option]):
        flash('All fields are required', 'danger')
        return redirect(url_for('question_bank'))
        
    # Handle image
    image_path = None
    if 'question_image' in request.files:
        file = request.files['question_image']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            if allowed_image(filename):
                ext = filename.rsplit('.', 1)[1].lower()
                timestamp = int(datetime.datetime.now().timestamp())
                new_filename = f"bank_{category_id}_{timestamp}.{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
                image_path = new_filename
    
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            INSERT INTO questions (test_id, category_id, question_text, option_a, option_b, option_c, option_d, correct_option, image_path)
            VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (category_id, question_text, option_a, option_b, option_c, option_d, correct_option, image_path))
        mysql.connection.commit()
        flash('Question added to bank successfully', 'success')
    except Exception as e:
        flash(f'Error adding question: {str(e)}', 'danger')
    finally:
        cur.close()
        
    return redirect(url_for('question_bank'))

@app.route('/upload-bank-questions', methods=['POST'])
def upload_bank_questions():
    if 'logged_in' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
        
    category_id = request.form.get('category_id')
    if not category_id:
        flash('Please select a category', 'danger')
        return redirect(url_for('question_bank'))
        
    if 'excel_file' not in request.files:
        flash('No file uploaded', 'danger')
        return redirect(url_for('question_bank'))
        
    file = request.files['excel_file']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('question_bank'))
        
    if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls') or file.filename.endswith('.csv')):
        flash('Invalid file type', 'danger')
        return redirect(url_for('question_bank'))
        
    try:
        if file.filename.endswith('.csv'):
            data = pd.read_csv(file)
        else:
            data = pd.read_excel(file, engine='openpyxl')
            
        # Validate columns
        required_cols = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d']
        missing = [col for col in required_cols if col not in data.columns]
        if missing:
            flash(f'Missing columns: {", ".join(missing)}', 'danger')
            return redirect(url_for('question_bank'))
            
        # Check correct option column
        correct_col = 'correct_option' if 'correct_option' in data.columns else 'correct_answer'
        if correct_col not in data.columns:
            flash('Missing correct_option column', 'danger')
            return redirect(url_for('question_bank'))
            
        cur = mysql.connection.cursor()
        count = 0
        
        for index, row in data.iterrows():
            question_text = row['question_text']
            # Skip empty rows
            if pd.isna(question_text) or str(question_text).strip() == '':
                continue
                
            option_a = row['option_a']
            option_b = row['option_b']
            option_c = row['option_c']
            option_d = row['option_d']
            correct_val = row.get(correct_col)
            correct_option = str(correct_val).strip().upper() if pd.notna(correct_val) else ''
            
            if correct_option not in ['A', 'B', 'C', 'D']:
                continue
                
            cur.execute("""
                INSERT INTO questions (test_id, category_id, question_text, option_a, option_b, option_c, option_d, correct_option)
                VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)
            """, (category_id, question_text, option_a, option_b, option_c, option_d, correct_option))
            count += 1
            
        mysql.connection.commit()
        cur.close()
        flash(f'{count} questions uploaded to category successfully', 'success')
        
    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'danger')
        
    return redirect(url_for('question_bank'))

@app.route('/create-test', methods=['GET', 'POST'])
def create_test():
    if 'logged_in' not in session or session['user_type'] != 'admin':
        flash('Please log in as an admin to access this page', 'danger')
        return redirect(url_for('login'))
    
    # Get categories for the form
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM categories")
    categories = cur.fetchall()
    
    # Add counts for Question Bank availability
    for cat in categories:
        cur.execute("SELECT COUNT(*) as count FROM questions WHERE test_id IS NULL AND category_id = %s", [cat['id']])
        result = cur.fetchone()
        cat['count'] = result['count']
        
    cur.close()
    
    if request.method == 'POST':
        # Generate from Question Bank
        if request.form.get('generate_from_bank') == '1':
            test_name = request.form['test_name']
            duration = request.form['duration']
            description = ''
            shuffle_questions = 1 if 'shuffle_questions' in request.form else 0
            
            # Per-test warning limit
            try:
                max_warnings = int(request.form.get('max_warnings', get_setting('max_warnings', '3')))
            except (ValueError, TypeError):
                max_warnings = int(get_setting('max_warnings', '3'))
            
            # Max attempts
            try:
                max_attempts = int(request.form.get('max_attempts', '1'))
            except (ValueError, TypeError):
                max_attempts = 1
            
            # Create test
            cur = mysql.connection.cursor()
            try:
                cur.execute("INSERT INTO tests (name, duration, admin_id, description, max_warnings, shuffle_questions, max_attempts) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                           [test_name, duration, session['user_id'], description, max_warnings, shuffle_questions, max_attempts])
                test_id = cur.lastrowid
                
                total_questions = 0
                # Process each category count
                for category in categories:
                    count_key = f"category_count_{category['id']}"
                    count = int(request.form.get(count_key, 0) or 0)
                    
                    if count > 0:
                        # Select random questions from bank
                        cur.execute("""
                            SELECT * FROM questions 
                            WHERE test_id IS NULL AND category_id = %s 
                            ORDER BY RAND() 
                            LIMIT %s
                        """, (category['id'], count))
                        
                        selected_questions = cur.fetchall()
                        
                        for q in selected_questions:
                            # Copy question to new test
                            # Note: We need to check if question has category_id column in fetch
                            # Since we fetched *, it should be there.
                            
                            # Insert copy
                            cur.execute("""
                                INSERT INTO questions (test_id, category_id, question_text, option_a, option_b, option_c, option_d, correct_option, image_path)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (test_id, category['id'], q[2], q[3], q[4], q[5], q[6], q[7], q[8])) # Adjust indices based on schema
                            
                            # Wait, indices might be wrong if using DictCursor? 
                            # Ah, `cur` here is default cursor (tuple).
                            # Let's check indices from schema:
                            # 0: id, 1: test_id, 2: question_text, 3: option_a, 4: option_b, 5: option_c, 6: option_d, 7: correct_option, 8: image_path, 9: question_type, 10: points, 11: category_id
                            
                            # Wait, fetchall returns tuples.
                            # We should use named access if possible or be careful.
                            # Let's use DictCursor for fetching to be safe.
                        
                        total_questions += len(selected_questions)
                
                mysql.connection.commit()
                cur.close()
                flash(f'Test created successfully with {total_questions} questions from bank', 'success')
                return redirect(url_for('admin_dashboard'))
                
            except Exception as e:
                flash(f'Error generating test: {str(e)}', 'danger')
                return render_template('create_test.html', categories=categories)

        # Excel/CSV file import
        if 'excel_file' in request.files and request.files['excel_file'].filename != '':
            file = request.files['excel_file']
            if file.filename.endswith(('.xlsx', '.xls')):
                try:
                    # Read Excel file
                    data = pd.read_excel(file, engine='openpyxl')
                except Exception as e:
                    flash(f'Error reading Excel file: {str(e)}', 'danger')
                    return render_template('create_test.html', categories=categories)
            elif file.filename.endswith('.csv'):
                try:
                    # Read CSV file
                    data = pd.read_csv(file)
                except Exception as e:
                    flash(f'Error reading CSV file: {str(e)}', 'danger')
                    return render_template('create_test.html', categories=categories)
            else:
                flash('Invalid file format. Please upload an Excel file (.xlsx, .xls) or CSV file (.csv)', 'danger')
                return render_template('create_test.html', categories=categories)
            
            try:
                # Validate file structure: accept either 'correct_option' or legacy 'correct_answer'
                base_required = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d']
                missing_base = [col for col in base_required if col not in data.columns]
                if missing_base:
                    flash(f'File is missing required columns: {", ".join(missing_base)}', 'danger')
                    return render_template('create_test.html', categories=categories)
                has_correct_option = 'correct_option' in data.columns
                has_correct_answer = 'correct_answer' in data.columns
                if not (has_correct_option or has_correct_answer):
                    flash('File is missing required column: correct_option (or legacy correct_answer)', 'danger')
                    return render_template('create_test.html', categories=categories)
                
                # Get test details from form
                test_name = request.form['test_name']
                duration = request.form['duration']
                description = ''
                shuffle_questions = 1 if 'shuffle_questions' in request.form else 0
                
                # Per-test warning limit (fallback to global setting)
                try:
                    max_warnings = int(request.form.get('max_warnings', get_setting('max_warnings', '3')))
                except (ValueError, TypeError):
                    max_warnings = int(get_setting('max_warnings', '3'))
                
                # Max attempts
                try:
                    max_attempts = int(request.form.get('max_attempts', '1'))
                except (ValueError, TypeError):
                    max_attempts = 1

                # Create test
                cur = mysql.connection.cursor()
                try:
                    cur.execute("INSERT INTO tests (name, duration, admin_id, description, max_warnings, shuffle_questions, max_attempts) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                               [test_name, duration, session['user_id'], description, max_warnings, shuffle_questions, max_attempts])
                except Exception as e:
                    # Fallback logic if columns missing (though ensure_schema runs)
                    try:
                        cur.execute("INSERT INTO tests (name, duration, admin_id, description, max_warnings) VALUES (%s, %s, %s, %s, %s)", 
                                   [test_name, duration, session['user_id'], description, max_warnings])
                    except:
                        cur.execute("INSERT INTO tests (name, duration, admin_id, description) VALUES (%s, %s, %s, %s)", 
                                   [test_name, duration, session['user_id'], description])
                                   
                mysql.connection.commit()
                test_id = cur.lastrowid
                
                # Process each row in file
                for index, row in data.iterrows():
                    question_text = row['question_text']
                    option_a = row['option_a']
                    option_b = row['option_b']
                    option_c = row['option_c']
                    option_d = row['option_d']
                    # Read correct option from either column
                    correct_col = 'correct_option' if has_correct_option else 'correct_answer'
                    val = row.get(correct_col)
                    correct_option = str(val).strip().upper() if pd.notna(val) else ''
                    
                    # Category mapping from Excel
                    category_id = None
                    if 'category' in data.columns:
                         cat_name = str(row['category']).strip()
                         # Find category ID (simple lookup)
                         for cat in categories:
                             if cat['name'].lower() == cat_name.lower():
                                 category_id = cat['id']
                                 break
                    
                    # Validate correct option
                    if correct_option not in ['A', 'B', 'C', 'D']:
                        flash(f'Invalid correct option "{correct_option}" in row {index+1}. Must be A, B, C, or D.', 'danger')
                        continue
                    
                    # Insert question
                    try:
                        cur.execute("INSERT INTO questions (test_id, question_text, option_a, option_b, option_c, option_d, correct_option, category_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                                   [test_id, question_text, option_a, option_b, option_c, option_d, correct_option, category_id])
                    except:
                        cur.execute("INSERT INTO questions (test_id, question_text, option_a, option_b, option_c, option_d, correct_option) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                                   [test_id, question_text, option_a, option_b, option_c, option_d, correct_option])
                
                mysql.connection.commit()
                cur.close()
                file_type = "Excel" if file.filename.endswith(('.xlsx', '.xls')) else "CSV"
                flash(f'Test created successfully with {len(data)} questions from {file_type} file', 'success')
                return redirect(url_for('admin_dashboard'))
                
            except Exception as e:
                flash(f'Error processing Excel file: {str(e)}', 'danger')
                return render_template('create_test.html', categories=categories)
        
        # Manual test submission
        elif 'test_name' in request.form:
            test_name = request.form['test_name'].strip()
            if not test_name:
                flash('Test Name is required', 'danger')
                return render_template('create_test.html', categories=categories)
            
            duration = request.form['duration']
            description = ''
            shuffle_questions = 1 if 'shuffle_questions' in request.form else 0
            
            # Per-test warning limit (fallback to global setting)
            try:
                max_warnings = int(request.form.get('max_warnings', get_setting('max_warnings', '3')))
            except (ValueError, TypeError):
                max_warnings = int(get_setting('max_warnings', '3'))
            
            # Max attempts
            try:
                max_attempts = int(request.form.get('max_attempts', '1'))
            except (ValueError, TypeError):
                max_attempts = 1

            cur = mysql.connection.cursor()
            try:
                cur.execute("INSERT INTO tests (name, duration, admin_id, description, max_warnings, shuffle_questions, max_attempts) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                           [test_name, duration, session['user_id'], description, max_warnings, shuffle_questions, max_attempts])
            except Exception as e:
                # Fallback
                try:
                    cur.execute("INSERT INTO tests (name, duration, admin_id, description, max_warnings) VALUES (%s, %s, %s, %s, %s)", 
                               [test_name, duration, session['user_id'], description, max_warnings])
                except:
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
                correct_option = request.form.get(f'correct_option_{i}')
                
                if not correct_option:
                    flash(f'Please select a correct answer for Question {i}', 'danger')
                    cur.close()
                    return render_template('create_test.html', categories=categories)

                # Category is no longer required in UI, set to None
                category_id = None
                
                image_path = None
                file_key = f'question_image_{i}'
                if file_key in request.files:
                    question_image = request.files[file_key]
                    if question_image and question_image.filename != '':
                        filename = secure_filename(question_image.filename)
                        if not allowed_image(filename):
                            flash(f'Invalid image format for question {i}. Allowed: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}', 'danger')
                            cur.close()
                            return render_template('create_test.html', categories=categories)
                        unique_filename = f"{test_id}_{i}_{filename}"
                        save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                        question_image.save(save_path)
                        
                        # Store only the filename for relative path usage in templates
                        image_path = unique_filename
                
                if image_path:
                    try:
                        cur.execute("INSERT INTO questions (test_id, question_text, option_a, option_b, option_c, option_d, correct_option, image_path, category_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                                   [test_id, question_text, option_a, option_b, option_c, option_d, correct_option, image_path, category_id])
                    except Exception as e:
                         # Fallback
                         cur.execute("INSERT INTO questions (test_id, question_text, option_a, option_b, option_c, option_d, correct_option, image_path) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                                   [test_id, question_text, option_a, option_b, option_c, option_d, correct_option, image_path])
                else:
                    try:
                        cur.execute("INSERT INTO questions (test_id, question_text, option_a, option_b, option_c, option_d, correct_option, category_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                                   [test_id, question_text, option_a, option_b, option_c, option_d, correct_option, category_id])
                    except:
                        cur.execute("INSERT INTO questions (test_id, question_text, option_a, option_b, option_c, option_d, correct_option) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                                   [test_id, question_text, option_a, option_b, option_c, option_d, correct_option])
            
            flash('Test created successfully', 'success')
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('admin_dashboard'))
    
    return render_template('create_test.html', categories=categories)

@app.route('/update-warning-limit', methods=['POST'])
def update_warning_limit():
    if 'logged_in' not in session or session['user_type'] != 'admin':
        flash('Please log in as an admin to access this page', 'danger')
        return redirect(url_for('login'))
    
    try:
        new_limit = int(request.form.get('max_warnings', '3'))
        if new_limit < 1:
            raise ValueError('Warning limit must be at least 1')
        if new_limit > 20:
            raise ValueError('Warning limit too high (max 20)')
        cur = mysql.connection.cursor()
        # Upsert setting
        cur.execute("SELECT id FROM settings WHERE `key` = %s", ['max_warnings'])
        exists = cur.fetchone()
        if exists:
            cur.execute("UPDATE settings SET `value` = %s WHERE `key` = %s", [str(new_limit), 'max_warnings'])
        else:
            cur.execute("INSERT INTO settings (`key`, `value`) VALUES (%s, %s)", ['max_warnings', str(new_limit)])
        mysql.connection.commit()
        cur.close()
        flash('Warnings limit updated successfully', 'success')
    except ValueError as ve:
        flash(str(ve), 'danger')
    except Exception as e:
        flash('Failed to update warnings limit: ' + str(e), 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/available-tests')
def available_tests():
    if 'logged_in' not in session or session['user_type'] != 'user':
        flash('Please log in as a user to access this page', 'danger')
        return redirect(url_for('login'))
    
    # Get available tests
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM tests")
    tests = list(cur.fetchall())
    
    # Add attempt info
    for test in tests:
        cur.execute("SELECT COUNT(*) as count FROM results WHERE user_id = %s AND test_id = %s", [session['user_id'], test['id']])
        result = cur.fetchone()
        test['attempts_count'] = result['count']
        
        # Ensure max_attempts is set (default 1)
        if 'max_attempts' not in test or test['max_attempts'] is None:
             test['max_attempts'] = 1

    cur.close()
    
    return render_template('available_tests.html', tests=tests)

@app.route('/take-test/<int:test_id>')
def take_test(test_id):
    if 'logged_in' not in session or session['user_type'] != 'user':
        flash('Please log in as a user to access this page', 'danger')
        return redirect(url_for('login'))
    
    # Get test details
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM tests WHERE id = %s", [test_id])
    test = cur.fetchone()
    
    if not test:
        flash('Test not found', 'danger')
        return redirect(url_for('available_tests'))
    
    # Check max attempts
    try:
        # We already have test data as dict, so we can use it directly if max_attempts is in it
        # But to be safe and consistent with existing logic, let's keep the separate check or use the dict
        # The original code did a separate query for max_attempts, which is redundant if we have * from tests
        # However, let's stick to the structure but use the dict values where possible
        
        max_attempts_limit = test.get('max_attempts', 1)
        if max_attempts_limit is None:
            max_attempts_limit = 1
            
        cur.execute("SELECT COUNT(*) as count FROM results WHERE user_id = %s AND test_id = %s", [session['user_id'], test_id])
        res = cur.fetchone()
        attempts_count = res['count']
        
        if attempts_count >= max_attempts_limit:
            flash(f'You have reached the maximum number of attempts ({max_attempts_limit}) for this test.', 'warning')
            return redirect(url_for('available_tests'))
    except Exception as e:
        print(f"Error checking attempts: {e}")

    # Debug: Print test data
    print(f"Test data: {test}")
    
    # Check shuffle status
    should_shuffle = bool(test.get('shuffle_questions', 0))

    # Get questions
    # cur is already DictCursor
    cur.execute("SELECT * FROM questions WHERE test_id = %s", [test_id])
    questions = list(cur.fetchall())
    cur.close()
    
    # Shuffle if enabled
    if should_shuffle:
        random.shuffle(questions)
    
    # Set test start time
    start_time = datetime.datetime.now().timestamp()
    session['test_start_time'] = start_time
    session['test_id'] = test_id
    
    # Handle duration - ensure it's a valid integer, default to 15 minutes if invalid
    try:
        duration = int(test['duration']) if test.get('duration') and str(test['duration']).strip() else 15
    except (ValueError, TypeError):
        duration = 15
    session['test_duration'] = duration
    
    # Determine per-test max warnings; fallback to global if not present
    try:
        max_warnings = int(test['max_warnings']) if test.get('max_warnings') is not None else int(get_setting('max_warnings', '3'))
    except (ValueError, TypeError):
        max_warnings = int(get_setting('max_warnings', '3'))

    # Initialize current question number, bookmarks, and user answers
    current_question_number = 1
    bookmarks = [False] * len(questions)
    user_answers = [None] * len(questions)
    
    return render_template('take_test_new.html', test=test, questions=questions, start_time=start_time, 
                          current_question_number=current_question_number, bookmarks=bookmarks, user_answers=user_answers, max_warnings=max_warnings)

@app.route('/submit-answer', methods=['POST'])
def submit_answer():
    if 'logged_in' not in session or session['user_type'] != 'user':
        return jsonify({'status': 'error', 'message': 'Not logged in as user'})
    
    # Get form data
    question_id = request.form.get('question_id')
    answer = request.form.get('answer')
    test_id = session.get('test_id')
    
    if not question_id or not test_id:
        return jsonify({'status': 'error', 'message': 'Missing question ID or test ID'})
    
    # Store answer in session temporarily
    if 'user_answers' not in session:
        session['user_answers'] = {}
    
    session['user_answers'][question_id] = answer
    session.modified = True
    
    return jsonify({'status': 'success', 'message': 'Answer saved'})

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
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM questions WHERE test_id = %s", [test_id])
    questions = cur.fetchall()
    
    # Calculate score
    score = 0
    for question in questions:
        question_id = question['id']
        correct_option = question['correct_option']  # Correct option (A, B, C, or D)
        
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

    # Ensure user_answers table exists
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_answers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                test_id INT NOT NULL,
                result_id INT NOT NULL,
                question_id INT NOT NULL,
                selected_option VARCHAR(1),
                is_correct BOOLEAN,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE,
                FOREIGN KEY (result_id) REFERENCES results(id) ON DELETE CASCADE,
                FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
            )
        """)
    except Exception as e:
        # Fallback if FK constraints fail (e.g. if tables use MyISAM)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_answers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                test_id INT NOT NULL,
                result_id INT NOT NULL,
                question_id INT NOT NULL,
                selected_option VARCHAR(1),
                is_correct BOOLEAN
            )
        """)

    # Save detailed answers
    for question in questions:
        question_id = question['id']
        correct_option = question['correct_option']
        user_answer = request.form.get(f'answer_{question_id}', '')
        is_correct = (user_answer == correct_option)
        
        cur.execute("INSERT INTO user_answers (user_id, test_id, result_id, question_id, selected_option, is_correct) VALUES (%s, %s, %s, %s, %s, %s)",
            [session['user_id'], test_id, result_id, question_id, user_answer, is_correct])
            
    mysql.connection.commit()
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
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT r.*, t.name as test_name, t.duration, u.full_name, u.username 
        FROM results r 
        JOIN tests t ON r.test_id = t.id 
        JOIN users u ON r.user_id = u.id 
        WHERE r.id = %s
    """, [result_id])
    result = cur.fetchone()
    
    if not result or (session['user_type'] == 'user' and result['user_id'] != session['user_id']):
        flash('Result not found or you do not have permission to view it', 'danger')
        cur.close()
        return redirect(url_for('user_dashboard' if session['user_type'] == 'user' else 'admin_dashboard'))
    
    # Ensure user_answers table exists (in case it wasn't created yet)
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_answers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                test_id INT NOT NULL,
                result_id INT NOT NULL,
                question_id INT NOT NULL,
                selected_option VARCHAR(1),
                is_correct BOOLEAN,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE,
                FOREIGN KEY (result_id) REFERENCES results(id) ON DELETE CASCADE,
                FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
            )
        """)
    except Exception:
        # Fallback if FK constraints fail
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_answers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    test_id INT NOT NULL,
                    result_id INT NOT NULL,
                    question_id INT NOT NULL,
                    selected_option VARCHAR(1),
                    is_correct BOOLEAN
                )
            """)
        except Exception:
            pass

    # Get detailed user answers joined with questions
    query = """
        SELECT 
            q.id as question_id,
            q.question_text,
            q.option_a,
            q.option_b,
            q.option_c,
            q.option_d,
            q.correct_option,
            q.image_path,
            ua.selected_option,
            ua.is_correct
        FROM questions q
        LEFT JOIN user_answers ua ON q.id = ua.question_id AND ua.result_id = %s
        WHERE q.test_id = %s
    """
    cur.execute(query, [result_id, result['test_id']])
    detailed_results = cur.fetchall()
    
    # Get warning count
    cur.execute("SELECT COUNT(*) as count FROM warnings WHERE user_id = %s AND test_id = %s", [result['user_id'], result['test_id']])
    warning_res = cur.fetchone()
    warning_count = warning_res['count'] if warning_res else 0
    
    cur.close()
    
    total_questions = len(detailed_results)
    percentage = result['percentage']
    
    # Generate analysis
    analysis = {
        'strength': [],
        'weakness': [],
        'suggestions': []
    }
    
    if percentage >= 90:
        analysis['strength'].append("Excellent command over the subject matter.")
        analysis['suggestions'].append("Keep up the consistency. Try more advanced tests.")
    elif percentage >= 75:
        analysis['strength'].append("Good understanding of core concepts.")
        analysis['suggestions'].append("Review the questions you got wrong to close the gaps.")
    elif percentage >= 50:
        analysis['strength'].append("Fair understanding, but needs improvement.")
        analysis['suggestions'].append("Focus on fundamental concepts and practice more.")
    else:
        analysis['weakness'].append("Significant gaps in understanding.")
        analysis['suggestions'].append("Recommend a complete review of the study material and retaking the test after preparation.")
    
    return render_template('test_result.html', result=result, detailed_results=detailed_results, 
                           total_questions=total_questions, percentage=percentage, 
                           warning_count=warning_count, analysis=analysis)

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
        SELECT u.username, u.full_name, t.name, r.score, r.percentage, r.date_taken,
        (SELECT COUNT(*) FROM warnings w WHERE w.user_id = r.user_id AND w.test_id = r.test_id) as warning_count
        FROM results r 
        JOIN users u ON r.user_id = u.id 
        JOIN tests t ON r.test_id = t.id
        ORDER BY r.date_taken DESC
    """)
    
    results = cur.fetchall()
    
    # Get participation data
    cur.execute("SELECT id, username, full_name, email, created_at FROM users")
    all_users = cur.fetchall()
    
    # Get user_ids who have taken tests
    cur.execute("SELECT DISTINCT user_id FROM results")
    participating_users = set(row[0] for row in cur.fetchall())
    
    # Get test counts per user
    cur.execute("SELECT user_id, COUNT(*) FROM results GROUP BY user_id")
    test_counts = {row[0]: row[1] for row in cur.fetchall()}
    
    # Get warning counts per user
    cur.execute("SELECT user_id, COUNT(*) FROM warnings GROUP BY user_id")
    warning_counts = {row[0]: row[1] for row in cur.fetchall()}
    
    # Get category performance per result
    category_data = []
    try:
        cur.execute("""
            SELECT r.id, u.username, u.full_name, t.name as test_name, c.name as category_name, 
                   SUM(ua.is_correct) as correct_count, COUNT(ua.id) as total_count
            FROM user_answers ua
            JOIN results r ON ua.result_id = r.id
            JOIN users u ON r.user_id = u.id
            JOIN tests t ON r.test_id = t.id
            JOIN questions q ON ua.question_id = q.id
            JOIN categories c ON q.category_id = c.id
            GROUP BY r.id, c.id
        """)
        raw_cat_data = cur.fetchall()
        
        # Process into a dictionary keyed by result_id
        # Structure: result_id -> {username, full_name, test_name, categories: {cat_name: percentage}}
        processed_data = {}
        all_categories = set()
        
        for row in raw_cat_data:
            rid = row[0]
            username = row[1]
            full_name = row[2]
            test_name = row[3]
            cat_name = row[4]
            correct = row[5]
            total = row[6]
            percentage = (correct / total * 100) if total > 0 else 0
            
            all_categories.add(cat_name)
            
            if rid not in processed_data:
                processed_data[rid] = {
                    'username': username,
                    'full_name': full_name,
                    'test_name': test_name,
                    'categories': {}
                }
            
            processed_data[rid]['categories'][cat_name] = round(percentage, 1)
            
        # Convert to list for DataFrame
        sorted_cats = sorted(list(all_categories))
        for rid, data in processed_data.items():
            row = [data['username'], data['full_name'], data['test_name']]
            for cat in sorted_cats:
                row.append(data['categories'].get(cat, 0))
            category_data.append(row)
            
        cat_columns = ['Username', 'Full Name', 'Test Name'] + sorted_cats
        
    except Exception as e:
        print(f"Error fetching category data: {e}")
        category_data = []
        cat_columns = ['Username', 'Full Name', 'Test Name']

    # Calculate Global Category Performance (Dashboard Data)
    global_category_performance = []
    try:
        cur.execute("""
            SELECT c.name, AVG(ua.is_correct) * 100 as average_percentage
            FROM user_answers ua
            JOIN questions q ON ua.question_id = q.id
            JOIN categories c ON q.category_id = c.id
            GROUP BY c.id, c.name
        """)
        cat_stats = cur.fetchall()
        for stat in cat_stats:
            global_category_performance.append([stat['name'], round(stat['average_percentage'], 1)])
            
        # Ensure all 4 sections are present
        existing_cats = set(item[0] for item in global_category_performance)
        default_categories = ['Quantitative', 'Logical Reasoning', 'Verbal Ability', 'General Awareness/Technical/Computer Basics']
        for cat in default_categories:
            if cat not in existing_cats:
                global_category_performance.append([cat, 0])
    except Exception as e:
        print(f"Error calculating global category stats: {e}")

    # Calculate Overall Test Performance (Dashboard Data)
    test_performance_data = []
    try:
        cur.execute("""
            SELECT t.name, AVG(r.percentage) as average_percentage
            FROM results r
            JOIN tests t ON r.test_id = t.id
            GROUP BY t.id, t.name
            ORDER BY t.created_at DESC
        """)
        test_stats = cur.fetchall()
        for stat in test_stats:
            test_performance_data.append([stat['name'], round(stat['average_percentage'], 1)])
    except Exception as e:
        print(f"Error calculating global test stats: {e}")
    
    cur.close()
    
    # Create a pandas DataFrame
    df = pd.DataFrame(results, columns=['Username', 'Full Name', 'Test Name', 'Score', 'Percentage', 'Date Taken', 'Cheating Warnings'])
    
    # Create Participation DataFrame
    participation_list = []
    for user in all_users:
        uid = user[0]
        username = user[1]
        full_name = user[2]
        email = user[3]
        joined = user[4]
        
        status = 'Participated' if uid in participating_users else 'Not Participated'
        count = test_counts.get(uid, 0)
        warnings = warning_counts.get(uid, 0)
        
        participation_list.append([username, full_name, email, status, count, warnings, joined])
        
    df_part = pd.DataFrame(participation_list, columns=['Username', 'Full Name', 'Email', 'Status', 'Tests Taken', 'Cheating Warnings', 'Joined Date'])
    
    # Create Category Analysis DataFrame
    df_cat = pd.DataFrame(category_data, columns=cat_columns)
    
    # Create Dashboard DataFrames
    df_global_cat = pd.DataFrame(global_category_performance, columns=['Section Name', 'Average Score (%)'])
    df_test_trend = pd.DataFrame(test_performance_data, columns=['Test Name', 'Average Score (%)'])

    # Create an in-memory Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Test Results', index=False)
        df_part.to_excel(writer, sheet_name='Participation Analysis', index=False)
        if not df_cat.empty:
            df_cat.to_excel(writer, sheet_name='Category Analysis', index=False)
        
        # Add Dashboard Data Sheets
        df_global_cat.to_excel(writer, sheet_name='Section Performance', index=False)
        df_test_trend.to_excel(writer, sheet_name='Test Trend Analysis', index=False)
        
        # Get the openpyxl workbook and worksheet objects
        workbook = writer.book
        
        # Format Test Results sheet
        worksheet = writer.sheets['Test Results']
        
        # Add some formatting
        from openpyxl.styles import Font, PatternFill, Alignment
        
        # Format header row
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4CAF50", end_color="4CAF50", fill_type="solid")
        
        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')
            
        # Adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
            
        # Format Participation Analysis sheet
        worksheet_part = writer.sheets['Participation Analysis']
        
        for cell in worksheet_part[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')
            
        # Adjust column widths for participation sheet
        for column in worksheet_part.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet_part.column_dimensions[column[0].column_letter].width = adjusted_width
            
        # Format Category Analysis sheet
        if 'Category Analysis' in writer.sheets:
            worksheet_cat = writer.sheets['Category Analysis']
            for cell in worksheet_cat[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal='center')
            
            for column in worksheet_cat.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet_cat.column_dimensions[column[0].column_letter].width = adjusted_width
        
        # Format Section Performance sheet
        if 'Section Performance' in writer.sheets:
            worksheet_sec = writer.sheets['Section Performance']
            for cell in worksheet_sec[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal='center')
            
            for column in worksheet_sec.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet_sec.column_dimensions[column[0].column_letter].width = adjusted_width

        # Format Test Trend Analysis sheet
        if 'Test Trend Analysis' in writer.sheets:
            worksheet_trend = writer.sheets['Test Trend Analysis']
            for cell in worksheet_trend[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal='center')
            
            for column in worksheet_trend.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet_trend.column_dimensions[column[0].column_letter].width = adjusted_width

        header_alignment = Alignment(horizontal="center", vertical="center")
        
        # Apply formatting to header row (re-applying to Test Results, but that's fine)
        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
        
        # Set column widths
        worksheet.column_dimensions['A'].width = 20  # Username column
        worksheet.column_dimensions['B'].width = 20  # Test Name column
        worksheet.column_dimensions['C'].width = 10  # Score column
        worksheet.column_dimensions['D'].width = 10  # Percentage column
        worksheet.column_dimensions['E'].width = 20  # Date Taken column
        worksheet.column_dimensions['F'].width = 20  # Cheating Warnings column
    
    # Set up the Http response
    output.seek(0)
    
    # Generate a timestamp for the filename
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'test_results_{timestamp}.xlsx'
    
    return send_file(output, download_name=filename, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/export_participation')
def export_participation():
    if 'logged_in' not in session or session['user_type'] != 'admin':
        flash('Please log in as an admin to access this page', 'danger')
        return redirect(url_for('login'))
    
    # Connect to database
    cur = mysql.connection.cursor()
    
    # Get participation data
    cur.execute("SELECT id, username, full_name, email, created_at FROM users")
    all_users = cur.fetchall()
    
    # Get user_ids who have taken tests
    cur.execute("SELECT DISTINCT user_id FROM results")
    participating_users = set(row[0] for row in cur.fetchall())
    
    # Get test counts per user
    cur.execute("SELECT user_id, COUNT(*) FROM results GROUP BY user_id")
    test_counts = {row[0]: row[1] for row in cur.fetchall()}
    
    # Get warning counts per user
    cur.execute("SELECT user_id, COUNT(*) FROM warnings GROUP BY user_id")
    warning_counts = {row[0]: row[1] for row in cur.fetchall()}
    
    cur.close()
    
    # Create Participation DataFrame
    participation_list = []
    for user in all_users:
        uid = user[0]
        username = user[1]
        full_name = user[2]
        email = user[3]
        joined = user[4]
        
        status = 'Participated' if uid in participating_users else 'Not Participated'
        count = test_counts.get(uid, 0)
        warnings = warning_counts.get(uid, 0)
        
        participation_list.append([username, full_name, email, status, count, warnings, joined])
        
    df_part = pd.DataFrame(participation_list, columns=['Username', 'Full Name', 'Email', 'Status', 'Tests Taken', 'Cheating Warnings', 'Joined Date'])
    
    # Create an in-memory Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_part.to_excel(writer, sheet_name='Participation Analysis', index=False)
        
        # Get the openpyxl workbook and worksheet objects
        worksheet_part = writer.sheets['Participation Analysis']
        
        # Add some formatting
        from openpyxl.styles import Font, PatternFill, Alignment
        
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4CAF50", end_color="4CAF50", fill_type="solid")
        
        for cell in worksheet_part[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')
            
        # Adjust column widths for participation sheet
        for column in worksheet_part.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet_part.column_dimensions[column[0].column_letter].width = adjusted_width
            
    # Set up the Http response
    output.seek(0)
    
    # Generate a timestamp for the filename
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'participation_list_{timestamp}.xlsx'
    
    return send_file(output, download_name=filename, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@app.route('/export_analytics')
def export_analytics():
    if 'logged_in' not in session or session['user_type'] != 'admin':
        flash('Please log in as an admin to access this page', 'danger')
        return redirect(url_for('login'))
    
    # Connect to database
    cur = mysql.connection.cursor()
    
    # Calculate Global Category Performance (Dashboard Data)
    global_category_performance = []
    try:
        cur.execute("""
            SELECT c.name, AVG(ua.is_correct) * 100 as average_percentage
            FROM user_answers ua
            JOIN questions q ON ua.question_id = q.id
            JOIN categories c ON q.category_id = c.id
            GROUP BY c.id, c.name
        """)
        cat_stats = cur.fetchall()
        for stat in cat_stats:
            global_category_performance.append([stat['name'], round(stat['average_percentage'], 1)])
            
        # Ensure all 4 sections are present
        existing_cats = set(item[0] for item in global_category_performance)
        default_categories = ['Quantitative', 'Logical Reasoning', 'Verbal Ability', 'General Awareness/Technical/Computer Basics']
        for cat in default_categories:
            if cat not in existing_cats:
                global_category_performance.append([cat, 0])
    except Exception as e:
        print(f"Error calculating global category stats: {e}")

    # Calculate Overall Test Performance (Dashboard Data)
    test_performance_data = []
    try:
        cur.execute("""
            SELECT t.name, AVG(r.percentage) as average_percentage
            FROM results r
            JOIN tests t ON r.test_id = t.id
            GROUP BY t.id, t.name
            ORDER BY t.created_at DESC
        """)
        test_stats = cur.fetchall()
        for stat in test_stats:
            test_performance_data.append([stat['name'], round(stat['average_percentage'], 1)])
    except Exception as e:
        print(f"Error calculating global test stats: {e}")
    
    cur.close()
    
    # Create Dashboard DataFrames
    df_global_cat = pd.DataFrame(global_category_performance, columns=['Section Name', 'Average Score (%)'])
    df_test_trend = pd.DataFrame(test_performance_data, columns=['Test Name', 'Average Score (%)'])
    
    # Create an in-memory Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Add Dashboard Data Sheets
        df_global_cat.to_excel(writer, sheet_name='Section Performance', index=False)
        df_test_trend.to_excel(writer, sheet_name='Test Trend Analysis', index=False)
        
        # Get the openpyxl workbook and worksheet objects
        workbook = writer.book
        
        from openpyxl.styles import Font, PatternFill, Alignment
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4CAF50", end_color="4CAF50", fill_type="solid")
        
        # Format Section Performance sheet
        if 'Section Performance' in writer.sheets:
            worksheet_sec = writer.sheets['Section Performance']
            for cell in worksheet_sec[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal='center')
            
            for column in worksheet_sec.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet_sec.column_dimensions[column[0].column_letter].width = adjusted_width

        # Format Test Trend Analysis sheet
        if 'Test Trend Analysis' in writer.sheets:
            worksheet_trend = writer.sheets['Test Trend Analysis']
            for cell in worksheet_trend[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal='center')
            
            for column in worksheet_trend.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet_trend.column_dimensions[column[0].column_letter].width = adjusted_width
            
    # Set up the Http response
    output.seek(0)
    
    # Generate a timestamp for the filename
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'performance_analytics_{timestamp}.xlsx'
    
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
