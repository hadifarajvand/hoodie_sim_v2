from __future__ import annotations

from src.analysis.state_representation_deadline_queue_feasibility_repair.config import NEW_STATE_REPRESENTATION_PROFILE
from src.analysis.full_training_reproduction_campaign.replay import build_state_window, build_state_window_tensor, build_state_vector
from tests.unit.test_state_representation_deadline_queue_feasibility_repair_schema import FakeTask


def test_state_vector_is_finite_and_bounded() -> None:
    task = FakeTask()
    observation = {
        "slot": 7,
        "queue_load": 5,
        "history_length": 2,
        "task_size": task.size,
        "processing_density": task.processing_density,
        "timeout_length": task.timeout_length,
        "absolute_deadline_slot": task.absolute_deadline_slot,
        "arrival_slot": task.arrival_slot,
        "source_agent_id": task.source_agent_id,
        "legal_action_mask": {"local": True, "horizontal": False, "vertical": True},
    }
    vector = build_state_vector(
        observation=observation,
        current_task=task,
        episode_length=110,
        state_representation_profile=NEW_STATE_REPRESENTATION_PROFILE,
    )
    assert len(vector) == 30
    assert all(value == value for value in vector)
    assert all(-1.0 <= float(value) <= 1.0 for value in vector)


def test_state_window_padding_matches_profile_dimension() -> None:
    task = FakeTask()
    observation = {
        "slot": 1,
        "queue_load": 0,
        "history_length": 0,
        "task_size": task.size,
        "processing_density": task.processing_density,
        "timeout_length": task.timeout_length,
        "absolute_deadline_slot": task.absolute_deadline_slot,
        "arrival_slot": task.arrival_slot,
        "source_agent_id": task.source_agent_id,
        "legal_action_mask": {"local": True, "horizontal": False, "vertical": False},
    }
    row = build_state_vector(
        observation=observation,
        current_task=task,
        episode_length=110,
        state_representation_profile=NEW_STATE_REPRESENTATION_PROFILE,
    )
    window = build_state_window([row], state_representation_profile=NEW_STATE_REPRESENTATION_PROFILE)
    tensor = build_state_window_tensor(window)
    assert len(window) == 10
    assert tensor.shape == (10, 30)

