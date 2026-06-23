"""Feedforward-only variant of HOODIE network (no LSTM).

Used for Figure 11 ablation study. All other properties identical to baseline.
Network architecture: Dense(1024) -> ReLU -> Dense(1024) -> ReLU -> Dense(1024) -> ReLU -> Dueling heads.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import torch
from torch import Tensor, nn

if TYPE_CHECKING:
    from .report import PaperHoodieNetworkConfig


class PaperHoodieDuelingNetworkNoLSTM(nn.Module):
    """Feedforward-only (no LSTM) variant of HOODIE dueling network.

    Identical to PaperHoodieDuelingNetwork except:
    - No LSTM encoder layer
    - Input goes directly into Q-body (takes last frame of state window)
    - All other properties and output shapes preserved
    """

    def __init__(self, config: "PaperHoodieNetworkConfig") -> None:
        super().__init__()
        if config.state_dim is None or config.state_dim <= 0:
            raise ValueError("state_dim is required and must be positive to build the network.")
        if config.action_count != 3:
            raise ValueError("Feature 039 keeps the stable action count fixed at 3.")
        if list(config.q_network_hidden_layers) != [1024, 1024, 1024]:
            raise ValueError("q_network_hidden_layers must equal [1024, 1024, 1024].")

        self.config = config
        self.state_dim = int(config.state_dim)
        self.lookback_w = int(config.lstm_lookback_w)
        self.action_count = int(config.action_count)
        self.q_network_hidden_layers = tuple(int(width) for width in config.q_network_hidden_layers)

        # No LSTM: directly use state_dim as input to q_body
        body_layers: list[nn.Module] = []
        body_input_dim = self.state_dim
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
        """Use last frame only (no LSTM encoding)."""
        self.validate_input(observation)
        # Take last frame of sequence (no history encoding)
        return observation[:, -1, :]

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
            "lstm_num_layers": 0,
            "lstm_hidden_size": 0,
            "forward_api_shape": f"batch_size x {self.action_count}",
            "input_api_shape": f"batch_size x {self.lookback_w} x state_dim",
            "dueling_enabled": True,
            "double_dqn_api_enabled": True,
            "lstm_enabled": False,
        }


def _build_seeded_network_no_lstm(config: "PaperHoodieNetworkConfig") -> PaperHoodieDuelingNetworkNoLSTM:
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(int(config.model_initialization_seed))
        network = PaperHoodieDuelingNetworkNoLSTM(config)
    network.eval()
    return network


def build_online_network_no_lstm(config: "PaperHoodieNetworkConfig") -> PaperHoodieDuelingNetworkNoLSTM:
    return _build_seeded_network_no_lstm(config)


def build_target_network_no_lstm(config: "PaperHoodieNetworkConfig") -> PaperHoodieDuelingNetworkNoLSTM:
    return _build_seeded_network_no_lstm(config)


__all__ = [
    "PaperHoodieDuelingNetworkNoLSTM",
    "build_online_network_no_lstm",
    "build_target_network_no_lstm",
]
