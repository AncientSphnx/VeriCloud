"""
Script to verify and re-export the face model in correct format.
Run this to ensure the model files are not corrupted.
"""
import os
import sys
import joblib
import xgboost as xgb

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def verify_and_export_models():
    """Verify existing models and export in correct format."""
    
    model_dir = os.path.dirname(__file__)
    
    # Try to load the PKL model
    pkl_path = os.path.join(model_dir, 'effective_lie_detector_model.pkl')
    json_path = os.path.join(model_dir, 'effective_lie_detector_model.json')
    scaler_path = os.path.join(model_dir, 'effective_feature_scaler.pkl')
    
    print("=" * 60)
    print("FACE MODEL VERIFICATION AND EXPORT")
    print("=" * 60)
    
    # Check if files exist
    print(f"\n[CHECK] PKL model exists: {os.path.exists(pkl_path)}")
    print(f"[CHECK] JSON model exists: {os.path.exists(json_path)}")
    print(f"[CHECK] Scaler exists: {os.path.exists(scaler_path)}")
    
    if not os.path.exists(pkl_path):
        print("\n❌ ERROR: PKL model not found!")
        return False
    
    # Try loading the PKL model
    print("\n[STEP 1] Loading PKL model...")
    try:
        model = joblib.load(pkl_path)
        print(f"✅ Successfully loaded PKL model: {type(model)}")
    except Exception as e:
        print(f"❌ Failed to load PKL model: {e}")
        return False
    
    # Try loading the scaler
    print("\n[STEP 2] Loading scaler...")
    try:
        scaler = joblib.load(scaler_path)
        print(f"✅ Successfully loaded scaler: {type(scaler)}")
    except Exception as e:
        print(f"❌ Failed to load scaler: {e}")
        return False
    
    # Export model to JSON format
    print("\n[STEP 3] Exporting model to JSON format...")
    try:
        if isinstance(model, xgb.XGBClassifier):
            model.save_model(json_path)
            print(f"✅ Successfully exported model to JSON: {json_path}")
            
            # Verify the JSON file
            json_size = os.path.getsize(json_path)
            print(f"   JSON file size: {json_size} bytes")
            
            # Try loading it back
            test_model = xgb.XGBClassifier()
            test_model.load_model(json_path)
            print(f"✅ JSON model verification successful!")
        else:
            print(f"⚠️  Model is not XGBClassifier, it's: {type(model)}")
            print("   Attempting to save anyway...")
            model.save_model(json_path)
            print(f"✅ Model exported to JSON")
    except Exception as e:
        print(f"❌ Failed to export model to JSON: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ MODEL VERIFICATION COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Upload the following files to S3:")
    print(f"   - {json_path}")
    print(f"   - {scaler_path}")
    print("2. Use S3 paths:")
    print("   - models/face/v1/effective_lie_detector_model.json")
    print("   - models/face/v1/effective_feature_scaler.pkl")
    
    return True

if __name__ == "__main__":
    success = verify_and_export_models()
    sys.exit(0 if success else 1)
