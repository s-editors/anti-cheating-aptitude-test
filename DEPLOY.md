# Deployment Guide

This guide provides instructions for deploying the Aptitude Test Platform to a production environment.

## Prerequisites

- A cloud hosting provider (e.g., Render, Railway, Heroku, DigitalOcean).
- A MySQL database hosted in the cloud.
- Git installed on your local machine.

## Option 1: Deploy to Render (Recommended)

Render is a cloud platform that supports Python and MySQL.

### 1. Database Setup
1. Create a MySQL database on Render (or another provider like Aiven or PlanetScale).
2. Note down the **Host**, **Database Name**, **User**, and **Password**.
3. You will need to import your database schema. You can use a tool like MySQL Workbench or DBeaver to connect to the remote database and run the contents of `database_schema.sql`.

### 2. Web Service Setup
1. Push your code to a GitHub/GitLab repository.
2. Sign up/Log in to [Render](https://render.com).
3. Click "New +" and select "Web Service".
4. Connect your repository.
5. Configure the service:
   - **Name:** aptitude-test-platform
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
6. Scroll down to "Environment Variables" and add the following:
   - `PYTHON_VERSION`: `3.9.18` (or your local version)
   - `SECRET_KEY`: (Generate a random string)
   - `MYSQL_HOST`: (Your database host)
   - `MYSQL_USER`: (Your database user)
   - `MYSQL_PASSWORD`: (Your database password)
   - `MYSQL_DB`: (Your database name)

7. Click "Create Web Service".

## Option 2: Deploy to a VPS (Ubuntu)

If you are deploying to a Virtual Private Server (DigitalOcean, Linode, AWS EC2).

1. **Update System:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
   sudo apt install mysql-server pkg-config libmysqlclient-dev
   ```

2. **Clone Repository:**
   ```bash
   git clone <your-repo-url>
   cd tidu
   ```

3. **Install Dependencies:**
   ```bash
   pip3 install -r requirements.txt
   pip3 install gunicorn
   ```

4. **Setup Database:**
   ```bash
   sudo mysql
   # Inside MySQL shell:
   CREATE DATABASE aptitude_test_db;
   CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'secure_password';
   GRANT ALL PRIVILEGES ON aptitude_test_db.* TO 'app_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```
   Then import the schema:
   ```bash
   mysql -u app_user -p aptitude_test_db < database_schema.sql
   ```

5. **Configure Environment:**
   Create a `.env` file:
   ```bash
   nano .env
   ```
   Add:
   ```
   SECRET_KEY=your_generated_secret_key
   MYSQL_HOST=localhost
   MYSQL_USER=app_user
   MYSQL_PASSWORD=secure_password
   MYSQL_DB=aptitude_test_db
   ```

6. **Run with Gunicorn (Testing):**
   ```bash
   gunicorn --bind 0.0.0.0:8000 app:app
   ```

7. **Setup Nginx & Systemd (Production):**
   - Create a systemd service file to keep the app running.
   - Configure Nginx as a reverse proxy to port 8000.

## Local Production Test (Windows)

To run the app in a production-like mode on Windows, use `waitress`:

1. Install waitress:
   ```bash
   pip install waitress
   ```

2. Run the server:
   ```bash
   waitress-serve --port=8080 app:app
   ```
