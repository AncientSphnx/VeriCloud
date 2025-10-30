@echo off
cd /d "c:\Users\91829\OneDrive\Desktop\VeriCloud"
git add backend/Face/predictor.py
git commit -m "Fix XGBoost JSON loading - write to temp file before load_model"
git push
echo Deployed!
