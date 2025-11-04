import subprocess
import os

os.chdir(r'c:\Users\91829\OneDrive\Desktop\VeriCloud')

subprocess.run(['git', 'add', 'frontend/src/pages/FaceAnalysis.tsx'])
subprocess.run(['git', 'commit', '-m', 'Increase timeout to 10 minutes and improve error handling'])
subprocess.run(['git', 'push'])
print("✅ Done!")
