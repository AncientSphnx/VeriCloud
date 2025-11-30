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
    create_user_report, create_session_summary_report, create_analysis_record
)

# Get database instance (lazy loading)
db = None

def get_database():
    """Get database instance with lazy loading"""
    global db
    if db is None:
        try:
            db = get_db()
            print("✅ Database connected successfully")
        except Exception as e:
            print(f"⚠️ Database connection failed: {e}")
            print("🔄 Running in memory mode - database operations will be skipped")
            db = None
    return db

# Ensure indexes for performance and constraints
def setup_indexes():
    """Set up database indexes for performance and constraints"""
    db_instance = get_database()
    if db_instance is None:
        print("⚠️ Skipping database setup - no connection available")
        return
    
    # Users collection - email must be unique
    db_instance.users.create_index("email", unique=True)
    
    # Sessions collection - index by user_id for faster queries
    db_instance.sessions.create_index("user_id")
    
    # Data collections - index by session_id
    db_instance.voice_data.create_index("session_id")
    db_instance.text_data.create_index("session_id")
    db_instance.video_data.create_index("session_id")
    
    # Results collection - index by session_id
    db_instance.detection_results.create_index("session_id")
    
    # S3-based collections - index by session_id and data_type
    db_instance.voice_data_s3.create_index([("session_id", 1), ("data_type", 1)])
    db_instance.face_data_s3.create_index([("session_id", 1), ("data_type", 1)])
    db_instance.text_data_s3.create_index([("session_id", 1), ("data_type", 1)])
    
    # Reports collection - index by user_id, session_id, and report_type
    db_instance.user_reports.create_index([("user_id", 1), ("timestamp", -1)])
    db_instance.user_reports.create_index([("session_id", 1), ("report_type", 1)])
    db_instance.user_reports.create_index("timestamp")
    
    # Analyses collection - index by user_id, analysis_id, and timestamp
    db_instance.analyses.create_index([("user_id", 1), ("timestamp", -1)])
    db_instance.analyses.create_index("analysis_id", unique=True)
    db_instance.analyses.create_index("session_id")
    db_instance.analyses.create_index("status")
    
    # Simple reports collection - index by user_id, module_type, and timestamp
    db_instance.simple_reports.create_index([("user_id", 1), ("timestamp", -1)])
    db_instance.simple_reports.create_index([("user_id", 1), ("module_type", 1)])
    db_instance.simple_reports.create_index("session_id")

# Initialize database indexes on module import
try:
    setup_indexes()
    print("✅ Database indexes initialized successfully")
except Exception as e:
    print(f"⚠️ Failed to initialize database indexes: {e}")
    # Continue without indexes - they can be created later

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

# ----------------------------
# Analysis operations (comprehensive analysis tracking)
# ----------------------------

def create_new_analysis(user_id, session_id, analysis_id):
    """
    Create a new analysis record
    
    Args:
        user_id (str): User ID
        session_id (str): Session ID
        analysis_id (str): Unique analysis identifier (UUID)
        
    Returns:
        str: MongoDB document ID
    """
    analysis = create_analysis_record(ObjectId(user_id), ObjectId(session_id), analysis_id)
    result = db.analyses.insert_one(analysis)
    return str(result.inserted_id)

def get_analysis_by_id(analysis_id):
    """
    Get an analysis by its analysis_id (UUID)
    
    Args:
        analysis_id (str): Analysis ID
        
    Returns:
        dict: Analysis document or None
    """
    return db.analyses.find_one({"analysis_id": analysis_id})

def get_analysis_by_mongo_id(mongo_id):
    """
    Get an analysis by its MongoDB _id
    
    Args:
        mongo_id (str): MongoDB document ID
        
    Returns:
        dict: Analysis document or None
    """
    return db.analyses.find_one({"_id": ObjectId(mongo_id)})

def get_user_analyses(user_id, limit=50, skip=0, status=None):
    """
    Get all analyses for a specific user
    
    Args:
        user_id (str): User ID
        limit (int): Maximum number of results
        skip (int): Number of results to skip (for pagination)
        status (str): Filter by status (optional)
        
    Returns:
        list: List of analysis documents
    """
    query = {"user_id": ObjectId(user_id)}
    if status:
        query["status"] = status
    
    return list(db.analyses.find(query).sort("timestamp", -1).limit(limit).skip(skip))

def get_session_analyses(session_id):
    """
    Get all analyses for a specific session
    
    Args:
        session_id (str): Session ID
        
    Returns:
        list: List of analysis documents
    """
    return list(db.analyses.find({"session_id": ObjectId(session_id)}).sort("timestamp", -1))

def update_analysis_files(analysis_id, file_type, file_data):
    """
    Update file information for an analysis
    
    Args:
        analysis_id (str): Analysis ID
        file_type (str): Type of file ('video', 'audio', 'transcript')
        file_data (dict): File data (s3_url, s3_key, size_bytes, etc.)
        
    Returns:
        bool: True if updated successfully
    """
    update_field = f"files.{file_type}"
    result = db.analyses.update_one(
        {"analysis_id": analysis_id},
        {"$set": {update_field: file_data}}
    )
    return result.modified_count > 0

def update_analysis_results(analysis_id, model_type, results_data):
    """
    Update prediction results for an analysis
    
    Args:
        analysis_id (str): Analysis ID
        model_type (str): Type of model ('text', 'voice', 'face', 'fusion')
        results_data (dict): Results data (prediction, confidence, features, etc.)
        
    Returns:
        bool: True if updated successfully
    """
    from datetime import datetime
    
    # Add processed timestamp
    results_data["processed_at"] = datetime.utcnow()
    
    update_field = f"results.{model_type}"
    result = db.analyses.update_one(
        {"analysis_id": analysis_id},
        {"$set": {update_field: results_data}}
    )
    return result.modified_count > 0

def update_analysis_status(analysis_id, status, metadata_updates=None):
    """
    Update analysis status and metadata
    
    Args:
        analysis_id (str): Analysis ID
        status (str): New status ('processing', 'completed', 'failed')
        metadata_updates (dict): Optional metadata updates
        
    Returns:
        bool: True if updated successfully
    """
    from datetime import datetime
    
    update_data = {"$set": {"status": status}}
    
    if status == "completed":
        update_data["$set"]["metadata.processing_end_time"] = datetime.utcnow()
    
    if metadata_updates:
        for key, value in metadata_updates.items():
            update_data["$set"][f"metadata.{key}"] = value
    
    result = db.analyses.update_one(
        {"analysis_id": analysis_id},
        update_data
    )
    return result.modified_count > 0

def add_analysis_error(analysis_id, error_message):
    """
    Add an error message to an analysis
    
    Args:
        analysis_id (str): Analysis ID
        error_message (str): Error message to add
        
    Returns:
        bool: True if updated successfully
    """
    from datetime import datetime
    
    error_entry = {
        "message": error_message,
        "timestamp": datetime.utcnow()
    }
    
    result = db.analyses.update_one(
        {"analysis_id": analysis_id},
        {"$push": {"metadata.errors": error_entry}}
    )
    return result.modified_count > 0

def delete_analysis(analysis_id):
    """
    Delete an analysis record
    
    Args:
        analysis_id (str): Analysis ID
        
    Returns:
        bool: True if deleted successfully
    """
    result = db.analyses.delete_one({"analysis_id": analysis_id})
    return result.deleted_count > 0

def get_user_analysis_stats(user_id):
    """
    Get statistics about user's analyses
    
    Args:
        user_id (str): User ID
        
    Returns:
        dict: Statistics including total, by status, recent analyses
    """
    user_obj_id = ObjectId(user_id)
    
    # Total analyses
    total = db.analyses.count_documents({"user_id": user_obj_id})
    
    # By status
    completed = db.analyses.count_documents({"user_id": user_obj_id, "status": "completed"})
    processing = db.analyses.count_documents({"user_id": user_obj_id, "status": "processing"})
    failed = db.analyses.count_documents({"user_id": user_obj_id, "status": "failed"})
    
    # Most recent analysis
    most_recent = db.analyses.find_one(
        {"user_id": user_obj_id},
        sort=[("timestamp", -1)]
    )
    
    # Get prediction distribution (from completed analyses)
    pipeline = [
        {"$match": {"user_id": user_obj_id, "status": "completed"}},
        {"$group": {
            "_id": "$results.fusion.final_prediction",
            "count": {"$sum": 1}
        }}
    ]
    prediction_distribution = list(db.analyses.aggregate(pipeline))
    
    return {
        "total_analyses": total,
        "completed": completed,
        "processing": processing,
        "failed": failed,
        "completion_rate": (completed / total * 100) if total > 0 else 0,
        "most_recent_analysis": most_recent,
        "prediction_distribution": prediction_distribution
    }

# ----------------------------
# Simple Report Operations (No AWS Required)
# ----------------------------

def create_simple_report(user_id, module_type, prediction, confidence, session_id=None):
    """
    Create a simple report without AWS S3 dependency
    
    Args:
        user_id (str): User ID
        module_type (str): 'text', 'voice', 'face'
        prediction (str): 'Truthful' or 'Deceptive'
        confidence (float): Confidence score (0-1)
        session_id (str): Optional session ID
        
    Returns:
        str: MongoDB document ID
    """
    from datetime import datetime
    
    # Create session if not provided
    if not session_id:
        session_id = str(create_new_session(user_id))
    
    report_data = {
        "user_id": ObjectId(user_id),
        "session_id": ObjectId(session_id),
        "module_type": module_type,
        "prediction": prediction,
        "confidence": confidence,
        "confidence_percentage": round(confidence * 100, 2),
        "timestamp": datetime.utcnow(),
        "status": "completed",
        "metadata": {
            "processing_time_ms": None,
            "model_version": "1.0",
            "source": "api_direct"
        }
    }
    
    result = db.simple_reports.insert_one(report_data)
    return str(result.inserted_id)

def get_user_simple_reports(user_id, limit=50, module_type=None):
    """
    Get simple reports for a user
    
    Args:
        user_id (str): User ID
        limit (int): Maximum number of results
        module_type (str): Filter by module type ('text', 'voice', 'face')
        
    Returns:
        list: List of simple report documents
    """
    query = {"user_id": ObjectId(user_id)}
    if module_type:
        query["module_type"] = module_type
    
    reports = list(db.simple_reports.find(query)
                   .sort("timestamp", -1)
                   .limit(limit))
    
    # Convert ObjectId to string for JSON serialization
    for report in reports:
        report["_id"] = str(report["_id"])
        report["user_id"] = str(report["user_id"])
        report["session_id"] = str(report["session_id"])
    
    return reports

def get_user_report_summary(user_id, days=30):
    """
    Get summary statistics for user's reports
    
    Args:
        user_id (str): User ID
        days (int): Number of days to look back
        
    Returns:
        dict: Summary statistics
    """
    from datetime import datetime, timedelta
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get recent reports
    query = {
        "user_id": ObjectId(user_id),
        "timestamp": {"$gte": start_date}
    }
    reports = list(db.simple_reports.find(query))
    
    if not reports:
        return {
            "total_reports": 0,
            "truthful_count": 0,
            "deceptive_count": 0,
            "average_confidence": 0,
            "module_breakdown": {},
            "recent_reports": []
        }
    
    # Calculate statistics
    total_reports = len(reports)
    truthful_count = len([r for r in reports if r["prediction"] == "Truthful"])
    deceptive_count = len([r for r in reports if r["prediction"] == "Deceptive"])
    average_confidence = sum(r["confidence"] for r in reports) / total_reports
    
    # Module breakdown
    module_breakdown = {}
    for report in reports:
        module = report["module_type"]
        if module not in module_breakdown:
            module_breakdown[module] = {
                "count": 0,
                "truthful": 0,
                "deceptive": 0,
                "avg_confidence": 0
            }
        module_breakdown[module]["count"] += 1
        if report["prediction"] == "Truthful":
            module_breakdown[module]["truthful"] += 1
        else:
            module_breakdown[module]["deceptive"] += 1
    
    # Calculate average confidence per module
    for module in module_breakdown:
        module_reports = [r for r in reports if r["module_type"] == module]
        module_breakdown[module]["avg_confidence"] = sum(r["confidence"] for r in module_reports) / len(module_reports)
    
    # Get recent reports (last 10)
    recent_reports = sorted(reports, key=lambda x: x["timestamp"], reverse=True)[:10]
    for report in recent_reports:
        report["_id"] = str(report["_id"])
        report["user_id"] = str(report["user_id"])
        report["session_id"] = str(report["session_id"])
    
    return {
        "total_reports": total_reports,
        "truthful_count": truthful_count,
        "deceptive_count": deceptive_count,
        "average_confidence": round(average_confidence * 100, 2),
        "module_breakdown": module_breakdown,
        "recent_reports": recent_reports
    }

def delete_simple_report(report_id):
    """Delete a single simple report by ID"""
    try:
        # Convert string ID to ObjectId
        object_id = ObjectId(report_id)
        
        # Delete the report
        result = db.simple_reports.delete_one({"_id": object_id})
        
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error deleting simple report: {e}")
        return False

def delete_all_user_simple_reports(user_id):
    """Delete all simple reports for a user"""
    try:
        # Convert string ID to ObjectId
        object_id = ObjectId(user_id)
        
        # Delete all reports for this user
        result = db.simple_reports.delete_many({"user_id": object_id})
        
        return result.deleted_count
    except Exception as e:
        print(f"Error deleting all user simple reports: {e}")
        return 0