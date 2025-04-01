import sys
import os

# Add the project directory to the path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# Import the app from main.py
from main import app as application

# Set a secret key in the application
application.secret_key = os.environ.get("SESSION_SECRET", "dev_key_for_testing")