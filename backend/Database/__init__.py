"""
VeriCloud Database Module
This package provides MongoDB database functionality for the lie detection project.
"""

from .db_connection import get_db, get_database_connection
from .models import (
    create_user, create_session, create_voice_data,
    create_text_data, create_video_data, create_detection_result,
    create_storage_reference, create_voice_data_s3, create_face_data_s3, create_text_data_s3
)
from .operations import (
    # User operations
    create_new_user, get_user_by_id, get_user_by_email, update_user,
    # Session operations
    create_new_session, get_session, get_user_sessions, end_session,
    # Voice data operations
    add_voice_data, get_voice_data, get_session_voice_data, update_voice_features,
    # Text data operations
    add_text_data, get_text_data, get_session_text_data, update_text_features,
    # S3-based Voice data operations
    add_voice_data_s3, get_voice_data_s3, get_session_voice_data_s3, update_voice_analysis_s3,
    # S3-based Face data operations
    add_face_data_s3, get_face_data_s3, get_session_face_data_s3, update_face_analysis_s3,
    # Report operations
    create_user_report_record, create_session_summary_report_record,
    get_user_reports, get_session_reports, get_reports_by_type, get_user_report_stats,
    update_report_status, delete_user_reports, get_reports_dashboard_data,
    # Index setup
    setup_indexes,
)
from .s3_storage import (
    upload_file_to_s3, upload_data_to_s3,
    generate_presigned_upload_url, generate_presigned_download_url
)
from .auth import (
    authenticate_user, generate_token, verify_token
)

# Database indexes are automatically set up when operations.py is imported