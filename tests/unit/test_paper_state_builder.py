import numpy as np
import pytest
from src.agents.paper_state_builder import PaperStateBuilder

def test_paper_state_builder_can_be_instantiated():
    builder = PaperStateBuilder(num_eas=3)
    assert builder is not None

def test_state_vector_dimensions():
    num_eas = 3
    builder = PaperStateBuilder(num_eas=num_eas)
    state = builder.build_state(
        task_size=2.0,
        processing_density=0.5,
        private_wait_time=1.0,
        offload_wait_time=2.0,
        public_queue_lengths=[1.0, 2.0, 3.0],
        load_forecast=[0.1, 0.2, 0.3]
    )
    # Expected length: 31 (one-hot) + 1 (density) + 1 (private wait) + 1 (offload wait) + num_eas (public queue) + num_eas (load forecast)
    expected_length = 31 + 1 + 1 + 1 + num_eas + num_eas
    assert len(state) == expected_length

def test_task_size_one_hot_encoding():
    num_eas = 1
    builder = PaperStateBuilder(num_eas=num_eas)
    # Test with task_size = 2.0 (first in the list)
    state = builder.build_state(
        task_size=2.0,
        processing_density=0.0,
        private_wait_time=0.0,
        offload_wait_time=0.0,
        public_queue_lengths=[0.0],
        load_forecast=[0.0]
    )
    # The first 31 elements should be the one-hot vector for 2.0
    one_hot_part = state[:31]
    expected_one_hot = [0.0] * 31
    expected_one_hot[0] = 1.0  # 2.0 is the first in the list [2.0, 2.1, ..., 5.0]
    np.testing.assert_array_equal(one_hot_part, expected_one_hot)

def test_processing_density_included():
    num_eas = 1
    builder = PaperStateBuilder(num_eas=num_eas)
    state = builder.build_state(
        task_size=2.0,
        processing_density=0.5,
        private_wait_time=0.0,
        offload_wait_time=0.0,
        public_queue_lengths=[0.0],
        load_forecast=[0.0]
    )
    # The element after the one-hot vector (index 31) should be the processing density
    assert state[31] == 0.5

def test_wait_times_included():
    num_eas = 1
    builder = PaperStateBuilder(num_eas=num_eas)
    state = builder.build_state(
        task_size=2.0,
        processing_density=0.0,
        private_wait_time=1.5,
        offload_wait_time=2.5,
        public_queue_lengths=[0.0],
        load_forecast=[0.0]
    )
    # Index 32: private wait time, index 33: offload wait time
    assert state[32] == 1.5
    assert state[33] == 2.5

def test_public_queue_lengths_included():
    num_eas = 3
    builder = PaperStateBuilder(num_eas=num_eas)
    state = builder.build_state(
        task_size=2.0,
        processing_density=0.0,
        private_wait_time=0.0,
        offload_wait_time=0.0,
        public_queue_lengths=[1.0, 2.0, 3.0],
        load_forecast=[0.0, 0.0, 0.0]
    )
    # After the first 34 elements (31+1+1+1) come the public queue lengths
    public_queue_start = 34
    public_queue_end = public_queue_start + num_eas
    np.testing.assert_allclose(
        state[public_queue_start:public_queue_end], 
        [1.0, 2.0, 3.0], 
        rtol=1e-6
    )

def test_load_forecast_included():
    num_eas = 2
    builder = PaperStateBuilder(num_eas=num_eas)
    state = builder.build_state(
        task_size=2.0,
        processing_density=0.0,
        private_wait_time=0.0,
        offload_wait_time=0.0,
        public_queue_lengths=[0.0, 0.0],
        load_forecast=[0.1, 0.2]
    )
    # After the first 34 + num_eas elements come the load forecast
    load_forecast_start = 34 + num_eas
    load_forecast_end = load_forecast_start + num_eas
    np.testing.assert_allclose(
        state[load_forecast_start:load_forecast_end], 
        [0.1, 0.2], 
        rtol=1e-6
    )