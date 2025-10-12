#!/usr/bin/env python3
"""
Simple MongoDB Collection Listing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Database.db_connection import get_database_connection

try:
    print("Connecting to MongoDB...")
    client, db = get_database_connection()

    collections = db.list_collection_names()
    collections.sort()

    print(f"\nFound {len(collections)} collections:")
    print("-" * 40)

    for collection in collections:
        count = db[collection].count_documents({})
        print(f"{collection} ({count} documents)")

    print("-" * 40)
    print("\nEssential collections (keep these):")
    print("• users, sessions, voice_data, text_data, video_data, detection_results, storage_references")

    print("\nPotentially unnecessary collections:")
    unnecessary = []
    for collection in collections:
        if collection not in ['users', 'sessions', 'voice_data', 'text_data', 'video_data', 'detection_results', 'storage_references']:
            unnecessary.append(collection)

    if unnecessary:
        for collection in unnecessary:
            print(f"• {collection}")
        print(f"\nYou can delete these {len(unnecessary)} collections if not needed.")
    else:
        print("All collections appear to be essential!")

except Exception as e:
    print(f"Error: {str(e)}")
