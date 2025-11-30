"""
Startup script for Database API (works both locally and on Render)
"""
import sys
import os

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(backend_dir)

sys.path.insert(0, project_root)
sys.path.insert(0, backend_dir)

# Now import and run the app
from backend.Database.api import app

if __name__ == "__main__":
    # Get port from environment (Render) or default to 5001 (local)
    port = int(os.environ.get('PORT', 5001))
    
    print("🚀 Starting VeriCloud Database API...")
    print(f"📍 Port: {port}")
    print("🗄️  MongoDB Atlas connecting...")
    print("🔧 Auto-save functionality enabled")
    print("=" * 50)
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Stopping database API...")
    except Exception as e:
        print(f"❌ Error starting API: {e}")
