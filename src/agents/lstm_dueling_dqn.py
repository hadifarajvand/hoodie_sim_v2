from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import torch
import torch.nn as nn


@dataclass(slots=True)
class LSTMState:
    hidden: tuple[torch.Tensor, torch.Tensor] | None = None


class LSTM_Dueling_DQN(nn.Module):
    def __init__(
        self,
        state_dim: int = 74,
        lookback: int = 10,
        num_actions: int = 22,
        hidden_sizes: list[int] | None = None,
        lstm_hidden: int = 20,
        lstm_layers: int = 1,
    ):
        super().__init__()
        if hidden_sizes is None:
            hidden_sizes = [1024, 1024, 1024]
        self.input_size = state_dim
        self.lookback = lookback
        self.num_actions = num_actions
        self.lstm_hidden = lstm_hidden
        self.hidden_sizes = hidden_sizes
        self.lstm = nn.LSTM(state_dim, lstm_hidden, num_layers=lstm_layers, batch_first=True)
        layers: list[nn.Module] = []
        in_features = lstm_hidden
        for size in hidden_sizes:
            layers.extend([nn.Linear(in_features, size), nn.ReLU()])
            in_features = size
        self.fc_layers = nn.Sequential(*layers)
        self.value_stream = nn.Sequential(nn.Linear(in_features, in_features), nn.ReLU(), nn.Linear(in_features, 1))
        self.advantage_stream = nn.Sequential(nn.Linear(in_features, in_features), nn.ReLU(), nn.Linear(in_features, num_actions))
        self._reset_parameters()
        self._forecast_history: list[torch.Tensor] = []

    def _reset_parameters(self) -> None:
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.kaiming_uniform_(module.weight, a=5 ** 0.5)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            if isinstance(module, nn.LSTM):
                for name, param in module.named_parameters():
                    if "weight" in name:
                        nn.init.xavier_uniform_(param)
                    elif "bias" in name:
                        nn.init.zeros_(param)

    def reset_forecast_state(self) -> None:
        self._forecast_history.clear()

    def forecast_features(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() != 3:
            raise ValueError("Expected [batch, lookback, state_dim]")
        output, _hidden = self.lstm(x)
        forecast = output[:, -1, :]
        self._forecast_history.append(forecast.detach())
        return forecast

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        forecast = self.forecast_features(x)
        latent = self.fc_layers(forecast)
        value = self.value_stream(latent)
        advantage = self.advantage_stream(latent)
        return value + advantage - advantage.mean(dim=-1, keepdim=True)

    def export_state(self) -> dict[str, Any]:
        return {
            "state_dict": self.state_dict(),
            "input_size": self.input_size,
            "lookback": self.lookback,
            "num_actions": self.num_actions,
            "lstm_hidden": self.lstm_hidden,
            "hidden_sizes": list(self.hidden_sizes),
            "forecast_history_length": len(self._forecast_history),
        }

    def load_export_state(self, state: dict[str, Any]) -> None:
        self.load_state_dict(state["state_dict"])
