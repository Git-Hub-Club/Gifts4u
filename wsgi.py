import sys
import os

# Add the project directory to the path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# Import the app from main.py
from main import app as application

# Use the explicitly configured session signing key. Admin access is disabled
# by app.py when SESSION_SECRET is missing.
application.secret_key = os.environ.get("SESSION_SECRET", "").strip() or None
