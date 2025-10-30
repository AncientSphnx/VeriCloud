@echo off
cd /d "c:\Users\91829\OneDrive\Desktop\VeriCloud"
git add backend/models/face/effective_lie_detector_model.pkl
git add backend/models/face/sanitize_booster_json.py
git commit -m "Deploy improved sanitized model with proper boolean conversion"
git push
echo Deployed!
