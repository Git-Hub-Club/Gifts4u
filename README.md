# Gifts4u - eBook Directory Website

A lightweight, minimalist eBook sharing platform for discovering and managing digital resources with a clean, user-friendly interface.

## Deployment Guide for PythonAnywhere

### 1. Sign Up for PythonAnywhere
- Go to [PythonAnywhere.com](https://www.pythonanywhere.com/)
- Sign up for a free account

### 2. Set Up a Web App
- Click on the "Web" tab in the dashboard
- Click "Add a new web app"
- Select "Flask" as the framework
- Choose Python 3.8 or higher

### 3. Upload Your Files
- On PythonAnywhere, click the "Files" tab
- Create a new directory for your project (optional)
- Upload all the project files from this repository
  - app.py
  - main.py
  - data.json
  - /static folder
  - /templates folder

### 4. Configure the WSGI File
- Click on the "Web" tab
- Click on the WSGI configuration file link
- Replace the content with:

```python
import sys
path = '/home/YOUR_PYTHONANYWHERE_USERNAME/YOUR_PROJECT_PATH'
if path not in sys.path:
    sys.path.append(path)

from main import app as application
```

### 5. Install Dependencies
- Click on "Consoles" tab
- Start a new Bash console
- Navigate to your project directory
- Run: `pip3 install --user -r pythonanywhere_requirements.txt`

### 6. Restart Web App
- Go back to the "Web" tab
- Click the "Reload" button for your web app

Your site should now be live at: `YOUR_USERNAME.pythonanywhere.com`

## Admin Access
- Access the admin area at: `/admin`
- Set the `ADMIN_PASSWORD` environment variable before starting the app. Admin login is disabled when it is not configured.

## Maintenance
- The website stores all data in data.json
- Make regular backups of this file to preserve your data