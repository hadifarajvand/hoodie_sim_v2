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
    sequence_length: int | None = None
    input_dim: int | None = None
    output_dim: int | None = None
    hidden_dim: int | None = None
    forecast_method: str | None = None
    paper_lstm_forecast: bool | None = None


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


def _safe_float_array(value: Any) -> np.ndarray | None:
    if value is None:
        return None
    if isinstance(value, str) and value.strip() in {"", "None"}:
        return None
    try:
        array = np.asarray(value, dtype=np.float32)
    except Exception:
        return None
    if not np.all(np.isfinite(array)):
        return None
    return array


class LSTMForecaster:
    def __init__(
        self,
        sequence_length: int,
        input_dim: int,
        hidden_dim: int,
        target: str,
        seed: int = 0,
        output_dim: int | None = None,
    ) -> None:
        if sequence_length <= 0:
            raise ValueError("sequence_length must be positive")
        if input_dim <= 0:
            raise ValueError("input_dim must be positive")
        if hidden_dim <= 0:
            raise ValueError("hidden_dim must be positive")
        if output_dim is not None and output_dim <= 0:
            raise ValueError("output_dim must be positive")
        if target != "active_load_vector":
            raise ValueError("target must be active_load_vector for Model 10")
        self.sequence_length = sequence_length
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim if output_dim is not None else input_dim
        self.target = target
        self.seed = seed
        self.forecast_method = "trained_lstm"
        self.model: _LoadHistoryForecaster | None = None
        if torch is not None:
            torch.manual_seed(seed)
            self.model = _LoadHistoryForecaster(input_dim, hidden_dim, self.output_dim)

    def _extract_vector(self, row: dict[str, Any]) -> np.ndarray | None:
        value = row.get("active_load_vector")
        if value is None or (isinstance(value, str) and value.strip() in {"", "None"}):
            value = row.get("active_load_vector_json")
        if value is None or (isinstance(value, str) and value.strip() in {"", "None"}):
            return None
        try:
            vector = np.asarray(value, dtype=np.float32).reshape(-1)
        except Exception:
            return None
        if vector.size != self.input_dim or not np.all(np.isfinite(vector)):
            return None
        return vector.astype(np.float32)

    def _group_key(self, row: dict[str, Any]) -> tuple[int, int]:
        episode_id = int(float(row.get("episode_id") or 0))
        agent_id = row.get("agent_id")
        if agent_id in (None, "", "None"):
            agent_id = row.get("source_agent")
        agent_id = int(float(agent_id or 0))
        return episode_id, agent_id

    def _sorted_rows(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        def sort_key(row: dict[str, Any]) -> tuple[int, int, int]:
            episode_id = int(float(row.get("episode_id") or 0))
            agent_id = row.get("agent_id")
            if agent_id in (None, "", "None"):
                agent_id = row.get("source_agent")
            agent_id = int(float(agent_id or 0))
            time_value = row.get("time")
            if time_value in (None, "", "None"):
                time_value = row.get("step_index")
            time_value = int(float(time_value or 0))
            return episode_id, agent_id, time_value

        return sorted(rows, key=sort_key)

    def build_sequences(self, rows: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray, str | None]:
        ordered = self._sorted_rows(rows)
        grouped: dict[tuple[int, int], list[dict[str, Any]]] = {}
        for row in ordered:
            vector = self._extract_vector(row)
            if vector is None:
                continue
            grouped.setdefault(self._group_key(row), []).append(row)

        sequences: list[np.ndarray] = []
        targets: list[np.ndarray] = []
        for _, group_rows in grouped.items():
            vectors = [self._extract_vector(row) for row in group_rows]
            vectors = [vector for vector in vectors if vector is not None]
            if len(vectors) < self.sequence_length + 1:
                continue
            for idx in range(self.sequence_length, len(vectors)):
                window = np.asarray(vectors[idx - self.sequence_length : idx], dtype=np.float32)
                target = np.asarray(vectors[idx], dtype=np.float32)
                if window.shape != (self.sequence_length, self.input_dim):
                    continue
                if target.shape != (self.output_dim,):
                    continue
                if not np.all(np.isfinite(window)) or not np.all(np.isfinite(target)):
                    continue
                sequences.append(window)
                targets.append(target)

        if not sequences:
            return (
                np.empty((0, self.sequence_length, self.input_dim), dtype=np.float32),
                np.empty((0, self.output_dim), dtype=np.float32),
                "not enough ordered active_load_vector samples for trained_lstm",
            )
        return np.asarray(sequences, dtype=np.float32), np.asarray(targets, dtype=np.float32), None

    def train(self, sequences: np.ndarray, targets: np.ndarray, epochs: int = 1, learning_rate: float = 1e-3) -> LSTMForecastResult:
        _require_torch()
        if self.model is None:
            raise RuntimeError("LSTM model is unavailable")
        if len(sequences) == 0:
            return LSTMForecastResult(
                target=self.target,
                sequences=0,
                mse=None,
                mae=None,
                skipped=True,
                reason="no sequences",
                sequence_length=self.sequence_length,
                input_dim=self.input_dim,
                output_dim=self.output_dim,
                hidden_dim=self.hidden_dim,
                forecast_method="trained_lstm",
                paper_lstm_forecast=False,
            )
        if sequences.ndim != 3 or sequences.shape[1:] != (self.sequence_length, self.input_dim):
            raise ValueError("sequences have incompatible shape")
        if targets.ndim != 2 or targets.shape[1] != self.output_dim:
            raise ValueError("targets have incompatible shape")
        if not np.all(np.isfinite(sequences)) or not np.all(np.isfinite(targets)):
            raise ValueError("sequences and targets must be finite")
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
        return LSTMForecastResult(
            target=self.target,
            sequences=int(len(sequences)),
            mse=mse,
            mae=mae,
            skipped=False,
            reason=None,
            sequence_length=self.sequence_length,
            input_dim=self.input_dim,
            output_dim=self.output_dim,
            hidden_dim=self.hidden_dim,
            forecast_method="trained_lstm",
            paper_lstm_forecast=True,
        )

    def predict(self, load_history: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("LSTM model is unavailable")
        _require_torch()
        sequence = np.asarray(load_history, dtype=np.float32)
        if sequence.ndim == 1:
            sequence = sequence.reshape(1, -1)
        if sequence.shape[-1] != self.input_dim:
            raise ValueError("load_history has incompatible feature dimension")
        if sequence.shape[0] < self.sequence_length:
            pad = np.zeros((self.sequence_length - sequence.shape[0], self.input_dim), dtype=np.float32)
            sequence = np.vstack([pad, sequence])
        sequence = sequence[-self.sequence_length :]
        if not np.all(np.isfinite(sequence)):
            raise ValueError("load_history must contain only finite values")
        with torch.no_grad():
            x = torch.as_tensor(sequence.reshape(1, self.sequence_length, self.input_dim), dtype=torch.float32)
            pred = self.model(x).cpu().numpy().reshape(-1)
        return pred.astype(np.float32)

    def save(self, path: str | Path) -> str:
        if self.model is None:
            raise RuntimeError("LSTM model is unavailable")
        path = str(path)
        torch.save(
            {
                "target": self.target,
                "sequence_length": self.sequence_length,
                "input_dim": self.input_dim,
                "output_dim": self.output_dim,
                "hidden_dim": self.hidden_dim,
                "seed": self.seed,
                "forecast_method": self.forecast_method,
                "state_dict": self.model.state_dict(),
            },
            path,
        )
        return path

    def load(self, path: str | Path) -> None:
        if self.model is None:
            raise RuntimeError("LSTM model is unavailable")
        checkpoint = torch.load(path, map_location="cpu")
        if checkpoint.get("target") != self.target:
            raise ValueError("checkpoint target does not match forecaster target")
        if checkpoint.get("forecast_method") != self.forecast_method:
            raise ValueError("checkpoint forecast_method does not match forecaster")
        if int(checkpoint.get("sequence_length", self.sequence_length)) != self.sequence_length:
            raise ValueError("checkpoint sequence_length does not match forecaster")
        if int(checkpoint.get("input_dim", self.input_dim)) != self.input_dim:
            raise ValueError("checkpoint input_dim does not match forecaster")
        if int(checkpoint.get("output_dim", self.output_dim)) != self.output_dim:
            raise ValueError("checkpoint output_dim does not match forecaster")
        if int(checkpoint.get("hidden_dim", self.hidden_dim)) != self.hidden_dim:
            raise ValueError("checkpoint hidden_dim does not match forecaster")
        self.model.load_state_dict(checkpoint["state_dict"])
