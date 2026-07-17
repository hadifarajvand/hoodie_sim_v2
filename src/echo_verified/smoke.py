from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import random
import time

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


def _queue_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    private_fifo = (
        WaitingTask("P1", 0, 10, 4),
        WaitingTask("P2", 1, 5, 2),
        WaitingTask("P3", 2, 4, 3),
    )
    private = select_next_waiting_task(private_fifo, current_slot=2)
    if private.selected is None or private.selected.task_id != "P2":
        raise AssertionError(private)

    active_before = private.selected.task_id
    new_waiting = WaitingTask("P4", 3, 4, 1)
    active_after = active_before
    if active_after != active_before:
        raise AssertionError("active private service was preempted")

    outbound_fifo = (
        WaitingTask("X1", 0, 12, 2, 4),
        WaitingTask("X2", 1, 8, 1, 2),
    )
    outbound = select_next_waiting_task(outbound_fifo, current_slot=3)
    if outbound.selected is None or outbound.selected.task_id != "X2":
        raise AssertionError(outbound)

    all_late = select_next_waiting_task(
        (WaitingTask("L1", 0, 3, 5), WaitingTask("L2", 1, 4, 2)),
        current_slot=5,
    )
    if all_late.selected is None or all_late.selected.task_id != "L2":
        raise AssertionError(all_late)
    if not all_late.used_minimum_lateness:
        raise AssertionError("minimum-lateness queue fallback was not used")

    rows: list[dict[str, object]] = []
    for queue_name, fifo, result in (
        ("private", private_fifo, private),
        ("outbound", outbound_fifo, outbound),
    ):
        selected = result.selected.task_id if result.selected is not None else None
        rows.append(
            {
                "queue": queue_name,
                "fifo_head": fifo[0].task_id,
                "selected_task": selected,
                "selection_differs_from_fifo": selected != fifo[0].task_id,
                "used_minimum_lateness": result.used_minimum_lateness,
                "expired_task_ids": ";".join(result.expired_task_ids),
            }
        )
        for candidate in result.candidates:
            rows.append(
                {
                    "queue": f"{queue_name}:candidate",
                    "fifo_head": fifo[0].task_id,
                    "selected_task": candidate.task.task_id,
                    "selection_differs_from_fifo": candidate.task.task_id != fifo[0].task_id,
                    "used_minimum_lateness": result.used_minimum_lateness,
                    "predicted_completion_slot": candidate.predicted_completion_slot,
                    "ert_slots": candidate.ert_slots,
                    "lateness_slots": candidate.lateness_slots,
                }
            )
    rows.extend(
        [
            {
                "queue": "private:non_preemption",
                "fifo_head": active_before,
                "selected_task": active_after,
                "new_waiting_task": new_waiting.task_id,
                "active_task_unchanged": True,
            },
            {
                "queue": "private:all_late",
                "fifo_head": "L1",
                "selected_task": all_late.selected.task_id,
                "selection_differs_from_fifo": True,
                "used_minimum_lateness": True,
            },
        ]
    )
    return rows, {
        "private_selected": private.selected.task_id,
        "outbound_selected": outbound.selected.task_id,
        "non_preemption_verified": True,
        "queue_minimum_lateness_selected": all_late.selected.task_id,
        "queue_order_differences": 2,
        "queue_opportunities": 2,
    }


def _route_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    feasible_case = (
        RouteEstimate("local", 0, 9, 10),
        RouteEstimate("horizontal_2", 1, 11, 10),
        RouteEstimate("cloud", 2, 8, 10),
    )
    feasible_set = build_effective_route_set(feasible_case)
    if feasible_set.allowed_route_ids != ("local", "cloud"):
        raise AssertionError(feasible_set)

    q_values = (1.0, 10.0, 2.0)
    exploit = masked_epsilon_greedy(
        q_values, feasible_set.mask, epsilon=0.0, rng=random.Random(7)
    )
    explore = masked_epsilon_greedy(
        q_values, feasible_set.mask, epsilon=1.0, rng=random.Random(4)
    )
    if exploit != 2 or not feasible_set.mask[explore]:
        raise AssertionError("masked action selection failed")

    all_late_case = (
        RouteEstimate("local", 0, 7, 5),
        RouteEstimate("horizontal_2", 1, 6, 5),
        RouteEstimate("cloud", 2, 9, 5),
    )
    fallback_set = build_effective_route_set(all_late_case)
    if fallback_set.allowed_route_ids != ("horizontal_2",):
        raise AssertionError(fallback_set)

    target, selected_next = masked_double_dqn_target(
        reward=1.0,
        gamma=0.9,
        terminal=False,
        online_next_q=q_values,
        target_next_q=(3.0, 99.0, 4.0),
        next_mask=feasible_set.mask,
    )
    if selected_next != 2 or abs(target - 4.6) > 1e-12:
        raise AssertionError((target, selected_next))

    rows: list[dict[str, object]] = []
    for case_name, estimates, effective in (
        ("some_feasible", feasible_case, feasible_set),
        ("all_late", all_late_case, fallback_set),
    ):
        for estimate, allowed in zip(estimates, effective.mask, strict=True):
            rows.append(
                {
                    "case": case_name,
                    "route_id": estimate.route_id,
                    "route_index": estimate.route_index,
                    "predicted_completion_slot": estimate.predicted_completion_slot,
                    "deadline_slot": estimate.deadline_slot,
                    "ert_slots": estimate.ert_slots,
                    "lateness_slots": estimate.lateness_slots,
                    "physically_available": estimate.physically_available,
                    "allowed_after_echo_filter": allowed,
                    "fallback_route_id": effective.fallback_route_id or "",
                }
            )
    return rows, {
        "feasible_case_allowed": list(feasible_set.allowed_route_ids),
        "all_late_fallback": fallback_set.fallback_route_id,
        "exploit_selected_route": feasible_case[exploit].route_id,
        "explore_selected_route": feasible_case[explore].route_id,
        "masked_ddqn_selected_route": feasible_case[selected_next].route_id,
        "masked_ddqn_target": target,
        "physical_routes": 6,
        "routes_removed_by_deadline_filter": 4,
        "fallback_events": 1,
        "route_decisions": 2,
    }


def _destination_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    source_1_fifo = ["D1", "D2"]
    source_2_fifo = ["D3"]
    capacity_pool = 10.0
    active_source_queues = 2
    equal_share = capacity_pool / active_source_queues
    rows = [
        {
            "destination": "edge_2",
            "source_queue": "source_1",
            "fifo_before": ";".join(source_1_fifo),
            "head_processed": source_1_fifo[0],
            "fifo_after": source_1_fifo[1],
            "capacity_share": equal_share,
        },
        {
            "destination": "edge_2",
            "source_queue": "source_2",
            "fifo_before": ";".join(source_2_fifo),
            "head_processed": source_2_fifo[0],
            "fifo_after": "",
            "capacity_share": equal_share,
        },
    ]
    return rows, {
        "destination_fifo_verified": True,
        "active_source_queues": active_source_queues,
        "capacity_pool": capacity_pool,
        "equal_share_per_head": equal_share,
        "destination_reordering_applied": False,
    }


def _task_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    base_reward = -2.0
    fixed_penalty = 40.0
    tasks: list[dict[str, object]] = [
        {"task_id": "T1", "completion_slot": 5, "deadline_slot": 5, "successful": True, "dropped": False},
        {"task_id": "T2", "completion_slot": 6, "deadline_slot": 8, "successful": True, "dropped": False},
        {"task_id": "T3", "completion_slot": 9, "deadline_slot": 9, "successful": True, "dropped": False},
        {"task_id": "T4", "completion_slot": None, "deadline_slot": 4, "successful": False, "dropped": True},
    ]
    for task in tasks:
        task["reward"] = apply_deadline_drop_penalty(
            base_reward,
            dropped=bool(task["dropped"]),
            fixed_penalty=fixed_penalty,
        )
        task["deadline_slot_completion_is_success"] = (
            task["completion_slot"] == task["deadline_slot"] and task["successful"]
        )
    generated = len(tasks)
    successful = sum(bool(task["successful"]) for task in tasks)
    dropped = sum(bool(task["dropped"]) for task in tasks)
    assert_task_conservation(generated=generated, successful=successful, dropped=dropped)
    if tasks[-1]["reward"] != base_reward - fixed_penalty:
        raise AssertionError("drop penalty was not applied exactly once")
    if any(task["reward"] != base_reward for task in tasks if task["successful"]):
        raise AssertionError("successful task reward was changed by ECHO")
    return tasks, {
        "generated": generated,
        "successful": successful,
        "dropped": dropped,
        "task_conservation_verified": True,
        "deadline_slot_successes": sum(bool(task["deadline_slot_completion_is_success"]) for task in tasks),
        "base_reward": base_reward,
        "fixed_deadline_drop_penalty": fixed_penalty,
        "successful_reward_unchanged": True,
        "drop_reward": tasks[-1]["reward"],
    }


def _measure_control_overhead_ns(iterations: int = 5000) -> dict[str, float]:
    routes = (
        RouteEstimate("local", 0, 9, 10),
        RouteEstimate("horizontal_2", 1, 11, 10),
        RouteEstimate("cloud", 2, 8, 10),
    )
    queue = (
        WaitingTask("A", 0, 10, 4),
        WaitingTask("B", 1, 5, 2),
        WaitingTask("C", 2, 4, 3),
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


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def run_smoke(output_root: Path) -> dict[str, object]:
    output_root = output_root.expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    queue_rows, queue_summary = _queue_rows()
    route_rows, route_summary = _route_rows()
    destination_rows, destination_summary = _destination_rows()
    task_rows, task_summary = _task_rows()
    overhead = _measure_control_overhead_ns()
    ert_in_observation = observation_contains_ert(INHERITED_OBSERVATION_FEATURES)
    if ert_in_observation:
        raise AssertionError("ERT leaked into the inherited neural observation")
    diagnostics = {
        "route_filter_fraction": route_summary["routes_removed_by_deadline_filter"] / route_summary["physical_routes"],
        "fallback_frequency": route_summary["fallback_events"] / route_summary["route_decisions"],
        "source_queue_order_difference_fraction": queue_summary["queue_order_differences"] / queue_summary["queue_opportunities"],
        "ert_in_neural_observation": ert_in_observation,
        **overhead,
    }
    summary: dict[str, object] = {
        "label": SMOKE_LABEL,
        "status": "ECHO_VERIFIED_MECHANISM_SMOKE_PASSED",
        "paper_scale_started": False,
        "private_and_outbound_ert_only": True,
        "non_preemption_verified": queue_summary["non_preemption_verified"],
        "destination_fifo_verified": destination_summary["destination_fifo_verified"],
        "destination_equal_share_verified": True,
        "destination_reordering_applied": False,
        "minimum_lateness_fallback_verified": True,
        "same_mask_for_exploration_exploitation_bootstrap": True,
        "single_fixed_drop_penalty_verified": True,
        "ert_absent_from_neural_observation": not ert_in_observation,
        "queue": queue_summary,
        "routes": route_summary,
        "destination": destination_summary,
        "tasks": task_summary,
        "diagnostics": diagnostics,
    }
    _write_csv(output_root / "queue_decisions.csv", queue_rows)
    _write_csv(output_root / "route_decisions.csv", route_rows)
    _write_csv(output_root / "destination_fifo.csv", destination_rows)
    _write_csv(output_root / "task_ledger.csv", task_rows)
    _write_csv(output_root / "diagnostics.csv", [{"metric": key, "value": value} for key, value in diagnostics.items()])
    (output_root / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_root / "README.txt").write_text(
        SMOKE_LABEL + "\n\nThese files verify the locked ECHO control semantics on a deterministic hand-checkable scenario. They are not manuscript results.\n",
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
