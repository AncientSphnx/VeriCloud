import subprocess
import os

os.chdir(r'c:\Users\91829\OneDrive\Desktop\VeriCloud')

subprocess.run(['git', 'add', 'backend/models/face/lie_detector_multimode.py'])
subprocess.run(['git', 'commit', '-m', 'Suppress harmless sklearn version warning'])
subprocess.run(['git', 'push'])
print("✅ Done!")
