import shutil
import os
from pathlib import Path

# Get project root directory (4 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
src = os.path.join(PROJECT_ROOT, "backend", "models", "face", "effective_lie_detector_model_safe.pkl")
dst = os.path.join(PROJECT_ROOT, "backend", "models", "face", "effective_lie_detector_model.pkl")

shutil.copy(src, dst)
print(f"✅ Model replaced")
print(f"   From: {src}")
print(f"   To: {dst}")
print(f"   Size: {os.path.getsize(dst)} bytes")
