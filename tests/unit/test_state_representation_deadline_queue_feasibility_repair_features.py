from __future__ import annotations

from src.analysis.state_representation_deadline_queue_feasibility_repair.config import LEGACY_STATE_REPRESENTATION_PROFILE, NEW_STATE_REPRESENTATION_PROFILE
from src.analysis.state_representation_deadline_queue_feasibility_repair.state_features import (
    LEGACY_STATE_FEATURE_NAMES,
    NEW_STATE_FEATURE_NAMES,
    STATE_FEATURE_GROUPS,
    build_profiled_state_vector,
    state_feature_group_coverage,
    state_feature_names,
)
from tests.unit.test_state_representation_deadline_queue_feasibility_repair_schema import FakeTask, make_state_feature_coverage_audit


def test_state_feature_groups_cover_deadline_queue_and_legal_availability() -> None:
    coverage = state_feature_group_coverage()
    assert coverage["minimal"]["covered"] is True
    assert coverage["deadline_timeout"]["covered"] is True
    assert coverage["action_path_feasibility"]["covered"] is True
    assert coverage["queue_pressure"]["covered"] is True
    assert coverage["legal_availability"]["covered"] is True
    assert coverage["source_context"]["covered"] is True
    assert coverage["optional_history"]["covered"] is False
    assert set(STATE_FEATURE_GROUPS) >= {"minimal", "deadline_timeout", "action_path_feasibility", "queue_pressure", "legal_availability", "source_context"}


def test_feature_name_profiles_include_expected_signals() -> None:
    assert state_feature_names(LEGACY_STATE_REPRESENTATION_PROFILE) == LEGACY_STATE_FEATURE_NAMES
    names = state_feature_names(NEW_STATE_REPRESENTATION_PROFILE)
    assert names == NEW_STATE_FEATURE_NAMES
    assert "deadline_slack_norm" in names
    assert "local_feasible_before_deadline" in names
    assert "legal_action_count_norm" in names


def test_profiled_state_vector_wraps_core_builder() -> None:
    task = FakeTask()
    observation = {
        "slot": 4,
        "queue_load": 3,
        "history_length": 1,
        "task_size": task.size,
        "processing_density": task.processing_density,
        "timeout_length": task.timeout_length,
        "absolute_deadline_slot": task.absolute_deadline_slot,
        "arrival_slot": task.arrival_slot,
        "source_agent_id": task.source_agent_id,
        "legal_action_mask": {"local": True, "horizontal": True, "vertical": False},
    }
    vector = build_profiled_state_vector(
        observation=observation,
        current_task=task,
        episode_length=110,
        state_representation_profile=NEW_STATE_REPRESENTATION_PROFILE,
    )
    assert len(vector) == 30
    assert vector[0] >= 0.0
    assert make_state_feature_coverage_audit()["state_feature_group_coverage"]["deadline_timeout"]["covered"] is True

