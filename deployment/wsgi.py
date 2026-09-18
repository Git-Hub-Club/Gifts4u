import sys
import os

# Add the project directory to the path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# Import the app from main.py
from main import app as application

# app.py validates SESSION_SECRET and disables admin access when it is missing,
# blank, or shorter than the required minimum.
