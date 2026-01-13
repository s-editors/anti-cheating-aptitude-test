-- Database schema for aptitude_test_db

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create admins table
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

-- Populate default categories
INSERT IGNORE INTO categories (name) VALUES 
('Quantitative'), 
('Logical Reasoning'), 
('Verbal Ability'), 
('General Awareness/Technical/Computer Basics');

-- Create tests table
CREATE TABLE IF NOT EXISTS tests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    duration INT NOT NULL, -- in minutes
    admin_id INT NOT NULL,
    allow_review BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    max_warnings INT DEFAULT 3,
    shuffle_questions BOOLEAN DEFAULT FALSE,
    max_attempts INT DEFAULT 1,
    FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE CASCADE
);

-- Create questions table
CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    test_id INT NULL,
    category_id INT NULL,
    question_text TEXT NOT NULL,
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    option_d TEXT,
    correct_option TEXT NOT NULL, -- 'A', 'B', 'C', 'D', or text answer for short answer questions
    question_type VARCHAR(20) DEFAULT 'multiple_choice', -- 'multiple_choice', 'true_false', 'short_answer'
    points INT DEFAULT 1,
    image_path TEXT,
    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- Create results table
CREATE TABLE IF NOT EXISTS results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    test_id INT NOT NULL,
    score INT NOT NULL,
    percentage FLOAT NOT NULL,
    date_taken TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE
);

-- Create warnings table
CREATE TABLE IF NOT EXISTS warnings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    test_id INT NOT NULL,
    warning_type VARCHAR(50) NOT NULL, -- 'tab_switch', 'app_switch', 'shortcut_key', etc.
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE
);

-- Create settings table for global configuration
CREATE TABLE IF NOT EXISTS settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(100) NOT NULL UNIQUE,
    `value` VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert default warnings limit
INSERT INTO settings (`key`, `value`) VALUES ('max_warnings', '3')
ON DUPLICATE KEY UPDATE `value` = VALUES(`value`);

-- Insert default admin user (password: admin123)
INSERT IGNORE INTO admins (username, email, password) VALUES 
('admin', 'admin@example.com', '$2b$12$1xxxxxxxxxxxxxxxxxxxxuZLbwlOLrNZkLOdKiXQQJAx1nwp2vXW');

-- Insert demo user (password: demo123)
INSERT IGNORE INTO users (username, email, password) VALUES 
('demo_user', 'demo@example.com', '$2b$12$1xxxxxxxxxxxxxxxxxxxxuZLbwlOLrNZkLOdKiXQQJAx1nwp2vXW');
