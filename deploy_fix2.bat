@echo off
cd /d "c:\Users\91829\OneDrive\Desktop\VeriCloud"
git add backend/Face/predictor.py
git commit -m "Fix EffectiveLieDetectorMultiMode constructor - pass file paths not objects"
git push
echo Deployed!
