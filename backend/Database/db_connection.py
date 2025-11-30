import os
from urllib.parse import quote_plus
from pymongo import MongoClient, errors
from datetime import datetime

# Try to load environment variables, but don't fail if dotenv is not installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, use default values
    pass

# MongoDB Connection Configuration
MONGO_URI = os.getenv('MONGO_URI')

if MONGO_URI:
    # Use the complete URI from environment if available
    MONGODB_URI = MONGO_URI
    # Extract database name from URI for get_db() function
    MONGO_DB = MONGO_URI.split('/')[-1].split('?')[0] if '/' in MONGO_URI else 'LieDetection'
else:
    # Fallback to individual components
    MONGO_USER = os.getenv('MONGO_USER', 'admin')
    MONGO_PASS = os.getenv('MONGO_PASS', 'password')
    MONGO_HOST = os.getenv('MONGO_HOST', 'cluster.mongodb.net')
    MONGO_DB = os.getenv('MONGO_DB', 'LieDetection')

    # Build the MongoDB URI
    MONGODB_URI = f"mongodb+srv://{quote_plus(MONGO_USER)}:{quote_plus(MONGO_PASS)}@{MONGO_HOST}/{MONGO_DB}?retryWrites=true&w=majority"

def get_database_connection():
    """
    Establishes and returns a connection to the MongoDB database.
    
    Returns:
        tuple: (client, db) MongoDB client and database objects
    """
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        # Ping to check connection
        client.admin.command("ping")
        print("✅ Connected to MongoDB Atlas successfully")
        
        # Get database
        db = client[MONGO_DB]
        return client, db
        
    except errors.ServerSelectionTimeoutError as e:
        print("❌ Server selection timeout — check Network Access (IP whitelist) and your internet.")
        print(str(e))
        raise
    except errors.OperationFailure as e:
        print("❌ Authentication / operation failure — check username/password and roles.")
        print(str(e))
        raise
    except Exception as e:
        print("❌ Unexpected error:", str(e))
        raise

# Get a database connection
def get_db():
    """
    Returns the database object.
    
    Returns:
        pymongo.database.Database: MongoDB database object
    """
    _, db = get_database_connection()
    return db