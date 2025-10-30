import subprocess
import os

os.chdir(r'c:\Users\91829\OneDrive\Desktop\VeriCloud')

# Check if model files are tracked
result = subprocess.run(['git', 'ls-files', 'backend/models/face/'], capture_output=True, text=True)
print("Git tracked files in backend/models/face/:")
print(result.stdout)

# Check git status
result = subprocess.run(['git', 'status', '--short', 'backend/models/face/'], capture_output=True, text=True)
print("\nGit status for backend/models/face/:")
print(result.stdout if result.stdout else "(no changes)")

# Check file sizes
import os
for f in ['effective_lie_detector_model.pkl', 'effective_feature_scaler.pkl']:
    path = f'backend/models/face/{f}'
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"\n✅ {f}: {size} bytes")
    else:
        print(f"\n❌ {f}: NOT FOUND")
