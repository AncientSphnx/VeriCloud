import subprocess
import os

os.chdir(r'c:\Users\91829\OneDrive\Desktop\VeriCloud')
subprocess.run(['git', 'add', 'backend/Face/predictor.py'])
subprocess.run(['git', 'commit', '-m', 'Add lazy loading for Face API startup speed'])
subprocess.run(['git', 'push'])
print("Done!")
