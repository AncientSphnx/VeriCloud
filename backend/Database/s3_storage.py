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

# ----------------------------
# Analysis-specific S3 functions
# ----------------------------

def upload_analysis_file(file_path, user_id, analysis_id, file_type):
    """
    Upload a file to S3 with organized structure: analyses/{user_id}/{analysis_id}/{file_type}
    
    Args:
        file_path (str): Local path to the file
        user_id (str): User ID for organizing files
        analysis_id (str): Analysis ID for organizing files
        file_type (str): Type of file ('video', 'audio', 'transcript')
        
    Returns:
        dict: Contains 's3_url', 's3_key', 'size_bytes', and 'format'
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Get file info
    file_extension = os.path.splitext(file_path)[1]
    file_size = os.path.getsize(file_path)
    
    # Determine filename based on type
    filename_map = {
        'video': f'video{file_extension}',
        'audio': f'audio{file_extension}',
        'transcript': f'transcript{file_extension}'
    }
    filename = filename_map.get(file_type, f'{file_type}{file_extension}')
    
    # Organize files: analyses/{user_id}/{analysis_id}/{filename}
    s3_key = f"analyses/{user_id}/{analysis_id}/{filename}"
    
    # Upload the file
    s3_client = get_s3_client()
    try:
        s3_client.upload_file(
            file_path, 
            S3_BUCKET_NAME, 
            s3_key,
            ExtraArgs={'ContentType': get_content_type(file_extension)}
        )
        
        # Generate the S3 URL
        s3_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
        
        return {
            's3_url': s3_url,
            's3_key': s3_key,
            'size_bytes': file_size,
            'format': file_extension.lstrip('.')
        }
    
    except ClientError as e:
        print(f"Error uploading analysis file to S3: {e}")
        raise

def upload_analysis_data(data, user_id, analysis_id, file_type, file_extension):
    """
    Upload data directly to S3 with organized structure
    
    Args:
        data (bytes or str): Data to upload
        user_id (str): User ID for organizing files
        analysis_id (str): Analysis ID for organizing files
        file_type (str): Type of file ('video', 'audio', 'transcript')
        file_extension (str): File extension (e.g., '.txt', '.json')
        
    Returns:
        dict: Contains 's3_url', 's3_key', 'size_bytes', and 'format'
    """
    # Determine filename based on type
    filename_map = {
        'video': f'video{file_extension}',
        'audio': f'audio{file_extension}',
        'transcript': f'transcript{file_extension}'
    }
    filename = filename_map.get(file_type, f'{file_type}{file_extension}')
    
    # Organize files: analyses/{user_id}/{analysis_id}/{filename}
    s3_key = f"analyses/{user_id}/{analysis_id}/{filename}"
    
    # Upload the data
    s3_client = get_s3_client()
    try:
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
            
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=data_bytes,
            ContentType=get_content_type(file_extension)
        )
        
        # Generate the S3 URL
        s3_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
        
        return {
            's3_url': s3_url,
            's3_key': s3_key,
            'size_bytes': len(data_bytes),
            'format': file_extension.lstrip('.')
        }
    
    except ClientError as e:
        print(f"Error uploading analysis data to S3: {e}")
        raise

def get_presigned_url_for_analysis(s3_key, expiration=3600):
    """
    Generate a presigned URL for viewing/downloading an analysis file
    
    Args:
        s3_key (str): S3 key of the file
        expiration (int): URL expiration time in seconds (default: 1 hour)
        
    Returns:
        str: Presigned URL for accessing the file
    """
    return generate_presigned_download_url(s3_key, expiration)

def delete_analysis_files(user_id, analysis_id):
    """
    Delete all files associated with an analysis
    
    Args:
        user_id (str): User ID
        analysis_id (str): Analysis ID
        
    Returns:
        int: Number of files deleted
    """
    s3_client = get_s3_client()
    prefix = f"analyses/{user_id}/{analysis_id}/"
    
    try:
        # List all objects with the prefix
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET_NAME,
            Prefix=prefix
        )
        
        if 'Contents' not in response:
            return 0
        
        # Delete all objects
        objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
        
        if objects_to_delete:
            s3_client.delete_objects(
                Bucket=S3_BUCKET_NAME,
                Delete={'Objects': objects_to_delete}
            )
        
        return len(objects_to_delete)
    
    except ClientError as e:
        print(f"Error deleting analysis files from S3: {e}")
        raise