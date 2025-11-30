"""
Entry point for the Database API on Render.
This module ensures proper Python path setup before importing the app.
"""
import sys
import os

# Add the project root to Python path so backend package can be imported
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import the app from the Database package
from backend.Database.api import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
