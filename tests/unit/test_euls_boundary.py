from __future__ import annotations

import sys
import types
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

if "matplotlib" not in sys.modules:
    matplotlib = types.ModuleType("matplotlib")
    pyplot = types.ModuleType("pyplot")
    matplotlib.pyplot = pyplot
    sys.modules["matplotlib"] = matplotlib
    sys.modules["matplotlib.pyplot"] = pyplot

if "torch" not in sys.modules:
    torch = types.ModuleType("torch")
    torch.manual_seed = lambda seed: None
    sys.modules["torch"] = torch

from euls.boundary import EULSBoundaryContract
from euls.kernel import EULSKernel
from environment.environment import Environment


def _environment() -> Environment:
    return Environment(
        static_frequency=0,
        number_of_servers=1,
        private_cpu_capacities=[1.0],
        public_cpu_capacities=[1.0],
        connection_matrix=np.array([[0.0]]),
        cloud_computational_capacity=1.0,
        episode_time=1,
        task_arrive_probabilities=[0.0],
        task_size_mins=[1.0],
        task_size_maxs=[1.0],
        task_size_distributions=["constant"],
        timeout_delay_mins=[10],
        timeout_delay_maxs=[10],
        timeout_delay_distributions=["constant"],
        priotiry_mins=[1],
        priotiry_maxs=[1],
        priotiry_distributions=["constant"],
        computational_density_mins=[1.0],
        computational_density_maxs=[1.0],
        computational_density_distributions=["constant"],
        drop_penalty_mins=[40],
        drop_penalty_maxs=[40],
        drop_penalty_distributions=["constant"],
    )


def test_kernel_wraps_environment():
    kernel = EULSKernel(_environment())
    assert kernel.environment is not None


def test_reset_delegates_and_returns_same_shape():
    env = _environment()
    kernel = EULSKernel(env)
    expected = env.reset()
    observed = kernel.reset(seed=7)
    assert len(observed) == len(expected)


def test_step_delegates_standard_tuple():
    kernel = EULSKernel(_environment())
    kernel.reset(seed=3)
    observation, reward, terminated, truncated, info = kernel.step("0")
    assert observation is not None
    assert isinstance(reward, (int, float, np.floating, np.ndarray))
    assert isinstance(terminated, bool)
    assert truncated is False or isinstance(truncated, bool)
    assert isinstance(info, dict)


def test_same_seed_same_actions_match_environment():
    env_a = _environment()
    env_b = _environment()
    kernel = EULSKernel(env_a)
    direct = env_b.reset()
    wrapped = kernel.reset(seed=11)
    assert len(direct) == len(wrapped)
    direct_step = env_b.step([0])
    wrapped_step = kernel.step("0")
    assert np.array_equal(direct_step[0][0], wrapped_step[0][0])
    assert np.array_equal(direct_step[1], wrapped_step[1])
    assert direct_step[2] == wrapped_step[2]
    assert wrapped_step[3] is False
    assert direct_step[3] == wrapped_step[4]


def test_wrapper_exposes_runtime_properties():
    kernel = EULSKernel(_environment())
    assert kernel.current_task is not None
    assert isinstance(kernel.current_slot, int)
    assert isinstance(kernel.queue_load, dict)


def test_boundary_contract_documentation_fields():
    contract = EULSBoundaryContract()
    assert "task arrival" in contract.owns
    assert "policy optimization" in contract.does_not_own
