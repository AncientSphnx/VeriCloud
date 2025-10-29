import cv2
import numpy as np
from scipy.spatial import distance as dist
from scipy import stats
from skimage import feature
import mediapipe as mp

class DeceptionFeatureExtractor:
    """
    Extracts 70+ deception-relevant facial features for lie detection.
    
    Feature Categories:
    1. Geometric Features (20): Eye/mouth/eyebrow ratios, asymmetry, distances
    2. Temporal Features (15): Frame-to-frame changes, blink detection, movement patterns
    3. Texture Features (15): LBP, HOG, skin texture analysis
    4. Eye Gaze Features (8): Horizontal/vertical direction, asymmetry, pupil size
    5. Skin Analysis Features (4): Brightness, variance, contrast, edge density
    6. Head Movement Features (8): Tilt, nod, shake, rotation angles
    """
    
    def __init__(self, shape_predictor_path=None):
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.prev_landmarks = None
        self.prev_face_image = None
        self.blink_history = []
        self.movement_history = []
        
    def extract_all_features(self, frame, landmarks=None):
        """
        Extract all 70+ deception features from a frame.
        
        Args:
            frame: BGR image frame
            landmarks: Pre-computed landmarks (optional)
            
        Returns:
            dict: Feature dictionary with all computed features
            np.array: Concatenated feature vector (70+ features)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h, w = frame.shape[:2]
        
        if landmarks is None:
            # Use MediaPipe for face detection and landmarks
            results = self.face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if not results.multi_face_landmarks:
                return None, None
            
            # Convert MediaPipe landmarks to numpy array (468 points)
            face_landmarks = results.multi_face_landmarks[0]
            landmarks = np.array([[lm.x * w, lm.y * h] for lm in face_landmarks.landmark])
        else:
            landmarks = landmarks
        
        features_dict = {}
        feature_vector = []
        
        # 1. GEOMETRIC FEATURES (20 features)
        geom_features, geom_vec = self._extract_geometric_features(landmarks)
        features_dict.update(geom_features)
        feature_vector.extend(geom_vec)
        
        # 2. TEMPORAL FEATURES (15 features)
        temp_features, temp_vec = self._extract_temporal_features(landmarks, gray)
        features_dict.update(temp_features)
        feature_vector.extend(temp_vec)
        
        # 3. TEXTURE FEATURES (15 features)
        texture_features, texture_vec = self._extract_texture_features(gray, landmarks)
        features_dict.update(texture_features)
        feature_vector.extend(texture_vec)
        
        # 4. EYE GAZE FEATURES (8 features)
        gaze_features, gaze_vec = self._extract_gaze_features(gray, landmarks)
        features_dict.update(gaze_features)
        feature_vector.extend(gaze_vec)
        
        # 5. SKIN ANALYSIS FEATURES (4 features)
        skin_features, skin_vec = self._extract_skin_features(gray, landmarks)
        features_dict.update(skin_features)
        feature_vector.extend(skin_vec)
        
        # 6. HEAD MOVEMENT FEATURES (8 features)
        head_features, head_vec = self._extract_head_movement_features(landmarks)
        features_dict.update(head_features)
        feature_vector.extend(head_vec)
        
        # Update history for temporal analysis
        self.prev_landmarks = landmarks.copy()
        self.prev_face_image = gray.copy()
        
        return features_dict, np.array(feature_vector, dtype=np.float32)
    
    def _extract_geometric_features(self, landmarks):
        """Extract 20 geometric features."""
        features = {}
        vec = []
        
        # Eye landmarks
        left_eye = landmarks[36:42]
        right_eye = landmarks[42:48]
        
        # 1-2: Eye Aspect Ratio (EAR)
        left_ear = self._eye_aspect_ratio(left_eye)
        right_ear = self._eye_aspect_ratio(right_eye)
        features['left_ear'] = left_ear
        features['right_ear'] = right_ear
        vec.extend([left_ear, right_ear])
        
        # 3: Average EAR
        avg_ear = (left_ear + right_ear) / 2.0
        features['avg_ear'] = avg_ear
        vec.append(avg_ear)
        
        # 4: EAR Asymmetry (deception indicator)
        ear_asymmetry = abs(left_ear - right_ear)
        features['ear_asymmetry'] = ear_asymmetry
        vec.append(ear_asymmetry)
        
        # Mouth landmarks
        mouth = landmarks[48:68]
        
        # 5: Mouth Aspect Ratio (MAR)
        mar = self._mouth_aspect_ratio(mouth)
        features['mar'] = mar
        vec.append(mar)
        
        # 6: Mouth Width
        mouth_width = dist.euclidean(mouth[0], mouth[6])
        features['mouth_width'] = mouth_width
        vec.append(mouth_width)
        
        # 7: Mouth Height
        mouth_height = dist.euclidean(mouth[2], mouth[10])
        features['mouth_height'] = mouth_height
        vec.append(mouth_height)
        
        # 8: Mouth Width-Height Ratio
        mouth_ratio = mouth_width / (mouth_height + 1e-6)
        features['mouth_ratio'] = mouth_ratio
        vec.append(mouth_ratio)
        
        # Eyebrow landmarks
        left_eyebrow = landmarks[17:22]
        right_eyebrow = landmarks[22:27]
        
        # 9-10: Eyebrow Height (inner)
        left_eyebrow_height = abs(left_eyebrow[0][1] - left_eyebrow[2][1])
        right_eyebrow_height = abs(right_eyebrow[0][1] - right_eyebrow[2][1])
        features['left_eyebrow_height'] = left_eyebrow_height
        features['right_eyebrow_height'] = right_eyebrow_height
        vec.extend([left_eyebrow_height, right_eyebrow_height])
        
        # 11: Eyebrow Height Asymmetry
        eyebrow_asymmetry = abs(left_eyebrow_height - right_eyebrow_height)
        features['eyebrow_asymmetry'] = eyebrow_asymmetry
        vec.append(eyebrow_asymmetry)
        
        # Nose landmarks
        nose = landmarks[27:36]
        
        # 12: Nose Width
        nose_width = dist.euclidean(nose[3], nose[5])
        features['nose_width'] = nose_width
        vec.append(nose_width)
        
        # Facial landmarks spread
        # 13: Face Width (distance between outer eye corners)
        face_width = dist.euclidean(landmarks[36], landmarks[45])
        features['face_width'] = face_width
        vec.append(face_width)
        
        # 14: Face Height (distance from forehead to chin)
        face_height = dist.euclidean(landmarks[19], landmarks[57])
        features['face_height'] = face_height
        vec.append(face_height)
        
        # 15: Face Aspect Ratio
        face_ar = face_width / (face_height + 1e-6)
        features['face_ar'] = face_ar
        vec.append(face_ar)
        
        # 16: Jaw Width
        jaw_width = dist.euclidean(landmarks[4], landmarks[12])
        features['jaw_width'] = jaw_width
        vec.append(jaw_width)
        
        # 17: Jaw Clenching (lower face height)
        lower_face_height = dist.euclidean(landmarks[30], landmarks[57])
        features['lower_face_height'] = lower_face_height
        vec.append(lower_face_height)
        
        # 18: Facial Tension (overall landmark spread variance)
        all_distances = []
        for i in range(len(landmarks)):
            for j in range(i+1, min(i+5, len(landmarks))):
                all_distances.append(dist.euclidean(landmarks[i], landmarks[j]))
        facial_tension = np.std(all_distances) if all_distances else 0
        features['facial_tension'] = facial_tension
        vec.append(facial_tension)
        
        # 19-20: Mouth Corner Heights (asymmetry indicator)
        left_mouth_corner_height = landmarks[48][1]
        right_mouth_corner_height = landmarks[54][1]
        mouth_corner_asymmetry = abs(left_mouth_corner_height - right_mouth_corner_height)
        features['mouth_corner_asymmetry'] = mouth_corner_asymmetry
        vec.append(mouth_corner_asymmetry)
        
        # Smile symmetry
        smile_symmetry = abs(dist.euclidean(landmarks[48], landmarks[54]) - 
                            dist.euclidean(landmarks[49], landmarks[53]))
        features['smile_symmetry'] = smile_symmetry
        vec.append(smile_symmetry)
        
        return features, vec
    
    def _extract_temporal_features(self, landmarks, gray):
        """Extract 15 temporal features (frame-to-frame changes)."""
        features = {}
        vec = []
        
        # Initialize with zeros if no previous frame
        if self.prev_landmarks is None:
            return {f'temporal_{i}': 0.0 for i in range(15)}, [0.0] * 15
        
        # 1-3: Landmark Movement (overall, eyes, mouth)
        landmark_movement = np.mean([dist.euclidean(landmarks[i], self.prev_landmarks[i]) 
                                     for i in range(len(landmarks))])
        features['landmark_movement'] = landmark_movement
        vec.append(landmark_movement)
        
        eye_movement = np.mean([dist.euclidean(landmarks[i], self.prev_landmarks[i]) 
                               for i in range(36, 48)])
        features['eye_movement'] = eye_movement
        vec.append(eye_movement)
        
        mouth_movement = np.mean([dist.euclidean(landmarks[i], self.prev_landmarks[i]) 
                                 for i in range(48, 68)])
        features['mouth_movement'] = mouth_movement
        vec.append(mouth_movement)
        
        # 4: Movement Consistency (variance of movements)
        movements = [dist.euclidean(landmarks[i], self.prev_landmarks[i]) 
                    for i in range(len(landmarks))]
        movement_variance = np.var(movements)
        features['movement_variance'] = movement_variance
        vec.append(movement_variance)
        
        # 5: Blink Detection (eye closure)
        left_ear_prev = self._eye_aspect_ratio(self.prev_landmarks[36:42])
        right_ear_prev = self._eye_aspect_ratio(self.prev_landmarks[42:48])
        left_ear_curr = self._eye_aspect_ratio(landmarks[36:42])
        right_ear_curr = self._eye_aspect_ratio(landmarks[42:48])
        
        blink_magnitude = abs((left_ear_curr + right_ear_curr) / 2 - 
                             (left_ear_prev + right_ear_prev) / 2)
        features['blink_magnitude'] = blink_magnitude
        vec.append(blink_magnitude)
        
        # 6: Blink Rate (track blinks over time)
        self.blink_history.append(blink_magnitude)
        if len(self.blink_history) > 30:
            self.blink_history.pop(0)
        blink_rate = sum(1 for b in self.blink_history if b > 0.15) / max(len(self.blink_history), 1)
        features['blink_rate'] = blink_rate
        vec.append(blink_rate)
        
        # 7: Eye Closure Speed (rate of change)
        eye_closure_speed = blink_magnitude * 30  # Assuming 30 FPS
        features['eye_closure_speed'] = eye_closure_speed
        vec.append(eye_closure_speed)
        
        # 8: Mouth Movement Speed
        mouth_movement_speed = mouth_movement * 30
        features['mouth_movement_speed'] = mouth_movement_speed
        vec.append(mouth_movement_speed)
        
        # 9: Head Movement (nose tip movement)
        nose_movement = dist.euclidean(landmarks[30], self.prev_landmarks[30])
        features['nose_movement'] = nose_movement
        vec.append(nose_movement)
        
        # 10: Eyebrow Movement
        eyebrow_movement = np.mean([dist.euclidean(landmarks[i], self.prev_landmarks[i]) 
                                   for i in range(17, 27)])
        features['eyebrow_movement'] = eyebrow_movement
        vec.append(eyebrow_movement)
        
        # 11: Jerky Movement Detection (sudden changes)
        self.movement_history.append(landmark_movement)
        if len(self.movement_history) > 10:
            self.movement_history.pop(0)
        jerkiness = np.std(self.movement_history) if len(self.movement_history) > 1 else 0
        features['jerkiness'] = jerkiness
        vec.append(jerkiness)
        
        # 12: Smooth vs Jerky (coefficient of variation)
        if landmark_movement > 0:
            smoothness = jerkiness / (landmark_movement + 1e-6)
        else:
            smoothness = 0
        features['smoothness'] = smoothness
        vec.append(smoothness)
        
        # 13: Mouth Opening Speed
        mar_curr = self._mouth_aspect_ratio(landmarks[48:68])
        mar_prev = self._mouth_aspect_ratio(self.prev_landmarks[48:68])
        mouth_opening_speed = abs(mar_curr - mar_prev) * 30
        features['mouth_opening_speed'] = mouth_opening_speed
        vec.append(mouth_opening_speed)
        
        # 14-15: Asymmetry Changes
        ear_asym_curr = abs(self._eye_aspect_ratio(landmarks[36:42]) - 
                           self._eye_aspect_ratio(landmarks[42:48]))
        ear_asym_prev = abs(self._eye_aspect_ratio(self.prev_landmarks[36:42]) - 
                           self._eye_aspect_ratio(self.prev_landmarks[42:48]))
        asymmetry_change = abs(ear_asym_curr - ear_asym_prev)
        features['asymmetry_change'] = asymmetry_change
        vec.append(asymmetry_change)
        
        # Facial tension change
        all_distances_curr = []
        for i in range(len(landmarks)):
            for j in range(i+1, min(i+5, len(landmarks))):
                all_distances_curr.append(dist.euclidean(landmarks[i], landmarks[j]))
        tension_curr = np.std(all_distances_curr) if all_distances_curr else 0
        
        all_distances_prev = []
        for i in range(len(self.prev_landmarks)):
            for j in range(i+1, min(i+5, len(self.prev_landmarks))):
                all_distances_prev.append(dist.euclidean(self.prev_landmarks[i], self.prev_landmarks[j]))
        tension_prev = np.std(all_distances_prev) if all_distances_prev else 0
        
        tension_change = abs(tension_curr - tension_prev)
        features['tension_change'] = tension_change
        vec.append(tension_change)
        
        return features, vec
    
    def _extract_texture_features(self, gray, landmarks):
        """Extract 15 texture features (LBP, HOG, skin texture)."""
        features = {}
        vec = []
        
        # Crop face region
        face_region = self._get_face_region(gray, landmarks)
        if face_region is None:
            return {f'texture_{i}': 0.0 for i in range(15)}, [0.0] * 15
        
        # Resize for consistent analysis
        face_resized = cv2.resize(face_region, (100, 100))
        
        # 1-8: LBP Histogram (8 bins instead of 26 for efficiency)
        lbp = feature.local_binary_pattern(face_resized, P=8, R=1, method="uniform")
        hist_lbp, _ = np.histogram(lbp.ravel(), bins=10, range=(0, 10))
        hist_lbp = hist_lbp.astype("float") / (hist_lbp.sum() + 1e-6)
        features.update({f'lbp_bin_{i}': hist_lbp[i] for i in range(8)})
        vec.extend(hist_lbp[:8])
        
        # 9: LBP Entropy (texture complexity)
        lbp_entropy = stats.entropy(hist_lbp + 1e-6)
        features['lbp_entropy'] = lbp_entropy
        vec.append(lbp_entropy)
        
        # 10: Face Image Contrast
        contrast = np.std(face_resized)
        features['contrast'] = contrast
        vec.append(contrast)
        
        # 11: Face Image Brightness
        brightness = np.mean(face_resized)
        features['brightness'] = brightness
        vec.append(brightness)
        
        # 12: Edge Density (Canny edges)
        edges = cv2.Canny(face_resized, 50, 150)
        edge_density = np.sum(edges > 0) / (edges.size + 1e-6)
        features['edge_density'] = edge_density
        vec.append(edge_density)
        
        # 13: Texture Uniformity (inverse of entropy)
        texture_uniformity = 1.0 / (lbp_entropy + 1e-6)
        features['texture_uniformity'] = texture_uniformity
        vec.append(texture_uniformity)
        
        # 14: Skin Roughness (high-frequency components)
        laplacian = cv2.Laplacian(face_resized, cv2.CV_64F)
        roughness = np.std(laplacian)
        features['roughness'] = roughness
        vec.append(roughness)
        
        # 15: Texture Variance
        texture_variance = np.var(face_resized)
        features['texture_variance'] = texture_variance
        vec.append(texture_variance)
        
        return features, vec
    
    def _extract_gaze_features(self, gray, landmarks):
        """Extract 8 eye gaze features."""
        features = {}
        vec = []
        
        # Extract eye regions
        left_eye = landmarks[36:42]
        right_eye = landmarks[42:48]
        
        # 1-2: Gaze Direction (horizontal)
        left_gaze_x = self._estimate_gaze_direction(gray, left_eye)[0]
        right_gaze_x = self._estimate_gaze_direction(gray, right_eye)[0]
        features['left_gaze_x'] = left_gaze_x
        features['right_gaze_x'] = right_gaze_x
        vec.extend([left_gaze_x, right_gaze_x])
        
        # 3-4: Gaze Direction (vertical)
        left_gaze_y = self._estimate_gaze_direction(gray, left_eye)[1]
        right_gaze_y = self._estimate_gaze_direction(gray, right_eye)[1]
        features['left_gaze_y'] = left_gaze_y
        features['right_gaze_y'] = right_gaze_y
        vec.extend([left_gaze_y, right_gaze_y])
        
        # 5: Gaze Asymmetry (looking in different directions)
        gaze_asymmetry = abs(left_gaze_x - right_gaze_x) + abs(left_gaze_y - right_gaze_y)
        features['gaze_asymmetry'] = gaze_asymmetry
        vec.append(gaze_asymmetry)
        
        # 6: Gaze Deviation (looking away from center)
        gaze_deviation = abs(left_gaze_x) + abs(right_gaze_x) + abs(left_gaze_y) + abs(right_gaze_y)
        features['gaze_deviation'] = gaze_deviation
        vec.append(gaze_deviation)
        
        # 7-8: Pupil Size (approximated by eye opening)
        left_ear = self._eye_aspect_ratio(left_eye)
        right_ear = self._eye_aspect_ratio(right_eye)
        features['left_pupil_size'] = left_ear
        features['right_pupil_size'] = right_ear
        vec.extend([left_ear, right_ear])
        
        return features, vec
    
    def _extract_skin_features(self, gray, landmarks):
        """Extract 4 skin analysis features."""
        features = {}
        vec = []
        
        # Get skin region (face area excluding eyes and mouth)
        skin_region = self._get_skin_region(gray, landmarks)
        if skin_region is None:
            return {f'skin_{i}': 0.0 for i in range(4)}, [0.0] * 4
        
        # 1: Skin Brightness (redness indicator)
        skin_brightness = np.mean(skin_region)
        features['skin_brightness'] = skin_brightness
        vec.append(skin_brightness)
        
        # 2: Skin Variance (flushing/perspiration)
        skin_variance = np.var(skin_region)
        features['skin_variance'] = skin_variance
        vec.append(skin_variance)
        
        # 3: Skin Contrast
        skin_contrast = np.std(skin_region)
        features['skin_contrast'] = skin_contrast
        vec.append(skin_contrast)
        
        # 4: Skin Edge Density (perspiration/texture)
        edges = cv2.Canny(skin_region, 30, 100)
        skin_edge_density = np.sum(edges > 0) / (edges.size + 1e-6)
        features['skin_edge_density'] = skin_edge_density
        vec.append(skin_edge_density)
        
        return features, vec
    
    def _extract_head_movement_features(self, landmarks):
        """Extract 8 head movement features."""
        features = {}
        vec = []
        
        if self.prev_landmarks is None:
            return {f'head_{i}': 0.0 for i in range(8)}, [0.0] * 8
        
        # 1: Head Tilt (rotation around z-axis)
        left_eye_curr = landmarks[36]
        right_eye_curr = landmarks[45]
        left_eye_prev = self.prev_landmarks[36]
        right_eye_prev = self.prev_landmarks[45]
        
        angle_curr = np.arctan2(left_eye_curr[1] - right_eye_curr[1], 
                               left_eye_curr[0] - right_eye_curr[0])
        angle_prev = np.arctan2(left_eye_prev[1] - right_eye_prev[1], 
                               left_eye_prev[0] - right_eye_prev[0])
        head_tilt = abs(angle_curr - angle_prev)
        features['head_tilt'] = head_tilt
        vec.append(head_tilt)
        
        # 2: Head Nod (vertical movement)
        nose_curr = landmarks[30]
        nose_prev = self.prev_landmarks[30]
        head_nod = abs(nose_curr[1] - nose_prev[1])
        features['head_nod'] = head_nod
        vec.append(head_nod)
        
        # 3: Head Shake (horizontal movement)
        head_shake = abs(nose_curr[0] - nose_prev[0])
        features['head_shake'] = head_shake
        vec.append(head_shake)
        
        # 4: Head Movement Magnitude
        head_movement = dist.euclidean(nose_curr, nose_prev)
        features['head_movement'] = head_movement
        vec.append(head_movement)
        
        # 5: Head Rotation X (pitch)
        chin_curr = landmarks[57]
        chin_prev = self.prev_landmarks[57]
        pitch = abs((chin_curr[1] - nose_curr[1]) - (chin_prev[1] - nose_prev[1]))
        features['head_pitch'] = pitch
        vec.append(pitch)
        
        # 6: Head Rotation Y (yaw)
        yaw = abs((chin_curr[0] - nose_curr[0]) - (chin_prev[0] - nose_prev[0]))
        features['head_yaw'] = yaw
        vec.append(yaw)
        
        # 7: Head Stability (consistency of movement)
        if len(self.movement_history) > 1:
            head_stability = 1.0 / (np.std(self.movement_history) + 1e-6)
        else:
            head_stability = 1.0
        features['head_stability'] = head_stability
        vec.append(head_stability)
        
        # 8: Head Movement Speed
        head_speed = head_movement * 30  # Assuming 30 FPS
        features['head_speed'] = head_speed
        vec.append(head_speed)
        
        return features, vec
    
    def _eye_aspect_ratio(self, eye):
        """Calculate eye aspect ratio."""
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        C = dist.euclidean(eye[0], eye[3])
        ear = (A + B) / (2.0 * C + 1e-6)
        return ear
    
    def _mouth_aspect_ratio(self, mouth):
        """Calculate mouth aspect ratio."""
        A = dist.euclidean(mouth[13], mouth[19])
        B = dist.euclidean(mouth[14], mouth[18])
        C = dist.euclidean(mouth[15], mouth[17])
        D = dist.euclidean(mouth[12], mouth[16])
        mar = (A + B + C) / (2.0 * D + 1e-6)
        return mar
    
    def _get_face_region(self, gray, landmarks):
        """Extract face region from image."""
        try:
            x_min = max(0, int(landmarks[:, 0].min()) - 10)
            x_max = min(gray.shape[1], int(landmarks[:, 0].max()) + 10)
            y_min = max(0, int(landmarks[:, 1].min()) - 10)
            y_max = min(gray.shape[0], int(landmarks[:, 1].max()) + 10)
            return gray[y_min:y_max, x_min:x_max]
        except:
            return None
    
    def _get_skin_region(self, gray, landmarks):
        """Extract skin region (cheeks area)."""
        try:
            # Use cheek area (between eyes and mouth, excluding mouth)
            left_cheek_x = int(landmarks[1][0])
            right_cheek_x = int(landmarks[15][0])
            cheek_y_start = int(landmarks[27][1])
            cheek_y_end = int(landmarks[57][1])
            
            x_min = max(0, left_cheek_x)
            x_max = min(gray.shape[1], right_cheek_x)
            y_min = max(0, cheek_y_start)
            y_max = min(gray.shape[0], cheek_y_end)
            
            if x_max > x_min and y_max > y_min:
                return gray[y_min:y_max, x_min:x_max]
            return None
        except:
            return None
    
    def _estimate_gaze_direction(self, gray, eye):
        """Estimate gaze direction from eye region."""
        try:
            eye_x = int(np.mean(eye[:, 0]))
            eye_y = int(np.mean(eye[:, 1]))
            eye_w = int(abs(eye[0, 0] - eye[3, 0]))
            eye_h = int(abs(eye[1, 1] - eye[5, 1]))
            
            x_min = max(0, eye_x - eye_w)
            x_max = min(gray.shape[1], eye_x + eye_w)
            y_min = max(0, eye_y - eye_h)
            y_max = min(gray.shape[0], eye_y + eye_h)
            
            if x_max > x_min and y_max > y_min:
                eye_region = gray[y_min:y_max, x_min:x_max]
                # Find pupil (darkest region)
                _, binary = cv2.threshold(eye_region, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours:
                    largest_contour = max(contours, key=cv2.contourArea)
                    M = cv2.moments(largest_contour)
                    if M["m00"] > 0:
                        pupil_x = M["m10"] / M["m00"]
                        pupil_y = M["m01"] / M["m00"]
                        # Normalize to -1 to 1 range
                        gaze_x = (pupil_x - eye_w) / eye_w
                        gaze_y = (pupil_y - eye_h) / eye_h
                        return gaze_x, gaze_y
            
            return 0.0, 0.0
        except:
            return 0.0, 0.0
