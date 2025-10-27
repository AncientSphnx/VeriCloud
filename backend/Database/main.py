"""
Entry point for the Database API on Render.
This module ensures proper Python path setup before importing the app.
"""
import sys
import os

# Add the parent directory (backend) to Python path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import the app
from api import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
