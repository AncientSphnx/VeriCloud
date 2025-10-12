"""
Database operations for the lie detection project.
This module provides CRUD operations for all collections.
"""
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
import hashlib
import os

from .db_connection import get_db
from .models import (
    create_user, create_session, create_voice_data,
    create_text_data, create_video_data, create_detection_result,
    create_storage_reference, create_voice_data_s3, create_face_data_s3, create_text_data_s3,
    create_user_report, create_session_summary_report
)

# Get database instance
db = get_db()

# Ensure indexes for performance and constraints
def setup_indexes():
    """Set up database indexes for performance and constraints"""
    # Users collection - email must be unique
    db.users.create_index("email", unique=True)
    
    # Sessions collection - index by user_id for faster queries
    db.sessions.create_index("user_id")
    
    # Data collections - index by session_id
    db.voice_data.create_index("session_id")
    db.text_data.create_index("session_id")
    db.video_data.create_index("session_id")
    
    # Results collection - index by session_id
    db.detection_results.create_index("session_id")
    
    # S3-based collections - index by session_id and data_type
    db.voice_data_s3.create_index([("session_id", 1), ("data_type", 1)])
    db.face_data_s3.create_index([("session_id", 1), ("data_type", 1)])
    db.text_data_s3.create_index([("session_id", 1), ("data_type", 1)])

    # Reports collection - index by user_id, session_id, and report_type
    db.user_reports.create_index([("user_id", 1), ("timestamp", -1)])
    db.user_reports.create_index([("session_id", 1), ("report_type", 1)])
    db.user_reports.create_index("timestamp")

# Helper function to hash passwords
def hash_password(password):
    """Hash a password for storing"""
    salt = os.urandom(32)  # 32 bytes = 256 bits
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000  # Number of iterations
    )
    return salt + key

# Helper function to verify passwords
def verify_password(stored_password, provided_password):
    """Verify a stored password against a provided password"""
    salt = stored_password[:32]  # 32 bytes = 256 bits
    stored_key = stored_password[32:]
    key = hashlib.pbkdf2_hmac(
        'sha256',
        provided_password.encode('utf-8'),
        salt,
        100000  # Number of iterations
    )
    return key == stored_key

# User operations
def create_new_user(name, email, password):
    """Create a new user with hashed password"""
    try:
        hashed_password = hash_password(password)
        user = create_user(name, email, hashed_password)
        result = db.users.insert_one(user)
        return str(result.inserted_id)
    except DuplicateKeyError:
        raise ValueError(f"User with email {email} already exists")

def get_user_by_id(user_id):
    """Get a user by ID"""
    return db.users.find_one({"_id": ObjectId(user_id)})

def get_user_by_email(email):
    """Get a user by email"""
    return db.users.find_one({"email": email})

def update_user(user_id, update_data):
    """Update user information"""
    # Don't allow email updates through this function to prevent duplicates
    if "email" in update_data:
        del update_data["email"]
    
    # Hash password if it's being updated
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])
    
    result = db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    return result.modified_count > 0

# Session operations
def create_new_session(user_id):
    """Create a new session for a user"""
    session = create_session(ObjectId(user_id))
    result = db.sessions.insert_one(session)
    return str(result.inserted_id)

def get_session(session_id):
    """Get a session by ID"""
    return db.sessions.find_one({"_id": ObjectId(session_id)})

def get_user_sessions(user_id):
    """Get all sessions for a user"""
    return list(db.sessions.find({"user_id": ObjectId(user_id)}).sort("start_time", -1))

def end_session(session_id):
    """End a session by setting its end time"""
    from datetime import datetime
    result = db.sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"end_time": datetime.utcnow(), "status": "completed"}}
    )
    return result.modified_count > 0

# Voice data operations
def add_voice_data(session_id, s3_file_path=None):
    """Add voice data to a session"""
    voice_data = create_voice_data(ObjectId(session_id), s3_file_path)
    result = db.voice_data.insert_one(voice_data)
    return str(result.inserted_id)

def get_voice_data(voice_data_id):
    """Get voice data by ID"""
    return db.voice_data.find_one({"_id": ObjectId(voice_data_id)})

def get_session_voice_data(session_id):
    """Get all voice data for a session"""
    return list(db.voice_data.find({"session_id": ObjectId(session_id)}))

def update_voice_features(voice_data_id, features):
    """Update extracted features for voice data"""
    result = db.voice_data.update_one(
        {"_id": ObjectId(voice_data_id)},
        {"$set": {"extracted_features": features, "processed": True}}
    )
    return result.modified_count > 0

# Text data operations
def add_text_data(session_id, input_text):
    """Add text data to a session"""
    text_data = create_text_data(ObjectId(session_id), input_text)
    result = db.text_data.insert_one(text_data)
    return str(result.inserted_id)

def get_text_data(text_data_id):
    """Get text data by ID"""
    return db.text_data.find_one({"_id": ObjectId(text_data_id)})

def get_session_text_data(session_id):
    """Get all text data for a session"""
    return list(db.text_data.find({"session_id": ObjectId(session_id)}))

def update_text_features(text_data_id, features):
    """Update extracted features for text data"""
    result = db.text_data.update_one(
        {"_id": ObjectId(text_data_id)},
        {"$set": {"extracted_features": features, "processed": True}}
    )
    return result.modified_count > 0

# Video data operations
def add_video_data(session_id, s3_file_path=None):
    """Add video data to a session"""
    video_data = create_video_data(ObjectId(session_id), s3_file_path)
    result = db.video_data.insert_one(video_data)
    return str(result.inserted_id)

def get_video_data(video_data_id):
    """Get video data by ID"""
    return db.video_data.find_one({"_id": ObjectId(video_data_id)})

def get_session_video_data(session_id):
    """Get all video data for a session"""
    return list(db.video_data.find({"session_id": ObjectId(session_id)}))

def update_video_features(video_data_id, features):
    """Update extracted features for video data"""
    result = db.video_data.update_one(
        {"_id": ObjectId(video_data_id)},
        {"$set": {"extracted_features": features, "processed": True}}
    )
    return result.modified_count > 0

# S3-based Voice data operations
def add_voice_data_s3(session_id, s3_file_path=None, file_metadata=None):
    """Add voice data with S3 storage to a session"""
    voice_data = create_voice_data_s3(ObjectId(session_id), s3_file_path, file_metadata)
    result = db.voice_data_s3.insert_one(voice_data)
    return str(result.inserted_id)

def get_voice_data_s3(voice_data_id):
    """Get S3-based voice data by ID"""
    return db.voice_data_s3.find_one({"_id": ObjectId(voice_data_id)})

def get_session_voice_data_s3(session_id):
    """Get all S3-based voice data for a session"""
    return list(db.voice_data_s3.find({"session_id": ObjectId(session_id)}))

def update_voice_analysis_s3(voice_data_id, analysis_results):
    """Update analysis results for S3-based voice data"""
    update_data = {"$set": {"processed": True}}
    if "analysis_features" in analysis_results:
        update_data["$set"]["analysis_features"] = analysis_results["analysis_features"]
    if "transcription" in analysis_results:
        update_data["$set"]["transcription"] = analysis_results["transcription"]
    if "emotion_scores" in analysis_results:
        update_data["$set"]["emotion_scores"] = analysis_results["emotion_scores"]

    result = db.voice_data_s3.update_one(
        {"_id": ObjectId(voice_data_id)},
        update_data
    )
    return result.modified_count > 0

# S3-based Face data operations
def add_face_data_s3(session_id, s3_file_path=None, file_metadata=None):
    """Add face data with S3 storage to a session"""
    face_data = create_face_data_s3(ObjectId(session_id), s3_file_path, file_metadata)
    result = db.face_data_s3.insert_one(face_data)
    return str(result.inserted_id)

def get_face_data_s3(face_data_id):
    """Get S3-based face data by ID"""
    return db.face_data_s3.find_one({"_id": ObjectId(face_data_id)})

def get_session_face_data_s3(session_id):
    """Get all S3-based face data for a session"""
    return list(db.face_data_s3.find({"session_id": ObjectId(session_id)}))

def update_face_analysis_s3(face_data_id, analysis_results):
    """Update analysis results for S3-based face data"""
    update_data = {"$set": {"processed": True}}
    if "analysis_features" in analysis_results:
        update_data["$set"]["analysis_features"] = analysis_results["analysis_features"]
    if "face_detections" in analysis_results:
        update_data["$set"]["face_detections"] = analysis_results["face_detections"]
    if "emotion_timeline" in analysis_results:
        update_data["$set"]["emotion_timeline"] = analysis_results["emotion_timeline"]
    if "micro_expressions" in analysis_results:
        update_data["$set"]["micro_expressions"] = analysis_results["micro_expressions"]

    result = db.face_data_s3.update_one(
        {"_id": ObjectId(face_data_id)},
        update_data
    )
    return result.modified_count > 0

# S3-based Text data operations
def add_text_data_s3(session_id, s3_file_path=None, text_content=None, file_metadata=None):
    """Add text data with S3 storage to a session"""
    text_data = create_text_data_s3(ObjectId(session_id), s3_file_path, text_content, file_metadata)
    result = db.text_data_s3.insert_one(text_data)
    return str(result.inserted_id)

def get_text_data_s3(text_data_id):
    """Get S3-based text data by ID"""
    return db.text_data_s3.find_one({"_id": ObjectId(text_data_id)})

def get_session_text_data_s3(session_id):
    """Get all S3-based text data for a session"""
    return list(db.text_data_s3.find({"session_id": ObjectId(session_id)}))

def update_text_analysis_s3(text_data_id, analysis_results):
    """Update analysis results for S3-based text data"""
    update_data = {"$set": {"processed": True}}
    if "analysis_features" in analysis_results:
        update_data["$set"]["analysis_features"] = analysis_results["analysis_features"]
    if "sentiment_score" in analysis_results:
        update_data["$set"]["sentiment_score"] = analysis_results["sentiment_score"]
    if "linguistic_features" in analysis_results:
        update_data["$set"]["linguistic_features"] = analysis_results["linguistic_features"]
    if "deception_indicators" in analysis_results:
        update_data["$set"]["deception_indicators"] = analysis_results["deception_indicators"]

    result = db.text_data_s3.update_one(
        {"_id": ObjectId(text_data_id)},
        update_data
    )
    return result.modified_count > 0

# Detection result operations
def add_detection_result(session_id, probability_score=None, final_label=None):
    """Add a detection result for a session"""
    result = create_detection_result(ObjectId(session_id), probability_score, final_label)
    result = db.detection_results.insert_one(result)
    return str(result.inserted_id)

def get_detection_result(result_id):
    """Get a detection result by ID"""
    return db.detection_results.find_one({"_id": ObjectId(result_id)})

def get_session_detection_result(session_id):
    """Get the detection result for a session"""
    return db.detection_results.find_one({"session_id": ObjectId(session_id)})

def update_detection_result(result_id, probability_score, final_label):
    """Update a detection result"""
    result = db.detection_results.update_one(
        {"_id": ObjectId(result_id)},
        {"$set": {"probability_score": probability_score, "final_label": final_label}}
    )
    return result.modified_count > 0

# Storage reference operations
def add_storage_reference(s3_location, data_type, session_id):
    """Add a storage reference"""
    reference = create_storage_reference(s3_location, data_type, ObjectId(session_id))
    result = db.storage_references.insert_one(reference)
    return str(result.inserted_id)

def get_storage_references(session_id, data_type=None):
    """Get storage references for a session, optionally filtered by data type"""
    query = {"session_id": ObjectId(session_id)}
    if data_type:
        query["data_type"] = data_type
    return list(db.storage_references.find(query))

# User Report operations
def create_user_report_record(user_id, session_id, report_type, data=None, s3_file_path=None):
    """Create a new user report record"""
    report = create_user_report(ObjectId(user_id), ObjectId(session_id), report_type, data, s3_file_path)
    result = db.user_reports.insert_one(report)
    return str(result.inserted_id)

def create_session_summary_report_record(session_id, user_id, summary_data=None, s3_file_path=None):
    """Create a session summary report record"""
    report = create_session_summary_report(ObjectId(session_id), ObjectId(user_id), summary_data, s3_file_path)
    result = db.user_reports.insert_one(report)
    return str(result.inserted_id)

def get_user_reports(user_id, limit=50, skip=0):
    """Get all reports for a specific user, ordered by timestamp (newest first)"""
    return list(db.user_reports.find(
        {"user_id": ObjectId(user_id)}
    ).sort("timestamp", -1).limit(limit).skip(skip))

def get_session_reports(session_id):
    """Get all reports for a specific session"""
    return list(db.user_reports.find({"session_id": ObjectId(session_id)}).sort("timestamp", -1))

def get_reports_by_type(user_id, report_type, limit=20):
    """Get reports of a specific type for a user"""
    return list(db.user_reports.find(
        {"user_id": ObjectId(user_id), "report_type": report_type}
    ).sort("timestamp", -1).limit(limit))

def get_user_report_stats(user_id):
    """Get statistics about user's reports"""
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id)}},
        {"$group": {
            "_id": "$report_type",
            "count": {"$sum": 1},
            "latest_report": {"$max": "$timestamp"},
            "avg_confidence": {"$avg": "$metadata.confidence_score"}
        }}
    ]

    stats = list(db.user_reports.aggregate(pipeline))

    # Also get total reports count
    total_reports = db.user_reports.count_documents({"user_id": ObjectId(user_id)})

    return {
        "total_reports": total_reports,
        "type_breakdown": stats,
        "most_recent_report": db.user_reports.find_one(
            {"user_id": ObjectId(user_id)},
            sort=[("timestamp", -1)]
        )
    }

def update_report_status(report_id, status, metadata_updates=None):
    """Update report status and metadata"""
    update_data = {"$set": {"status": status}}

    if metadata_updates:
        update_data["$set"]["metadata"] = metadata_updates

    result = db.user_reports.update_one(
        {"_id": ObjectId(report_id)},
        update_data
    )
    return result.modified_count > 0

def delete_user_reports(user_id, older_than_days=None):
    """Delete old reports for a user (optional: older than specified days)"""
    query = {"user_id": ObjectId(user_id)}

    if older_than_days:
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
        query["timestamp"] = {"$lt": cutoff_date}

    result = db.user_reports.delete_many(query)
    return result.deleted_count

def get_reports_dashboard_data(user_id, days=30):
    """Get dashboard data for user's recent reports"""
    from datetime import datetime, timedelta
    start_date = datetime.utcnow() - timedelta(days=days)

    # Get reports from the last N days
    recent_reports = list(db.user_reports.find({
        "user_id": ObjectId(user_id),
        "timestamp": {"$gte": start_date}
    }).sort("timestamp", -1))

    # Calculate statistics
    total_reports = len(recent_reports)
    completed_reports = len([r for r in recent_reports if r.get("status") == "completed"])

    # Get report type distribution
    type_counts = {}
    for report in recent_reports:
        report_type = report.get("report_type", "unknown")
        type_counts[report_type] = type_counts.get(report_type, 0) + 1

    # Get average confidence scores
    confidence_scores = [r.get("metadata", {}).get("confidence_score", 0)
                        for r in recent_reports if r.get("metadata", {}).get("confidence_score")]

    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

    return {
        "period_days": days,
        "total_reports": total_reports,
        "completed_reports": completed_reports,
        "completion_rate": (completed_reports / total_reports * 100) if total_reports > 0 else 0,
        "report_types": type_counts,
        "average_confidence": avg_confidence,
        "recent_reports": recent_reports[:10]  # Last 10 reports
    }