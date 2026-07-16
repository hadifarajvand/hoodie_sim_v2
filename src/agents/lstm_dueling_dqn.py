from __future__ import annotations

from collections import deque
from typing import Any

import torch
from torch import nn


def _init_module(module: nn.Module) -> None:
    if isinstance(module, nn.Linear):
        nn.init.xavier_uniform_(module.weight)
        if module.bias is not None:
            nn.init.zeros_(module.bias)
    elif isinstance(module, nn.LSTM):
        for name, parameter in module.named_parameters():
            if "weight" in name:
                nn.init.xavier_uniform_(parameter)
            else:
                nn.init.zeros_(parameter)


class LSTM_Dueling_DQN(nn.Module):
    """Dueling Q network with an optional causal LSTM forecast path.

    Input is always a complete fixed-size history window. The network deliberately
    does not retain hidden state between calls: replay minibatches are independent
    samples and carrying hidden state across samples would leak information between
    episodes and make checkpoint replay non-deterministic.
    """

    def __init__(
        self,
        state_dim: int = 74,
        lookback: int = 10,
        num_actions: int = 22,
        hidden_sizes: list[int] | None = None,
        lstm_hidden: int = 20,
        *,
        use_lstm: bool = True,
        seed: int = 0,
    ) -> None:
        super().__init__()
        if state_dim <= 0 or lookback <= 0 or num_actions <= 1:
            raise ValueError("invalid LSTM dueling network dimensions")
        self.input_size = int(state_dim)
        self.lookback = int(lookback)
        self.num_actions = int(num_actions)
        self.lstm_hidden = int(lstm_hidden)
        self.use_lstm = bool(use_lstm)
        self.hidden_sizes = hidden_sizes or [1024, 1024, 1024]
        self.forecast_target_dim = min(20, self.input_size)
        self.history = deque(maxlen=self.lookback)
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(int(seed))
            self.lstm = nn.LSTM(
                input_size=self.input_size,
                hidden_size=self.lstm_hidden,
                num_layers=1,
                batch_first=True,
            )
            self.forecast_head = nn.Linear(
                self.lstm_hidden, self.forecast_target_dim
            )
            body_input = self.input_size
            layers: list[nn.Module] = []
            for width in self.hidden_sizes:
                layers.extend((nn.Linear(body_input, width), nn.ReLU()))
                body_input = width
            self.fc_layers = nn.Sequential(*layers)
            self.value_stream = nn.Sequential(
                nn.Linear(body_input, body_input),
                nn.ReLU(),
                nn.Linear(body_input, 1),
            )
            self.advantage_stream = nn.Sequential(
                nn.Linear(body_input, body_input),
                nn.ReLU(),
                nn.Linear(body_input, self.num_actions),
            )
            self.apply(_init_module)

    def reset_hidden_state(self) -> None:
        self.history.clear()

    def _forecast(self, x: torch.Tensor) -> torch.Tensor:
        if not self.use_lstm:
            return x[:, -1, : self.forecast_target_dim]
        lstm_output, _hidden = self.lstm(x)
        return self.forecast_head(lstm_output[:, -1, :])

    def forecast_features(self, x: torch.Tensor) -> torch.Tensor:
        if x.ndim != 3:
            raise ValueError("Input must be [batch, lookback, state_dim]")
        if x.shape[1] != self.lookback or x.shape[2] != self.input_size:
            raise ValueError("Unexpected input shape")
        forecast = self._forecast(x)
        if self.use_lstm:
            base = x[:, -1, : self.input_size - self.forecast_target_dim]
            return torch.cat((base, forecast), dim=-1)
        return x[:, -1, :]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.forecast_features(x)
        encoded = self.fc_layers(features)
        value = self.value_stream(encoded)
        advantage = self.advantage_stream(encoded)
        return value + advantage - advantage.mean(dim=-1, keepdim=True)

    def append_observation(
        self, observation: torch.Tensor | list[float] | tuple[float, ...]
    ) -> None:
        tensor = torch.as_tensor(observation, dtype=torch.float32)
        if tensor.ndim != 1 or tensor.shape[0] != self.input_size:
            raise ValueError("observation must be 1D state vector")
        self.history.append(tensor)

    def build_window(self) -> torch.Tensor:
        rows = list(self.history)
        if len(rows) < self.lookback:
            padding = [
                torch.zeros(self.input_size, dtype=torch.float32)
                for _ in range(self.lookback - len(rows))
            ]
            rows = padding + rows
        return torch.stack(rows, dim=0).unsqueeze(0)

    def state_dict(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        payload = super().state_dict(*args, **kwargs)
        payload["_use_lstm"] = torch.tensor(int(self.use_lstm))
        return payload

    def load_state_dict(self, state_dict: dict[str, Any], strict: bool = True):
        copied = dict(state_dict)
        use_lstm = bool(copied.pop("_use_lstm", torch.tensor(1)).item())
        result = super().load_state_dict(copied, strict=strict)
        self.use_lstm = use_lstm
        return result
