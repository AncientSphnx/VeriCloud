import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import librosa
import soundfile as sf
from tqdm import tqdm


@dataclass
class PitchConfig:
    input_folder: str
    output_file: str  # CSV or JSON
    metadata_csv: Optional[str] = None  # optional labels

    # Audio
    sample_rate: int = 16000

    # Short frames for pitch/stress
    frame_ms: float = 25.0
    hop_ms: float = 10.0
    window: str = "hann"

    # YIN parameters
    fmin: float = 50.0
    fmax: float = 500.0
    yin_frame_length: Optional[int] = None  # None → derived from frame_ms
    yin_threshold: float = 0.1

    # Tonal/stress heuristics
    tonal_delta_hz: float = 5.0  # change per hop considered rising/falling
    energy_eps: float = 1e-8

    # Output format
    format: str = "csv"  # 'csv' or 'json'


def _load_mono(path: str, target_sr: int) -> np.ndarray:
    try:
        signal, sr = sf.read(path, always_2d=False)
        if signal.ndim > 1:
            signal = np.mean(signal, axis=1)
    except Exception:
        signal, sr = librosa.load(path, sr=None, mono=True)
    if sr != target_sr:
        signal = librosa.resample(signal, orig_sr=sr, target_sr=target_sr)
    return signal.astype(np.float32)


def _frame_and_hop_samples(cfg: PitchConfig) -> Tuple[int, int]:
    frame = int(round(cfg.sample_rate * (cfg.frame_ms / 1000.0)))
    hop = int(round(cfg.sample_rate * (cfg.hop_ms / 1000.0)))
    return frame, hop


def segment_frames(signal: np.ndarray, sr: int, frame: int, hop: int) -> np.ndarray:
    """Return a framed 2D array shape (num_frames, frame)."""
    if len(signal) < frame:
        return np.empty((0, frame), dtype=signal.dtype)
    pad = (len(signal) - frame) % hop
    if pad != 0:
        signal = np.pad(signal, (0, hop - pad))
    frames = librosa.util.frame(signal, frame_length=frame, hop_length=hop).T
    return frames


def compute_pitch_yin(
    frames: np.ndarray,
    sr: int,
    cfg: PitchConfig,
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute pitch contour using librosa.yin per frame."""
    if frames.size == 0:
        return np.zeros((0,), dtype=np.float32), np.zeros((0,), dtype=bool)
    frame_len = frames.shape[1]
    win_len = cfg.yin_frame_length or frame_len
    f0_list: List[float] = []
    voiced_list: List[bool] = []
    for i in range(frames.shape[0]):
        f0 = librosa.yin(frames[i], fmin=cfg.fmin, fmax=cfg.fmax, sr=sr,
                         frame_length=win_len, trough_threshold=cfg.yin_threshold)
        val = float(f0.mean()) if f0.size > 0 else 0.0
        f0_list.append(val if np.isfinite(val) else 0.0)
        voiced_list.append(val > 0)
    return np.asarray(f0_list, dtype=np.float32), np.asarray(voiced_list, dtype=bool)


def estimate_f0_from_pitch(f0_hz: np.ndarray, voiced: np.ndarray) -> float:
    """Estimate global F0 for the segment as median over voiced frames."""
    if f0_hz.size == 0 or not np.any(voiced):
        return 0.0
    return float(np.median(f0_hz[voiced]))


def extract_tonal_features(f0_hz: np.ndarray, voiced: np.ndarray, cfg: PitchConfig) -> Dict[str, float]:
    """Extract simple tonal descriptors: rising/falling ratios and stability."""
    if f0_hz.size == 0:
        return {"rise_ratio": 0.0, "fall_ratio": 0.0, "stable_ratio": 0.0}
    f = f0_hz.copy()
    f[~voiced] = np.nan
    d = np.diff(f)
    valid = ~np.isnan(d)
    if not np.any(valid):
        return {"rise_ratio": 0.0, "fall_ratio": 0.0, "stable_ratio": 0.0}
    threshold = cfg.tonal_delta_hz
    rise = np.sum((d[valid] > threshold).astype(np.float32))
    fall = np.sum((d[valid] < -threshold).astype(np.float32))
    stable = np.sum((np.abs(d[valid]) <= threshold).astype(np.float32))
    total = float(np.sum(valid))
    return {
        "rise_ratio": float(rise / total),
        "fall_ratio": float(fall / total),
        "stable_ratio": float(stable / total),
    }


def _rms_energy(frames: np.ndarray, eps: float) -> np.ndarray:
    if frames.size == 0:
        return np.zeros((0,), dtype=np.float32)
    return np.sqrt(np.mean(frames.astype(np.float32) ** 2, axis=1) + eps)


def extract_stress_features(frames: np.ndarray, cfg: PitchConfig) -> Dict[str, float]:
    """Heuristic stress features from short-time energy and zero-crossing rate."""
    if frames.size == 0:
        return {"zcr_mean": 0.0, "zcr_std": 0.0, "energy_cv": 0.0}
    energy = _rms_energy(frames, cfg.energy_eps)
    energy_cv = float(np.std(energy) / (np.mean(energy) + 1e-8))
    zcr = librosa.feature.zero_crossing_rate(frames.T).mean(axis=1)
    return {"zcr_mean": float(np.mean(zcr)), "zcr_std": float(np.std(zcr)), "energy_cv": energy_cv}


def _find_audio_files(folder: str) -> List[str]:
    exts = (".wav", ".flac", ".mp3", ".m4a", ".ogg")
    paths: List[str] = []
    for root, _, files in os.walk(folder):
        for n in files:
            if any(n.lower().endswith(e) for e in exts):
                paths.append(os.path.join(root, n))
    return sorted(paths)


def run_feature_extraction(cfg: PitchConfig) -> pd.DataFrame:
    """Run steps (i)-(ix) and return a DataFrame with features per file."""
    rows: List[Dict[str, object]] = []

    for path in tqdm(_find_audio_files(cfg.input_folder), desc="Feature extraction"):
        signal = _load_mono(path, target_sr=cfg.sample_rate)
        frame, hop = _frame_and_hop_samples(cfg)
        frames = segment_frames(signal, cfg.sample_rate, frame, hop)

        # ✅ window length always matches frame size
        window = librosa.filters.get_window(cfg.window, frames.shape[1], fftbins=True).astype(np.float32)
        frames_win = frames * window[None, :]

        # Pitch contour via YIN and F0 summary
        f0, voiced = compute_pitch_yin(frames_win, sr=cfg.sample_rate, cfg=cfg)
        f0_median = estimate_f0_from_pitch(f0, voiced)

        # Tonal and stress features
        tonal = extract_tonal_features(f0, voiced, cfg)
        stress = extract_stress_features(frames_win, cfg)

        # ✅ Auto-label based on filename
        fname = os.path.basename(path).lower()
        if "lie" in fname:
            label = "lie"
        elif "truth" in fname:
            label = "truth"
        else:
            label = None

        row = {
            "file_id": os.path.basename(path),
            "f0_median": f0_median,
            **{f"tonal_{k}": v for k, v in tonal.items()},
            **{f"stress_{k}": v for k, v in stress.items()},
            "label": label,
        }
        rows.append(row)

    df_out = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(cfg.output_file) or ".", exist_ok=True)
    if cfg.format.lower() == "csv":
        df_out.to_csv(cfg.output_file, index=False)
    else:
        df_out.to_json(cfg.output_file, orient="records", lines=False)
    return df_out
