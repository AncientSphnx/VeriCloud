import json
import os
from typing import Dict

import h5py
import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, roc_auc_score,
    roc_curve, precision_recall_curve
)
import matplotlib.pyplot as plt

from src.models import RNNClassifier, RNNConfig


def _load_model(ckpt_path: str, device: str = 'cpu') -> RNNClassifier:
    """
    Load the trained RNN/BiLSTM model for evaluation.
    Automatically detects if checkpoint is raw state_dict or dict with 'model_state_dict'.
    """
    ckpt = torch.load(ckpt_path, map_location=device)

    cfg = RNNConfig(
        input_size=39,    # Must match training (n_mfcc)
        hidden_size=256,
        num_layers=2,
        dropout=0.3,
        num_classes=2,
        model_type="bilstm"
    )

    if isinstance(ckpt, dict) and "model_state_dict" in ckpt:
        state_dict = ckpt["model_state_dict"]
    else:
        state_dict = ckpt

    model = RNNClassifier(cfg).to(device)
    model.load_state_dict(state_dict)
    model.eval()
    return model


def evaluate_model_on_h5(model_path: str, h5_path: str, out_dir: str, device: str = 'cpu') -> Dict[str, float]:
    os.makedirs(out_dir, exist_ok=True)
    model = _load_model(model_path, device=device)

    # Load features and labels
    with h5py.File(h5_path, 'r') as h5:
        x = h5['features'][:]  # (N, T, F)
        labels = h5['labels'][:]

    # Convert labels to clean strings
    labels = np.array([s.decode('utf-8') if isinstance(s, bytes) else str(s) for s in labels])
    y_true = np.array([0 if s.startswith('t') else 1 for s in labels], dtype=np.int64)

    print(f"[DEBUG] x shape: {x.shape}, y_true shape: {y_true.shape}")

    with torch.no_grad():
        logits = model(torch.from_numpy(x).to(device))
        probs = torch.softmax(logits, dim=1).cpu().numpy()
        y_pred = np.argmax(probs, axis=1)

    # Basic metrics
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, average='macro', zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, average='macro', zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, average='macro')),
    }

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(5, 4))
    plt.imshow(cm, cmap='Blues')
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'confusion_matrix.png'))
    plt.close()

    # Binary ROC/PR metrics (2-class assumption)
    y_true_bin = y_true
    roc_fpr, roc_tpr, _ = roc_curve(y_true_bin, probs[:, 1])
    roc_auc = float(roc_auc_score(y_true_bin, probs[:, 1]))
    prec, rec, _ = precision_recall_curve(y_true_bin, probs[:, 1])

    plt.figure()
    plt.plot(roc_fpr, roc_tpr)
    plt.xlabel('FPR')
    plt.ylabel('TPR')
    plt.title(f'ROC AUC={roc_auc:.3f}')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'roc_curve.png'))
    plt.close()

    plt.figure()
    plt.plot(rec, prec)
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'pr_curve.png'))
    plt.close()

    metrics['roc_auc'] = roc_auc

    # Save metrics
    with open(os.path.join(out_dir, 'metrics.json'), 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)

    return metrics

