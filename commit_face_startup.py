import subprocess
import os

os.chdir(r'c:\Users\91829\OneDrive\Desktop\VeriCloud')

subprocess.run(['git', 'add', 'backend/Face/app.py'])
subprocess.run(['git', 'commit', '-m', 'Add model pre-loading on startup to prevent timeout'])
subprocess.run(['git', 'push'])
print("✅ Done!")
