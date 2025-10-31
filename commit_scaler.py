import subprocess
import os

os.chdir(r'c:\Users\91829\OneDrive\Desktop\VeriCloud')

# Commit and push
print("Committing scaler changes...")
subprocess.run(['git', 'add', 'backend/models/face/effective_feature_scaler.pkl'])
subprocess.run(['git', 'commit', '-m', 'Regenerate scaler with current sklearn version'])
subprocess.run(['git', 'push'])
print("✅ Done!")
