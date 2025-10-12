#!/usr/bin/env python3
"""
Comprehensive Lie Detection Reporting System Demo
Shows how to integrate S3 storage with MongoDB reporting for user activity tracking
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Database.db_connection import get_database_connection
from Database.operations import (
    create_new_user, create_new_session,
    add_voice_data_s3, add_face_data_s3, add_text_data_s3,
    create_user_report_record, create_session_summary_report_record,
    get_user_reports, get_reports_dashboard_data
)
from Database.s3_storage import upload_data_to_s3

def demonstrate_reporting_system():
    """Demonstrate the complete reporting system with S3 integration"""

    print("📊 Lie Detection Reporting System Demo")
    print("=" * 60)

    try:
        # Connect to database
        client, db = get_database_connection()

        # 1. Create demo user and session
        print("1️⃣ Creating demo user and session...")
        user_id = create_new_user("john_doe", "john@example.com", "password123")
        session_id = create_new_session(user_id)
        print(f"   ✅ Created user: {user_id}")
        print(f"   ✅ Created session: {session_id}")

        # 2. Simulate uploading data to S3 and storing in MongoDB
        print("\n2️⃣ Uploading analysis data to S3...")

        # Voice analysis data
        voice_analysis = {
            "transcription": "I went to the store and bought groceries yesterday",
            "emotion_scores": {"confidence": 0.75, "stress": 0.3, "excitement": 0.1},
            "acoustic_features": {"pitch_variation": 0.85, "speech_rate": 120},
            "deception_probability": 0.25
        }

        # Face analysis data
        face_analysis = {
            "emotion_timeline": [
                {"timestamp": 0, "emotion": "neutral", "confidence": 0.8},
                {"timestamp": 15, "emotion": "slight_smile", "confidence": 0.6},
                {"timestamp": 30, "emotion": "neutral", "confidence": 0.9}
            ],
            "micro_expressions": ["brow_furrow", "eye_dart"],
            "facial_symmetry": 0.92,
            "deception_indicators": ["avoidance_gaze", "inconsistent_smile"]
        }

        # Text analysis data
        text_analysis = {
            "sentiment_score": 0.1,
            "linguistic_features": {
                "word_count": 8,
                "complexity_score": 0.3,
                "hedging_words": 0,
                "sensory_words": 1
            },
            "deception_indicators": ["lack_of_detail", "vague_timeline"],
            "overall_risk": 0.4
        }

        # Upload analysis data to S3 (simulated)
        voice_s3_url = "https://vericloud-media.s3.amazonaws.com/reports/voice_analysis.json"
        face_s3_url = "https://vericloud-media.s3.amazonaws.com/reports/face_analysis.json"
        text_s3_url = "https://vericloud-media.s3.amazonaws.com/reports/text_analysis.json"

        print("   📤 Uploaded voice analysis report to S3")
        print("   📤 Uploaded face analysis report to S3")
        print("   📤 Uploaded text analysis report to S3")

        # 3. Create individual analysis reports
        print("\n3️⃣ Creating analysis reports...")

        voice_report_id = create_user_report_record(
            user_id=user_id,
            session_id=session_id,
            report_type="voice_analysis",
            data=voice_analysis,
            s3_file_path=voice_s3_url
        )
        print(f"   ✅ Voice analysis report: {voice_report_id}")

        face_report_id = create_user_report_record(
            user_id=user_id,
            session_id=session_id,
            report_type="face_analysis",
            data=face_analysis,
            s3_file_path=face_s3_url
        )
        print(f"   ✅ Face analysis report: {face_report_id}")

        text_report_id = create_user_report_record(
            user_id=user_id,
            session_id=session_id,
            report_type="text_analysis",
            data=text_analysis,
            s3_file_path=text_s3_url
        )
        print(f"   ✅ Text analysis report: {text_report_id}")

        # 4. Create session summary report
        print("\n4️⃣ Creating session summary report...")

        combined_analysis = {
            "overall_risk_score": 0.35,
            "confidence_level": 0.78,
            "analysis_summary": "Multiple indicators suggest moderate deception risk",
            "key_findings": [
                "Voice analysis shows stress indicators",
                "Facial micro-expressions detected",
                "Text analysis reveals lack of detail"
            ],
            "recommendations": [
                "Consider follow-up questions",
                "Request additional evidence",
                "Note conflicting indicators"
            ]
        }

        summary_s3_url = "https://vericloud-media.s3.amazonaws.com/reports/session_summary.pdf"

        summary_report_id = create_session_summary_report_record(
            session_id=session_id,
            user_id=user_id,
            summary_data=combined_analysis,
            s3_file_path=summary_s3_url
        )
        print(f"   ✅ Session summary report: {summary_report_id}")

        # 5. Demonstrate report retrieval
        print("\n5️⃣ Retrieving user reports...")

        user_reports = get_user_reports(user_id, limit=10)
        print(f"   📊 Total reports for user: {len(user_reports)}")

        # Show report types
        report_types = {}
        for report in user_reports:
            rtype = report.get('report_type', 'unknown')
            report_types[rtype] = report_types.get(rtype, 0) + 1

        print("   📋 Report breakdown:")
        for rtype, count in report_types.items():
            print(f"      • {rtype}: {count}")

        # 6. Get dashboard data
        print("\n6️⃣ Generating dashboard data...")
        dashboard = get_reports_dashboard_data(user_id, days=30)

        print(f"   📈 Reports in last 30 days: {dashboard['total_reports']}")
        print(f"   ✅ Completion rate: {dashboard['completion_rate']:.1f}%")
        print(f"   🎯 Average confidence: {dashboard['average_confidence']:.1f}")
        # 7. Show sample report structure
        print("\n7️⃣ Sample report data structure:")

        if user_reports:
            sample_report = user_reports[0]
            print(f"   📄 Report ID: {sample_report['_id']}")
            print(f"   🏷️  Type: {sample_report['report_type']}")
            print(f"   📅 Created: {sample_report['timestamp']}")
            print(f"   🔗 S3 File: {sample_report.get('s3_file_path', 'N/A')}")

            if 'data' in sample_report and sample_report['data']:
                data_keys = list(sample_report['data'].keys())[:3]  # Show first 3 keys
                print(f"   📊 Data keys: {', '.join(data_keys)}")

        print("\n🎉 Reporting system demo complete!")

        print("\n📋 Available API Endpoints:")
        print("   GET  /api/reports/user/<user_id> - Get all user reports")
        print("   GET  /api/reports/session/<session_id> - Get session reports")
        print("   GET  /api/reports/user/<user_id>/stats - Get user statistics")
        print("   GET  /api/reports/user/<user_id>/dashboard - Get dashboard data")
        print("   POST /api/reports/create - Create new report")

        print("\n💾 Data Storage:")
        print("   • Report metadata stored in MongoDB (user_reports collection)")
        print("   • Large report files stored in S3 with links in MongoDB")
        print("   • Automatic indexing for fast queries")
        print("   • Cloud-connected for frontend access")

        return True

    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Reporting Demo...")
    success = demonstrate_reporting_system()

    if success:
        print("\n✅ Demo completed successfully!")
        print("\n🔧 Setup Requirements:")
        print("   1. Configure AWS S3 credentials in .env")
        print("   2. Create S3 bucket 'vericloud-media'")
        print("   3. Set up frontend to call the report API endpoints")
        print("   4. Reports will be accessible via REST API")
    else:
        print("\n💥 Demo failed - check your MongoDB connection and AWS credentials")
