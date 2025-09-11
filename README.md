# Aptitude Test Platform with Anti-Cheating Features

A comprehensive web application for conducting online aptitude tests with robust anti-cheating mechanisms. The platform includes separate modules for administrators and test takers, with features for test creation, test taking, and result management.

## Features

### User Module
- User registration and login
- View available tests
- Take tests with anti-cheating protection
- View test results and performance history
- Password reset functionality
- Demo user account for testing

### Admin Module
- Admin login with pre-saved main admin account
- Create and manage tests (Google Forms-like interface)
- View test results and statistics
- Manage other admin users (create/remove)
- Dashboard with analytics

### Anti-Cheating Measures
- Tab/application switching detection
- Keyboard shortcut monitoring (Ctrl+C, Ctrl+V, etc.)
- Right-click prevention
- Warning system with test termination after three warnings
- Logging of suspicious activities

## Installation

### Prerequisites
- Python 3.8 or higher
- MySQL 5.7 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository**
   ```
   git clone <repository-url>
   cd aptitude-test-platform
   ```

2. **Create and activate a virtual environment**
   ```
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Set up the database**
   - Create a MySQL database
   ```
   mysql -u username -p
   CREATE DATABASE aptitude_test_db;
   exit;
   ```
   - Import the database schema from `database_schema.sql`
   ```
   mysql -u username -p aptitude_test_db < database_schema.sql
   ```

5. **Configure the application**
   - Create a `.env` file in the project root with the following variables:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   MYSQL_HOST=localhost
   MYSQL_USER=your_mysql_username
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DB=aptitude_test_db
   ```

6. **Run the application**
   ```
   flask run
   ```

7. **Access the application**
   - Open a web browser and navigate to `http://localhost:5000`

## Default Credentials

### Admin
- Username: admin
- Password: admin123

### Demo User
- Username: demo
- Password: demo123

## Usage

### For Administrators
1. Log in using admin credentials
2. Create tests using the intuitive form interface
3. View test results and statistics
4. Manage other admin accounts (if you are the main admin)

### For Test Takers
1. Register a new account or log in with existing credentials
2. Browse available tests
3. Start a test and answer the questions
4. View your results after completing the test

## Database Structure

The application uses a MySQL database with the following tables:
- `users`: Stores user information
- `admins`: Stores admin information
- `tests`: Stores test information
- `questions`: Stores test questions and options
- `results`: Stores test results
- `warnings`: Stores anti-cheating warnings

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Authentication**: Flask-Login, Bcrypt
- **Form Handling**: Flask-WTF

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Bootstrap for the responsive UI components
- Font Awesome for the icons
- Flask and its extensions for the backend framework