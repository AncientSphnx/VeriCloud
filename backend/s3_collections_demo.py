#!/usr/bin/env python3
"""
Example script showing how to use S3-based collections for lie detection
This demonstrates the schema with voice, face, and text data stored in S3
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Database.db_connection import get_database_connection
from Database.operations import create_new_user, create_new_session
from Database.operations import (
    add_voice_data_s3, add_face_data_s3, add_text_data_s3,
    get_session_voice_data_s3, get_session_face_data_s3, get_session_text_data_s3
)
from Database.s3_storage import upload_file_to_s3, upload_data_to_s3

def demonstrate_s3_collections():
    """Demonstrate S3-based collections for lie detection"""

    print("🎭 Lie Detection S3 Collections Demo")
    print("=" * 50)

    try:
        # Connect to database
        client, db = get_database_connection()

        # Create a test user and session
        print("1️⃣ Creating test user and session...")
        user_id = create_new_user("demo_user", "demo@example.com", "demo123")
        session_id = create_new_session(user_id)
        print(f"   ✅ Created session: {session_id}")

        # Simulate uploading voice file to S3
        print("\n2️⃣ Uploading voice data to S3...")
        voice_file_path = "demo_voice.wav"  # This would be the actual file path
        # In real usage, you'd upload an actual voice file
        # voice_s3_url = upload_file_to_s3(voice_file_path, "voice", session_id)

        # For demo, we'll simulate an S3 URL
        voice_s3_url = "https://vericloud-media.s3.amazonaws.com/voice/demo_session/voice_sample.wav"

        # Add voice data to MongoDB with S3 reference
        voice_metadata = {
            "duration": 30.5,
            "format": "wav",
            "sample_rate": 44100,
            "channels": 1
        }

        voice_data_id = add_voice_data_s3(
            session_id=session_id,
            s3_file_path=voice_s3_url,
            file_metadata=voice_metadata
        )
        print(f"   ✅ Added voice data: {voice_data_id}")

        # Simulate uploading face video to S3
        print("\n3️⃣ Uploading face data to S3...")
        face_file_path = "demo_face.mp4"  # This would be the actual video file
        # face_s3_url = upload_file_to_s3(face_file_path, "face", session_id)

        # For demo, simulate S3 URL
        face_s3_url = "https://vericloud-media.s3.amazonaws.com/face/demo_session/face_video.mp4"

        face_metadata = {
            "duration": 45.2,
            "fps": 30,
            "resolution": "1080p",
            "format": "mp4"
        }

        face_data_id = add_face_data_s3(
            session_id=session_id,
            s3_file_path=face_s3_url,
            file_metadata=face_metadata
        )
        print(f"   ✅ Added face data: {face_data_id}")

        # Add text data (can be stored directly in MongoDB or also in S3)
        print("\n4️⃣ Adding text data...")
        sample_text = """
        I went to the store yesterday and bought some groceries.
        The weather was nice and sunny. I had a great day overall.
        Everything went according to plan and I got home safely.
        """

        # You can also upload text to S3 if needed
        # text_s3_url = upload_data_to_s3(sample_text, "text", ".txt", session_id)

        text_data_id = add_text_data_s3(
            session_id=session_id,
            s3_file_path=None,  # Text can be stored directly in MongoDB
            text_content=sample_text.strip(),
            file_metadata={"length": len(sample_text), "type": "statement"}
        )
        print(f"   ✅ Added text data: {text_data_id}")

        # Retrieve and display the data
        print("\n5️⃣ Retrieving session data...")
        voice_data = get_session_voice_data_s3(session_id)
        face_data = get_session_face_data_s3(session_id)
        text_data = get_session_text_data_s3(session_id)

        print(f"   Voice files: {len(voice_data)}")
        print(f"   Face videos: {len(face_data)}")
        print(f"   Text entries: {len(text_data)}")

        # Show sample data structure
        if voice_data:
            print("\nSample voice data structure:")
            print(f"   S3 Path: {voice_data[0]['s3_file_path']}")
            print(f"   Duration: {voice_data[0]['file_metadata']['duration']}s")
            print(f"   Processed: {voice_data[0]['processed']}")

        if text_data:
            print("\nSample text data structure:")
            print(f"   Content length: {len(text_data[0]['text_content'])} characters")
            print(f"   Processed: {text_data[0]['processed']}")

        # Demonstrate updating analysis results
        print("\n6️⃣ Updating analysis results...")
        if voice_data:
            analysis_results = {
                "analysis_features": {"pitch_variation": 0.85, "speech_rate": 120},
                "transcription": "I went to the store yesterday and bought some groceries.",
                "emotion_scores": {"confidence": 0.7, "stress": 0.3}
            }
            from Database.operations import update_voice_analysis_s3
            update_voice_analysis_s3(voice_data[0]['_id'], analysis_results)
            print("   ✅ Updated voice analysis results")

        print("\n🎉 Demo complete! Your S3-based collections are ready.")
        print("\n📊 Schema Summary:")
        print("   • voice_data_s3 - Voice recordings stored in S3")
        print("   • face_data_s3 - Face/video data stored in S3")
        print("   • text_data_s3 - Text data (stored in MongoDB)")
        print("   • S3 URLs used for file references")
        print("   • Metadata and analysis results stored in MongoDB")

        return True

    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting S3 Collections Demo...")
    success = demonstrate_s3_collections()

    if success:
        print("\n✅ Demo completed successfully!")
        print("\n🔧 Next steps:")
        print("   1. Set your AWS credentials in .env file")
        print("   2. Create an S3 bucket named 'vericloud-media'")
        print("   3. Update your frontend to use these S3-based collections")
    else:
        print("\n💥 Demo failed - check your AWS credentials and S3 setup")
