# Gifts4u - PythonAnywhere Deployment Guide

## Step 1: Create a PythonAnywhere Account
- Go to [PythonAnywhere.com](https://www.pythonanywhere.com/)
- Sign up for a free account

## Step 2: Upload Your Files
1. Log in to PythonAnywhere
2. Click on "Files" in the top menu
3. Create a new directory for your project (e.g., "gifts4u")
4. Upload all these files:
   - `app.py`
   - `main.py`
   - `wsgi.py`
   - `data.json`
   - `pythonanywhere_requirements.txt` (rename to `requirements.txt` after upload)
   - All files in `/static` folder (maintain the same folder structure)
   - All files in `/templates` folder (maintain the same folder structure)

## Step 3: Set Up Virtual Environment
1. Click on "Consoles" in the top menu
2. Start a new Bash console
3. Run these commands:
   ```bash
   cd gifts4u  # or whatever directory you created
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Step 4: Create a Web App
1. Click on "Web" in the top menu
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select Python 3.8 or higher
5. Enter your project path (e.g., `/home/yourusername/gifts4u`)

## Step 5: Configure WSGI File
1. On the web app configuration page, click on the link to the WSGI configuration file
2. Replace the contents with:
   ```python
   import sys
   import os

   # Add your project directory to the path
   path = '/home/yourusername/gifts4u'  # Change this to your actual path
   if path not in sys.path:
       sys.path.append(path)

   # Import the app
   from main import app as application

   # The app reads SESSION_SECRET from the environment. Admin access is
   # disabled when it is missing, blank, or shorter than 32 characters.
   ```

## Step 6: Configure Static Files
1. On the web app configuration page, scroll down to "Static files"
2. Add a new mapping:
   - URL: `/static/`
   - Directory: `/home/yourusername/gifts4u/static`

## Step 7: Set Environment Variables
1. On the web app configuration page, scroll down to "Environment variables"
2. Add these variables:
    - `ADMIN_PASSWORD` = Use at least 12 characters with at least 3 of uppercase, lowercase, number, or symbol
    - `SESSION_SECRET` = Generate a random value at least 32 characters long
3. Admin login is disabled unless both `ADMIN_PASSWORD` meets the strength requirement and a valid `SESSION_SECRET` are configured.

## Step 8: Reload Your Web App
1. Click the "Reload" button at the top of the web app configuration page

Your site should now be live at: `yourusername.pythonanywhere.com`

## Important Notes:
- The free tier of PythonAnywhere has CPU time and bandwidth limits
- Your site may sleep after periods of inactivity
- Make regular backups of your `data.json` file to preserve your data
- PythonAnywhere provides a simple command to pull changes from GitHub if you want to set that up