import subprocess
import os

os.chdir(r'c:\Users\91829\OneDrive\Desktop\VeriCloud')

subprocess.run(['git', 'add', 'backend/Face/predictor.py', 'frontend/src/pages/FaceAnalysis.tsx'])
subprocess.run(['git', 'commit', '-m', 'Add model caching and increase frontend timeout to 5 minutes'])
subprocess.run(['git', 'push'])
print("✅ Done!")
