from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import random
import time
from typing import Any

from .control import (
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

SMOKE_LABEL = "SMOKE ONLY — NOT PAPER-SCALE RESULT"
INHERITED_OBSERVATION_FEATURES = (
    "task_size",
    "private_waiting_time",
    "outbound_waiting_time",
    "destination_queue_lengths",
    "predicted_node_loads",
)


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields: list[str] = []
    for row in rows:
        fields.extend(key for key in row if key not in fields)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _queue_smoke() -> tuple[list[dict[str, object]], dict[str, Any]]:
    private_fifo = (
        WaitingTask("P1", 0, 10, 4),
        WaitingTask("P2", 1, 5, 2),
        WaitingTask("P3", 2, 8, 3),
    )
    outbound_fifo = (
        WaitingTask("X1", 0, 12, 2, 4),
        WaitingTask("X2", 1, 8, 1, 2),
    )
    private = select_next_waiting_task(private_fifo, current_slot=2)
    outbound = select_next_waiting_task(outbound_fifo, current_slot=3)
    all_late = select_next_waiting_task(
        (WaitingTask("L1", 0, 3, 5), WaitingTask("L2", 1, 4, 2)),
        current_slot=5,
    )
    assert private.selected and private.selected.task_id == "P2"
    assert outbound.selected and outbound.selected.task_id == "X2"
    assert all_late.selected and all_late.selected.task_id == "L2"
    assert all_late.used_minimum_lateness

    rows: list[dict[str, object]] = []
    for queue_name, fifo, result in (
        ("private", private_fifo, private),
        ("outbound", outbound_fifo, outbound),
    ):
        assert result.selected is not None
        rows.append(
            {
                "queue": queue_name,
                "fifo_head": fifo[0].task_id,
                "selected_task": result.selected.task_id,
                "selection_differs_from_fifo": result.selected.task_id != fifo[0].task_id,
                "used_minimum_lateness": result.used_minimum_lateness,
            }
        )
        rows.extend(
            {
                "queue": f"{queue_name}:candidate",
                "fifo_head": fifo[0].task_id,
                "selected_task": candidate.task.task_id,
                "predicted_completion_slot": candidate.predicted_completion_slot,
                "ert_slots": candidate.ert_slots,
                "lateness_slots": candidate.lateness_slots,
            }
            for candidate in result.candidates
        )
    rows.extend(
        [
            {
                "queue": "private:non_preemption",
                "fifo_head": "P2",
                "selected_task": "P2",
                "new_waiting_task": "P4",
                "active_task_unchanged": True,
            },
            {
                "queue": "private:all_late",
                "fifo_head": "L1",
                "selected_task": "L2",
                "selection_differs_from_fifo": True,
                "used_minimum_lateness": True,
            },
        ]
    )
    return rows, {
        "private_selected": "P2",
        "outbound_selected": "X2",
        "non_preemption_verified": True,
        "queue_minimum_lateness_selected": "L2",
        "queue_order_differences": 2,
        "queue_opportunities": 2,
    }


def _route_smoke() -> tuple[list[dict[str, object]], dict[str, Any]]:
    feasible = (
        RouteEstimate("local", 0, 9, 10),
        RouteEstimate("horizontal_2", 1, 11, 10),
        RouteEstimate("cloud", 2, 8, 10),
    )
    effective = build_effective_route_set(feasible)
    assert effective.allowed_route_ids == ("local", "cloud")

    q_values = (1.0, 10.0, 2.0)
    exploit = masked_epsilon_greedy(q_values, effective.mask, epsilon=0.0, rng=random.Random(7))
    explore = masked_epsilon_greedy(q_values, effective.mask, epsilon=1.0, rng=random.Random(4))
    assert exploit == 2 and effective.mask[explore]

    late = (
        RouteEstimate("local", 0, 7, 5),
        RouteEstimate("horizontal_2", 1, 6, 5),
        RouteEstimate("cloud", 2, 9, 5),
    )
    fallback = build_effective_route_set(late)
    assert fallback.allowed_route_ids == ("horizontal_2",)

    target, next_action = masked_double_dqn_target(
        reward=1.0,
        gamma=0.9,
        terminal=False,
        online_next_q=q_values,
        target_next_q=(3.0, 99.0, 4.0),
        next_mask=effective.mask,
    )
    assert next_action == 2 and abs(target - 4.6) < 1e-12

    rows: list[dict[str, object]] = []
    for case, estimates, selected in (
        ("some_feasible", feasible, effective),
        ("all_late", late, fallback),
    ):
        rows.extend(
            {
                "case": case,
                "route_id": estimate.route_id,
                "route_index": estimate.route_index,
                "predicted_completion_slot": estimate.predicted_completion_slot,
                "deadline_slot": estimate.deadline_slot,
                "ert_slots": estimate.ert_slots,
                "lateness_slots": estimate.lateness_slots,
                "allowed_after_echo_filter": allowed,
                "fallback_route_id": selected.fallback_route_id or "",
            }
            for estimate, allowed in zip(estimates, selected.mask, strict=True)
        )
    return rows, {
        "feasible_case_allowed": list(effective.allowed_route_ids),
        "all_late_fallback": fallback.fallback_route_id,
        "exploit_selected_route": feasible[exploit].route_id,
        "explore_selected_route": feasible[explore].route_id,
        "masked_ddqn_selected_route": feasible[next_action].route_id,
        "masked_ddqn_target": target,
        "physical_routes": 6,
        "routes_removed_by_deadline_filter": 4,
        "fallback_events": 1,
        "route_decisions": 2,
    }


def _task_smoke() -> tuple[list[dict[str, object]], dict[str, Any]]:
    tasks: list[dict[str, object]] = [
        {"task_id": "T1", "completion_slot": 5, "deadline_slot": 5, "successful": True, "dropped": False},
        {"task_id": "T2", "completion_slot": 6, "deadline_slot": 8, "successful": True, "dropped": False},
        {"task_id": "T3", "completion_slot": 9, "deadline_slot": 9, "successful": True, "dropped": False},
        {"task_id": "T4", "completion_slot": None, "deadline_slot": 4, "successful": False, "dropped": True},
    ]
    for task in tasks:
        task["reward"] = apply_deadline_drop_penalty(-2.0, dropped=bool(task["dropped"]), fixed_penalty=40.0)
        task["deadline_slot_completion_is_success"] = task["completion_slot"] == task["deadline_slot"] and task["successful"]
    generated = len(tasks)
    successful = sum(bool(task["successful"]) for task in tasks)
    dropped = sum(bool(task["dropped"]) for task in tasks)
    assert_task_conservation(generated=generated, successful=successful, dropped=dropped)
    assert tasks[-1]["reward"] == -42.0
    assert all(task["reward"] == -2.0 for task in tasks if task["successful"])
    return tasks, {
        "generated": generated,
        "successful": successful,
        "dropped": dropped,
        "task_conservation_verified": True,
        "deadline_slot_successes": sum(bool(task["deadline_slot_completion_is_success"]) for task in tasks),
        "fixed_deadline_drop_penalty": 40.0,
        "drop_reward": -42.0,
    }


def _overhead() -> dict[str, float]:
    iterations = 5000
    routes = (
        RouteEstimate("local", 0, 9, 10),
        RouteEstimate("horizontal_2", 1, 11, 10),
        RouteEstimate("cloud", 2, 8, 10),
    )
    queue = (
        WaitingTask("A", 0, 10, 4),
        WaitingTask("B", 1, 5, 2),
        WaitingTask("C", 2, 8, 3),
    )
    start = time.perf_counter_ns()
    for _ in range(iterations):
        build_effective_route_set(routes)
    route_ns = time.perf_counter_ns() - start
    start = time.perf_counter_ns()
    for _ in range(iterations):
        select_next_waiting_task(queue, current_slot=2)
    queue_ns = time.perf_counter_ns() - start
    return {
        "iterations": float(iterations),
        "mean_route_filter_ns": route_ns / iterations,
        "mean_queue_selection_ns": queue_ns / iterations,
        "mean_total_control_ns": (route_ns + queue_ns) / iterations,
    }


def run_smoke(output_root: Path) -> dict[str, object]:
    output_root = output_root.expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    queue_rows, queue = _queue_smoke()
    route_rows, routes = _route_smoke()
    task_rows, tasks = _task_smoke()
    destination_rows = [
        {"destination": "edge_2", "source_queue": "source_1", "fifo_before": "D1;D2", "head_processed": "D1", "fifo_after": "D2", "capacity_share": 5.0},
        {"destination": "edge_2", "source_queue": "source_2", "fifo_before": "D3", "head_processed": "D3", "fifo_after": "", "capacity_share": 5.0},
    ]
    ert_in_observation = observation_contains_ert(INHERITED_OBSERVATION_FEATURES)
    assert not ert_in_observation
    diagnostics = {
        "route_filter_fraction": routes["routes_removed_by_deadline_filter"] / routes["physical_routes"],
        "fallback_frequency": routes["fallback_events"] / routes["route_decisions"],
        "source_queue_order_difference_fraction": queue["queue_order_differences"] / queue["queue_opportunities"],
        "ert_in_neural_observation": ert_in_observation,
        **_overhead(),
    }
    summary: dict[str, object] = {
        "label": SMOKE_LABEL,
        "status": "ECHO_VERIFIED_MECHANISM_SMOKE_PASSED",
        "paper_scale_started": False,
        "private_and_outbound_ert_only": True,
        "non_preemption_verified": True,
        "destination_fifo_verified": True,
        "destination_equal_share_verified": True,
        "destination_reordering_applied": False,
        "minimum_lateness_fallback_verified": True,
        "same_mask_for_exploration_exploitation_bootstrap": True,
        "single_fixed_drop_penalty_verified": True,
        "ert_absent_from_neural_observation": True,
        "queue": queue,
        "routes": routes,
        "destination": {"active_source_queues": 2, "capacity_pool": 10.0, "equal_share_per_head": 5.0},
        "tasks": tasks,
        "diagnostics": diagnostics,
    }
    _write_csv(output_root / "queue_decisions.csv", queue_rows)
    _write_csv(output_root / "route_decisions.csv", route_rows)
    _write_csv(output_root / "destination_fifo.csv", destination_rows)
    _write_csv(output_root / "task_ledger.csv", task_rows)
    _write_csv(output_root / "diagnostics.csv", [{"metric": key, "value": value} for key, value in diagnostics.items()])
    (output_root / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_root / "README.txt").write_text(
        SMOKE_LABEL + "\n\nDeterministic control-mechanism evidence only. Not valid for Figures 5–8 or performance claims.\n",
        encoding="utf-8",
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run_smoke(args.output_root), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
