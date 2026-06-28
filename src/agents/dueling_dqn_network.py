from __future__ import annotations

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Tuple, List, Optional


class DuelingDQNNetwork(nn.Module):
    """
    Dueling Deep Q-Network with three shared hidden layers of 1024 units each,
    followed by separate value and advantage streams.
    """
    
    def __init__(
        self, 
        state_dim: int, 
        action_dim: int,
        hidden_size: int = 1024,
        num_hidden_layers: int = 3,
        learning_rate: float = 0.001
    ):
        super(DuelingDQNNetwork, self).__init__()
        
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        
        # Shared layers
        self.shared_layers = nn.ModuleList()
        for i in range(num_hidden_layers):
            if i == 0:
                self.shared_layers.append(nn.Linear(state_dim, hidden_size))
            else:
                self.shared_layers.append(nn.Linear(hidden_size, hidden_size))
        
        # Value stream
        self.value_layers = nn.ModuleList()
        for i in range(num_hidden_layers):
            if i == 0:
                self.value_layers.append(nn.Linear(hidden_size, hidden_size))
            else:
                self.value_layers.append(nn.Linear(hidden_size, hidden_size))
        self.value_output = nn.Linear(hidden_size, 1)
        
        # Advantage stream
        self.advantage_layers = nn.ModuleList()
        for i in range(num_hidden_layers):
            if i == 0:
                self.advantage_layers.append(nn.Linear(hidden_size, hidden_size))
            else:
                self.advantage_layers.append(nn.Linear(hidden_size, hidden_size))
        self.advantage_output = nn.Linear(hidden_size, action_dim)
        
        # Activation function
        self.relu = nn.ReLU()
        
        # Optimizer
        self.optimizer = torch.optim.Adam(self.parameters(), lr=learning_rate)
        
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Forward pass returning Q-values for each action.
        
        Args:
            state: Tensor of shape (batch_size, state_dim)
            
        Returns:
            q_values: Tensor of shape (batch_size, action_dim)
        """
        # Shared layers
        x = state
        for layer in self.shared_layers:
            x = self.relu(layer(x))
        
        # Value stream
        v = x
        for layer in self.value_layers:
            v = self.relu(layer(v))
        value = self.value_output(v)  # Shape: (batch_size, 1)
        
        # Advantage stream
        a = x
        for layer in self.advantage_layers:
            a = self.relu(layer(a))
        advantage = self.advantage_output(a)  # Shape: (batch_size, action_dim)
        
        # Combine: Q(s,a) = V(s) + (A(s,a) - mean_a' A(s,a'))
        q_values = value + (advantage - advantage.mean(dim=1, keepdim=True))
        return q_values
    
    def learn_from_batch(
        self,
        states: torch.Tensor,
        actions: torch.Tensor,
        rewards: torch.Tensor,
        next_states: torch.Tensor,
        dones: torch.Tensor,
        gamma: float = 0.99,
        target_net: Optional['DuelingDQNNetwork'] = None
    ) -> float:
        """
        Perform a learning step on a batch of transitions.
        
        Args:
            states: Tensor of shape (batch_size, state_dim)
            actions: Tensor of shape (batch_size,) containing action indices
            rewards: Tensor of shape (batch_size,)
            next_states: Tensor of shape (batch_size, state_dim)
            dones: Tensor of shape (batch_size,) with 1.0 if done, 0.0 otherwise
            gamma: Discount factor
            target_net: Target network to use for computing next state values.
                       If None, uses self (not recommended for DQN).
        
        Returns:
            Loss value (float)
        """
        self.train()
        
        # Compute current Q-values for taken actions
        current_q_values = self.forward(states)  # (batch_size, action_dim)
        current_q_values = current_q_values.gather(1, actions.unsqueeze(1))  # (batch_size, 1)
        
        # Compute next state values using target network
        if target_net is None:
            target_net = self
        target_net.eval()
        with torch.no_grad():
            next_q_values = target_net.forward(next_states)  # (batch_size, action_dim)
            max_next_q_values = next_q_values.max(1)[0]  # (batch_size,)
            target_q_values = rewards + (gamma * max_next_q_values * (1 - dones))  # (batch_size,)
        
        # Compute loss
        loss_fn = nn.MSELoss()
        loss = loss_fn(current_q_values.squeeze(), target_q_values)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        return loss.item()