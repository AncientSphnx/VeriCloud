import subprocess
import os

os.chdir(r'c:\Users\91829\OneDrive\Desktop\VeriCloud')

subprocess.run(['git', 'add', 'frontend/src/pages/FaceAnalysis.tsx', 'backend/Face/predictor.py'])
subprocess.run(['git', 'commit', '-m', 'Remove timeout and reduce frame processing for faster analysis'])
subprocess.run(['git', 'push'])
print("✅ Done!")
