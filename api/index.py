import os
import sys

# Ensure project root is in module search path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from web_app import app

# WSGI application handle for Vercel
app = app
