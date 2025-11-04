import subprocess
import os

os.chdir(r'c:\Users\91829\OneDrive\Desktop\VeriCloud')

subprocess.run(['git', 'add', 'frontend/src/pages/VoiceAnalysis.tsx'])
subprocess.run(['git', 'commit', '-m', 'Fix Voice API endpoint - add /predict to URL'])
subprocess.run(['git', 'push'])
print("✅ Done!")
