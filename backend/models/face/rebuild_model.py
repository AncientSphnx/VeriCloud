"""
Rebuild the model in a version-agnostic way using only the prediction logic.
This extracts the booster and saves it in a format that works across XGBoost versions.
"""
import os
import sys
import json
import joblib
import xgboost as xgb
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

def rebuild_model_compatible():
    """Rebuild model using get_booster().save_raw() which is more compatible."""
    
    model_dir = os.path.dirname(__file__)
    pkl_path = os.path.join(model_dir, 'effective_lie_detector_model.pkl')
    ubj_path = os.path.join(model_dir, 'effective_lie_detector_model.ubj')
    scaler_path = os.path.join(model_dir, 'effective_feature_scaler.pkl')
    
    print("=" * 60)
    print("REBUILD MODEL - UNIVERSAL BINARY FORMAT")
    print("=" * 60)
    
    # Load the original model
    print("\n[STEP 1] Loading original PKL model...")
    try:
        model = joblib.load(pkl_path)
        print(f"✅ Loaded: {type(model)}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Get booster and save in universal binary format
    print("\n[STEP 2] Extracting booster and saving in UBJ format...")
    try:
        booster = model.get_booster()
        # UBJ (Universal Binary JSON) is more compatible than JSON
        booster.save_model(ubj_path)
        file_size = os.path.getsize(ubj_path)
        print(f"✅ Saved to UBJ format: {ubj_path}")
        print(f"   File size: {file_size} bytes")
    except Exception as e:
        print(f"❌ Failed to save: {e}")
        return False
    
    # Verify we can load it back
    print("\n[STEP 3] Verifying UBJ can be loaded...")
    try:
        test_booster = xgb.Booster()
        test_booster.load_model(ubj_path)
        print(f"✅ Verification successful!")
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    
    # Also create a wrapper class that can be pickled
    print("\n[STEP 4] Creating wrapper class...")
    try:
        wrapper_code = '''
import xgboost as xgb
import numpy as np

class XGBoostModelWrapper:
    """Wrapper that loads XGBoost model from UBJ format."""
    
    def __init__(self, ubj_path):
        self.ubj_path = ubj_path
        self.booster = None
        self._load_model()
    
    def _load_model(self):
        """Load model from UBJ file."""
        self.booster = xgb.Booster()
        self.booster.load_model(self.ubj_path)
    
    def predict(self, X):
        """Make predictions."""
        dmatrix = xgb.DMatrix(X)
        return self.booster.predict(dmatrix)
    
    def predict_proba(self, X):
        """Get prediction probabilities."""
        dmatrix = xgb.DMatrix(X)
        proba = self.booster.predict(dmatrix)
        # Convert to probabilities if needed
        if len(proba.shape) == 1:
            # Binary classification
            neg_proba = 1 - proba
            return np.column_stack([neg_proba, proba])
        return proba
    
    def __getstate__(self):
        """For pickling."""
        return {'ubj_path': self.ubj_path}
    
    def __setstate__(self, state):
        """For unpickling."""
        self.ubj_path = state['ubj_path']
        self._load_model()
'''
        wrapper_path = os.path.join(model_dir, 'xgboost_wrapper.py')
        with open(wrapper_path, 'w') as f:
            f.write(wrapper_code)
        print(f"✅ Created wrapper class at: {wrapper_path}")
    except Exception as e:
        print(f"❌ Failed to create wrapper: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ MODEL REBUILD COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Upload to S3:")
    print(f"   - {ubj_path}")
    print(f"   - {scaler_path}")
    print("2. Update environment variable:")
    print("   FACE_MODEL_KEY=models/face/v1/effective_lie_detector_model.ubj")
    
    return True

if __name__ == "__main__":
    success = rebuild_model_compatible()
    sys.exit(0 if success else 1)
