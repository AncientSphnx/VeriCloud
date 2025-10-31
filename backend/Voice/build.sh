#!/bin/bash
# Pre-download Voice model during build to cache it locally
echo "🔄 Pre-downloading Voice model from S3..."

python << 'EOF'
import os
import boto3
import tempfile

bucket = os.getenv("S3_BUCKET_NAME", "lie-detection-project")
model_key = os.getenv("VOICE_MODEL_KEY", "models/voice/v1/model_final2.pth")

try:
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("S3_REGION", "us-east-1")
    )
    
    # Create cache directory
    cache_dir = os.path.expanduser("~/.vericloud_cache")
    os.makedirs(cache_dir, exist_ok=True)
    
    local_path = os.path.join(cache_dir, os.path.basename(model_key))
    
    print(f"Downloading from s3://{bucket}/{model_key}")
    s3.download_file(bucket, model_key, local_path)
    print(f"✅ Model cached at {local_path}")
    
except Exception as e:
    print(f"⚠️ Could not pre-download model: {e}")
    print("Will download on first request instead")

EOF

echo "✅ Build script complete"
