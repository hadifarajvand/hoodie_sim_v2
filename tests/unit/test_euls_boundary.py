from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.euls.boundary import EULSBoundaryContract
from src.euls.kernel import EULSKernel
from src.environment.gym_adapter import HoodieGymEnvironment


def _environment() -> HoodieGymEnvironment:
    return HoodieGymEnvironment(episode_length=2)


def test_kernel_wraps_environment():
    env = _environment()
    kernel = EULSKernel(env)
    assert kernel.environment is env


def test_reset_delegates_and_returns_same_shape():
    env = _environment()
    kernel = EULSKernel(env)
    env_observation, env_info = env.reset(seed=7)
    kernel_observation, kernel_info = kernel.reset(seed=7)
    assert type(kernel_observation) is type(env_observation)
    assert type(kernel_info) is type(env_info)


def test_step_delegates_standard_tuple():
    env = _environment()
    kernel = EULSKernel(_environment())
    env.reset(seed=3)
    kernel.reset(seed=3)
    env_obs, env_reward, env_terminated, env_truncated, env_info = env.step("local")
    ker_obs, ker_reward, ker_terminated, ker_truncated, ker_info = kernel.step("local")
    assert type(ker_obs) is type(env_obs)
    assert ker_reward == env_reward
    assert ker_terminated == env_terminated
    assert ker_truncated == env_truncated
    assert type(ker_info) is type(env_info)


def test_same_seed_same_actions_match_environment():
    env_a = _environment()
    env_b = _environment()
    kernel = EULSKernel(env_a)
    direct_reset = env_b.reset(seed=11)
    wrapped_reset = kernel.reset(seed=11)
    assert type(direct_reset[0]) is type(wrapped_reset[0])
    assert type(direct_reset[1]) is type(wrapped_reset[1])
    direct_step = env_b.step("local")
    wrapped_step = kernel.step("local")
    assert direct_step[1] == wrapped_step[1]
    assert direct_step[2] == wrapped_step[2]
    assert direct_step[3] == wrapped_step[3]


def test_wrapper_exposes_runtime_properties():
    kernel = EULSKernel(_environment())
    assert kernel.current_task is None
    assert isinstance(kernel.current_slot, int)
    assert isinstance(kernel.queue_load, int)


def test_boundary_contract_documentation_fields():
    contract = EULSBoundaryContract()
    assert "task arrival" in contract.owns
    assert "policy optimization" in contract.does_not_own
