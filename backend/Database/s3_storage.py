"""
S3 integration for media storage in the lie detection project.
This module provides functions to upload and retrieve files from AWS S3.
"""
import boto3
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import uuid

load_dotenv()

# AWS S3 Configuration
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY', '')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY', '')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'vericloud-media')
S3_REGION = os.getenv('S3_REGION', 'us-east-1')

# Initialize S3 client
def get_s3_client():
    """Get an S3 client with the configured credentials"""
    return boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=S3_REGION
    )

# Upload a file to S3
def upload_file_to_s3(file_path, data_type, session_id=None):
    """
    Upload a file to S3 bucket
    
    Args:
        file_path (str): Local path to the file
        data_type (str): Type of data ('voice', 'video', 'text')
        session_id (str, optional): Session ID for organizing files
        
    Returns:
        str: S3 URL of the uploaded file
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Generate a unique filename
    file_extension = os.path.splitext(file_path)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Organize files by data type and session
    if session_id:
        s3_key = f"{data_type}/{session_id}/{unique_filename}"
    else:
        s3_key = f"{data_type}/{unique_filename}"
    
    # Upload the file
    s3_client = get_s3_client()
    try:
        s3_client.upload_file(file_path, S3_BUCKET_NAME, s3_key)
        
        # Generate the S3 URL
        s3_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
        return s3_url
    
    except ClientError as e:
        print(f"Error uploading file to S3: {e}")
        raise

# Upload data directly to S3 (for text or binary data)
def upload_data_to_s3(data, data_type, file_extension, session_id=None):
    """
    Upload data directly to S3 bucket
    
    Args:
        data (bytes or str): Data to upload
        data_type (str): Type of data ('voice', 'video', 'text')
        file_extension (str): File extension (e.g., '.txt', '.json')
        session_id (str, optional): Session ID for organizing files
        
    Returns:
        str: S3 URL of the uploaded file
    """
    # Generate a unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Organize files by data type and session
    if session_id:
        s3_key = f"{data_type}/{session_id}/{unique_filename}"
    else:
        s3_key = f"{data_type}/{unique_filename}"
    
    # Upload the data
    s3_client = get_s3_client()
    try:
        if isinstance(data, str):
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Body=data.encode('utf-8')
            )
        else:
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Body=data
            )
        
        # Generate the S3 URL
        s3_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
        return s3_url
    
    except ClientError as e:
        print(f"Error uploading data to S3: {e}")
        raise

# Generate a presigned URL for direct browser upload
def generate_presigned_upload_url(data_type, file_extension, session_id=None, expiration=3600):
    """
    Generate a presigned URL for direct browser upload to S3
    
    Args:
        data_type (str): Type of data ('voice', 'video', 'text')
        file_extension (str): File extension (e.g., '.wav', '.mp4')
        session_id (str, optional): Session ID for organizing files
        expiration (int, optional): URL expiration time in seconds (default: 1 hour)
        
    Returns:
        dict: Contains 'url' for the presigned URL and 's3_key' for the file location
    """
    # Generate a unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Organize files by data type and session
    if session_id:
        s3_key = f"{data_type}/{session_id}/{unique_filename}"
    else:
        s3_key = f"{data_type}/{unique_filename}"
    
    # Generate the presigned URL
    s3_client = get_s3_client()
    try:
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': S3_BUCKET_NAME,
                'Key': s3_key,
                'ContentType': get_content_type(file_extension)
            },
            ExpiresIn=expiration
        )
        
        # Generate the final S3 URL (for after upload)
        s3_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
        
        return {
            'presigned_url': presigned_url,
            's3_url': s3_url,
            's3_key': s3_key
        }
    
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        raise

# Generate a presigned URL for downloading a file
def generate_presigned_download_url(s3_key, expiration=3600):
    """
    Generate a presigned URL for downloading a file from S3
    
    Args:
        s3_key (str): S3 key of the file
        expiration (int, optional): URL expiration time in seconds (default: 1 hour)
        
    Returns:
        str: Presigned URL for downloading the file
    """
    s3_client = get_s3_client()
    try:
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': S3_BUCKET_NAME,
                'Key': s3_key
            },
            ExpiresIn=expiration
        )
        return presigned_url
    
    except ClientError as e:
        print(f"Error generating presigned download URL: {e}")
        raise

# Helper function to get content type based on file extension
def get_content_type(file_extension):
    """Get the content type based on file extension"""
    content_types = {
        '.wav': 'audio/wav',
        '.mp3': 'audio/mpeg',
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.txt': 'text/plain',
        '.json': 'application/json',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png'
    }
    return content_types.get(file_extension.lower(), 'application/octet-stream')