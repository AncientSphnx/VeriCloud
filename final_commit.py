import subprocess
import os

os.chdir(r'c:\Users\91829\OneDrive\Desktop\VeriCloud')

# Add all build scripts and render config
subprocess.run(['git', 'add', 'backend/Voice/build.sh', 'backend/Face/build.sh', 'backend/Text/build.sh', 'render.yaml'])
subprocess.run(['git', 'commit', '-m', 'Add pre-download build scripts and parallel deployment config'])
subprocess.run(['git', 'push'])
print("✅ Done!")
