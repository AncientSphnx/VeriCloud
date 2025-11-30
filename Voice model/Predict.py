import torch
import torch.nn as nn
import numpy as np
import librosa
import os
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import customtkinter as ctk
from tkinter import filedialog, messagebox

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
        lstm_out, _ = self.lstm(x)
        attn_weights = torch.softmax(self.attention(lstm_out), dim=1)
        context = torch.sum(attn_weights * lstm_out, dim=1)
        out = self.classifier(context)
        return out

# -----------------------------
# 2. Load Model
# -----------------------------
def load_model(model_path):
    model = BiLSTM_Attention()
    state = torch.load(model_path, map_location="cpu")
    model.load_state_dict(state, strict=False)
    model.eval()
    return model

# -----------------------------
# 3. Handle Any File Type → WAV
# -----------------------------
def convert_to_wav(input_path):
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
# 4. Audio → MFCC Extraction
# -----------------------------
def extract_mfcc(file_path, n_mfcc=39):
    y, sr = librosa.load(file_path, sr=16000)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    return mfcc.T

# -----------------------------
# 5. Prediction Function
# -----------------------------
def predict(file_path, model_path, threshold=0.5):
    wav_path = convert_to_wav(file_path)
    model = load_model(model_path)
    mfcc = extract_mfcc(wav_path)
    x = torch.tensor(mfcc, dtype=torch.float32).unsqueeze(0)

    with torch.no_grad():
        output = model(x)
        probs = torch.softmax(output, dim=1)[0]
        lie_prob = probs[1].item()

    if lie_prob >= threshold:
        label = "Lie"
        confidence = lie_prob * 100
    else:
        label = "Truth"
        confidence = (1 - lie_prob) * 100

    return label, confidence

# -----------------------------
# 6. Sexy GUI with customtkinter
# -----------------------------
def launch_gui(model_path):
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("🔥 Lie Detector Pro 🔥")
    app.geometry("400x300")

    title_label = ctk.CTkLabel(app, text="Lie Detector AI", font=("Arial", 24, "bold"))
    title_label.pack(pady=20)

    result_label = ctk.CTkLabel(app, text="", font=("Arial", 18))
    result_label.pack(pady=10)

    def select_file():
        file_path = filedialog.askopenfilename(
            title="Select audio/video file",
            filetypes=[("Media files", "*.mp3 *.wav *.mp4 *.avi *.mov *.mkv *.ogg *.flac")]
        )
        if file_path:
            try:
                label, confidence = predict(file_path, model_path)
                result_label.configure(text=f"{label} ({confidence:.2f}%)")
                if label == "Lie":
                    result_label.configure(text_color="red")
                else:
                    result_label.configure(text_color="green")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    upload_button = ctk.CTkButton(app, text="🎵 Select File", command=select_file, width=200, height=40)
    upload_button.pack(pady=20)

    exit_button = ctk.CTkButton(app, text="Exit", command=app.destroy, width=200, height=40)
    exit_button.pack(pady=10)

    app.mainloop()

# -----------------------------
# 7. Run GUI
# -----------------------------
if __name__ == "__main__":
    model_path = r"C:\Users\91829\OneDrive\Desktop\Project truth 7.0\Project truth 6.0\src\models\model_final2.pth"  # Change to your model path
    launch_gui(model_path)
