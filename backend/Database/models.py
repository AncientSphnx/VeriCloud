"""
MongoDB schema models for the lie detection project.
These models define the structure of documents in each collection.
"""
from datetime import datetime
from bson import ObjectId

# User model - with password instead of role as requested
def create_user(name, email, password):
    """
    Create a user document
    """
    return {
        "name": name,
        "email": email,
        "password": password,  # Note: In production, this should be hashed
        "created_at": datetime.utcnow()
    }

# Session model
def create_session(user_id):
    """
    Create a session document
    """
    return {
        "user_id": user_id,
        "start_time": datetime.utcnow(),
        "end_time": None,
        "status": "active"
    }

# Voice data model
def create_voice_data(session_id, s3_file_path=None):
    """
    Create a voice data document
    """
    return {
        "session_id": session_id,
        "file_path": s3_file_path,  # S3 bucket URL
        "timestamp": datetime.utcnow(),
        "extracted_features": None,
        "processed": False
    }

# Text data model
def create_text_data(session_id, input_text):
    """
    Create a text data document
    """
    return {
        "session_id": session_id,
        "input_text": input_text,
        "timestamp": datetime.utcnow(),
        "extracted_features": None,
        "processed": False
    }

# Video data model
def create_video_data(session_id, s3_file_path=None):
    """
    Create a video data document
    """
    return {
        "session_id": session_id,
        "file_path": s3_file_path,  # S3 bucket URL
        "timestamp": datetime.utcnow(),
        "extracted_features": None,
        "processed": False
    }

# Lie detection result model
def create_detection_result(session_id, probability_score=None, final_label=None):
    """
    Create a lie detection result document
    """
    return {
        "session_id": session_id,
        "probability_score": probability_score,
        "final_label": final_label,
        "timestamp": datetime.utcnow()
    }

# Voice data model (S3-based)
def create_voice_data_s3(session_id, s3_file_path=None, file_metadata=None):
    """
    Create a voice data document with S3 storage

    Args:
        session_id (str): Session ID
        s3_file_path (str): S3 URL of the voice file
        file_metadata (dict): Optional metadata about the file (duration, format, etc.)
    """
    return {
        "session_id": session_id,
        "data_type": "voice",
        "s3_file_path": s3_file_path,  # S3 URL instead of local file path
        "file_metadata": file_metadata or {},
        "timestamp": datetime.utcnow(),
        "processed": False,
        "analysis_features": None,  # Will store extracted features
        "transcription": None,  # Will store speech-to-text results
        "emotion_scores": None  # Will store emotion analysis results
    }

# Face/Video data model (S3-based)
def create_face_data_s3(session_id, s3_file_path=None, file_metadata=None):
    """
    Create a face data document with S3 storage

    Args:
        session_id (str): Session ID
        s3_file_path (str): S3 URL of the video/face file
        file_metadata (dict): Optional metadata about the file (duration, fps, etc.)
    """
    return {
        "session_id": session_id,
        "data_type": "face",
        "s3_file_path": s3_file_path,  # S3 URL instead of local file path
        "file_metadata": file_metadata or {},
        "timestamp": datetime.utcnow(),
        "processed": False,
        "analysis_features": None,  # Will store facial expression features
        "face_detections": None,  # Will store face detection results
        "emotion_timeline": None,  # Will store emotion changes over time
        "micro_expressions": None  # Will store micro-expression analysis
    }

# Text data model (S3-based)
def create_text_data_s3(session_id, s3_file_path=None, text_content=None, file_metadata=None):
    """
    Create a text data document with S3 storage

    Args:
        session_id (str): Session ID
        s3_file_path (str): S3 URL of the text file (optional)
        text_content (str): The actual text content (optional)
        file_metadata (dict): Optional metadata about the file
    """
    return {
        "session_id": session_id,
        "data_type": "text",
        "s3_file_path": s3_file_path,  # S3 URL for the text file
        "text_content": text_content,  # Store text content directly in MongoDB for analysis
        "file_metadata": file_metadata or {},
        "timestamp": datetime.utcnow(),
        "processed": False,
        "analysis_features": None,  # Will store text analysis features
        "sentiment_score": None,  # Will store sentiment analysis results
        "linguistic_features": None,  # Will store linguistic analysis results
        "deception_indicators": None  # Will store deception detection results
    }

# Report data model (comprehensive user activity tracking)
def create_user_report(user_id, session_id, report_type, data=None, s3_file_path=None):
    """
    Create a comprehensive user report document

    Args:
        user_id (str): User ID
        session_id (str): Session ID
        report_type (str): Type of report ('voice_analysis', 'face_analysis', 'text_analysis', 'combined_analysis', 'session_summary')
        data (dict): Report data and analysis results
        s3_file_path (str): S3 URL for detailed report files (PDFs, CSVs, etc.)
    """
    return {
        "user_id": user_id,
        "session_id": session_id,
        "report_type": report_type,
        "data": data or {},  # Analysis results, scores, insights
        "s3_file_path": s3_file_path,  # Link to detailed report file in S3
        "timestamp": datetime.utcnow(),
        "status": "completed",  # completed, processing, failed
        "version": "1.0",
        "metadata": {
            "analysis_timestamp": datetime.utcnow(),
            "processing_time_ms": None,
            "data_sources": [],  # List of data sources used (voice, face, text)
            "confidence_score": None,
            "report_format": "json"  # json, pdf, csv
        }
    }

# Session summary report model
def create_session_summary_report(session_id, user_id, summary_data=None, s3_file_path=None):
    """
    Create a session summary report with overall analysis

    Args:
        session_id (str): Session ID
        user_id (str): User ID
        summary_data (dict): Overall session analysis and conclusions
        s3_file_path (str): S3 URL for detailed summary report
    """
    return {
        "user_id": user_id,
        "session_id": session_id,
        "report_type": "session_summary",
        "data": summary_data or {},
        "s3_file_path": s3_file_path,
        "timestamp": datetime.utcnow(),
        "status": "completed",
        "summary": {
            "overall_risk_score": None,  # Combined deception probability
            "analysis_types": [],  # Types of analysis performed
            "key_findings": [],  # Key insights from all analyses
            "recommendations": [],  # Recommendations based on analysis
            "confidence_level": None,  # Overall confidence in results
            "session_duration": None,  # Total session time
            "data_quality_score": None  # Quality assessment of input data
        }
    }

# Storage reference model for S3 file tracking
def create_storage_reference(file_path, file_type, metadata=None):
    """
    Create a storage reference document for tracking S3 files

    Args:
        file_path (str): S3 URL of the file
        file_type (str): Type of file (voice, face, text, report)
        metadata (dict): Optional metadata about the file
    """
    return {
        "file_path": file_path,
        "file_type": file_type,
        "metadata": metadata or {},
        "timestamp": datetime.utcnow(),
        "status": "active"
    }

# Analysis record model (comprehensive analysis tracking with S3 integration)
def create_analysis_record(user_id, session_id, analysis_id):
    """
    Create a comprehensive analysis record for tracking complete analysis lifecycle

    Args:
        user_id (ObjectId): User ID
        session_id (ObjectId): Session ID
        analysis_id (str): Unique analysis identifier (UUID)
    """
    return {
        "analysis_id": analysis_id,
        "user_id": user_id,
        "session_id": session_id,
        "timestamp": datetime.utcnow(),
        "status": "processing",  # processing, completed, failed
        "files": {
            "video": {
                "s3_url": None,
                "s3_key": None,
                "size_bytes": None,
                "duration_seconds": None,
                "format": None
            },
            "audio": {
                "s3_url": None,
                "s3_key": None,
                "size_bytes": None,
                "duration_seconds": None,
                "format": None
            },
            "transcript": {
                "s3_url": None,
                "s3_key": None,
                "text_content": None,
                "word_count": None
            }
        },
        "results": {
            "text": {
                "prediction": None,
                "confidence": None,
                "features": None,
                "processed_at": None
            },
            "voice": {
                "prediction": None,
                "confidence": None,
                "features": None,
                "processed_at": None
            },
            "face": {
                "prediction": None,
                "confidence": None,
                "features": None,
                "processed_at": None
            },
            "fusion": {
                "final_prediction": None,
                "final_confidence": None,
                "final_score": None,
                "breakdown": None,
                "reasoning": None,
                "weights_used": None,
                "processed_at": None
            }
        },
        "metadata": {
            "upload_time": datetime.utcnow(),
            "processing_start_time": None,
            "processing_end_time": None,
            "total_processing_time_ms": None,
            "models_used": [],
            "errors": []
        },
        "version": "1.0"
    }