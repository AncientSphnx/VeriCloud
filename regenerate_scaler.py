#!/usr/bin/env python
"""Regenerate the scaler with current sklearn version to fix version mismatch."""
import joblib
import os
from sklearn.preprocessing import StandardScaler
import numpy as np

scaler_path = r"c:\Users\91829\OneDrive\Desktop\VeriCloud\backend\models\face\effective_feature_scaler.pkl"

try:
    # Load old scaler
    print(f"Loading old scaler from {scaler_path}...")
    old_scaler = joblib.load(scaler_path)
    
    # Create new scaler with same parameters
    new_scaler = StandardScaler()
    
    # Copy the fitted parameters from old scaler
    if hasattr(old_scaler, 'mean_'):
        new_scaler.mean_ = old_scaler.mean_
        new_scaler.var_ = old_scaler.var_
        new_scaler.scale_ = old_scaler.scale_
        new_scaler.n_features_in_ = old_scaler.n_features_in_
        new_scaler.n_samples_seen_ = old_scaler.n_samples_seen_
        print("✅ Copied scaler parameters")
    
    # Save with current sklearn version
    joblib.dump(new_scaler, scaler_path)
    print(f"✅ Regenerated scaler saved to {scaler_path}")
    print(f"   File size: {os.path.getsize(scaler_path)} bytes")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
