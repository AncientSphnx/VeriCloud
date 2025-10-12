#!/usr/bin/env python3
"""
Simple MongoDB Collection Listing Script
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Database.db_connection import get_database_connection

def list_all_collections():
    """List all collections with their document counts"""
    try:
        print("🔍 Checking MongoDB collections...")
        client, db = get_database_connection()

        collections = db.list_collection_names()
        collections.sort()  # Sort alphabetically

        if not collections:
            print("📭 No collections found in the database")
            return

        print(f"\n📋 Found {len(collections)} collections in your MongoDB database:")
        print("=" * 60)

        essential_collections = {
            'users': '👥 User accounts',
            'sessions': '🔄 Lie detection sessions',
            'voice_data': '🎤 Voice analysis data',
            'text_data': '📝 Text analysis data',
            'video_data': '🎥 Video analysis data',
            'detection_results': '📊 Analysis results',
            'storage_references': '💾 File references'
        }

        for collection in collections:
            count = db[collection].count_documents({})
            status = "✅ Essential" if collection in essential_collections else "❓ Maybe unnecessary"
            description = essential_collections.get(collection, "Unknown collection")

            print(f"📁 {collection}")
            print(f"   Documents: {count}")
            print(f"   Status: {status}")
            print(f"   Purpose: {description}")
            print()

        # Summary
        essential = [c for c in collections if c in essential_collections]
        potentially_unnecessary = [c for c in collections if c not in essential_collections]

        print("📊 Summary:")
        print(f"   • Essential collections: {len(essential)}")
        print(f"   • Potentially unnecessary: {len(potentially_unnecessary)}")

        if potentially_unnecessary:
            print("\n❓ Potentially unnecessary collections:")
            for coll in potentially_unnecessary:
                print(f"   • {coll}")
            print("\n💡 Recommendation: You can safely delete these if they're not needed:")
            print("   python -c \"from Database.db_connection import get_database_connection; client, db = get_database_connection(); db['COLLECTION_NAME'].drop(); print('✅ Deleted collection')\"")

        return collections

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

if __name__ == "__main__":
    list_all_collections()
