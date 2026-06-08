from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
except Exception:  # pragma: no cover
    torch = None
    nn = None
    optim = None


@dataclass
class LSTMForecastResult:
    target: str
    sequences: int
    mse: float | None
    mae: float | None
    skipped: bool
    reason: str | None = None


def _require_torch() -> None:
    if torch is None or nn is None or optim is None:
        raise RuntimeError("PyTorch is required for LSTM forecasting")


class _LoadHistoryForecaster(nn.Module):  # type: ignore[misc]
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int) -> None:
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.head = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):  # type: ignore[override]
        out, _ = self.lstm(x)
        return self.head(out[:, -1, :])


class LSTMForecaster:
    def __init__(self, sequence_length: int, input_dim: int, hidden_dim: int, target: str, seed: int = 0, output_dim: int | None = None) -> None:
        self.sequence_length = sequence_length
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim if output_dim is not None else input_dim
        self.target = target
        self.seed = seed
        self.model: _LoadHistoryForecaster | None = None
        if torch is not None:
            torch.manual_seed(seed)
            self.model = _LoadHistoryForecaster(input_dim, hidden_dim, self.output_dim)

    def _extract_history(self, row: dict[str, Any]) -> np.ndarray | None:
        value = row.get("load_history")
        if value in (None, "", "None"):
            return None
        try:
            history = np.asarray(value, dtype=np.float32)
        except Exception:
            return None
        if history.ndim == 1:
            history = history.reshape(1, -1)
        if history.ndim < 2:
            return None
        last = history[-1].reshape(-1)
        if last.size != self.input_dim:
            return None
        return last.astype(np.float32)

    def _extract_target(self, row: dict[str, Any]) -> np.ndarray | None:
        value = row.get("active_load_vector") or row.get("predicted_next_load")
        if value in (None, "", "None"):
            return None
        try:
            target = np.asarray(value, dtype=np.float32).reshape(-1)
        except Exception:
            return None
        if target.size != self.output_dim:
            return None
        return target.astype(np.float32)

    def build_sequences(self, rows: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray, str | None]:
        histories: list[np.ndarray] = []
        targets: list[np.ndarray] = []
        for row in rows:
            history = self._extract_history(row)
            target = self._extract_target(row)
            if history is None or target is None:
                continue
            histories.append(history)
            targets.append(target)
        if len(histories) < self.sequence_length:
            return np.empty((0, self.sequence_length, self.input_dim), dtype=np.float32), np.empty((0, self.output_dim), dtype=np.float32), "not enough samples for load-history forecasting"
        sequences = []
        out_targets = []
        for idx in range(self.sequence_length - 1, len(histories)):
            window = histories[idx - self.sequence_length + 1 : idx + 1]
            sequences.append(window)
            out_targets.append(targets[idx])
        return np.asarray(sequences, dtype=np.float32), np.asarray(out_targets, dtype=np.float32), None

    def train(self, sequences: np.ndarray, targets: np.ndarray, epochs: int = 1, learning_rate: float = 1e-3) -> LSTMForecastResult:
        _require_torch()
        if self.model is None:
            raise RuntimeError("LSTM model is unavailable")
        if len(sequences) == 0:
            return LSTMForecastResult(self.target, 0, None, None, True, "no sequences")
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        loss_fn = nn.MSELoss()
        x = torch.as_tensor(sequences, dtype=torch.float32)
        y = torch.as_tensor(targets, dtype=torch.float32)
        for _ in range(epochs):
            pred = self.model(x)
            loss = loss_fn(pred, y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        with torch.no_grad():
            pred = self.model(x)
            mse = float(torch.mean((pred - y) ** 2).item())
            mae = float(torch.mean(torch.abs(pred - y)).item())
        return LSTMForecastResult(self.target, len(sequences), mse, mae, False)

    def predict(self, load_history: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("LSTM model is unavailable")
        _require_torch()
        if load_history.ndim == 1:
            load_history = load_history.reshape(1, -1)
        if load_history.shape[-1] != self.input_dim:
            raise ValueError("load_history has incompatible feature dimension")
        sequence = np.asarray(load_history, dtype=np.float32)
        if sequence.shape[0] < self.sequence_length:
            pad = np.full((self.sequence_length - sequence.shape[0], self.input_dim), np.nan, dtype=np.float32)
            sequence = np.vstack([pad, sequence])
        sequence = sequence[-self.sequence_length :]
        sequence = np.nan_to_num(sequence, nan=0.0)
        with torch.no_grad():
            x = torch.as_tensor(sequence.reshape(1, self.sequence_length, self.input_dim), dtype=torch.float32)
            pred = self.model(x).cpu().numpy().reshape(-1)
        return pred.astype(np.float32)

    def save(self, path: str | Path) -> str:
        if self.model is None:
            raise RuntimeError("LSTM model is unavailable")
        path = str(path)
        torch.save({"target": self.target, "input_dim": self.input_dim, "output_dim": self.output_dim, "state_dict": self.model.state_dict()}, path)
        return path

    def load(self, path: str | Path) -> None:
        if self.model is None:
            raise RuntimeError("LSTM model is unavailable")
        checkpoint = torch.load(path, map_location="cpu")
        self.model.load_state_dict(checkpoint["state_dict"])
