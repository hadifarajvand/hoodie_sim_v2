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
        if config.action_count != 3:
            raise ValueError("Feature 039 keeps the stable action count fixed at 3.")
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

        body_layers: list[nn.Module] = []
        body_input_dim = self.lstm_hidden_size
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

    def forward_components(self, observation: Tensor) -> tuple[Tensor, Tensor, Tensor]:
        encoded = self.encode_history(observation)
        body_output = self.q_body(encoded)
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
