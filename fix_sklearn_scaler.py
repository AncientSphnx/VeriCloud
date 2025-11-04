#!/usr/bin/env python
"""Regenerate scaler with sklearn 1.2.2 to match Render environment."""
import joblib
import os
from sklearn.preprocessing import StandardScaler

scaler_path = r"c:\Users\91829\OneDrive\Desktop\VeriCloud\backend\models\face\effective_feature_scaler.pkl"

try:
    print(f"Loading scaler from {scaler_path}...")
    old_scaler = joblib.load(scaler_path)
    
    # Create new scaler
    new_scaler = StandardScaler()
    
    # Copy fitted parameters
    if hasattr(old_scaler, 'mean_'):
        new_scaler.mean_ = old_scaler.mean_
        new_scaler.var_ = old_scaler.var_
        new_scaler.scale_ = old_scaler.scale_
        new_scaler.n_features_in_ = old_scaler.n_features_in_
        new_scaler.n_samples_seen_ = old_scaler.n_samples_seen_
        print("✅ Copied scaler parameters")
    
    # Save with current sklearn version
    joblib.dump(new_scaler, scaler_path)
    print(f"✅ Scaler regenerated: {os.path.getsize(scaler_path)} bytes")
    
    # Verify it loads without warning
    test = joblib.load(scaler_path)
    print("✅ Verification: Scaler loads successfully")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
