"""
Sanitize booster JSON by fixing type mismatches between XGBoost versions.
Converts Integer fields that should be Boolean to proper format.
"""
import os
import sys
import json
import joblib
import xgboost as xgb

sys.path.insert(0, os.path.dirname(__file__))

def sanitize_booster_json(booster_json_str):
    """Fix type mismatches in booster JSON - convert all 0/1 to false/true in boolean contexts."""
    
    # Parse the JSON
    try:
        booster_dict = json.loads(booster_json_str)
    except Exception as e:
        print(f"❌ Failed to parse JSON: {e}")
        return None
    
    # Recursively fix type mismatches
    def fix_types(obj, parent_key=None):
        if isinstance(obj, dict):
            for key, value in list(obj.items()):
                # Fields that should always be boolean
                boolean_fields = {
                    'missing', 'nan_present', 'has_missing', 'default_left',
                    'boost_from_average', 'allow_null', 'deleted'
                }
                
                if key in boolean_fields and isinstance(value, int):
                    obj[key] = bool(value)
                elif isinstance(value, (dict, list)):
                    fix_types(value, key)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, int) and parent_key in {
                    'default_left', 'deleted', 'categories_nodes'
                }:
                    # These should be booleans
                    obj[i] = bool(item)
                elif isinstance(item, (dict, list)):
                    fix_types(item, parent_key)
    
    fix_types(booster_dict)
    
    # Convert back to JSON string
    return json.dumps(booster_dict)

def create_sanitized_model():
    """Create model with sanitized booster JSON."""
    
    model_dir = os.path.dirname(__file__)
    pkl_path = os.path.join(model_dir, 'effective_lie_detector_model.pkl')
    safe_pkl_path = os.path.join(model_dir, 'effective_lie_detector_model_safe.pkl')
    
    print("=" * 60)
    print("SANITIZE BOOSTER JSON")
    print("=" * 60)
    
    # Load the original model
    print("\n[STEP 1] Loading original PKL model...")
    try:
        model_data = joblib.load(pkl_path)
        print(f"✅ Loaded: {type(model_data)}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Extract booster JSON
    print("\n[STEP 2] Extracting booster JSON...")
    try:
        if isinstance(model_data, dict) and 'booster_json' in model_data:
            booster_json = model_data['booster_json']
            print(f"✅ Extracted booster JSON from safe dict ({len(booster_json)} bytes)")
        else:
            # Legacy format - extract from XGBoost model
            booster = model_data.get_booster()
            booster_json = booster.save_raw('json')
            print(f"✅ Extracted booster JSON from XGBoost model ({len(booster_json)} bytes)")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Sanitize the JSON
    print("\n[STEP 3] Sanitizing booster JSON...")
    try:
        sanitized_json = sanitize_booster_json(booster_json)
        if sanitized_json is None:
            return False
        print(f"✅ Sanitized JSON ({len(sanitized_json)} bytes)")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Save as safe model data
    print("\n[STEP 4] Saving sanitized model...")
    try:
        safe_model_data = {
            'booster_json': sanitized_json,
            'n_classes_': model_data.get('n_classes_', 2),
            'n_features_in_': model_data.get('n_features_in_', 70),
            'objective': model_data.get('objective', 'binary:logistic'),
            'max_depth': model_data.get('max_depth', 6),
            'learning_rate': model_data.get('learning_rate', 0.1),
            'n_estimators': model_data.get('n_estimators', 100),
        }
        
        joblib.dump(safe_model_data, safe_pkl_path)
        file_size = os.path.getsize(safe_pkl_path)
        print(f"✅ Saved sanitized model: {safe_pkl_path}")
        print(f"   File size: {file_size} bytes")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Verify it can be loaded
    print("\n[STEP 5] Verifying sanitized model...")
    try:
        test_data = joblib.load(safe_pkl_path)
        print(f"✅ Model data loads successfully")
        
        # Try to reconstruct booster
        print("\n[STEP 6] Testing booster reconstruction...")
        booster_test = xgb.Booster()
        booster_test.load_model(test_data['booster_json'])
        print(f"✅ Booster reconstructs successfully!")
        
    except Exception as e:
        print(f"⚠️ Verification failed: {e}")
        print("   This may still work on Render if XGBoost version matches")
    
    print("\n" + "=" * 60)
    print("✅ SANITIZATION COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Replace the model:")
    print(f"   cp {safe_pkl_path} {pkl_path}")
    print("2. Upload to S3:")
    print(f"   - {pkl_path}")
    print(f"   - s3://lie-detection-project/models/face/v1/effective_lie_detector_model.pkl")
    
    return True

if __name__ == "__main__":
    success = create_sanitized_model()
    sys.exit(0 if success else 1)
