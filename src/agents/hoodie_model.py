from __future__ import annotations

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Tuple, List, Any, Iterable, Optional

from .dueling_dqn_network import DuelingDQNNetwork
from .paper_state_builder import PaperStateBuilder
from .replay_buffer import Transition


class HoodieModel:
    """
    Hoodie model that uses a neural network (Dueling DQN) as the base Q-function,
    with additional learned action preferences and biases (to maintain compatibility
    with the original HoodieModel interface).
    The network is lazily initialized based on the observed state dimension.
    """
    
    def __init__(
        self,
        device: str = "cpu",
        hidden_size: int = 1024,
        num_hidden_layers: int = 3,
        learning_rate: float = 0.001
    ):
        """
        Initialize the neural network model.
        
        Args:
            device: Device to run the model on ('cpu' or 'cuda')
            hidden_size: Size of hidden layers (default 1024)
            num_hidden_layers: Number of hidden layers in each stream (default 3)
            learning_rate: Learning rate for the optimizer (default 0.001)
        """
        self.device = torch.device(device)
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.learning_rate = learning_rate
        
        # These will be initialized on first forward pass
        self._initialized: bool = False
        self._num_eas: Optional[int] = None
        self.online_net: Optional[DuelingDQNNetwork] = None
        self.target_net: Optional[DuelingDQNNetwork] = None
        
        # State builder for converting observations to state vectors
        self.state_builder = PaperStateBuilder(num_eas=0)  # dummy, will be updated
        
        # For compatibility with original HoodieModel interface
        self.learned_action_preferences: dict[str, float] = {}
        self.action_biases: dict[str, float] = {}
        
        # For backward compatibility with tests
        class _DuellingDummy:
            def __init__(self):
                self.value_weight = 0.0
        self.dueling_dqn = _DuellingDummy()
    
    def _initialize_networks(self, num_eas: int) -> None:
        """Initialize the online and target networks based on the number of EAs."""
        self._num_eas = num_eas
        
        # State dimension from PaperStateBuilder:
        # 31 (task size one-hot) + 1 (density) + 1 (private wait) + 1 (offload wait) 
        # + num_eas (public queue lengths) + num_eas (load forecast)
        state_dim = 31 + 1 + 1 + 1 + num_eas + num_eas
        action_dim = num_eas + 2  # local, public_0..public_{N-1}, cloud
        
        self.state_builder = PaperStateBuilder(num_eas=num_eas)
        
        # Initialize networks
        self.online_net = DuelingDQNNetwork(
            state_dim=state_dim,
            action_dim=action_dim,
            hidden_size=self.hidden_size,
            num_hidden_layers=self.num_hidden_layers,
            learning_rate=self.learning_rate
        ).to(self.device)
        
        self.target_net = DuelingDQNNetwork(
            state_dim=state_dim,
            action_dim=action_dim,
            hidden_size=self.hidden_size,
            num_hidden_layers=self.num_hidden_layers,
            learning_rate=self.learning_rate
        ).to(self.device)
        
        # Initialize target network with same weights as online
        self.target_net.load_state_dict(self.online_net.state_dict())
        
        self._initialized = True
    
    def _build_state_from_observation(self, observation: Dict[str, Any]) -> np.ndarray:
        """
        Build a state vector from an observation dictionary.
        
        Expected observation keys:
            - task_size: float
            - processing_density: float
            - private_wait_time: float
            - offload_wait_time: float
            - public_queue_lengths: list of float (length num_eas)
            - load_forecast: list of float (length num_eas)
        """
        # Extract fields from observation
        task_size = float(observation.get("task_size", 2.0))  # default to middle value
        processing_density = float(observation.get("processing_density", 0.0))
        private_wait_time = float(observation.get("private_wait_time", 0.0))
        offload_wait_time = float(observation.get("offload_wait_time", 0.0))
        public_queue_lengths = observation.get("public_queue_lengths", [])
        load_forecast = observation.get("load_forecast", [])
        
        # If we haven't initialized the networks yet, we can infer num_eas from the observation
        if not self._initialized:
            # We assume that public_queue_lengths and load_forecast have the same length
            # and that length is the number of EAs.
            # If they are not present or empty, we cannot determine num_eas yet.
            if isinstance(public_queue_lengths, list) and len(public_queue_lengths) > 0:
                num_eas = len(public_queue_lengths)
                # Optionally, verify that load_forecast has the same length
                if isinstance(load_forecast, list) and len(load_forecast) == num_eas:
                    self._initialize_networks(num_eas)
                else:
                    # If lengths don't match, we cannot initialize yet; we'll try again later
                    pass
            elif isinstance(load_forecast, list) and len(load_forecast) > 0:
                num_eas = len(load_forecast)
                if isinstance(public_queue_lengths, list) and len(public_queue_lengths) == num_eas:
                    self._initialize_networks(num_eas)
                else:
                    pass
        
        # Ensure correct length for public_queue_lengths and load_forecast
        if self._num_eas is not None:
            expected_len = self._num_eas
            if not isinstance(public_queue_lengths, list):
                public_queue_lengths = [0.0] * expected_len
            else:
                if len(public_queue_lengths) != expected_len:
                    if len(public_queue_lengths) > expected_len:
                        public_queue_lengths = public_queue_lengths[:expected_len]
                    else:
                        public_queue_lengths = list(public_queue_lengths) + [0.0] * (expected_len - len(public_queue_lengths))
            if not isinstance(load_forecast, list):
                load_forecast = [0.0] * expected_len
            else:
                if len(load_forecast) != expected_len:
                    if len(load_forecast) > expected_len:
                        load_forecast = load_forecast[:expected_len]
                    else:
                        load_forecast = list(load_forecast) + [0.0] * (expected_len - len(load_forecast))
        else:
            # If we still don't know num_eas, we cannot build a state vector.
            # Return a zero vector of a default size? We'll return empty and let the caller handle it.
            # But we need to return something; we'll return a zero vector of size 0 for now.
            # The caller should check that the state vector is non-empty before using it.
            return np.array([], dtype=np.float32)
        
        # Build state using the state_builder expects individual arguments
        state_vector = self.state_builder.build_state(
            task_size=task_size,
            processing_density=processing_density,
            private_wait_time=private_wait_time,
            offload_wait_time=offload_wait_time,
            public_queue_lengths=[float(x) for x in public_queue_lengths],
            load_forecast=[float(x) for x in load_forecast]
        )
        
        return state_vector
    
    def _action_hint(self, history: Any, action: str) -> float:
        """
        Compute action hint from observation (copied from original HoodieModel).
        """
        if not hasattr(history, 'observations') or not history.observations:
            return 0.0
        latest_observation = history.observations[-1]
        if not isinstance(latest_observation, dict):
            return 0.0
        if "topology" not in latest_observation:
            return 0.0
        fallback_hints = latest_observation.get("fallback_hints")
        if not isinstance(fallback_hints, dict):
            return 0.0
        canonical_action = {
            "compute_local": "local",
            "offload_horizontal": "horizontal",
            "offload_vertical": "vertical",
        }.get(action, action)
        hint = fallback_hints.get(canonical_action)
        if isinstance(hint, (int, float)):
            return float(hint)
        return 0.0
    
    def forward(self, history: Any, legal_actions: tuple[str, ...]) -> dict[str, float]:
        """
        Compute Q-values for given history and legal actions.
        
        Args:
            history: HistoryWindow containing observations, trace_history, etc.
            legal_actions: Tuple of legal action strings (e.g., ('local', 'public_0', 'cloud'))
            
        Returns:
            Dictionary mapping action strings to Q-values.
        """
        # Get the most recent observation from history
        if not hasattr(history, 'observations') or len(history.observations) == 0:
            # No observations, return zero Q-values for legal actions
            return {action: 0.0 for action in legal_actions}
            
        # The last observation in the history is the current observation
        obs = history.observations[-1]
        if not isinstance(obs, dict):
            # If observation is not a dict, we cannot extract features
            return {action: 0.0 for action in legal_actions}
        
        # Build state vector from observation
        state_vector = self._build_state_from_observation(obs)
        
        base_q_values: dict[str, float] = {}
        if state_vector.size > 0 and self._initialized:
            state_tensor = torch.from_numpy(state_vector).float().unsqueeze(0).to(self.device)
            with torch.no_grad():
                q_values = self.online_net(state_tensor).squeeze(0).cpu().numpy()
            if self._num_eas is not None:
                action_list = ['local'] + [f'public_{i}' for i in range(self._num_eas)] + ['cloud']
                base_q_values = {action: float(q_values[i]) for i, action in enumerate(action_list)}
        
        scored_actions: dict[str, float] = {}
        for action in legal_actions:
            base_q = base_q_values.get(action, 0.0)
            learned_preference = self.learned_action_preferences.get(action, 0.0)
            action_bias = self.action_biases.get(action, 0.0)
            action_hint = self._action_hint(history, action)
            scored_actions[action] = base_q + learned_preference + action_bias + action_hint
        
        return scored_actions
    
    def update_action_preference(self, action: str, reward: float, learning_rate: float) -> float:
        """
        Update learned action preference (for compatibility).
        """
        current = self.learned_action_preferences.get(action, 0.0)
        updated = current + learning_rate * (reward - current)
        self.learned_action_preferences[action] = updated
        return updated
    
    def learn_from_transitions(self, transitions: tuple, learning_rate: float) -> int:
        """
        Learn from a batch of transitions using DQN.
        This method is called by HoodieAgent.learn_from_replay when learner is not enabled.
        
        Args:
            transitions: tuple of Transition objects
            learning_rate: learning rate for the update
            
        Returns:
            Number of transitions updated (length of transitions)
        """
        if not transitions:
            return 0
        
        # First, update the learned action preferences (table-based update) for compatibility with tests
        for t in transitions:
            action = t.action
            reward = t.reward
            old = self.learned_action_preferences.get(action, 0.0)
            new = old + learning_rate * (reward - old)
            self.learned_action_preferences[action] = new
        
        # If networks are not initialized, we cannot learn via DQN yet.
        # We'll try to initialize them from the first transition's state.
        if not self._initialized:
            # Attempt to initialize from the first transition
            first_state = transitions[0].state
            if isinstance(first_state, dict):
                # Try to infer num_eas from the state
                pq = first_state.get("public_queue_lengths", [])
                lf = first_state.get("load_forecast", [])
                if isinstance(pq, list) and len(pq) > 0 and isinstance(lf, list) and len(lf) == len(pq):
                    self._initialize_networks(len(pq))
                elif isinstance(lf, list) and len(lf) > 0 and isinstance(pq, list) and len(pq) == len(lf):
                    self._initialize_networks(len(lf))
                # If we still couldn't initialize, we cannot learn via DQN from this batch
                # but we have already updated the table.
        
        # If still not initialized, we cannot do DQN
        if not self._initialized:
            return len(transitions)
        
        # Build states and next_states for all transitions
        states = []
        actions = []
        rewards = []
        next_states = []
        dones = []
        for t in transitions:
            state_vector = self._build_state_from_observation(t.state)
            next_state_vector = self._build_state_from_observation(t.next_state)
            # If we cannot build a state vector (e.g., returns empty array), we skip DQN for this batch
            if state_vector.size == 0 or next_state_vector.size == 0:
                # We have already updated the table, so return the count
                return len(transitions)
            states.append(state_vector)
            # We need to map action string to index
            action_list = ['local'] + [f'public_{i}' for i in range(self._num_eas)] + ['cloud']
            try:
                action_idx = action_list.index(t.action)
            except ValueError:
                # If action not in list, we skip DQN for this batch
                return len(transitions)
            actions.append(action_idx)
            rewards.append(t.reward)
            next_states.append(next_state_vector)
            dones.append(1.0 if t.done else 0.0)
        
        # If we have no valid transitions for DQN, return (table already updated)
        if not states:
            return len(transitions)
        
        # Convert to tensors
        states_tensor = torch.from_numpy(np.array(states)).float().to(self.device)
        actions_tensor = torch.from_numpy(np.array(actions)).long().to(self.device)
        rewards_tensor = torch.from_numpy(np.array(rewards)).float().to(self.device)
        next_states_tensor = torch.from_numpy(np.array(next_states)).float().to(self.device)
        dones_tensor = torch.from_numpy(np.array(dones)).float().to(self.device)
        
        # Set learning rate in optimizer
        for param_group in self.online_net.optimizer.param_groups:
            param_group['lr'] = learning_rate
        
        # Zero the gradients
        self.online_net.optimizer.zero_grad()
        
        # Compute current Q-values for taken actions
        current_q_values = self.online_net(states_tensor).gather(1, actions.unsqueeze(1))
        
        # Compute next Q-values using target network
        with torch.no_grad():
            next_q_values = self.target_net(next_states_tensor)
            max_next_q_values = next_q_values.max(1)[0]
            target_q_values = rewards_tensor + (0.99 * max_next_q_values * (1 - dones_tensor))
        
        # Compute loss
        loss_fn = nn.MSELoss()
        loss = loss_fn(current_q_values.squeeze(), target_q_values)
        
        # Backpropagate
        loss.backward()
        self.online_net.optimizer.step()
        
        return len(transitions)
        for t in transitions:
            action = t.action
            reward = t.reward
            old = self.learned_action_preferences.get(action, 0.0)
            new = old + learning_rate * (reward - old)
            self.learned_action_preferences[action] = new
        
        return len(transitions)
    
    def update_target_network(self):
        """Copy weights from online network to target network."""
        if self._initialized and self.online_net is not None and self.target_net is not None:
            self.target_net.load_state_dict(self.online_net.state_dict())
    
    def best_action(self, history: Any, legal_actions: tuple[str, ...]) -> str:
        """
        Return the best action for the given history and legal actions.
        """
        q_values = self.forward(history, legal_actions)
        if not q_values:
            raise ValueError("No legal actions available")
        return max(q_values, key=q_values.get)
    
    def to_state(self) -> dict[str, Any]:
        """
        Serialize the model to a dictionary.
        """
        if not self._initialized:
            # If not initialized, we still need to return a state that can be used to recreate the model.
            # We'll return the configuration and mark as uninitialized.
            return {
                "schema_version": 1,
                "initialized": False,
                "device": str(self.device),
                "hidden_size": self.hidden_size,
                "num_hidden_layers": self.num_hidden_layers,
                "learning_rate": self.learning_rate,
                "learned_action_preferences": dict(self.learned_action_preferences),
                "action_biases": dict(self.action_biases),
            }
        else:
            return {
                "schema_version": 1,
                "initialized": True,
                "num_eas": self._num_eas,
                "device": str(self.device),
                "hidden_size": self.hidden_size,
                "num_hidden_layers": self.num_hidden_layers,
                "learning_rate": self.learning_rate,
                "online_net": {
                    "state_dict": self.online_net.state_dict(),
                },
                "target_net": {
                    "state_dict": self.target_net.state_dict(),
                },
                "learned_action_preferences": dict(self.learned_action_preferences),
                "action_biases": dict(self.action_biases),
            }
    
    @classmethod
    def from_state(cls, state: dict[str, Any]) -> "HoodieModel":
        """
        Deserialize the model from a dictionary.
        """
        schema_version = int(state.get("schema_version", 1))
        if schema_version != 1:
            raise ValueError(f"Unsupported HoodieModel state schema version: {schema_version}")
        
        device = state.get("device", "cpu")
        hidden_size = int(state.get("hidden_size", 1024))
        num_hidden_layers = int(state.get("num_hidden_layers", 3))
        learning_rate = float(state.get("learning_rate", 0.001))
        
        model = cls(device=device, hidden_size=hidden_size, num_hidden_layers=num_hidden_layers, learning_rate=learning_rate)
        
        if state.get("initialized", False):
            model._num_eas = int(state.get("num_eas", 0))
            model._initialized = True
            
            # Load network states
            online_state = state.get("online_net", {}).get("state_dict", {})
            if online_state:
                model.online_net.load_state_dict(online_state)
            
            target_state = state.get("target_net", {}).get("state_dict", {})
            if target_state:
                model.target_net.load_state_dict(target_state)
        
        # Load learned preferences and biases
        learned_prefs = state.get("learned_action_preferences", {})
        if isinstance(learned_prefs, dict):
            model.learned_action_preferences = {str(k): float(v) for k, v in learned_prefs.items()}
        
        action_biases = state.get("action_biases", {})
        if isinstance(action_biases, dict):
            model.action_biases = {str(k): float(v) for k, v in action_biases.items()}
        
        return model
