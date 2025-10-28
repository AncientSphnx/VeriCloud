import os
import sys
import cv2
import boto3
import numpy as np
import tempfile
from pathlib import Path

# ----------------------------
# Add Face model directory path
# ----------------------------
face_model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Face model'))
if face_model_path not in sys.path:
    sys.path.insert(0, face_model_path)

from effective_face_features import DeceptionFeatureExtractor
from lie_detector_multimode import EffectiveLieDetectorMultiMode, BaselineEstablisher


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
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
        region_name=os.getenv('S3_REGION')
    )

    tmp_dir = tempfile.mkdtemp()

    local_model_path = os.path.join(tmp_dir, os.path.basename(s3_model_key))
    local_scaler_path = os.path.join(tmp_dir, os.path.basename(s3_scaler_key))

    print(f"Downloading face model from s3://{bucket}/{s3_model_key}")
    s3.download_file(bucket, s3_model_key, local_model_path)

    print(f"Downloading scaler from s3://{bucket}/{s3_scaler_key}")
    s3.download_file(bucket, s3_scaler_key, local_scaler_path)

    return local_model_path, local_scaler_path


def load_face_model():
    """
    Loads the face deception detection model (from S3 or local fallback).
    """
    try:
        bucket = os.getenv("S3_BUCKET_NAME")
        model_key = os.getenv("FACE_MODEL_KEY", "models/face/v1/effective_lie_detector_model.pkl")
        scaler_key = os.getenv("FACE_SCALER_KEY", "models/face/v1/effective_feature_scaler.pkl")

        model_path, scaler_path = download_model_from_s3(bucket, model_key, scaler_key)

        detector = EffectiveLieDetectorMultiMode(
            model_path=model_path,
            scaler_path=scaler_path
        )
        print("✅ Face model loaded successfully from S3.")
        return detector

    except Exception as e:
        print(f"⚠️ Failed to load model from S3: {e}")
        # fallback to local if available
        local_model_path = os.path.join(face_model_path, 'effective_lie_detector_model.pkl')
        local_scaler_path = os.path.join(face_model_path, 'effective_feature_scaler.pkl')

        if os.path.exists(local_model_path) and os.path.exists(local_scaler_path):
            print("Using local face model as fallback.")
            return EffectiveLieDetectorMultiMode(local_model_path, local_scaler_path)
        else:
            raise RuntimeError("❌ Face model not found locally or in S3.")


# ----------------------------
# Predict from video
# ----------------------------
def predict_face_video(video_path, detector=None):
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
