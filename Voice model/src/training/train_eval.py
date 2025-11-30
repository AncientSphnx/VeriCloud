import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset, random_split
import numpy as np
import h5py
from sklearn.metrics import accuracy_score, f1_score
from src.models.ernn import RNNConfig, RNNClassifier


def load_h5_data(h5_path):
    with h5py.File(h5_path, "r") as f:
        X = np.array(f["features"])
        raw_y = np.array(f["labels"])

    # Convert raw_y (which may be bytes) -> clean strings
    y_strs = []
    for lbl in raw_y:
        if isinstance(lbl, bytes):
            s = lbl.decode("utf-8", errors="ignore")
        else:
            s = str(lbl)
        s = s.strip().lower()
        y_strs.append(s)

    # Debug: show a few raw label strings
    print("[DEBUG] sample label strings:", y_strs[:20])

    # Map to ints: 0 = truth, 1 = lie
    mapped = []
    for s in y_strs:
        if s.startswith("t"):     # 'truth' -> 0
            mapped.append(0)
        elif s.startswith("l"):   # 'lie'   -> 1
            mapped.append(1)
        else:
            # Fail loudly if an unexpected label appears
            raise ValueError(f"Unexpected label string '{s}' in {h5_path}. Allowed: truth, lie")

    y = np.array(mapped, dtype=np.int64)

    # Final debug
    unique, counts = np.unique(y, return_counts=True)
    print(f"[DEBUG] mapped label distribution: {dict(zip(unique, counts))}")

    return X, y



def train_validate_test(h5_path, fuzzy_params=None, model_type="lstm", device="cpu",
                        epochs=20, batch_size=64, return_model=False):
    X, y = load_h5_data(h5_path)

    # convert to tensors
    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.long)

    dataset = TensorDataset(X_tensor, y_tensor)
    train_size = int(0.7 * len(dataset))
    val_size = int(0.15 * len(dataset))
    test_size = len(dataset) - train_size - val_size
    train_ds, val_ds, test_ds = random_split(dataset, [train_size, val_size, test_size])

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size)
    test_loader = DataLoader(test_ds, batch_size=batch_size)

    # === Hyperparameters ===
    learning_rate = fuzzy_params.get("learning_rate", 0.001) if fuzzy_params else 0.001
    hidden_size = int(fuzzy_params.get("hidden_size", 128)) if fuzzy_params else 128
    dropout = fuzzy_params.get("dropout", 0.3) if fuzzy_params else 0.3

    # === Fix: get number of classes dynamically ===
    num_classes = len(np.unique(y))
    print(f"[DEBUG] Detected num_classes = {num_classes}")

    cfg = RNNConfig(
        input_size=X.shape[2],
        hidden_size=hidden_size,
        dropout=dropout,
        num_classes=num_classes,
        model_type=model_type,
        learning_rate=learning_rate
        
    )

    model = RNNClassifier(cfg).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # === Training Loop ===
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)
            optimizer.zero_grad()
            preds = model(xb)
            loss = criterion(preds, yb)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"[DEBUG] Epoch {epoch+1}/{epochs} | Loss: {total_loss/len(train_loader):.4f}")

    # === Validation/Test Evaluation ===
    def eval_model(loader):
        model.eval()
        all_preds, all_true = [], []
        with torch.no_grad():
            for xb, yb in loader:
                xb, yb = xb.to(device), yb.to(device)
                preds = model(xb).argmax(dim=1)
                all_preds.extend(preds.cpu().numpy())
                all_true.extend(yb.cpu().numpy())
        return accuracy_score(all_true, all_preds), f1_score(all_true, all_preds)

    val_acc, val_f1 = eval_model(val_loader)
    test_acc, test_f1 = eval_model(test_loader)

    metrics = {
        "val_acc": val_acc,
        "val_f1": val_f1,
        "test_acc": test_acc,
        "test_f1": test_f1
    }

    print(f"[DEBUG] Final Metrics: {metrics}")

    if return_model:
        return metrics, model
    return metrics
