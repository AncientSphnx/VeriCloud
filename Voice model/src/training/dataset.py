import os
from typing import Dict, List, Tuple

import h5py
import numpy as np
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import Dataset, DataLoader

# 🔒 Fixed, explicit label order for your dataset
FIXED_LABEL_MAP: Dict[str, int] = {"lie": 0, "truth": 1}
LABEL_MAP: Dict[str, int] = FIXED_LABEL_MAP.copy()


def _norm(s: str) -> str:
    return str(s).strip().lower()


def _encode_labels(str_labels: List[str]) -> np.ndarray:
    """Encode with FIXED_LABEL_MAP and fail fast on unknowns."""
    normalized = [_norm(s) for s in str_labels]
    unknown = sorted({s for s in normalized if s not in FIXED_LABEL_MAP})
    if unknown:
        raise ValueError(
            f"Found unknown labels in H5: {unknown}. Expected exactly {list(FIXED_LABEL_MAP.keys())}."
        )

    # build encoded array
    encoded = np.array([FIXED_LABEL_MAP[_norm(s)] for s in str_labels], dtype=np.int64)

    # Debug print
    print(f"[INFO] Label map: {FIXED_LABEL_MAP}  | Unique encoded: {sorted(set(encoded.tolist()))}")
    return encoded


class H5MFCCDataset(Dataset):
    def __init__(self, h5_path: str, indices: np.ndarray):
        super().__init__()
        self.h5_path = h5_path
        self.indices = indices
        self._h5 = None

    def __len__(self) -> int:
        return len(self.indices)

    def _ensure_open(self):
        if self._h5 is None:
            self._h5 = h5py.File(self.h5_path, 'r')

    def __getitem__(self, idx: int):
        self._ensure_open()
        i = int(self.indices[idx])
        features = self._h5['features'][i]  # (frames, mfcc)

        raw_label = self._h5['labels'][i]
        label_str = raw_label.decode('utf-8') if isinstance(raw_label, bytes) else str(raw_label)
        label_str = _norm(label_str)

        # 🔒 Only accept known labels; map to fixed ids
        if label_str not in FIXED_LABEL_MAP:
            raise ValueError(f"Unknown label '{label_str}' at index {i}. Expected {list(FIXED_LABEL_MAP.keys())}.")
        label = FIXED_LABEL_MAP[label_str]

        x = torch.from_numpy(features.astype(np.float32))
        y = torch.tensor(label, dtype=torch.long)
        return x, y

    def close(self):
        if self._h5 is not None:
            self._h5.close()
            self._h5 = None


def create_dataloaders_from_h5(
    h5_path: str,
    batch_size: int = 64,
    val_size: float = 0.2,
    test_size: float = 0.1,
    stratify: bool = True,
) -> Tuple[DataLoader, DataLoader, DataLoader, int, int]:
    """Create train/val/test loaders and return mfcc_dim, num_classes."""
    with h5py.File(h5_path, 'r') as h5:
        features = h5['features'][:]  # (N, T, F)
        labels = [s.decode('utf-8') if isinstance(s, bytes) else str(s) for s in h5['labels'][:]]
        mfcc_dim = features.shape[2]

    encoded = _encode_labels(labels)  # will raise on unknowns

    num_classes = 2  # 🔒 fixed for lie/truth
    indices = np.arange(features.shape[0])

    strat = encoded if stratify else None
    idx_train_val, idx_test = train_test_split(indices, test_size=test_size, random_state=42, stratify=strat)
    strat_tv = encoded[idx_train_val] if stratify else None
    idx_train, idx_val = train_test_split(idx_train_val, test_size=val_size, random_state=42, stratify=strat_tv)

    train_ds = H5MFCCDataset(h5_path, idx_train)
    val_ds   = H5MFCCDataset(h5_path, idx_val)
    test_ds  = H5MFCCDataset(h5_path, idx_test)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,  drop_last=False)
    val_loader   = DataLoader(val_ds,   batch_size=batch_size, shuffle=False, drop_last=False)
    test_loader  = DataLoader(test_ds,  batch_size=batch_size, shuffle=False, drop_last=False)

    print(f"[INFO] Dims -> mfcc_dim={mfcc_dim}, num_classes={num_classes}")
    return train_loader, val_loader, test_loader, mfcc_dim, num_classes
