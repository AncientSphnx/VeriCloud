@echo off
cd /d "c:\Users\91829\OneDrive\Desktop\VeriCloud"
git add backend/models/face/effective_lie_detector_model.pkl
git add backend/models/face/effective_feature_scaler.pkl
git commit -m "Update sanitized model files for Render deployment"
git push
echo Done!
