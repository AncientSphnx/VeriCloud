@echo off
cd /d "c:\Users\91829\OneDrive\Desktop\VeriCloud"
git add backend/models/face/lie_detector_multimode.py
git commit -m "Handle safe dict format in lie_detector_multimode - reconstruct XGBoost model from JSON"
git push
echo Deployed!
