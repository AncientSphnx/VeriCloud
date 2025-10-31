import subprocess
import os

os.chdir(r'c:\Users\91829\OneDrive\Desktop\VeriCloud')

# Upload scaler to S3
print("Uploading scaler to S3...")
result = subprocess.run([
    'aws', 's3', 'cp',
    r'backend\models\face\effective_feature_scaler.pkl',
    's3://lie-detection-project/models/face/v1/effective_feature_scaler.pkl'
], capture_output=True, text=True)

if result.returncode == 0:
    print("✅ Scaler uploaded to S3")
else:
    print(f"⚠️ S3 upload output: {result.stdout}")
    if result.stderr:
        print(f"Error: {result.stderr}")

# Commit and push
print("Committing changes...")
subprocess.run(['git', 'add', 'backend/models/face/effective_feature_scaler.pkl'])
subprocess.run(['git', 'commit', '-m', 'Regenerate scaler with current sklearn version'])
subprocess.run(['git', 'push'])
print("✅ Done!")
