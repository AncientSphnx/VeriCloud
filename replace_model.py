import shutil
import os

src = r"c:\Users\91829\OneDrive\Desktop\VeriCloud\backend\models\face\effective_lie_detector_model_safe.pkl"
dst = r"c:\Users\91829\OneDrive\Desktop\VeriCloud\backend\models\face\effective_lie_detector_model.pkl"

if os.path.exists(src):
    shutil.copy(src, dst)
    print(f"✅ Copied {src} to {dst}")
    print(f"   New file size: {os.path.getsize(dst)} bytes")
else:
    print(f"❌ Source file not found: {src}")
