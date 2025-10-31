#!/bin/bash
# Pre-download Face model and scaler during build to cache them locally
echo "🔄 Pre-downloading Face model and scaler from S3..."

python << 'EOF'
import os
import boto3

bucket = os.getenv("S3_BUCKET_NAME", "lie-detection-project")
model_key = os.getenv("FACE_MODEL_KEY", "models/face/v1/effective_lie_detector_model.pkl")
scaler_key = os.getenv("FACE_SCALER_KEY", "models/face/v1/effective_feature_scaler.pkl")

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
    
    # Download model
    model_path = os.path.join(cache_dir, os.path.basename(model_key))
    print(f"Downloading model from s3://{bucket}/{model_key}")
    s3.download_file(bucket, model_key, model_path)
    print(f"✅ Model cached at {model_path}")
    
    # Download scaler
    scaler_path = os.path.join(cache_dir, os.path.basename(scaler_key))
    print(f"Downloading scaler from s3://{bucket}/{scaler_key}")
    s3.download_file(bucket, scaler_key, scaler_path)
    print(f"✅ Scaler cached at {scaler_path}")
    
except Exception as e:
    print(f"⚠️ Could not pre-download models: {e}")
    print("Will download on first request instead")

EOF

echo "✅ Build script complete"
