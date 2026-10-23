import os
import sys

# Ensure temporary directory is used for HuggingFace caching if needed
os.environ.setdefault("HF_HOME", "/tmp/huggingface")
os.environ.setdefault("TRANSFORMERS_CACHE", "/tmp/huggingface")

# Ensure project root is in module search path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from web_app import app

# WSGI application handle for Vercel
app = app
