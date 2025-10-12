#!/usr/bin/env python3
"""
MongoDB Collection Management Script
Lists all collections and allows deletion of unnecessary ones
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Database.db_connection import get_database_connection

def list_collections():
    """List all collections in the database"""
    try:
        client, db = get_database_connection()
        collections = db.list_collection_names()

        if not collections:
            print("📭 No collections found in the database")
            return []

        print("📋 Collections in your MongoDB database:")
        print("=" * 50)

        for i, collection in enumerate(collections, 1):
            # Get document count for each collection
            count = db[collection].count_documents({})
            print(f"{i:2d}. {collection} ({count} documents)")

        print("=" * 50)
        return collections

    except Exception as e:
        print(f"❌ Error connecting to database: {str(e)}")
        return []

def delete_collection(collection_name):
    """Delete a specific collection"""
    try:
        client, db = get_database_connection()
        db[collection_name].drop()
        print(f"✅ Deleted collection: {collection_name}")
        return True
    except Exception as e:
        print(f"❌ Error deleting collection {collection_name}: {str(e)}")
        return False

def cleanup_database():
    """Main function to clean up the database"""
    print("🧹 MongoDB Collection Cleanup Tool")
    print("=" * 50)

    # List current collections
    collections = list_collections()

    if not collections:
        return

    print("\n📝 Essential collections you should keep:")
    print("   • users (for user accounts)")
    print("   • sessions (for lie detection sessions)")
    print("   • voice_data (for voice analysis data)")
    print("   • text_data (for text analysis data)")
    print("   • video_data (for video analysis data)")
    print("   • detection_results (for analysis results)")
    print("   • storage_references (for file references)")

    print("\n❓ Collections you might want to delete:")
    unnecessary = []

    for collection in collections:
        if collection not in ['users', 'sessions', 'voice_data', 'text_data', 'video_data', 'detection_results', 'storage_references']:
            unnecessary.append(collection)
            print(f"   • {collection}")

    if not unnecessary:
        print("   None found - all collections appear to be essential!")
        return

    print(f"\nFound {len(unnecessary)} potentially unnecessary collections.")

    # Ask user which collections to delete
    print("\nEnter collection names to delete (comma-separated), or 'all' to delete all unnecessary ones:")
    print("Examples: 'test_data,old_results' or 'all'")

    user_input = input("> ").strip()

    if user_input.lower() == 'all':
        collections_to_delete = unnecessary
    else:
        collections_to_delete = [c.strip() for c in user_input.split(',') if c.strip()]

    # Validate collection names
    valid_collections = []
    for collection in collections_to_delete:
        if collection in collections:
            valid_collections.append(collection)
        else:
            print(f"⚠️  Collection '{collection}' not found - skipping")

    if not valid_collections:
        print("No valid collections to delete.")
        return

    # Confirm deletion
    print(f"\n⚠️  You are about to delete {len(valid_collections)} collection(s):")
    for collection in valid_collections:
        count = db[collection].count_documents({})
        print(f"   • {collection} ({count} documents)")

    confirm = input("\nAre you sure? Type 'yes' to confirm: ").strip().lower()

    if confirm == 'yes':
        deleted_count = 0
        for collection in valid_collections:
            if delete_collection(collection):
                deleted_count += 1

        print(f"\n✅ Successfully deleted {deleted_count} collection(s)!")
    else:
        print("\n❌ Deletion cancelled.")

if __name__ == "__main__":
    cleanup_database()
