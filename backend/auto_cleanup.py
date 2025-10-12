#!/usr/bin/env python3
"""
Auto-cleanup MongoDB collections
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Database.db_connection import get_database_connection

# Essential collections that should NOT be deleted
ESSENTIAL_COLLECTIONS = {
    'users', 'sessions', 'voice_data', 'text_data',
    'video_data', 'detection_results', 'storage_references'
}

def cleanup_collections():
    """Delete unnecessary collections"""
    try:
        print("🧹 Starting MongoDB cleanup...")
        client, db = get_database_connection()

        # Get all collections
        all_collections = db.list_collection_names()
        print(f"📋 Found {len(all_collections)} collections")

        unnecessary_collections = []
        essential_collections = []

        # Categorize collections
        for collection in all_collections:
            if collection in ESSENTIAL_COLLECTIONS:
                essential_collections.append(collection)
            else:
                unnecessary_collections.append(collection)

        print(f"\n✅ Essential collections ({len(essential_collections)}):")
        for coll in sorted(essential_collections):
            count = db[coll].count_documents({})
            print(f"   • {coll} ({count} documents)")

        if unnecessary_collections:
            print(f"\n🗑️  Unnecessary collections ({len(unnecessary_collections)}):")
            for coll in sorted(unnecessary_collections):
                count = db[coll].count_documents({})
                print(f"   • {coll} ({count} documents)")

            # Delete unnecessary collections
            deleted_count = 0
            for coll in unnecessary_collections:
                try:
                    db[coll].drop()
                    print(f"   ✅ Deleted: {coll}")
                    deleted_count += 1
                except Exception as e:
                    print(f"   ❌ Failed to delete {coll}: {str(e)}")

            print(f"\n🎉 Cleanup complete! Deleted {deleted_count} unnecessary collections.")
        else:
            print("\n✨ No unnecessary collections found - your database is clean!")

        return True

    except Exception as e:
        print(f"❌ Error during cleanup: {str(e)}")
        return False

if __name__ == "__main__":
    cleanup_collections()
