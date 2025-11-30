"""
Fix model corruption by extracting just the booster and re-pickling without XGBoost's problematic __setstate__.
"""
import os
import sys
import pickle
import joblib
import xgboost as xgb

sys.path.insert(0, os.path.dirname(__file__))

def fix_model_corruption():
    """Extract booster and save as safe pickle."""
    
    model_dir = os.path.dirname(__file__)
    pkl_path = os.path.join(model_dir, 'effective_lie_detector_model.pkl')
    safe_pkl_path = os.path.join(model_dir, 'effective_lie_detector_model_safe.pkl')
    
    print("=" * 60)
    print("FIX MODEL CORRUPTION")
    print("=" * 60)
    
    # Load the original model
    print("\n[STEP 1] Loading original PKL model...")
    try:
        model = joblib.load(pkl_path)
        print(f"✅ Loaded: {type(model)}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Extract booster as JSON string (safe format)
    print("\n[STEP 2] Extracting booster as JSON...")
    try:
        booster = model.get_booster()
        booster_json = booster.save_raw('json')
        print(f"✅ Extracted booster JSON")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Save booster JSON and metadata separately (simpler approach)
    print("\n[STEP 3] Saving booster JSON and metadata...")
    
    try:
        # Save as a simple dict that can be pickled
        safe_model_data = {
            'booster_json': booster_json,
            'n_classes_': model.n_classes_,
            'n_features_in_': model.n_features_in_,
            'objective': model.objective,
            'max_depth': model.max_depth,
            'learning_rate': model.learning_rate,
            'n_estimators': model.n_estimators,
        }
        
        joblib.dump(safe_model_data, safe_pkl_path)
        file_size = os.path.getsize(safe_pkl_path)
        print(f"✅ Saved safe model: {safe_pkl_path}")
        print(f"   File size: {file_size} bytes")
        
        # Verify it can be loaded
        print("\n[STEP 4] Verifying safe model...")
        test_model = joblib.load(safe_pkl_path)
        print(f"✅ Safe model loads successfully")
        print(f"   - Classes: {test_model['n_classes_']}")
        print(f"   - Features: {test_model['n_features_in_']}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✅ FIX COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Replace the corrupted model:")
    print(f"   cp {safe_pkl_path} {pkl_path}")
    print("2. Upload to S3:")
    print(f"   - {pkl_path}")
    print(f"   - s3://lie-detection-project/models/face/v1/effective_lie_detector_model.pkl")
    
    return True

if __name__ == "__main__":
    success = fix_model_corruption()
    sys.exit(0 if success else 1)
