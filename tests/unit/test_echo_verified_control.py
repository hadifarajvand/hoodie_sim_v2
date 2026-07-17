from __future__ import annotations

import math
import random

import pytest

from src.echo_verified.control import (
    RouteEstimate,
    WaitingTask,
    apply_deadline_drop_penalty,
    assert_task_conservation,
    build_effective_route_set,
    masked_double_dqn_target,
    masked_epsilon_greedy,
    observation_contains_ert,
    select_next_waiting_task,
)


def test_private_source_selection_uses_smallest_nonnegative_ert() -> None:
    result = select_next_waiting_task(
        (WaitingTask("fifo", 0, 10, 4), WaitingTask("urgent", 1, 5, 2)),
        current_slot=2,
    )
    assert result.selected is not None
    assert result.selected.task_id == "urgent"
    assert result.used_minimum_lateness is False


def test_all_late_queue_selection_uses_minimum_lateness() -> None:
    result = select_next_waiting_task(
        (WaitingTask("more_late", 0, 5, 5), WaitingTask("less_late", 1, 5, 2)),
        current_slot=5,
    )
    assert result.selected is not None
    assert result.selected.task_id == "less_late"
    assert result.used_minimum_lateness is True


def test_expired_waiting_tasks_are_removed_before_selection() -> None:
    result = select_next_waiting_task(
        (WaitingTask("expired", 0, 4, 1), WaitingTask("live", 1, 8, 1)),
        current_slot=5,
    )
    assert result.expired_task_ids == ("expired",)
    assert result.selected is not None
    assert result.selected.task_id == "live"


def test_route_filter_and_fallback() -> None:
    effective = build_effective_route_set(
        (
            RouteEstimate("local", 0, 9, 10),
            RouteEstimate("edge", 1, 11, 10),
            RouteEstimate("cloud", 2, 8, 10),
        )
    )
    assert effective.allowed_route_ids == ("local", "cloud")
    assert effective.mask == (True, False, True)
    assert effective.fallback_route_id is None

    fallback = build_effective_route_set(
        (
            RouteEstimate("local", 0, 7, 5),
            RouteEstimate("edge", 1, 6, 5),
            RouteEstimate("cloud", 2, 9, 5),
        )
    )
    assert fallback.allowed_route_ids == ("edge",)
    assert fallback.fallback_route_id == "edge"


def test_same_mask_is_used_for_all_learning_paths() -> None:
    q_values = (1.0, 100.0, 2.0)
    mask = (True, False, True)
    greedy = masked_epsilon_greedy(q_values, mask, epsilon=0.0, rng=random.Random(1))
    exploratory = masked_epsilon_greedy(q_values, mask, epsilon=1.0, rng=random.Random(2))
    target, selected = masked_double_dqn_target(
        reward=1.0,
        gamma=0.9,
        terminal=False,
        online_next_q=q_values,
        target_next_q=(3.0, 999.0, 4.0),
        next_mask=mask,
    )
    assert greedy == 2
    assert mask[exploratory]
    assert selected == 2
    assert math.isclose(target, 4.6)


def test_only_realized_drop_receives_one_fixed_penalty() -> None:
    assert apply_deadline_drop_penalty(-2.0, dropped=False, fixed_penalty=40.0) == -2.0
    assert apply_deadline_drop_penalty(-2.0, dropped=True, fixed_penalty=40.0) == -42.0
    with pytest.raises(ValueError):
        apply_deadline_drop_penalty(-2.0, dropped=True, fixed_penalty=-1.0)


def test_ert_is_not_in_inherited_neural_observation() -> None:
    inherited = (
        "task_size",
        "private_waiting_time",
        "outbound_waiting_time",
        "destination_queue_lengths",
        "predicted_node_loads",
    )
    assert observation_contains_ert(inherited) is False
    assert observation_contains_ert((*inherited, "local_ert")) is True


def test_task_conservation_is_fail_closed() -> None:
    assert_task_conservation(generated=4, successful=3, dropped=1)
    with pytest.raises(AssertionError):
        assert_task_conservation(generated=4, successful=2, dropped=1)
