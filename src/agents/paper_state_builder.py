from __future__ import annotations

from dataclasses import dataclass
from typing import List
import numpy as np

from src.policies.policy_interface import PolicyContext


@dataclass
class PaperStateBuilder:
    """Builds the full state vector as described in the HOODIE paper."""
    
    num_eas: int = 20  # Default to 20 EAs as in the paper
    
    def build_state(self, task_size: float, processing_density: float,
                   private_wait_time: float, offload_wait_time: float,
                   public_queue_lengths: List[float], load_forecast: List[float]) -> np.ndarray:
        """Build the complete state vector for the HOODIE agent.
        
        The state vector consists of:
        - Task characteristics: size (one-hot [2,2.1,...,5]), processing density (scalar)
        - Queue state: private wait time, offload wait time (slots)
        - Public queue lengths: N scalars (one per EA)
        - Load forecast: N scalars from LSTM (W=10 history → LSTM 1×20 → predict next slot)
        
        Args:
            task_size: Task size in Mbits
            processing_density: Processing density in Gcyc/Mbit
            private_wait_time: Time spent in private queue (slots)
            offload_wait_time: Time spent in offload queue (slots)
            public_queue_lengths: List of queue lengths for each EA
            load_forecast: List of load forecast values for each EA
            
        Returns:
            numpy array representing the state vector
        """
        # Task size one-hot encoding: [2, 2.1, 2.2, ..., 5.0]
        size_values = [2.0 + 0.1 * i for i in range(31)]  # 2.0 to 5.0 in steps of 0.1
        size_one_hot = [0.0] * len(size_values)
        
        # Find the closest size value and set corresponding index to 1.0
        if size_values:
            closest_index = min(range(len(size_values)), 
                              key=lambda i: abs(size_values[i] - task_size))
            size_one_hot[closest_index] = 1.0
        
        # Public queue lengths: N scalars (one per EA)
        # Use the provided values, or zeros if not enough provided
        if len(public_queue_lengths) < self.num_eas:
            # Pad with zeros if not enough values provided
            public_queue_lengths = list(public_queue_lengths) + [0.0] * (self.num_eas - len(public_queue_lengths))
        else:
            # Truncate if too many values provided
            public_queue_lengths = list(public_queue_lengths[:self.num_eas])
        
        # Load forecast: N scalars from LSTM (to be implemented when LSTM component is ready)
        # Use the provided values, or zeros if not enough provided
        if len(load_forecast) < self.num_eas:
            # Pad with zeros if not enough values provided
            load_forecast = list(load_forecast) + [0.0] * (self.num_eas - len(load_forecast))
        else:
            # Truncate if too many values provided
            load_forecast = list(load_forecast[:self.num_eas])
        
        # Concatenate all components
        state_vector = np.concatenate([
            np.array(size_one_hot, dtype=np.float32),
            np.array([processing_density], dtype=np.float32),
            np.array([private_wait_time, offload_wait_time], dtype=np.float32),
            np.array(public_queue_lengths, dtype=np.float32),
            np.array(load_forecast, dtype=np.float32)
        ])
        
        return state_vector