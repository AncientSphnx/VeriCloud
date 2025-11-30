import json
import os
from typing import Dict, List, Literal

import h5py
import numpy as np
import torch
import matplotlib.pyplot as plt
from captum.attr import IntegratedGradients
import shap
from lime.lime_tabular import LimeTabularExplainer

from src.models import RNNClassifier, RNNConfig


def _load_model(model_path: str, device: str) -> RNNClassifier:
    ckpt = torch.load(model_path, map_location=device)
    cfg = RNNConfig(**ckpt["model_config"])
    model = RNNClassifier(cfg).to(device)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    return model


def _load_subset(h5_path: str, count: int) -> np.ndarray:
    with h5py.File(h5_path, "r") as h5:
        X = h5["features"][:]
    return X[:count]


def _plot_heatmap(attr: np.ndarray, out_path: str, title: str) -> None:
    plt.figure(figsize=(6, 3))
    plt.imshow(attr, aspect="auto", origin="lower", cmap="RdBu_r")
    plt.colorbar()
    plt.title(title)
    plt.xlabel("Frame")
    plt.ylabel("MFCC")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def explain_samples(
    model_path: str,
    h5_eval: str,
    out_dir: str,
    method: Literal["ig", "shap", "lime"] = "ig",
    max_samples: int = 10,
    device: str = "cpu",
) -> List[Dict[str, str]]:
    os.makedirs(out_dir, exist_ok=True)
    model = _load_model(model_path, device)
    X = _load_subset(h5_eval, count=max_samples)

    results: List[Dict[str, str]] = []
    inputs = torch.from_numpy(X).float().to(device)

    if method == "ig":
        ig = IntegratedGradients(model)
        for i in range(inputs.shape[0]):
            x = inputs[i : i + 1]
            x = x.clone().detach().requires_grad_(True)

            with torch.no_grad():
                logits = model(x)
            pred_class = int(logits.argmax(dim=1).item())

            # fix CuDNN backward issue
            with torch.backends.cudnn.flags(enabled=False):
                attributions = ig.attribute(x, target=pred_class, n_steps=32)

            attr_np = attributions.squeeze(0).detach().cpu().numpy()
            attr_np = np.abs(attr_np).T  # (F, T)

            out_path = os.path.join(out_dir, f"ig_{i}.png")
            _plot_heatmap(attr_np, out_path, f"Integrated Gradients | pred={pred_class}")
            results.append({"index": str(i), "plot": out_path})

    elif method == "shap":
        X_flat = X.reshape(X.shape[0], -1)
        f = lambda z: torch.softmax(
            model(torch.from_numpy(z.reshape(-1, X.shape[1], X.shape[2])).float().to(device)), dim=1
        ).detach().cpu().numpy()
        background = shap.kmeans(X_flat, 10).data
        explainer = shap.KernelExplainer(f, background)
        shap_values = explainer.shap_values(X_flat[:max_samples], nsamples=100)
        for i in range(min(max_samples, X_flat.shape[0])):
            out_path = os.path.join(out_dir, f"shap_{i}.png")
            plt.figure(figsize=(6, 3))
            shap.summary_plot([sv[i] for sv in shap_values], X_flat[i : i + 1], show=False)
            plt.tight_layout()
            plt.savefig(out_path)
            plt.close()
            results.append({"index": str(i), "plot": out_path})

    else:  # lime
        X_flat = X.reshape(X.shape[0], -1)
        predict_fn = lambda z: torch.softmax(
            model(torch.from_numpy(z.reshape(-1, X.shape[1], X.shape[2])).float().to(device)), dim=1
        ).detach().cpu().numpy()
        explainer = LimeTabularExplainer(X_flat, mode="classification")
        for i in range(min(max_samples, X_flat.shape[0])):
            exp = explainer.explain_instance(X_flat[i], predict_fn, num_features=10)
            out_path = os.path.join(out_dir, f"lime_{i}.png")
            fig = exp.as_pyplot_figure()
            plt.tight_layout()
            fig.savefig(out_path)
            plt.close(fig)
            results.append({"index": str(i), "plot": out_path})

    with open(os.path.join(out_dir, f"explanations_{method}.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    return results
