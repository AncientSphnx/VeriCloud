# src/models/ernn.py
import torch
import torch.nn as nn
from dataclasses import dataclass


@dataclass
class RNNConfig:
    input_size: int
    hidden_size: int = 128
    num_layers: int = 2
    dropout: float = 0.3
    num_classes: int = 2
    model_type: str = "lstm"   # "lstm" | "bilstm" | "gru"
    learning_rate: float = 0.001
    with_attention: bool = True     # NEW: enable attention
    attention_size: int = 64         # NEW: hidden size of attention MLP


class RNNClassifier(nn.Module):
    def __init__(self, config: RNNConfig):
        super(RNNClassifier, self).__init__()
        self.config = config
        self.model_type = config.model_type.lower()

        # Build RNN core
        if self.model_type == "lstm":
            self.rnn = nn.LSTM(
                input_size=config.input_size,
                hidden_size=config.hidden_size,
                num_layers=config.num_layers,
                batch_first=True,
                dropout=config.dropout if config.num_layers > 1 else 0.0,
                bidirectional=False
            )
            rnn_out_dim = config.hidden_size

        elif self.model_type == "bilstm":
            self.rnn = nn.LSTM(
                input_size=config.input_size,
                hidden_size=config.hidden_size,
                num_layers=config.num_layers,
                batch_first=True,
                dropout=config.dropout if config.num_layers > 1 else 0.0,
                bidirectional=True
            )
            rnn_out_dim = config.hidden_size * 2

        elif self.model_type == "gru":
            self.rnn = nn.GRU(
                input_size=config.input_size,
                hidden_size=config.hidden_size,
                num_layers=config.num_layers,
                batch_first=True,
                dropout=config.dropout if config.num_layers > 1 else 0.0,
                bidirectional=False
            )
            rnn_out_dim = config.hidden_size

        else:
            raise ValueError(f"Unknown model_type: {self.model_type}")

        self.rnn_out_dim = rnn_out_dim

        # Attention block (optional)
        self.with_attention = bool(config.with_attention)
        if self.with_attention:
            # small MLP that scores each timestep: (B,T,rnn_out) -> (B,T,1)
            self.attn_net = nn.Sequential(
                nn.Linear(rnn_out_dim, config.attention_size),
                nn.Tanh(),
                nn.Linear(config.attention_size, 1)
            )
        else:
            self.attn_net = None

        # Classifier head: input dim depends on attention (context dim == rnn_out_dim)
        self.classifier = nn.Sequential(
            nn.Dropout(config.dropout),
            nn.Linear(rnn_out_dim, max(64, rnn_out_dim // 2)),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(max(64, rnn_out_dim // 2), config.num_classes)
        )

    def forward(self, x):
        """
        x: (B, T, F) or (B, F) (we convert 2D -> (B,1,F))
        returns logits (B, num_classes)
        """
        if x.ndim == 2:
            x = x.unsqueeze(1)

        # RNN outputs: out (B, T, hidden*dir), _ (hidden states)
        out, _ = self.rnn(x)  # out: (B, T, rnn_out_dim)

        if self.with_attention:
            # compute unnormalized scores (B, T, 1) -> squeeze -> (B, T)
            scores = self.attn_net(out).squeeze(-1)       # (B,T)
            alpha = torch.softmax(scores, dim=1)         # (B,T)
            alpha = alpha.unsqueeze(-1)                  # (B,T,1)
            context = (alpha * out).sum(dim=1)           # (B, rnn_out_dim)
            rep = context
        else:
            # use final timestep representation
            rep = out[:, -1, :]                           # (B, rnn_out_dim)

        logits = self.classifier(rep)                    # (B, num_classes)
        return logits
