# backend/predictor.py
import torch
import torch.nn as nn
import numpy as np
import librosa
import os
from moviepy.editor import VideoFileClip
from pydub import AudioSegment

# -----------------------------
# 1. Model Definition (BiLSTM + Attention)
# -----------------------------
class BiLSTM_Attention(nn.Module):
    def __init__(self, input_size=39, hidden_size=256, num_classes=2):
        super(BiLSTM_Attention, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, bidirectional=True, batch_first=True)
        self.attention = nn.Linear(hidden_size * 2, 1)
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size * 2, 256),
            nn.ReLU(),
            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        lstm_out, _ = self.lstm(x)  # (batch, seq_len, hidden*2)
        attn_weights = torch.softmax(self.attention(lstm_out), dim=1)  # (batch, seq_len, 1)
        context = torch.sum(attn_weights * lstm_out, dim=1)  # Weighted sum
        out = self.classifier(context)
        return out

# -----------------------------
# 2. Load Model
# -----------------------------
def load_model(model_path: str) -> nn.Module:
    model = BiLSTM_Attention()
    state = torch.load(model_path, map_location="cpu")
    model.load_state_dict(state, strict=False)
    model.eval()
    return model

# -----------------------------
# 3. Handle Any File Type → WAV
# -----------------------------
def convert_to_wav(input_path: str) -> str:
    ext = os.path.splitext(input_path)[1].lower()
    temp_wav = "temp_audio.wav"

    if ext in [".mp4", ".avi", ".mov", ".mkv"]:
        clip = VideoFileClip(input_path)
        clip.audio.write_audiofile(temp_wav, verbose=False, logger=None)
        return temp_wav

    if ext in [".mp3", ".ogg", ".flac"]:
        audio = AudioSegment.from_file(input_path)
        audio.export(temp_wav, format="wav")
        return temp_wav

    if ext == ".wav":
        return input_path

    raise ValueError(f"Unsupported file format: {ext}")

# -----------------------------
# 4. Audio → Feature Extraction (MFCC + Δ + ΔΔ = 39 features)
# -----------------------------
def extract_features(file_path: str, n_mfcc: int = 13) -> np.ndarray:
    y, sr = librosa.load(file_path, sr=16000)

    # Base MFCCs
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)

    # Delta (1st derivative)
    delta = librosa.feature.delta(mfcc)

    # Delta-Delta (2nd derivative)
    delta2 = librosa.feature.delta(mfcc, order=2)

    # Stack them: [mfcc; delta; delta2] → (39, time_steps)
    combined = np.vstack([mfcc, delta, delta2])

    # Transpose to shape (time_steps, 39) to match training data
    return combined.T

# -----------------------------
# 5. Prediction Function
# -----------------------------
def predict(file_path: str, model_path: str, threshold: float = 0.5):
    # Convert to wav if needed
    wav_path = convert_to_wav(file_path)

    # Load model
    model = load_model(model_path)

    # Extract features
    feats = extract_features(wav_path)   # shape: (time_steps, 39)
    x = torch.tensor(feats, dtype=torch.float32).unsqueeze(0)  # (1, seq_len, 39)

    # Forward pass
    with torch.no_grad():
        output = model(x)
        probs = torch.softmax(output, dim=1)[0]
        lie_prob = probs[1].item()

    # Decision
    if lie_prob >= threshold:
        label = "Lie"
        confidence = lie_prob * 100
    else:
        label = "Truth"
        confidence = (1 - lie_prob) * 100

    return label, confidence
