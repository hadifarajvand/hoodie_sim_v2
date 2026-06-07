from __future__ import annotations

from dataclasses import dataclass, asdict
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


class _LSTMRegressor(nn.Module):  # type: ignore[misc]
    def __init__(self, input_dim: int, hidden_dim: int) -> None:
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.head = nn.Linear(hidden_dim, 1)

    def forward(self, x):  # type: ignore[override]
        out, _ = self.lstm(x)
        return self.head(out[:, -1, :]).squeeze(-1)


class LSTMForecaster:
    def __init__(self, sequence_length: int, input_dim: int, hidden_dim: int, target: str, seed: int = 0) -> None:
        self.sequence_length = sequence_length
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.target = target
        self.seed = seed
        self.model: _LSTMRegressor | None = None
        if torch is not None:
            torch.manual_seed(seed)
            self.model = _LSTMRegressor(input_dim, hidden_dim)

    def _row_feature_vector(self, row: dict[str, Any]) -> list[float] | None:
        if "load_history" in row and row["load_history"] not in (None, "", "None"):
            try:
                history = np.asarray(row["load_history"], dtype=np.float32)
                if history.ndim >= 2:
                    feature_vector = history[-1].reshape(-1)
                else:
                    feature_vector = history.reshape(-1)
                if feature_vector.size == self.input_dim:
                    return feature_vector.astype(np.float32).tolist()
            except Exception:
                pass
        if "state" in row and row["state"] not in (None, "", "None"):
            try:
                state = np.asarray(row["state"], dtype=np.float32).reshape(-1)
                if state.size == self.input_dim:
                    return state.astype(np.float32).tolist()
            except Exception:
                pass
        try:
            return [float(row.get("time") or row.get("step_index") or 0.0)] * self.input_dim
        except Exception:
            return None

    def build_sequences(self, rows: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray, str | None]:
        if self.target not in {"latency", "queue_length", "reward"}:
            return np.empty((0, self.sequence_length, self.input_dim), dtype=np.float32), np.empty((0,), dtype=np.float32), f"unsupported target {self.target}"
        values: list[float] = []
        features: list[list[float]] = []
        for row in rows:
            target_value = row.get(self.target)
            if target_value in (None, "", "None"):
                continue
            try:
                feature_vector = self._row_feature_vector(row)
                if feature_vector is None:
                    continue
                features.append(feature_vector)
                values.append(float(target_value))
            except Exception:
                continue
        if len(features) < self.sequence_length:
            return np.empty((0, self.sequence_length, self.input_dim), dtype=np.float32), np.empty((0,), dtype=np.float32), f"not enough samples for target {self.target}"
        sequences = []
        targets = []
        for idx in range(self.sequence_length - 1, len(features)):
            window = features[idx - self.sequence_length + 1 : idx + 1]
            sequences.append(window)
            targets.append(values[idx])
        return np.asarray(sequences, dtype=np.float32), np.asarray(targets, dtype=np.float32), None

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

    def save(self, path: str | Path) -> str:
        if self.model is None:
            raise RuntimeError("LSTM model is unavailable")
        path = str(path)
        torch.save({"target": self.target, "state_dict": self.model.state_dict()}, path)
        return path

    def load(self, path: str | Path) -> None:
        if self.model is None:
            raise RuntimeError("LSTM model is unavailable")
        checkpoint = torch.load(path, map_location="cpu")
        self.model.load_state_dict(checkpoint["state_dict"])
