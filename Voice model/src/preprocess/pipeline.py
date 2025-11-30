import math
import os
from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import librosa
import soundfile as sf
from tqdm import tqdm


# ----------------------------- Data Classes -----------------------------

@dataclass
class SegmentMeta:
	file_id: str
	start_sample: int
	end_sample: int
	label: Optional[str] = None


@dataclass
class PreprocessConfig:
	# IO
	input_folder: str
	output_file: str
	metadata_csv: Optional[str] = None
	allowed_extensions: Tuple[str, ...] = (".wav", ".flac", ".mp3", ".m4a", ".ogg")

	# Audio
	sample_rate: int = 16000
	pre_emphasis: float = 0.97

	# Segmentation
	segment_seconds: float = 1.0
	hop_seconds: float = 1.0
	drop_last: bool = True

	# STFT / Windowing
	n_fft: int = 1024
	hop_length: Optional[int] = None  # defaults to n_fft // 4 if None
	window: str = "hann"  # 'hann' or 'hamming'

	# Mel / MFCC
	n_mels: int = 64
	n_mfcc: int = 39
	fmin: float = 20.0
	fmax: Optional[float] = None

	# Reproducibility / Misc
	seed: int = 42


# ----------------------------- Utilities -----------------------------

def find_audio_files(folder: str, extensions: Sequence[str]) -> List[str]:
	"""Recursively find audio files with given extensions."""
	paths: List[str] = []
	for root, _, files in os.walk(folder):
		for name in files:
			if any(name.lower().endswith(ext) for ext in extensions):
				paths.append(os.path.join(root, name))
	return sorted(paths)


def load_audio_file(path: str, target_sr: int) -> Tuple[np.ndarray, int]:
	"""Load an audio file and resample to target sample rate if needed."""
	try:
		# First try soundfile for reliability
		signal, sr = sf.read(path, always_2d=False)
		if signal.ndim > 1:
			# Convert to mono by averaging channels
			signal = np.mean(signal, axis=1)
	except Exception:
		# Fallback to librosa
		signal, sr = librosa.load(path, sr=None, mono=True)

	if sr != target_sr:
		signal = librosa.resample(signal, orig_sr=sr, target_sr=target_sr)
		sr = target_sr
	return signal.astype(np.float32), sr


def apply_pre_emphasis(signal: np.ndarray, coefficient: float = 0.97) -> np.ndarray:
	"""Apply a pre-emphasis filter to boost high-frequency components."""
	if len(signal) == 0:
		return signal
	# y[t] = x[t] - a * x[t-1]
	# Implement with np.concatenate for speed
	return np.concatenate([[signal[0]], signal[1:] - coefficient * signal[:-1]]).astype(np.float32)


def _samples_for_seconds(seconds: float, sr: int) -> int:
	return int(round(seconds * sr))


def segment_signal(
	signal: np.ndarray,
	sr: int,
	segment_seconds: float,
	hop_seconds: float,
	drop_last: bool = True,
) -> List[Tuple[int, int]]:
	"""Return list of (start_sample, end_sample) segments."""
	segment_len = _samples_for_seconds(segment_seconds, sr)
	hop_len = _samples_for_seconds(hop_seconds, sr)
	indices: List[Tuple[int, int]] = []
	for start in range(0, len(signal) - (0 if not drop_last else segment_len) + 1, hop_len):
		end = start + segment_len
		if end > len(signal):
			if drop_last:
				break
			end = len(signal)
		indices.append((start, end))
	return indices


def extract_mfcc_from_segment(
	segment: np.ndarray,
	sr: int,
	n_fft: int,
	hop_length: Optional[int],
	window: str,
	n_mels: int,
	n_mfcc: int,
	fmin: float,
	fmax: Optional[float],
) -> np.ndarray:
	"""Compute MFCCs from a 1D audio segment. Returns shape (num_frames, num_mfcc)."""
	if hop_length is None:
		hop_length = n_fft // 4
	# STFT magnitude power
	stft = librosa.stft(segment, n_fft=n_fft, hop_length=hop_length, window=window, center=True)
	power_spec = np.abs(stft) ** 2
	# Mel scaling
	mel_spec = librosa.feature.melspectrogram(S=power_spec, sr=sr, n_mels=n_mels, fmin=fmin, fmax=fmax)
	log_mel = librosa.power_to_db(mel_spec, ref=np.max)
	# MFCCs from log-mel
	mfcc = librosa.feature.mfcc(S=log_mel, n_mfcc=n_mfcc)
	# librosa returns (n_mfcc, frames) -> transpose to (frames, n_mfcc)
	return mfcc.T.astype(np.float32)


def _read_labels(metadata_csv: Optional[str]) -> Dict[str, str]:
	if not metadata_csv:
		return {}
	df = pd.read_csv(metadata_csv)
	# Expect columns: filepath,label
	if not {"filepath", "label"}.issubset(df.columns):
		raise ValueError("metadata_csv must contain columns: filepath,label")
	# Normalize paths to basenames for matching irrespective of directory nesting
	return {os.path.basename(str(p)): str(l) for p, l in zip(df["filepath"], df["label"])}


def compute_dataset_mfcc(
	filepaths: Sequence[str],
	config: PreprocessConfig,
) -> Tuple[List[np.ndarray], List[SegmentMeta]]:
	"""Compute MFCCs and metadata for all files. Returns per-segment features and metadata."""
	labels = _read_labels(config.metadata_csv)
	features: List[np.ndarray] = []
	metas: List[SegmentMeta] = []
	for path in tqdm(filepaths, desc="Processing audio"):
		signal, sr = load_audio_file(path, target_sr=config.sample_rate)
		signal = apply_pre_emphasis(signal, coefficient=config.pre_emphasis)
		segments = segment_signal(
			signal,
			sr,
			segment_seconds=config.segment_seconds,
			hop_seconds=config.hop_seconds,
			drop_last=config.drop_last,
		)
		for start, end in segments:
			seg = signal[start:end]
			mfcc = extract_mfcc_from_segment(
				seg,
				sr,
				n_fft=config.n_fft,
				hop_length=config.hop_length,
				window=config.window,
				n_mels=config.n_mels,
				n_mfcc=config.n_mfcc,
				fmin=config.fmin,
				fmax=config.fmax,
			)
			features.append(mfcc)
			metas.append(
				SegmentMeta(
					file_id=os.path.basename(path),
					start_sample=int(start),
					end_sample=int(end),
					label=labels.get(os.path.basename(path)),
				)
			)
	return features, metas


def compute_feature_stats(feature_list: Sequence[np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
	"""Compute dataset-wide mean and std per MFCC feature dimension.

	All arrays in feature_list must be shaped (frames, n_mfcc). Returns (mean, std) each of shape (n_mfcc,).
	"""
	if not feature_list:
		raise ValueError("feature_list is empty")
	# Accumulate sums over frames
	n_mfcc = feature_list[0].shape[1]
	sum_vec = np.zeros((n_mfcc,), dtype=np.float64)
	sumsq_vec = np.zeros((n_mfcc,), dtype=np.float64)
	count_frames = 0
	for arr in feature_list:
		if arr.ndim != 2 or arr.shape[1] != n_mfcc:
			raise ValueError("All feature arrays must have shape (frames, n_mfcc) and same n_mfcc")
		sum_vec += arr.sum(axis=0)
		sumsq_vec += (arr ** 2).sum(axis=0)
		count_frames += arr.shape[0]
	mean = sum_vec / max(count_frames, 1)
	var = (sumsq_vec / max(count_frames, 1)) - (mean ** 2)
	std = np.sqrt(np.maximum(var, 1e-12))
	return mean.astype(np.float32), std.astype(np.float32)


def normalize_feature_list(feature_list: Sequence[np.ndarray], mean: np.ndarray, std: np.ndarray) -> List[np.ndarray]:
	"""Normalize each array in the list with given mean/std."""
	normed: List[np.ndarray] = []
	for arr in feature_list:
		normed.append(((arr - mean) / std).astype(np.float32))
	return normed


def _pad_or_trim_to_length(arr: np.ndarray, target_frames: int) -> np.ndarray:
	"""Pad with zeros or trim to target number of frames along axis 0."""
	frames, n_mfcc = arr.shape
	if frames == target_frames:
		return arr
	if frames > target_frames:
		return arr[:target_frames]
	# pad
	pad = np.zeros((target_frames - frames, n_mfcc), dtype=arr.dtype)
	return np.vstack([arr, pad])


def save_hdf5(
	output_file: str,
	feature_list: Sequence[np.ndarray],
	metas: Sequence[SegmentMeta],
	mean: np.ndarray,
	std: np.ndarray,
	config: PreprocessConfig,
) -> None:
	"""Save normalized features and metadata to HDF5 with fixed-length sequences.

	We compute the expected number of frames per segment using librosa.time_to_frames to achieve
	a consistent tensor shape, then pad/trim each segment accordingly.
	"""
	import h5py  # local import to avoid import time if unused

	if len(feature_list) != len(metas):
		raise ValueError("feature_list and metas must have the same length")

	# Expected frames per segment given hop_length and n_fft
	hop_length = config.hop_length or (config.n_fft // 4)
	segment_frames = 1 + math.floor(
		(_samples_for_seconds(config.segment_seconds, config.sample_rate) - config.n_fft) / hop_length
	) if _samples_for_seconds(config.segment_seconds, config.sample_rate) >= config.n_fft else max(1, math.floor(_samples_for_seconds(config.segment_seconds, config.sample_rate) / hop_length))

	# Normalize features to fixed shape
	fixed = [_pad_or_trim_to_length(arr, target_frames=segment_frames) for arr in feature_list]
	features = np.stack(fixed, axis=0).astype(np.float32)  # (num_segments, frames, n_mfcc)

	os.makedirs(os.path.dirname(output_file), exist_ok=True)
	print(f"Saving features to {output_file} ...")
	with h5py.File(output_file, "w") as h5:
		# Datasets
		h5.create_dataset("features", data=features, dtype="float32", compression="gzip")
		str_dt = h5py.string_dtype(encoding="utf-8")
		h5.create_dataset("file_ids", data=[m.file_id for m in metas], dtype=str_dt)
		h5.create_dataset("start_sample", data=[m.start_sample for m in metas], dtype="int64")
		h5.create_dataset("end_sample", data=[m.end_sample for m in metas], dtype="int64")
		labels = [m.label if m.label is not None else "" for m in metas]
		h5.create_dataset("labels", data=labels, dtype=str_dt)

		# Attributes
		h5.attrs["feature_mean"] = mean.astype(np.float32)
		h5.attrs["feature_std"] = std.astype(np.float32)
		# Store config as attributes
		for key, value in asdict(config).items():
			# Store simple types only
			if isinstance(value, (int, float, str, bool)) or value is None:
				h5.attrs[f"config.{key}"] = "" if value is None else value
	



def run_preprocessing(config: PreprocessConfig) -> None:
	"""End-to-end preprocessing routine."""
	filepaths = find_audio_files(config.input_folder, config.allowed_extensions)
	if not filepaths:
		raise FileNotFoundError(f"No audio files found in: {config.input_folder}")

	features, metas = compute_dataset_mfcc(filepaths, config)
	mean, std = compute_feature_stats(features)
	norm_features = normalize_feature_list(features, mean, std)
	save_hdf5(config.output_file, norm_features, metas, mean, std, config)


