#!/usr/bin/env python
import subprocess
import os

os.chdir(r'c:\Users\91829\OneDrive\Desktop\VeriCloud')

# Commit
result = subprocess.run(['git', 'commit', '-m', 'Remove read-only property assignments'], capture_output=True, text=True)
print("COMMIT:")
print(result.stdout)
if result.stderr:
    print(result.stderr)

# Push
result = subprocess.run(['git', 'push'], capture_output=True, text=True)
print("\nPUSH:")
print(result.stdout)
if result.stderr:
    print(result.stderr)
