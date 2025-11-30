"""
Export model in a safe format that doesn't rely on XGBoost's internal serialization.
This creates a JSON file with model parameters that can be reconstructed.
"""
import os
import sys
import json
import joblib
import xgboost as xgb

sys.path.insert(0, os.path.dirname(__file__))

def safe_export_model():
    """Export model to safe JSON format with parameters."""
    
    model_dir = os.path.dirname(__file__)
    pkl_path = os.path.join(model_dir, 'effective_lie_detector_model.pkl')
    safe_json_path = os.path.join(model_dir, 'effective_lie_detector_model_safe.json')
    scaler_path = os.path.join(model_dir, 'effective_feature_scaler.pkl')
    
    print("=" * 60)
    print("SAFE MODEL EXPORT")
    print("=" * 60)
    
    # Load the original model
    print("\n[STEP 1] Loading original PKL model...")
    try:
        model = joblib.load(pkl_path)
        print(f"✅ Loaded: {type(model)}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Get model parameters
    print("\n[STEP 2] Extracting model parameters...")
    try:
        # For XGBoost models, we can get the booster
        if hasattr(model, 'get_booster'):
            booster = model.get_booster()
            # Get model as JSON string
            model_json_str = booster.save_raw('json')
            print(f"✅ Extracted model as JSON")
        else:
            print(f"⚠️  Model doesn't have get_booster method")
            return False
    except Exception as e:
        print(f"❌ Failed to extract: {e}")
        return False
    
    # Save to file
    print("\n[STEP 3] Saving to safe JSON format...")
    try:
        with open(safe_json_path, 'wb') as f:
            if isinstance(model_json_str, str):
                f.write(model_json_str.encode('utf-8'))
            else:
                f.write(model_json_str)
        file_size = os.path.getsize(safe_json_path)
        print(f"✅ Saved to: {safe_json_path}")
        print(f"   File size: {file_size} bytes")
    except Exception as e:
        print(f"❌ Failed to save: {e}")
        return False
    
    # Verify we can load it back
    print("\n[STEP 4] Verifying safe JSON can be loaded...")
    try:
        test_model = xgb.Booster()
        test_model.load_model(safe_json_path)
        print(f"✅ Verification successful!")
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ SAFE EXPORT COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Upload to S3:")
    print(f"   - {safe_json_path}")
    print(f"   - {scaler_path}")
    print("2. Update environment variable:")
    print("   FACE_MODEL_KEY=models/face/v1/effective_lie_detector_model_safe.json")
    
    return True

if __name__ == "__main__":
    success = safe_export_model()
    sys.exit(0 if success else 1)
