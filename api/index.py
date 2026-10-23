import os
import sys
import traceback

# In Vercel serverless lambdas, home directory is read-only; use /tmp for caching
os.environ.setdefault("HF_HOME", "/tmp/huggingface")
os.environ.setdefault("TRANSFORMERS_CACHE", "/tmp/huggingface")

# Ensure project root is in module search path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from web_app import app
except Exception as e:
    err_msg = traceback.format_exc()
    from flask import Flask, Response
    app = Flask(__name__)
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def catch_all(path):
        return Response(f"Initialization Error:\n{err_msg}", mimetype="text/plain", status=500)
