# Deployment Guide

This guide provides instructions for deploying the Aptitude Test Platform.

## Recommended: Vercel (Frontend/Backend) + Supabase (Database)

This combination offers a generous free tier and easy setup.

### 1. Database Setup (Supabase)
1.  Go to [Supabase](https://supabase.com/) and sign up/log in.
2.  Create a new project.
3.  Go to the **SQL Editor** (sidebar).
4.  Open `database_schema_postgres.sql` from this repository, copy the content, paste it into the SQL Editor, and click **Run**.
5.  Go to **Project Settings** -> **Database**.
6.  Copy the **Connection String** (URI) mode. It should look like: `postgresql://postgres:[PASSWORD]@db.project.supabase.co:5432/postgres`.
    *   *Note: Replace `[PASSWORD]` with the database password you set in step 2.*

### 2. Application Deployment (Vercel)
1.  Push your code to a GitHub repository.
2.  Go to [Vercel](https://vercel.com/) and sign up/log in.
3.  Click **Add New...** -> **Project**.
4.  Import your GitHub repository.
5.  In the "Configure Project" screen:
    *   **Framework Preset:** Other (or Flask if detected, but usually Other/Python is fine).
    *   **Environment Variables:**
        *   `DATABASE_URL`: Paste your Supabase connection string.
        *   `SECRET_KEY`: Generate a random secure string (e.g., run `openssl rand -hex 32` in terminal).
6.  Click **Deploy**.

### Notes
- The application automatically detects if `DATABASE_URL` is present and switches to PostgreSQL mode.
- `vercel.json` is configured to serve the Flask app via serverless functions.

---

## Alternative: Render (MySQL)

### 1. Database Setup
1. Create a MySQL database on Render (or another provider).
2. Import `database_schema.sql` using a tool like MySQL Workbench or DBeaver.

### 2. Web Service Setup
1. Connect your repo to Render.
2. Set Build Command: `pip install -r requirements.txt`
3. Set Start Command: `gunicorn app:app`
4. Add Environment Variables:
   - `MYSQL_HOST`
   - `MYSQL_USER`
   - `MYSQL_PASSWORD`
   - `MYSQL_DB`
   - `SECRET_KEY`

---

## Local Development
1. Install dependencies: `pip install -r requirements.txt`
2. Create `.env` file based on `.env.example`.
3. Run `python app.py`.
