from __future__ import annotations

from src.echo_verified.kernel import (
    PairedPhysicalKernel,
    PilotKernelConfig,
    TaskBlueprint,
    assert_echo_disabled_equivalence,
    generate_trace,
)


def test_echo_disabled_is_identical_to_hoodie() -> None:
    config = PilotKernelConfig(decision_slots=18, drain_slots=20)
    blueprints = generate_trace(
        seed=19,
        episode_index=2,
        scenario="equivalence",
        config=config,
        arrival_probability=0.7,
        timeout_slots=10,
    )
    hoodie = PairedPhysicalKernel(
        method="HOODIE",
        trace_id="equivalence",
        seed=19,
        scenario="equivalence",
        blueprints=blueprints,
        config=config,
    ).run()
    disabled = PairedPhysicalKernel(
        method="ECHO_DISABLED",
        trace_id="equivalence",
        seed=19,
        scenario="equivalence",
        blueprints=blueprints,
        config=config,
    ).run()
    assert_echo_disabled_equivalence(hoodie, disabled)


def test_deadline_slot_completion_is_success_and_counts_conserve() -> None:
    config = PilotKernelConfig(decision_slots=2, drain_slots=3)
    blueprint = TaskBlueprint(
        task_id="boundary",
        source_id=0,
        arrival_slot=0,
        deadline_slot=0,
        size_mbits=1.0,
        q_values=(3.0, 2.0, 1.0),
    )
    result = PairedPhysicalKernel(
        method="HOODIE",
        trace_id="deadline-boundary",
        seed=1,
        scenario="boundary",
        blueprints=(blueprint,),
        config=config,
    ).run()
    assert result.metrics["generated"] == 1
    assert result.metrics["successful"] == 1
    assert result.metrics["dropped"] == 0
    assert result.tasks[0]["completion_slot"] == 0


def test_tight_high_load_exercises_echo_filter_without_fabricated_oracle() -> None:
    config = PilotKernelConfig(decision_slots=30, drain_slots=20)
    blueprints = generate_trace(
        seed=101,
        episode_index=0,
        scenario="high_tight",
        config=config,
        arrival_probability=0.8,
        timeout_slots=8,
    )
    result = PairedPhysicalKernel(
        method="ECHO",
        trace_id="high-tight",
        seed=101,
        scenario="high_tight",
        blueprints=blueprints,
        config=config,
    ).run()
    assert result.metrics["generated"] == (
        result.metrics["successful"] + result.metrics["dropped"]
    )
    assert float(result.diagnostics["route_filter_fraction"]) > 0.0
    assert result.diagnostics["ert_in_neural_observation"] is False
    assert result.diagnostics["destination_queue_order"] == "FIFO"
    assert result.diagnostics["active_service_preemption"] is False
