"""
Verify local model is valid and provide S3 upload instructions.
"""
import os
import sys
import joblib
import boto3

sys.path.insert(0, os.path.dirname(__file__))

def verify_and_prepare_upload():
    """Verify model and prepare for S3 upload."""
    
    model_dir = os.path.dirname(__file__)
    pkl_path = os.path.join(model_dir, 'effective_lie_detector_model.pkl')
    scaler_path = os.path.join(model_dir, 'effective_feature_scaler.pkl')
    
    print("=" * 60)
    print("VERIFY LOCAL MODEL")
    print("=" * 60)
    
    # Check files exist
    print(f"\n[CHECK] PKL model exists: {os.path.exists(pkl_path)}")
    print(f"[CHECK] Scaler exists: {os.path.exists(scaler_path)}")
    
    if not os.path.exists(pkl_path) or not os.path.exists(scaler_path):
        print("❌ Files not found!")
        return False
    
    # Verify model can be loaded
    print("\n[STEP 1] Verifying model integrity...")
    try:
        model = joblib.load(pkl_path)
        print(f"✅ Model loaded: {type(model)}")
        print(f"   - Classes: {model.n_classes_}")
        print(f"   - Features: {model.n_features_in_}")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return False
    
    # Verify scaler
    print("\n[STEP 2] Verifying scaler...")
    try:
        scaler = joblib.load(scaler_path)
        print(f"✅ Scaler loaded: {type(scaler)}")
    except Exception as e:
        print(f"❌ Failed to load scaler: {e}")
        return False
    
    # Get file sizes
    pkl_size = os.path.getsize(pkl_path)
    scaler_size = os.path.getsize(scaler_path)
    
    print(f"\n[STEP 3] File sizes:")
    print(f"   - Model: {pkl_size} bytes")
    print(f"   - Scaler: {scaler_size} bytes")
    
    # Try to upload to S3
    print("\n[STEP 4] Uploading to S3...")
    try:
        s3 = boto3.client('s3')
        bucket = 'lie-detection-project'
        
        # Upload model
        model_key = 'models/face/v1/effective_lie_detector_model.pkl'
        print(f"   Uploading model to s3://{bucket}/{model_key}...")
        s3.upload_file(pkl_path, bucket, model_key)
        print(f"   ✅ Model uploaded")
        
        # Upload scaler
        scaler_key = 'models/face/v1/effective_feature_scaler.pkl'
        print(f"   Uploading scaler to s3://{bucket}/{scaler_key}...")
        s3.upload_file(scaler_path, bucket, scaler_key)
        print(f"   ✅ Scaler uploaded")
        
        print("\n✅ S3 UPLOAD SUCCESSFUL")
        
    except Exception as e:
        print(f"⚠️ S3 upload failed: {e}")
        print("\nManual upload instructions:")
        print(f"1. Upload {pkl_path}")
        print(f"   to: s3://lie-detection-project/models/face/v1/effective_lie_detector_model.pkl")
        print(f"2. Upload {scaler_path}")
        print(f"   to: s3://lie-detection-project/models/face/v1/effective_feature_scaler.pkl")
    
    print("\n" + "=" * 60)
    print("✅ VERIFICATION COMPLETE")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = verify_and_prepare_upload()
    sys.exit(0 if success else 1)
