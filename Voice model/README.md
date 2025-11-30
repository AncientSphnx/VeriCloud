## Voice Preprocessing Pipeline (MFCC)

This repository contains a reproducible audio preprocessing pipeline that follows the steps you specified:

1. Load audio recordings
2. Validate/standardize file formats and sample rate
3. Apply pre-emphasis
4. Segment audio (fixed duration or sliding window)
5. Apply windowing function
6. Compute Fourier transform (STFT)
7. Convert to log-Mel and MFCCs
8. Normalize MFCCs using dataset-wide mean/std
9. Save processed features to HDF5 for efficient training

### Install

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Usage

```bash
python scripts/preprocess_audio.py \
  --input_folder path/to/audio \
  --output_file data/processed/mfcc.h5 \
  --sample_rate 16000 \
  --segment_seconds 1.0 \
  --hop_seconds 1.0 \
  --window hann \
  --n_fft 1024 \
  --n_mels 64 \
  --n_mfcc 20
```

Optional: provide a CSV with `filepath,label` columns via `--metadata_csv` to store labels alongside features.

The HDF5 file contains:
- `features`: float32 `[num_segments, num_frames, num_mfcc]`
- `file_ids`: variable-length strings
- `start_sample`, `end_sample`: int64 per segment
- `labels` (optional): variable-length strings
- Attributes: `feature_mean`, `feature_std`, and preprocessing parameters used

### Notes

- Fixed-length segmentation ensures rectangular tensors for efficient batching.
- Last incomplete segment is dropped by default; control with `--drop_last false`.
- This code is intended for research; voice-based lie detection is scientifically contentious and may be unreliable.

## Feature Extraction (Pitch, Tonal, Stress)

Extract pitch contours (YIN), estimate F0, compute tonal rise/fall/stability, and stress features (energy/ZCR) per file.

### Usage

```bash
python scripts/extract_features.py \
  --input_folder path/to/audio \
  --output_file data/processed/features.csv \
  --sample_rate 16000 \
  --frame_ms 25 --hop_ms 10 \
  --window hann \
  --fmin 50 --fmax 500 \
  --yin_threshold 0.1 \
  --format csv
```

Output columns include: `file_id`, `f0_median`, `tonal_rise_ratio`, `tonal_fall_ratio`, `tonal_stable_ratio`, `stress_zcr_mean`, `stress_zcr_std`, `stress_energy_cv`, and optional `label` if `--metadata_csv` is provided.

## Fuzzy Optimization

Suggest ERNN hyperparameters from extracted features.

```bash
python scripts/fuzzy_optimize.py \
  --features_file data/processed/features.csv \
  --output_json experiments/fuzzy_params.json \
  --feature_inputs tonal_stable_ratio stress_energy_cv
```

## Train ERNN

Train, validate, test the ERNN classifier using HDF5 MFCCs and fuzzy hyperparameters.

```bash
python scripts/train_ernn.py \
  --h5_features data/processed/mfcc.h5 \
  --fuzzy_json experiments/fuzzy_params.json \
  --output_model experiments/ernn.pt \
  --epochs 30 --batch 64 --patience 5 --device cpu
```

## Evaluate ERNN

```bash
python scripts/evaluate_ernn.py \
  --model experiments/ernn.pt \
  --h5_eval data/processed/mfcc.h5 \
  --out_dir experiments/eval --device cpu
```

Saves: `metrics.json`, `confusion_matrix.png`, and if binary labels: `roc_curve.png`, `pr_curve.png`.

## Explainable AI (IG/SHAP/LIME)

Generate explanations on a subset of samples from the evaluation HDF5.

```bash
python scripts/explain_ernn.py \
  --model experiments/ernn.pt \
  --h5_eval data/processed/mfcc.h5 \
  --out_dir experiments/xai \
  --method ig --max_samples 10
```

Outputs method-specific plots per sample and a JSON manifest in `out_dir`.


