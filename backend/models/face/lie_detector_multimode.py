import cv2
import numpy as np
import joblib
from collections import deque
import time
from effective_face_features import DeceptionFeatureExtractor
import os
from pathlib import Path
import xgboost as xgb
import warnings

# Suppress sklearn version warning - scaler works fine across versions
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn') 

class BaselineEstablisher:
    """Establishes baseline of normal behavior for each person."""
    
    def __init__(self, duration_seconds=30, fps=30):
        self.duration_seconds = duration_seconds
        self.fps = fps
        self.max_frames = duration_seconds * fps
        self.baseline_features = deque(maxlen=self.max_frames)
        self.baseline_stats = {}
        self.is_established = False
    
    def add_frame(self, feature_vector):
        """Add a frame to baseline."""
        if feature_vector is not None:
            self.baseline_features.append(feature_vector)
    
    def establish_baseline(self):
        """Calculate baseline statistics."""
        if len(self.baseline_features) < self.max_frames * 0.8:
            return False
        
        features_array = np.array(list(self.baseline_features))
        
        self.baseline_stats = {
            'mean': np.mean(features_array, axis=0),
            'std': np.std(features_array, axis=0),
            'min': np.min(features_array, axis=0),
            'max': np.max(features_array, axis=0),
        }
        
        self.is_established = True
        return True
    
    def get_deviation_score(self, feature_vector):
        """Calculate deviation from baseline."""
        if not self.is_established or feature_vector is None:
            return 0.0
        
        std = self.baseline_stats['std']
        std = np.where(std < 1e-6, 1e-6, std)
        
        z_scores = np.abs((feature_vector - self.baseline_stats['mean']) / std)
        deviation = np.mean(np.clip(z_scores, 0, 5)) / 5.0
        
        return deviation


class EffectiveLieDetectorMultiMode:
    """Lie detection supporting webcam and video file input."""
    
    def __init__(self, model_path='effective_lie_detector_model.pkl',
                 scaler_path='effective_feature_scaler.pkl'):
        
        print("[INFO] Loading model and scaler...")
        try:
            # ✅ Detect if model is XGBoost JSON format
            if model_path.endswith(".json"):
                self.model = xgb.XGBClassifier()
                self.model.load_model(model_path)
                print("✅ XGBoost JSON model loaded successfully.")
            else:
                model_data = joblib.load(model_path)
                
                # Check if it's the safe dict format with booster_json
                if isinstance(model_data, dict) and 'booster_json' in model_data:
                    print("[INFO] Detected safe dict format - reconstructing XGBoost model...")
                    import tempfile
                    # Write JSON to temp file and load from there
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                        f.write(model_data['booster_json'])
                        temp_json_path = f.name
                    try:
                        booster = xgb.Booster()
                        booster.load_model(temp_json_path)
                        # Create XGBClassifier and set booster
                        self.model = xgb.XGBClassifier()
                        self.model._Booster = booster
                        print("✅ Safe dict format model reconstructed successfully.")
                    finally:
                        os.unlink(temp_json_path)
                else:
                    self.model = model_data
                    print("✅ Pickle model loaded successfully.")
            
            # Load scaler as usual (suppress sklearn version warning)
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=UserWarning)
                self.scaler = joblib.load(scaler_path)
            self.extractor = DeceptionFeatureExtractor()

            # Patch deprecated field if exists - set to None instead of deleting
            try:
                if hasattr(self.model, "use_label_encoder"):
                    self.model.use_label_encoder = None
                    print("⚙️ Patched deprecated 'use_label_encoder' attribute in XGBClassifier.")
            except Exception as e:
                print(f"⚠️ Could not patch use_label_encoder: {e}")
                
        except FileNotFoundError as e:
            print(f"[ERROR] Failed to load model: {e}")
            print("[INFO] Please run train_effective_face_model.py first")
            raise
        
        self.baseline = BaselineEstablisher(duration_seconds=30)
        self.confidence_history = deque(maxlen=60)
        self.deviation_history = deque(maxlen=60)
        self.prediction_history = deque(maxlen=60)
        
        self.frame_count = 0
        self.deception_frames = 0
        self.baseline_phase = True
        self.baseline_start_time = None
    
    def process_frame(self, frame):
        """Process a single frame."""
        self.frame_count += 1
        
        features_dict, feature_vec = self.extractor.extract_all_features(frame)
        
        if feature_vec is None:
            return {
                'confidence': 0.0,
                'deviation': 0.0,
                'label': 'No Face Detected',
                'baseline_phase': self.baseline_phase,
                'baseline_progress': 0
            }
        
        if self.baseline_phase:
            self.baseline.add_frame(feature_vec)
            
            if self.baseline_start_time is None:
                self.baseline_start_time = time.time()
            
            elapsed = time.time() - self.baseline_start_time
            progress = min(100, int((elapsed / 30.0) * 100))
            
            if elapsed > 30:
                if self.baseline.establish_baseline():
                    self.baseline_phase = False
                    print("\n[SUCCESS] Baseline established! Starting deception detection...")
            
            return {
                'confidence': 0.0,
                'deviation': 0.0,
                'label': f'Establishing Baseline ({progress}%)',
                'baseline_phase': True,
                'baseline_progress': progress
            }
        
        feature_vec_scaled = self.scaler.transform(feature_vec.reshape(1, -1))
        
        prediction = self.model.predict(feature_vec_scaled)[0]
        confidence = self.model.predict_proba(feature_vec_scaled)[0][1]
        
        deviation = self.baseline.get_deviation_score(feature_vec)
        
        combined_score = (confidence * 0.5) + (deviation * 0.5)
        
        self.confidence_history.append(confidence)
        self.deviation_history.append(deviation)
        self.prediction_history.append(prediction)
        
        if len(self.confidence_history) >= 5:
            smoothed_confidence = np.mean(list(self.confidence_history)[-5:])
        else:
            smoothed_confidence = confidence
        
        if smoothed_confidence > 0.3:
            label = "DECEPTION DETECTED"
            self.deception_frames += 1
        else:
            label = "Truthful"
        
        return {
            'confidence': smoothed_confidence,
            'deviation': deviation,
            'combined_score': combined_score,
            'label': label,
            'baseline_phase': False,
            'baseline_progress': 100,
            'raw_confidence': confidence,
            'features_dict': features_dict
        }
    
    def get_summary(self):
        """Get session summary."""
        if self.frame_count == 0:
            return {}
        
        deception_percentage = (self.deception_frames / self.frame_count) * 100
        avg_confidence = np.mean(list(self.confidence_history)) if self.confidence_history else 0
        
        return {
            'total_frames': self.frame_count,
            'deception_frames': self.deception_frames,
            'deception_percentage': deception_percentage,
            'average_confidence': avg_confidence,
        }
    
    def reset(self):
        """Reset for new session."""
        self.baseline = BaselineEstablisher(duration_seconds=30)
        self.confidence_history = deque(maxlen=60)
        self.deviation_history = deque(maxlen=60)
        self.prediction_history = deque(maxlen=60)
        self.frame_count = 0
        self.deception_frames = 0
        self.baseline_phase = True
        self.baseline_start_time = None


def draw_ui(frame, result, detector):
    """Draw UI elements on frame."""
    h, w = frame.shape[:2]
    
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 100), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
    
    cv2.putText(frame, "EFFECTIVE FACE LIE DETECTOR", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    
    if result['baseline_phase']:
        status_text = f"Baseline: {result['baseline_progress']}%"
        color = (0, 255, 255)
    else:
        confidence = result['confidence']
        if confidence > 0.7:
            color = (0, 0, 255)
        elif confidence > 0.5:
            color = (0, 165, 255)
        else:
            color = (0, 255, 0)
        
        status_text = f"{result['label']} ({confidence:.2f})"
    
    cv2.putText(frame, status_text, (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    
    # Confidence bar
    bar_x, bar_y = w - 150, 20
    bar_w, bar_h = 130, 30
    
    if not result['baseline_phase']:
        confidence = result['confidence']
        filled_w = int(bar_w * confidence)
        
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), -1)
        
        if confidence > 0.7:
            color = (0, 0, 255)
        elif confidence > 0.5:
            color = (0, 165, 255)
        else:
            color = (0, 255, 0)
        
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + filled_w, bar_y + bar_h), color, -1)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (255, 255, 255), 2)
        
        cv2.putText(frame, "Deception Score", (bar_x - 20, bar_y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    cv2.putText(frame, "Press 'q' to quit", (10, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    return frame


def run_webcam():
    """Run real-time webcam detection."""
    
    print("\n" + "=" * 60)
    print("WEBCAM MODE - REAL-TIME LIE DETECTION")
    print("=" * 60)
    print("\n[INFO] Initializing detector...")
    
    try:
        detector = EffectiveLieDetectorMultiMode()
    except Exception as e:
        print(f"[ERROR] {e}")
        return
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam")
        return
    
    print("[INFO] Webcam opened. Starting detection...")
    print("[INFO] Phase 1: Establishing baseline (30 seconds)")
    print("[INFO] Keep your face neutral and still during baseline")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        result = detector.process_frame(frame)
        frame = draw_ui(frame, result, detector)
        
        cv2.imshow("Lie Detector - Webcam", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    summary = detector.get_summary()
    print("\n" + "=" * 60)
    print("FINAL SESSION REPORT")
    print("=" * 60)
    print(f"Total frames processed: {summary.get('total_frames', 0)}")
    print(f"Deception frames detected: {summary.get('deception_frames', 0)}")
    print(f"Deception percentage: {summary.get('deception_percentage', 0):.2f}%")
    print(f"Average deception confidence: {summary.get('average_confidence', 0):.4f}")
    print("=" * 60)
    
    if summary.get('deception_percentage', 0) > 30:
        print("\n[ALERT] High deception indicators detected!")
    elif summary.get('deception_percentage', 0) > 10:
        print("\n[NOTICE] Moderate deception indicators detected")
    else:
        print("\n[INFO] Low deception indicators - appears truthful")


def run_video_file(video_path):
    """Run detection on video file."""
    
    if not os.path.exists(video_path):
        print(f"[ERROR] Video file not found: {video_path}")
        return
    
    print("\n" + "=" * 60)
    print("VIDEO FILE MODE - LIE DETECTION")
    print("=" * 60)
    print(f"[INFO] Processing video: {video_path}")
    print("\n[INFO] Initializing detector...")
    
    try:
        detector = EffectiveLieDetectorMultiMode()
    except Exception as e:
        print(f"[ERROR] {e}")
        return
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("[ERROR] Could not open video file")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"[INFO] Video FPS: {fps}")
    print(f"[INFO] Total frames: {total_frames}")
    print(f"[INFO] Duration: {total_frames/fps:.2f} seconds")
    print("[INFO] Phase 1: Establishing baseline (30 seconds)")
    print("[INFO] Processing...")
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        result = detector.process_frame(frame)
        frame = draw_ui(frame, result, detector)
        
        frame_count += 1
        if frame_count % 30 == 0:
            progress = (frame_count / total_frames) * 100
            print(f"[PROGRESS] {progress:.1f}% - {result['label']}")
        
        cv2.imshow("Lie Detector - Video", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    summary = detector.get_summary()
    print("\n" + "=" * 60)
    print("VIDEO ANALYSIS REPORT")
    print("=" * 60)
    print(f"Total frames processed: {summary.get('total_frames', 0)}")
    print(f"Deception frames detected: {summary.get('deception_frames', 0)}")
    print(f"Deception percentage: {summary.get('deception_percentage', 0):.2f}%")
    print(f"Average deception confidence: {summary.get('average_confidence', 0):.4f}")
    print("=" * 60)
    
    if summary.get('deception_percentage', 0) > 30:
        print("\n[ALERT] High deception indicators detected!")
    elif summary.get('deception_percentage', 0) > 10:
        print("\n[NOTICE] Moderate deception indicators detected")
    else:
        print("\n[INFO] Low deception indicators - appears truthful")


def main():
    """Main menu."""
    
    print("\n" + "=" * 60)
    print("EFFECTIVE FACE LIE DETECTOR - MULTI-MODE")
    print("=" * 60)
    print("\nSelect mode:")
    print("1. Webcam (Live Detection)")
    print("2. Video File (Upload & Analyze)")
    print("3. Exit")
    print("\n" + "=" * 60)
    
    while True:
        choice = input("\nEnter choice (1/2/3): ").strip()
        
        if choice == '1':
            run_webcam()
        elif choice == '2':
            video_path = input("\nEnter video file path: ").strip()
            if video_path:
                run_video_file(video_path)
            else:
                print("[ERROR] No path provided")
        elif choice == '3':
            print("[INFO] Exiting...")
            break
        else:
            print("[ERROR] Invalid choice. Please enter 1, 2, or 3")


if __name__ == "__main__":
    main()
