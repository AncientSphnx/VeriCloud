import os
import sys
import cv2
import boto3
import numpy as np
import tempfile
from pathlib import Path
import joblib
import xgboost as xgb

# ----------------------------
# Add Face model directory path
# ----------------------------
# Try multiple possible locations for the Face model directory
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(_current_dir)
_project_root = os.path.dirname(_backend_dir)

# Priority order for finding Face model files
_possible_paths = [
    os.path.join(_backend_dir, 'models', 'face'),  # backend/models/face
    os.path.join(_project_root, 'Face model'),      # Face model (root level)
    os.path.join(_backend_dir, 'Face'),             # backend/Face
]

face_model_path = None
for path in _possible_paths:
    if os.path.exists(path):
        face_model_path = path
        print(f"[INFO] Found Face model directory at: {face_model_path}")
        break

if face_model_path is None:
    # Fallback to first option (will fail gracefully if files don't exist)
    face_model_path = _possible_paths[0]
    print(f"[WARN] Face model directory not found. Will try: {face_model_path}")

if face_model_path not in sys.path:
    sys.path.insert(0, face_model_path)

# Lazy imports - will be imported on first use to speed up startup
DeceptionFeatureExtractor = None
EffectiveLieDetectorMultiMode = None
BaselineEstablisher = None

def _ensure_imports():
    """Lazy load heavy dependencies on first use."""
    global DeceptionFeatureExtractor, EffectiveLieDetectorMultiMode, BaselineEstablisher
    if DeceptionFeatureExtractor is None:
        from effective_face_features import DeceptionFeatureExtractor as DFE
        from lie_detector_multimode import EffectiveLieDetectorMultiMode as ELDM, BaselineEstablisher as BE
        DeceptionFeatureExtractor = DFE
        EffectiveLieDetectorMultiMode = ELDM
        BaselineEstablisher = BE


# ----------------------------
# Load model from S3
# ----------------------------
def download_model_from_s3(bucket, s3_model_key, s3_scaler_key):
    """
    Downloads model and scaler from AWS S3 to a temporary directory.
    Returns local file paths.
    """
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('S3_REGION')
    )

    tmp_dir = tempfile.mkdtemp()

    local_model_path = os.path.join(tmp_dir, os.path.basename(s3_model_key))
    local_scaler_path = os.path.join(tmp_dir, os.path.basename(s3_scaler_key))

    print(f"[INFO] Downloading face model from s3://{bucket}/{s3_model_key}")
    s3.download_file(bucket, s3_model_key, local_model_path)
    model_size = os.path.getsize(local_model_path)
    print(f"[INFO] Model file size: {model_size} bytes")

    print(f"[INFO] Downloading scaler from s3://{bucket}/{s3_scaler_key}")
    s3.download_file(bucket, s3_scaler_key, local_scaler_path)
    scaler_size = os.path.getsize(local_scaler_path)
    print(f"[INFO] Scaler file size: {scaler_size} bytes")

    return local_model_path, local_scaler_path


def load_face_model():
    """
    Loads the face deception detection model from S3 (primary) or local fallback.
    Handles both safe dict format and legacy XGBoost format.
    """
    _ensure_imports()  # Lazy load heavy dependencies
    # Attempt 1: Try S3 first (primary source)
    try:
        bucket = os.getenv("S3_BUCKET_NAME")
        model_key = os.getenv("FACE_MODEL_KEY", "models/face/v1/effective_lie_detector_model.pkl")
        scaler_key = os.getenv("FACE_SCALER_KEY", "models/face/v1/effective_feature_scaler.pkl")
        
        if not bucket:
            raise ValueError("S3_BUCKET_NAME not configured")
        
        print(f"[DEBUG] Attempting S3 download from bucket: {bucket}")
        print(f"[DEBUG] Model key: {model_key}")
        print(f"[DEBUG] Scaler key: {scaler_key}")
        
        model_path, scaler_path = download_model_from_s3(bucket, model_key, scaler_key)
        print(f"[INFO] Downloaded from S3: {model_path}, {scaler_path}")

        # ✅ Validate file integrity before loading
        model_size = os.path.getsize(model_path)
        scaler_size = os.path.getsize(scaler_path)
        
        if model_size < 100:
            raise ValueError(f"Model file too small ({model_size} bytes) - likely corrupted")
        if scaler_size < 100:
            raise ValueError(f"Scaler file too small ({scaler_size} bytes) - likely corrupted")

        print(f"[DEBUG] File sizes - Model: {model_size} bytes, Scaler: {scaler_size} bytes")

        # ✅ Load model from S3
        print("[INFO] Loading model from S3...")
        model_data = joblib.load(model_path)
        
        # Check if it's the safe dict format or legacy XGBoost format
        if isinstance(model_data, dict) and 'booster_json' in model_data:
            print("[INFO] Detected safe dict format - reconstructing model...")
            import tempfile
            import os as os_module
            # XGBoost's load_model expects a file path, not a JSON string
            # Write JSON to temp file and load from there
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                f.write(model_data['booster_json'])
                temp_json_path = f.name
            try:
                booster = xgb.Booster()
                booster.load_model(temp_json_path)
                model = xgb.XGBClassifier()
                model._Booster = booster
            finally:
                os_module.unlink(temp_json_path)
        else:
            print("[INFO] Detected legacy XGBoost format")
            model = model_data
        
        detector = EffectiveLieDetectorMultiMode(model_path=model_path, scaler_path=scaler_path)
        print("✅ Face model loaded successfully from S3.")
        return detector

    except Exception as e:
        print(f"⚠️ Failed to load model from S3: {e}")
        import traceback
        traceback.print_exc()
        
        # Attempt 2: Fallback to local model
        print("[INFO] Attempting to load from local model as fallback...")
        local_model_path_pkl = os.path.join(face_model_path, 'effective_lie_detector_model.pkl')
        local_scaler_path = os.path.join(face_model_path, 'effective_feature_scaler.pkl')

        print(f"[DEBUG] Local model path: {local_model_path_pkl}")
        print(f"[DEBUG] Local model exists: {os.path.exists(local_model_path_pkl)}")
        print(f"[DEBUG] Local scaler path: {local_scaler_path}")
        print(f"[DEBUG] Local scaler exists: {os.path.exists(local_scaler_path)}")

        if os.path.exists(local_model_path_pkl) and os.path.exists(local_scaler_path):
            try:
                print("[INFO] Loading local model...")
                model_data = joblib.load(local_model_path_pkl)
                print(f"[DEBUG] Loaded model data type: {type(model_data)}")
                
                # Check if it's the safe dict format or legacy XGBoost format
                if isinstance(model_data, dict) and 'booster_json' in model_data:
                    print("[INFO] Detected safe dict format - reconstructing model...")
                    import tempfile
                    import os as os_module
                    # XGBoost's load_model expects a file path, not a JSON string
                    # Write JSON to temp file and load from there
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                        f.write(model_data['booster_json'])
                        temp_json_path = f.name
                    try:
                        booster = xgb.Booster()
                        booster.load_model(temp_json_path)
                        model = xgb.XGBClassifier()
                        model._Booster = booster
                    finally:
                        os_module.unlink(temp_json_path)
                else:
                    print("[INFO] Detected legacy XGBoost format")
                    model = model_data
                
                detector = EffectiveLieDetectorMultiMode(model_path=local_model_path_pkl, scaler_path=local_scaler_path)
                print("✅ Face model loaded successfully from local files.")
                return detector
            except Exception as e2:
                print(f"⚠️ Failed to load local model: {e2}")
                import traceback
                traceback.print_exc()
        else:
            print(f"[DEBUG] Local files not found - model exists: {os.path.exists(local_model_path_pkl)}, scaler exists: {os.path.exists(local_scaler_path)}")

        # All attempts failed
        raise RuntimeError("❌ Face model not found in S3 or locally. Please ensure the model file is available.")


# ----------------------------
# Predict from video
# ----------------------------
def predict_face_video(video_path, detector=None):
    _ensure_imports()  # Lazy load heavy dependencies
    if detector is None:
        detector = load_face_model()

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")

    predictions = []
    confidences = []
    frame_count = 0
    max_frames = 2400
    baseline_frames = 0
    baseline_complete = False

    try:
        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break

            result = detector.process_frame(frame)

            if result and 'Establishing Baseline' in str(result.get('label', '')):
                baseline_frames += 1
                frame_count += 1
                continue

            if result and result.get('label') not in ['No Face Detected', 'Establishing Baseline']:
                predictions.append(result.get('label', 'Unknown'))
                confidences.append(result.get('confidence', 0.0))
                baseline_complete = True

            frame_count += 1

        cap.release()

        if not predictions:
            if baseline_complete:
                return "Unable to determine", 0.0
            else:
                return "Insufficient data - baseline not completed", 0.0

        most_common_prediction = max(set(predictions), key=predictions.count)
        avg_confidence = np.mean(confidences)

        print(f"Processed {frame_count} frames, baseline: {baseline_frames}, predictions: {len(predictions)}")
        print(f"Final prediction: {most_common_prediction} (Confidence: {avg_confidence:.2f})")

        return most_common_prediction, float(avg_confidence)

    except Exception as e:
        cap.release()
        print(f"Error processing video: {e}")
        raise


# ----------------------------
# Predict from image
# ----------------------------
def predict_face_image(image_path, detector=None):
    _ensure_imports()  # Lazy load heavy dependencies
    if detector is None:
        detector = load_face_model()

    frame = cv2.imread(image_path)
    if frame is None:
        raise ValueError(f"Cannot read image file: {image_path}")

    result = detector.process_frame(frame)

    if result is None or result.get('label') == 'No Face Detected':
        return "No Face Detected", 0.0

    label = result.get('label', 'Unknown')
    confidence = result.get('confidence', 0.0)

    return label, float(confidence)


# ----------------------------
# Main unified predictor
# ----------------------------
def predict_face(file_path, is_video=True):
    try:
        detector = load_face_model()

        if is_video:
            return predict_face_video(file_path, detector)
        else:
            return predict_face_image(file_path, detector)

    except Exception as e:
        print(f"Error in face prediction: {e}")
        raise


# ----------------------------
# Local testing entry point
# ----------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python predictor.py <file_path> [--video|--image]")
        sys.exit(1)

    file_path = sys.argv[1]
    is_video = True
    if len(sys.argv) > 2 and sys.argv[2] == "--image":
        is_video = False

    label, confidence = predict_face(file_path, is_video)
    print(f"Prediction: {label} (Confidence: {confidence:.2f})")
