import shutil
import os

src = r'c:\Users\91829\OneDrive\Desktop\VeriCloud\backend\models\face\effective_lie_detector_model_safe.pkl'
dst = r'c:\Users\91829\OneDrive\Desktop\VeriCloud\backend\models\face\effective_lie_detector_model.pkl'

shutil.copy(src, dst)
print(f"✅ Model replaced")
print(f"   From: {src}")
print(f"   To: {dst}")
print(f"   Size: {os.path.getsize(dst)} bytes")
