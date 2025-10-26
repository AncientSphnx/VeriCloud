import os
import sys
import joblib
import cv2
import numpy as np
import tempfile
from pathlib import Path

# Add the Face model directory to the path
face_model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Face model'))
if face_model_path not in sys.path:
    sys.path.insert(0, face_model_path)

from effective_face_features import DeceptionFeatureExtractor
from lie_detector_multimode import EffectiveLieDetectorMultiMode, BaselineEstablisher


def load_face_model():
    """
    Load the trained face deception detection model.
    """
    model_dir = face_model_path
    
    model_path = os.path.join(model_dir, 'effective_lie_detector_model.pkl')
    scaler_path = os.path.join(model_dir, 'effective_feature_scaler.pkl')
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Face model not found at {model_path}")
    if not os.path.exists(scaler_path):
        raise FileNotFoundError(f"Feature scaler not found at {scaler_path}")
    
    print(f"Loading face model from {model_path}")
    
    try:
        detector = EffectiveLieDetectorMultiMode(
            model_path=model_path,
            scaler_path=scaler_path
        )
        return detector
    except Exception as e:
        print(f"Error loading face model: {e}")
        raise


def predict_face_video(video_path, detector=None):
    """
    Predict deception from a video file using face analysis.
    
    Args:
        video_path: Path to video file
        detector: EffectiveLieDetectorMultiMode instance (optional)
    
    Returns:
        tuple: (label, confidence)
    """
    if detector is None:
        detector = load_face_model()
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")
    
    predictions = []
    confidences = []
    frame_count = 0
    max_frames = 2400  # Process up to 2400 frames (~80 seconds at 30fps for longer videos)
    baseline_frames = 0
    baseline_complete = False
    
    try:
        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            result = detector.process_frame(frame)
            
            # Check if baseline is still being established
            if result and 'Establishing Baseline' in str(result.get('label', '')):
                baseline_frames += 1
                # Skip baseline frames, don't count them
                frame_count += 1
                continue
            
            # Once baseline is complete, collect predictions
            if result and result.get('label') not in ['No Face Detected', 'Establishing Baseline']:
                predictions.append(result.get('label', 'Unknown'))
                confidences.append(result.get('confidence', 0.0))
                baseline_complete = True
            
            frame_count += 1
        
        cap.release()
        
        if not predictions:
            # If no predictions after baseline, return a default
            if baseline_complete:
                return "Unable to determine", 0.0
            else:
                return "Insufficient data - baseline not completed", 0.0
        
        # Aggregate results
        most_common_prediction = max(set(predictions), key=predictions.count)
        avg_confidence = np.mean(confidences)
        
        print(f"Processed {frame_count} frames, baseline frames: {baseline_frames}, predictions collected: {len(predictions)}")
        print(f"Final prediction: {most_common_prediction} with confidence: {avg_confidence:.2f}")
        
        return most_common_prediction, float(avg_confidence)
    
    except Exception as e:
        cap.release()
        print(f"Error processing video: {e}")
        raise


def predict_face_image(image_path, detector=None):
    """
    Predict deception from a single image using face analysis.
    
    Args:
        image_path: Path to image file
        detector: EffectiveLieDetectorMultiMode instance (optional)
    
    Returns:
        tuple: (label, confidence)
    """
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


def predict_face(file_path, is_video=True):
    """
    Main prediction function that handles both images and videos.
    
    Args:
        file_path: Path to media file
        is_video: Boolean indicating if file is video (True) or image (False)
    
    Returns:
        tuple: (label, confidence)
    """
    try:
        detector = load_face_model()
        
        if is_video:
            return predict_face_video(file_path, detector)
        else:
            return predict_face_image(file_path, detector)
    
    except Exception as e:
        print(f"Error in face prediction: {e}")
        raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python predictor.py <file_path> [--video|--image]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    is_video = True
    
    if len(sys.argv) > 2:
        if sys.argv[2] == "--image":
            is_video = False
    
    label, confidence = predict_face(file_path, is_video)
    print(f"Prediction: {label} (Confidence: {confidence:.2f})")
