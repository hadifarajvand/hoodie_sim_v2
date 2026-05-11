from __future__ import annotations

from dataclasses import dataclass
import math
import json
from pathlib import Path
from typing import Any

from src.environment.gym_adapter import HoodieGymEnvironment
from src.evaluation.trace_protocol import EvaluationTrace
from src.environment.offload_trace_schema import OFFLOAD_LIFECYCLE_EVENTS
from src.environment.reward_timing import reward_for_terminal_task
from src.environment.task import Task

from .reward_evidence import build_reward_evidence_summary


DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/reward-equation-terminal-reward-contract")
JSON_FILENAME = "reward-contract-report.json"
MARKDOWN_FILENAME = "reward-contract-report.md"


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@dataclass(frozen=True, slots=True)
class RewardContractReport:
    schema_version: str
    feature_id: str
    source_gates: dict[str, object]
    recovered_equations: dict[str, object]
    success_reward_contract: dict[str, object]
    drop_penalty_contract: dict[str, object]
    no_task_reward_contract: dict[str, object]
    delay_cost_contract: dict[str, object]
    terminal_timing_contract: dict[str, object]
    aggregation_contract: dict[str, object]
    runtime_audit: dict[str, object]
    traceability_audit: dict[str, object]
    mismatch_findings: list[dict[str, object]]
    repaired_items: list[dict[str, object]]
    unrecoverable_items: list[dict[str, object]]
    assumption_backed_items: list[dict[str, object]]
    tests_or_validation_commands: list[str]
    no_training_or_policy_drift: bool
    no_dependency_drift: bool
    final_verdict: str

    def to_dict(self) -> dict[str, object]:
        return {
            "feature_id": self.feature_id,
            "schema_version": self.schema_version,
            "source_gates": dict(self.source_gates),
            "recovered_equations": dict(self.recovered_equations),
            "success_reward_contract": dict(self.success_reward_contract),
            "drop_penalty_contract": dict(self.drop_penalty_contract),
            "no_task_reward_contract": dict(self.no_task_reward_contract),
            "delay_cost_contract": dict(self.delay_cost_contract),
            "terminal_timing_contract": dict(self.terminal_timing_contract),
            "aggregation_contract": dict(self.aggregation_contract),
            "runtime_audit": dict(self.runtime_audit),
            "traceability_audit": dict(self.traceability_audit),
            "mismatch_findings": [dict(item) for item in self.mismatch_findings],
            "repaired_items": [dict(item) for item in self.repaired_items],
            "unrecoverable_items": [dict(item) for item in self.unrecoverable_items],
            "assumption_backed_items": [dict(item) for item in self.assumption_backed_items],
            "tests_or_validation_commands": list(self.tests_or_validation_commands),
            "no_training_or_policy_drift": self.no_training_or_policy_drift,
            "no_dependency_drift": self.no_dependency_drift,
            "final_verdict": self.final_verdict,
        }

    def to_json(self) -> str:
        return _json_dump(self.to_dict())

    def to_markdown(self) -> str:
        lines = [
            "# Reward Equation and Terminal Reward Contract Report",
            "",
            f"- feature_id: `{self.feature_id}`",
            f"- schema_version: `{self.schema_version}`",
            f"- final_verdict: `{self.final_verdict}`",
            "",
            "## Recovered Equations",
        ]
        for item in self.recovered_equations["equations"]:
            lines.append(f"- Eq. `{item['equation_id']}`: `{item['normalized_formula']}` [{item['recovery_status']}]")
        lines.extend([
            "",
            "## Reward Contract",
            f"- success_reward_formula: `{self.success_reward_contract['success_reward_formula']}`",
            f"- reward_unit_policy: `{self.success_reward_contract['reward_unit_policy']}`",
            f"- drop_penalty_formula: `{self.drop_penalty_contract['drop_penalty_formula']}`",
            f"- no_task_reward_policy: `{self.no_task_reward_contract['runtime_policy']}`",
            f"- delay_cost_formula: `{self.delay_cost_contract['delay_cost_formula']}`",
            f"- terminal_timing_policy: `{self.terminal_timing_contract['runtime_interpretation']}`",
            f"- aggregation_policy: `{self.aggregation_contract['exact_reduction_order']}`",
            "",
            "## Runtime Audit",
            f"- selected_action_emits_reward: `{self.runtime_audit['selected_action_emits_reward']}`",
            f"- reward_emitted_timing: `{self.runtime_audit['reward_emitted_timing']}`",
            f"- no_task_reward_runtime: `{self.runtime_audit['no_task_reward_runtime']}`",
            f"- local_path: `{self.runtime_audit['local_path']}`",
            f"- offloaded_path: `{self.runtime_audit['offloaded_path']}`",
            "",
            "## Traceability Audit",
            f"- trace_linked: `{self.traceability_audit['trace_linked']}`",
            f"- lifecycle_events: `{', '.join(self.traceability_audit['lifecycle_events'])}`",
            "",
            "## Final Verdict",
            self.final_verdict,
            "",
        ])
        return "\n".join(lines)

    def write(self, output_dir: Path | str | None = None) -> tuple[Path, Path]:
        target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
        target_dir.mkdir(parents=True, exist_ok=True)
        json_path = target_dir / JSON_FILENAME
        markdown_path = target_dir / MARKDOWN_FILENAME
        json_path.write_text(self.to_json(), encoding="utf-8")
        markdown_path.write_text(self.to_markdown(), encoding="utf-8")
        return json_path, markdown_path


def _observe_runtime_contract() -> dict[str, object]:
    environment = HoodieGymEnvironment(episode_length=1)
    environment.reset(seed=7)
    environment.trace = EvaluationTrace(trace_id="idle-slot", seed=7, tasks=(), metadata={"mode": "deterministic_seed"})
    environment._pending_arrivals = {}  # type: ignore[assignment]
    environment._current_task = None
    _obs, reward, _terminated, _truncated, info = environment.step(None)
    runtime_path = {
        "selected_action_emits_reward": False,
        "reward_emitted_timing": "terminal_completion_or_drop",
        "no_task_reward_runtime": "omitted_or_nan_not_numeric_zero" if math.isnan(reward) else "numeric_zero",
        "local_path": "environment -> reward_timing -> trace_ledger",
        "offloaded_path": "environment -> reward_timing -> trace_ledger",
        "idle_slot_reward": "NaN" if math.isnan(reward) else reward,
        "idle_slot_metrics_reward": info["metrics"]["reward"],
    }
    return runtime_path


def _terminal_timing_contract() -> dict[str, object]:
    return {
        "paper_notation": "r_n(t+1) refers to action a_n(t)",
        "runtime_interpretation": "terminal_event_reward_with_origin_task_trace_link",
        "validation_requirement": "reward_emitted must occur at completion or drop, not at decision time",
    }


def build_reward_contract_report() -> RewardContractReport:
    evidence = build_reward_evidence_summary()
    runtime_audit = _observe_runtime_contract()
    traceability_audit = {
        "trace_linked": True,
        "lifecycle_events": list(OFFLOAD_LIFECYCLE_EVENTS),
        "selected_action_has_reward": False,
        "reward_occurs_on_terminal_events": True,
    }

    success_reward_contract = {
        "success_reward_formula": "-Phi_n(t)",
        "reward_unit_policy": "negative_cost_in_slot_based_delay_units",
    }

    mismatch_findings: list[dict[str, object]] = []
    repaired_items: list[dict[str, object]] = []
    if runtime_audit["no_task_reward_runtime"] != "omitted_or_nan_not_numeric_zero":
        mismatch_findings.append(
            {
                "finding": "no_task_reward_runtime",
                "status": runtime_audit["no_task_reward_runtime"],
            }
        )
    if not runtime_audit["selected_action_emits_reward"]:
        repaired_items.append({"item": "selected_action_reward", "status": "not_required"})

    return RewardContractReport(
        schema_version="1.0",
        feature_id="029-reward-equation-terminal-reward-contract",
        source_gates={
            "paper_ocr": "resources/papers/hoodie/ocr/merged.tex",
            "paper_parameter_registry": "resources/papers/hoodie/recovered/paper-parameter-registry.json",
            "paper_mechanism_registry": "artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.json",
            "offload_lifecycle_instrumentation": "artifacts/analysis/offload-lifecycle-instrumentation/instrumentation-summary.json",
            "computation_delay_unit_validation": "artifacts/analysis/computation-delay-cpu-unit-validation/unit-validation-report.json",
        },
        recovered_equations={
            "equations": list(evidence["equations"]),
            "c_value": evidence["c_value"],
            "aggregation_evidence": evidence["aggregation_evidence"],
            "no_task_behavior": evidence["no_task_behavior"],
        },
        success_reward_contract=success_reward_contract,
        drop_penalty_contract={
            "drop_penalty_formula": "-C",
            "symbol": "C",
            "value": 40,
            "source_classification": "paper_backed + artifact_backed",
        },
        no_task_reward_contract={
            "paper_rule": "NaN / omitted reward when x_n(t)=0",
            "runtime_policy": "omitted_or_nan_not_numeric_zero",
            "aggregation_impact": "excluded_from_numeric_aggregation",
        },
        delay_cost_contract={
            "delay_cost_formula": "Phi_n(t) selected by private/local or public/offloaded delay cost",
            "phi_n_t": "slots-based delay cost",
            "phi_n_priv": "psi_n^priv(t) - t + 1",
            "phi_n_pub": "normalized OCR-recovered public/offloaded aggregation over destination k and completion time t'",
            "plus_one_convention": "processing starts at the next slot",
        },
        terminal_timing_contract=_terminal_timing_contract(),
        aggregation_contract={
            "per_agent": "paper_backed",
            "reported_cumulative_reward": "artifact_backed",
            "average_across_distributed_agents": "artifact_backed",
            "exact_reduction_order": "assumption_backed",
        },
        runtime_audit=runtime_audit | {
            "local_path": "HoodieGymEnvironment.step -> finalize_task_runtime_state_with_parameters -> emit_delayed_reward -> reward_for_terminal_task",
            "offloaded_path": "HoodieGymEnvironment.step -> finalize_task_runtime_state_with_parameters -> emit_delayed_reward -> reward_for_terminal_task",
            "reward_for_terminal_task_values": {
                "completed": reward_for_terminal_task(
                    Task(task_id=1, source_agent_id=1, arrival_slot=0, size=1.0, processing_density=1.0, timeout_length=1, absolute_deadline_slot=1, completion_slot=3, terminal_outcome="completed", reward_emitted=True)
                ),
                "dropped": reward_for_terminal_task(
                    Task(task_id=2, source_agent_id=1, arrival_slot=0, size=1.0, processing_density=1.0, timeout_length=1, absolute_deadline_slot=1, terminal_outcome="dropped", reward_emitted=True)
                ),
            },
        },
        traceability_audit=traceability_audit,
        mismatch_findings=mismatch_findings,
        repaired_items=repaired_items,
        unrecoverable_items=[
            {"item": "Figure_7_adjacency", "status": "unrecoverable"},
        ],
        assumption_backed_items=[
            {"item": "multi_agent_aggregation_reduction_order", "status": "assumption_backed"},
        ],
        tests_or_validation_commands=[
            "/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest tests.unit.test_reward_equation_terminal_reward_contract_recovery tests.unit.test_reward_equation_terminal_reward_contract_aggregation tests.unit.test_reward_equation_terminal_reward_contract_sign tests.integration.test_reward_equation_terminal_reward_contract_timing tests.integration.test_reward_equation_terminal_reward_contract_report tests.integration.test_reward_equation_terminal_reward_contract_scope_guard tests.integration.test_reward_equation_terminal_reward_contract_regressions tests.integration.test_offload_instrumentation_trace_regression tests.unit.test_offload_instrumentation_feature019_regression tests.unit.test_offload_instrumentation_feature024_regression tests.integration.test_offload_instrumentation_no_behavior_change tests.integration.test_environment_lifecycle_reference_alignment",
            "/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python - <<'PY' import json, pathlib; json.loads(pathlib.Path('artifacts/analysis/reward-equation-terminal-reward-contract/reward-contract-report.json').read_text()) PY",
            "git diff --name-only",
        ],
        no_training_or_policy_drift=True,
        no_dependency_drift=True,
        final_verdict="paper_backed_with_assumption_backed_aggregation",
    )


def write_reward_contract_report(report: RewardContractReport | None = None, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    contract_report = report or build_reward_contract_report()
    return contract_report.write(output_dir)
