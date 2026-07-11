from __future__ import annotations

import warnings
from typing import Any

import torch
import torch.nn as nn

from src.analysis.paper_hoodie_network_implementation import PaperHoodieDuelingNetwork, PaperHoodieNetworkConfig


class LSTM_Dueling_DQN(nn.Module):
    """Delegation wrapper around PaperHoodieDuelingNetwork.

    Maintains backward compatibility with existing tests.
    The canonical implementation lives in
    src/analysis/paper_hoodie_network_implementation/network.py
    """

    def __init__(self, state_dim: int = 74, lookback: int = 10, num_actions: int = 22,
                 hidden_sizes: list[int] | None = None, lstm_hidden: int = 20):
        super().__init__()
        if hidden_sizes is None:
            hidden_sizes = [1024, 1024, 1024]
        config = PaperHoodieNetworkConfig.standard(
            state_dim=state_dim, action_count=num_actions,
        )
        self._impl = PaperHoodieDuelingNetwork(config)
        self.lstm = self._impl.encoder
        self.input_size = state_dim
        self.lstm_hidden = lstm_hidden
        self.lookback = lookback
        self.hidden_sizes = hidden_sizes
        self.num_actions = num_actions

    @property
    def fc_layers(self) -> nn.Sequential:
        return self._impl.q_body

    @property
    def value_stream(self) -> nn.Sequential:
        warnings.warn("value_stream accessed via wrapper; use _impl directly", stacklevel=2)
        return nn.Sequential(self._impl.value_head)

    @property
    def advantage_stream(self) -> nn.Sequential:
        warnings.warn("advantage_stream accessed via wrapper; use _impl directly", stacklevel=2)
        return nn.Sequential(self._impl.advantage_head)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self._impl(x)


__all__ = ["LSTM_Dueling_DQN"]
