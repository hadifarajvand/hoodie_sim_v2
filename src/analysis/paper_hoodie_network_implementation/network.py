from __future__ import annotations

from typing import TYPE_CHECKING, Any

import torch
from torch import Tensor, nn

if TYPE_CHECKING:
    from .report import PaperHoodieNetworkConfig


class PaperHoodieDuelingNetwork(nn.Module):
    """Torch implementation of the architecture-only HOODIE network surface."""

    def __init__(self, config: "PaperHoodieNetworkConfig") -> None:
        super().__init__()
        if config.state_dim is None or config.state_dim <= 0:
            raise ValueError("state_dim is required and must be positive to build the network.")
        if config.action_count not in (3, 22):
            raise ValueError("PaperHoodieDuelingNetwork.action_count must be 3 (legacy) or 22 (paper-faithful).")
        if list(config.q_network_hidden_layers) != [1024, 1024, 1024]:
            raise ValueError("q_network_hidden_layers must equal [1024, 1024, 1024].")
        if config.lstm_num_layers != 1:
            raise ValueError("lstm_num_layers must equal 1.")
        if config.lstm_hidden_size != 20:
            raise ValueError("lstm_hidden_size must equal 20.")

        self.config = config
        self.state_dim = int(config.state_dim)
        self.lookback_w = int(config.lstm_lookback_w)
        self.action_count = int(config.action_count)
        self.lstm_hidden_size = int(config.lstm_hidden_size)
        self.lstm_num_layers = int(config.lstm_num_layers)
        self.q_network_hidden_layers = tuple(int(width) for width in config.q_network_hidden_layers)

        self.encoder = nn.LSTM(
            input_size=self.state_dim,
            hidden_size=self.lstm_hidden_size,
            num_layers=self.lstm_num_layers,
            batch_first=True,
        )

        # Paper Section IV-A: LSTM predicts load forecast from load_history.
        # Forecast concatenated with base state (task + queue + wait dims)
        # forms the full state vector. Only active in paper 74-dim mode.
        self.forecast_output_dim = 20  # num_eas = 20
        if self.state_dim > self.forecast_output_dim:
            self.base_state_dim = self.state_dim - self.forecast_output_dim
            self.forecast_head = nn.Linear(self.lstm_hidden_size, self.forecast_output_dim)
            body_input_dim = self.state_dim
        else:
            # Legacy mode: forecast not applicable, use LSTM hidden directly
            self.base_state_dim = 0
            self.forecast_head = None
            body_input_dim = self.lstm_hidden_size
        body_layers: list[nn.Module] = []
        for width in self.q_network_hidden_layers:
            body_layers.append(nn.Linear(body_input_dim, width))
            body_layers.append(nn.ReLU())
            body_input_dim = width
        self.q_body = nn.Sequential(*body_layers)
        self.value_head = nn.Linear(body_input_dim, 1)
        self.advantage_head = nn.Linear(body_input_dim, self.action_count)

    def validate_input(self, observation: Tensor) -> None:
        if observation.ndim != 3:
            raise ValueError("Input must have shape batch_size x lookback_w x state_dim.")
        batch_size, lookback_w, state_dim = observation.shape
        if lookback_w != self.lookback_w:
            raise ValueError(f"Input lookback window must equal {self.lookback_w}.")
        if state_dim != self.state_dim:
            raise ValueError(f"Input state_dim must equal {self.state_dim}.")
        if batch_size <= 0:
            raise ValueError("Batch size must be positive.")

    def encode_history(self, observation: Tensor) -> Tensor:
        self.validate_input(observation)
        encoder_output, _ = self.encoder(observation)
        return encoder_output[:, -1, :]

    def encode_and_forecast(self, observation: Tensor) -> tuple[Tensor, Tensor]:
        """Encode with LSTM, produce load forecast, reconstruct full state.

        Returns (reconstructed_state, encoder_hidden) where reconstructed_state
        is either the full 74-dim state (base from obs + forecast from LSTM head)
        or the legacy raw LSTM hidden when forecast is disabled.
        """
        encoded = self.encode_history(observation)
        if self.forecast_head is not None:
            forecast = self.forecast_head(encoded)  # (batch, 20)
            base = observation[:, -1, :self.base_state_dim]  # (batch, 54)
            reconstructed = torch.cat([base, forecast], dim=-1)  # (batch, 74)
            return reconstructed, encoded
        return encoded, encoded

    def forward_components(self, observation: Tensor) -> tuple[Tensor, Tensor, Tensor]:
        combined, _ = self.encode_and_forecast(observation)
        body_output = self.q_body(combined)
        value = self.value_head(body_output)
        advantage = self.advantage_head(body_output)
        q_values = value + advantage - advantage.mean(dim=-1, keepdim=True)
        return value, advantage, q_values

    def forward(self, observation: Tensor) -> Tensor:
        return self.forward_components(observation)[2]

    def architecture_signature(self) -> dict[str, Any]:
        return {
            "class_name": self.__class__.__name__,
            "state_dim": self.state_dim,
            "lookback_w": self.lookback_w,
            "action_count": self.action_count,
            "q_network_hidden_layers": list(self.q_network_hidden_layers),
            "lstm_num_layers": self.lstm_num_layers,
            "lstm_hidden_size": self.lstm_hidden_size,
            "forward_api_shape": f"batch_size x {self.action_count}",
            "input_api_shape": f"batch_size x {self.lookback_w} x state_dim",
            "dueling_enabled": True,
            "double_dqn_api_enabled": True,
        }


def _build_seeded_network(config: "PaperHoodieNetworkConfig") -> PaperHoodieDuelingNetwork:
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(int(config.model_initialization_seed))
        network = PaperHoodieDuelingNetwork(config)
    network.eval()
    return network


def build_online_network(config: "PaperHoodieNetworkConfig") -> PaperHoodieDuelingNetwork:
    return _build_seeded_network(config)


def build_target_network(config: "PaperHoodieNetworkConfig") -> PaperHoodieDuelingNetwork:
    return _build_seeded_network(config)


__all__ = [
    "PaperHoodieDuelingNetwork",
    "build_online_network",
    "build_target_network",
]
