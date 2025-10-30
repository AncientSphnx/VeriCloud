import shutil
import os
import joblib
import xgboost as xgb

src = r'c:\Users\91829\OneDrive\Desktop\VeriCloud\backend\models\face\effective_lie_detector_model_safe.pkl'
dst = r'c:\Users\91829\OneDrive\Desktop\VeriCloud\backend\models\face\effective_lie_detector_model.pkl'

# Replace
shutil.copy(src, dst)
print(f"✅ Model replaced")
print(f"   Size: {os.path.getsize(dst)} bytes")

# Verify it loads
print("\n[VERIFY] Testing model load...")
try:
    model_data = joblib.load(dst)
    print(f"✅ Model data loads successfully")
    
    # Try to reconstruct booster
    print("[VERIFY] Testing booster reconstruction...")
    booster = xgb.Booster()
    booster.load_model(model_data['booster_json'])
    print(f"✅ Booster reconstructs successfully!")
    print(f"   - Classes: {model_data['n_classes_']}")
    print(f"   - Features: {model_data['n_features_in_']}")
    
except Exception as e:
    print(f"❌ Verification failed: {e}")
    import traceback
    traceback.print_exc()
