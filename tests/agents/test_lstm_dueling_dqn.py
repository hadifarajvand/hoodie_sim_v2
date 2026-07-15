import torch
import torch.nn as nn

from src.agents.lstm_dueling_dqn import LSTM_Dueling_DQN


def test_network_initialization():
    state_dim = 10
    lookback = 10
    num_actions = 5
    hidden_sizes = [32, 32, 32]
    lstm_hidden = 20

    net = LSTM_Dueling_DQN(
        state_dim=state_dim,
        lookback=lookback,
        num_actions=num_actions,
        hidden_sizes=hidden_sizes,
        lstm_hidden=lstm_hidden,
    )

    assert hasattr(net, "lstm")
    assert isinstance(net.lstm, nn.LSTM)
    assert net.lstm.input_size == state_dim
    assert net.lstm.hidden_size == lstm_hidden
    assert net.lstm.num_layers == 1

    assert hasattr(net, "fc_layers")
    assert len(list(net.fc_layers)) == len(hidden_sizes) * 2
    assert isinstance(net.fc_layers[0], nn.Linear)
    assert net.fc_layers[0].in_features == lstm_hidden

    assert hasattr(net, "value_stream")
    assert hasattr(net, "advantage_stream")
    assert net.value_stream[-1].out_features == 1
    assert net.advantage_stream[-1].out_features == num_actions


def test_forward_pass_shape():
    batch_size = 4
    state_dim = 10
    lookback = 10
    num_actions = 5

    net = LSTM_Dueling_DQN(
        state_dim=state_dim,
        lookback=lookback,
        num_actions=num_actions,
        hidden_sizes=[32, 32, 32],
        lstm_hidden=20,
    )

    x = torch.randn(batch_size, lookback, state_dim)
    q_values = net(x)
    assert q_values.shape == (batch_size, num_actions)


def test_gradient_flow():
    batch_size = 2
    state_dim = 10
    lookback = 10
    num_actions = 5

    net = LSTM_Dueling_DQN(
        state_dim=state_dim,
        lookback=lookback,
        num_actions=num_actions,
        hidden_sizes=[32, 32, 32],
        lstm_hidden=20,
    )

    x = torch.randn(batch_size, lookback, state_dim)
    q_values = net(x)
    loss = q_values.sum()
    loss.backward()
    assert any(param.grad is not None for param in net.parameters())


def test_edge_case_empty_batch():
    net = LSTM_Dueling_DQN(state_dim=5, lookback=5, num_actions=3, hidden_sizes=[16, 16], lstm_hidden=10)
    x = torch.randn(1, 5, 5)
    q_values = net(x)
    assert q_values.shape == (1, 3)


def test_zero_padding_in_lstm():
    net = LSTM_Dueling_DQN(state_dim=8, lookback=10, num_actions=4, hidden_sizes=[16, 16], lstm_hidden=16)
    x = torch.zeros(2, 10, 8)
    q_values = net(x)
    assert q_values.shape == (2, 4)
    assert not torch.isnan(q_values).any()
    assert not torch.isinf(q_values).any()
