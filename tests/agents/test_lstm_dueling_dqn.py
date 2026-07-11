import torch
import torch.nn as nn
import pytest

# Superseded by PaperHoodieDuelingNetwork in analysis/paper_hoodie_network_implementation/
pytestmark = pytest.mark.xfail(reason="LSTM_Dueling_DQN stub superseded by PaperHoodieDuelingNetwork")

# We'll try to import the class; if it doesn't exist, the test will fail
try:
    from src.agents.lstm_dueling_dqn import LSTM_Dueling_DQN
except ImportError:
    # Define a dummy class to allow test to run but fail
    class LSTM_Dueling_DQN(nn.Module):
        def __init__(self, *args, **kwargs):
            super().__init__()
            raise NotImplementedError("Network not implemented yet")
        
        def forward(self, x):
            raise NotImplementedError("Network not implemented yet")

def test_network_initialization():
    """Test that the network initializes with correct layer sizes."""
    state_dim = 10  # Example: task features, wait times, queue lengths, etc.
    lookback = 10
    num_actions = 5  # Example: local + 4 edge nodes + cloud? Actually, depends on topology
    hidden_sizes = [1024, 1024, 1024]  # Three FC layers
    lstm_hidden = 20
    
    # This should fail because the class doesn't exist yet
    net = LSTM_Dueling_DQN(
        state_dim=state_dim,
        lookback=lookback,
        num_actions=num_actions,
        hidden_sizes=hidden_sizes,
        lstm_hidden=lstm_hidden
    )
    
    # Check that the network has the expected layers
    assert hasattr(net, 'lstm')
    assert isinstance(net.lstm, nn.LSTM)
    assert net.lstm.input_size == state_dim
    assert net.lstm.hidden_size == lstm_hidden
    assert net.lstm.num_layers == 1  # Default unless specified
    
    # Check FC layers
    assert hasattr(net, 'fc_layers')
    assert len(net.fc_layers) == len(hidden_sizes)
    assert net.fc_layers[0].in_features == lstm_hidden
    assert net.fc_layers[-1].out_features == hidden_sizes[-1]
    
    # Check dueling heads
    assert hasattr(net, 'value_stream')
    assert hasattr(net, 'advantage_stream')
    assert net.value_stream[-1].out_features == 1
    assert net.advantage_stream[-1].out_features == num_actions

def test_forward_pass_shape():
    """Test forward pass produces correct output shape."""
    batch_size = 4
    state_dim = 10
    lookback = 10
    num_actions = 5
    
    net = LSTM_Dueling_DQN(
        state_dim=state_dim,
        lookback=lookback,
        num_actions=num_actions,
        hidden_sizes=[1024, 1024, 1024],
        lstm_hidden=20
    )
    
    # Input: [batch, lookback, state_dim]
    x = torch.randn(batch_size, lookback, state_dim)
    q_values = net(x)
    
    # Output: [batch, num_actions]
    assert q_values.shape == (batch_size, num_actions)

def test_gradient_flow():
    """Test that gradients flow through the network."""
    batch_size = 2
    state_dim = 10
    lookback = 10
    num_actions = 5
    
    net = LSTM_Dueling_DQN(
        state_dim=state_dim,
        lookback=lookback,
        num_actions=num_actions,
        hidden_sizes=[1024, 1024, 1024],
        lstm_hidden=20
    )
    
    x = torch.randn(batch_size, lookback, state_dim)
    q_values = net(x)
    
    # Compute a dummy loss and backprop
    loss = q_values.sum()
    loss.backward()
    
    # Check that gradients are not None for at least one parameter
    has_grad = False
    for param in net.parameters():
        if param.grad is not None:
            has_grad = True
            break
    assert has_grad, "No gradients computed"

def test_edge_case_empty_batch():
    """Test with batch size 1 (minimal batch)."""
    state_dim = 5
    lookback = 5
    num_actions = 3
    
    net = LSTM_Dueling_DQN(
        state_dim=state_dim,
        lookback=lookback,
        num_actions=num_actions,
        hidden_sizes=[64, 64, 64],  # Smaller for quick test
        lstm_hidden=10
    )
    
    x = torch.randn(1, lookback, state_dim)
    q_values = net(x)
    assert q_values.shape == (1, num_actions)

def test_zero_padding_in_lstm():
    """Test that the network can handle zero inputs (padding)."""
    batch_size = 2
    state_dim = 8
    lookback = 10
    num_actions = 4
    
    net = LSTM_Dueling_DQN(
        state_dim=state_dim,
        lookback=lookback,
        num_actions=num_actions,
        hidden_sizes=[128, 128, 128],
        lstm_hidden=16
    )
    
    # Input with zeros (simulating padding)
    x = torch.zeros(batch_size, lookback, state_dim)
    q_values = net(x)
    assert q_values.shape == (batch_size, num_actions)
    # Output should not be NaN or Inf
    assert not torch.isnan(q_values).any()
    assert not torch.isinf(q_values).any()
