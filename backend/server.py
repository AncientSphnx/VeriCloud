"""
Main server file for the VeriCloud application.
This file runs the Flask API server for authentication and database operations.
"""
import os
import sys
from Database.api import app

if __name__ == '__main__':
    try:
        # Use environment variables for configuration
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 5001))
        debug = os.getenv('DEBUG', 'True').lower() == 'true'

        print(f"Starting VeriCloud server on {host}:{port}")
        print(f"Debug mode: {debug}")

        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=True,
            threaded=True
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)