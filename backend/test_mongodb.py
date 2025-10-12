#!/usr/bin/env python3
"""
Test MongoDB connection script
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Database.db_connection import get_database_connection

def test_connection():
    try:
        print("Testing MongoDB connection...")
        client, db = get_database_connection()
        print("✅ Successfully connected to MongoDB!")

        # Test database operations
        users_collection = db.users
        user_count = users_collection.count_documents({})
        print(f"📊 Current users in database: {user_count}")

        # Test creating a test user (optional)
        print("🔄 Testing user creation...")
        from Database.operations import create_new_user
        test_user_id = create_new_user("test_user", "test@example.com", "testpass123")
        print(f"✅ Test user created with ID: {test_user_id}")

        # Clean up test user
        users_collection.delete_one({"_id": test_user_id})
        print("🗑️  Test user cleaned up")

        return True

    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_connection()
    if success:
        print("\n🎉 MongoDB connection is working correctly!")
    else:
        print("\n💥 MongoDB connection failed. Please check your credentials and Atlas settings.")
