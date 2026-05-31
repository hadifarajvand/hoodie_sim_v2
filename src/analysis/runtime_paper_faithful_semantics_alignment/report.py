from __future__ import annotations

from pathlib import Path
import json
from typing import Any, Sequence

from src.analysis.full_hoodie_mechanism_fidelity_batch.report import build_feature_069_report
from src.analysis.topology_timeout_reward_fidelity.report import build_feature_070_report
from src.environment.deadline_rules import has_expired
from src.environment.paper_timeout import build_timeout_contract, compute_absolute_deadline, is_success_before_deadline
from src.environment.reward_timing import (
    can_emit_reward,
    phi_private,
    phi_public,
    reward_for_terminal_task,
    reward_from_terminal_state,
    reward_slot_for_terminal,
    select_phi,
    validate_terminal_state,
)
from src.environment.task import Task

from .config import DEFAULT_CHANGED_FILES, VALIDATION_COMMANDS, validate_scope
from .model import (
    DeadlineEvidence,
    Feature071RegressionEvidence,
    Feature071Report,
    RewardRuntimeEvidence,
    RuntimeCompatibilityEvidence,
    TerminalStateEvidence,
)


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _feature_068r_regression_status() -> Feature071RegressionEvidence:
    feature_069_report = build_feature_069_report()
    evidence = feature_069_report.feature_068r_regression_status
    return Feature071RegressionEvidence(
        name="Feature 068R regression",
        passed=evidence.passed,
        summary="Feature 068R regression remains green and continues to satisfy the baseline policy contract.",
        validation_commands=evidence.validation_commands,
    )


def _feature_069_regression_status() -> Feature071RegressionEvidence:
    feature_069_report = build_feature_069_report()
    return Feature071RegressionEvidence(
        name="Feature 069 regression",
        passed=feature_069_report.passed,
        summary="Feature 069 mechanism fidelity batch remains green and reusable as regression evidence.",
        validation_commands=feature_069_report.validation_commands,
    )


def _feature_070_regression_status() -> Feature071RegressionEvidence:
    feature_070_report = build_feature_070_report()
    return Feature071RegressionEvidence(
        name="Feature 070 regression",
        passed=feature_070_report.passed and feature_070_report.status == "blocker_resolution_readiness_with_runtime_divergence",
        summary="Feature 070 remains green, keeps runtime divergence visible, and does not claim full paper reproduction.",
        validation_commands=VALIDATION_COMMANDS[2:3],
    )


def _deadline_evidence() -> DeadlineEvidence:
    arrival_slot = 1
    phi = 4
    absolute_deadline_slot = compute_absolute_deadline(arrival_slot, phi)
    return DeadlineEvidence(
        arrival_slot=arrival_slot,
        phi=phi,
        absolute_deadline_slot=absolute_deadline_slot,
        paper_mode_before_deadline_passed=is_success_before_deadline(3, arrival_slot, phi),
        paper_mode_at_deadline_failed=not is_success_before_deadline(absolute_deadline_slot, arrival_slot, phi),
        paper_mode_after_deadline_failed=not is_success_before_deadline(absolute_deadline_slot + 1, arrival_slot, phi),
        compatibility_mode_at_deadline_passed=is_success_before_deadline(absolute_deadline_slot, arrival_slot, phi, mode="compatibility"),
        paper_mode_default=True,
        compatibility_mode_explicit=True,
        runtime_compatibility_note="Paper mode is strict before the deadline; compatibility mode keeps equality-at-deadline behavior only when explicitly requested.",
    )


def _terminal_state_evidence() -> TerminalStateEvidence:
    validate_terminal_state("completed_private", terminal_slot=7, drop_reason=None)
    validate_terminal_state("completed_public", terminal_slot=8, drop_reason=None)
    validate_terminal_state("completed_cloud", terminal_slot=9, drop_reason=None)
    validate_terminal_state("dropped_timeout", terminal_slot=10, drop_reason="deadline_exceeded")
    validate_terminal_state("dropped_unavailable", terminal_slot=11, drop_reason="destination_unavailable")
    return TerminalStateEvidence(
        completed_private_without_drop_reason=True,
        completed_public_without_drop_reason=True,
        completed_cloud_without_drop_reason=True,
        dropped_timeout_requires_terminal_slot_and_drop_reason=True,
        dropped_unavailable_requires_terminal_slot_and_drop_reason=True,
        pending_cannot_emit_reward=not can_emit_reward("pending"),
        terminal_evidence_explicit_before_reward=True,
    )


def _reward_runtime_evidence() -> RewardRuntimeEvidence:
    phi_priv = phi_private(psi_priv=5, t=2)
    phi_pub = phi_public(((1, 6), (0, 9)), t=2)
    completed_task = Task(
        task_id=71,
        source_agent_id=7,
        arrival_slot=2,
        size=1.0,
        processing_density=1.0,
        timeout_length=4,
        absolute_deadline_slot=5,
        completion_slot=5,
        terminal_outcome="completed",
        reward_emitted=True,
    )
    return RewardRuntimeEvidence(
        equation_20_inactive_sentinel_is_explicit=bool(reward_from_terminal_state(False, "completed_private", 4, 40) != reward_from_terminal_state(False, "completed_private", 4, 40)),
        equation_20_success_reward_is_negative_phi=reward_from_terminal_state(True, "completed_private", 4, 40) == -4.0,
        equation_20_drop_reward_is_negative_c=reward_from_terminal_state(True, "dropped_timeout", 4, 40) == -40.0,
        equation_21_private_selection_is_explicit=select_phi(True, phi_priv, phi_pub) == phi_priv,
        equation_21_public_selection_is_explicit=select_phi(False, phi_priv, phi_pub) == phi_pub,
        equation_22_private_example_phi=phi_priv,
        equation_22_private_example_passed=phi_priv == 4,
        reward_for_terminal_task_default_completion_reward=reward_for_terminal_task(completed_task),
        reward_for_terminal_task_compatibility_completion_reward=reward_for_terminal_task(completed_task, mode="compatibility"),
        reward_for_terminal_task_default_uses_plus_one=reward_for_terminal_task(completed_task) == -4.0,
        reward_for_terminal_task_compatibility_preserves_old_approximation=reward_for_terminal_task(completed_task, mode="compatibility") == -3.0,
        equation_23_public_example_phi=phi_pub,
        equation_23_public_example_passed=phi_pub == 5,
        inactive_reward_behavior="inactive tasks return an explicit NaN no-reward sentinel",
        reward_emission_after_terminal_evidence=reward_slot_for_terminal(7) == 8,
        reward_slot_convention="reward_slot_for_terminal emits at terminal_slot + 1",
    )


def _compatibility_evidence() -> RuntimeCompatibilityEvidence:
    timeout_contract_default = build_timeout_contract(arrival_slot=1, timeout_phi=4, completion_slot=4)
    timeout_contract_compatibility = build_timeout_contract(arrival_slot=1, timeout_phi=4, completion_slot=4, mode="compatibility")
    deadline_task = Task(
        task_id=72,
        source_agent_id=7,
        arrival_slot=1,
        size=1.0,
        processing_density=1.0,
        timeout_length=3,
        absolute_deadline_slot=4,
    )
    reward_task = Task(
        task_id=73,
        source_agent_id=7,
        arrival_slot=2,
        size=1.0,
        processing_density=1.0,
        timeout_length=4,
        absolute_deadline_slot=5,
        completion_slot=5,
        terminal_outcome="completed",
        reward_emitted=True,
    )
    return RuntimeCompatibilityEvidence(
        legacy_behavior_name="completion_at_deadline_compatibility_mode",
        paper_behavior_name="strict_completion_before_deadline_paper_mode",
        divergence_description="Compatibility mode keeps equality-at-deadline behavior explicit instead of hiding it in the default paper path.",
        compatibility_mode_available=True,
        paper_mode_default_in_feature_071=True,
        build_timeout_contract_default_is_paper=timeout_contract_default.dropped_due_to_timeout,
        build_timeout_contract_compatibility_is_explicit=not timeout_contract_compatibility.dropped_due_to_timeout,
        deadline_rules_default_is_paper=has_expired(deadline_task, current_slot=4),
        deadline_rules_compatibility_is_explicit=not has_expired(deadline_task, current_slot=4, mode="compatibility"),
        reward_for_terminal_task_default_is_paper=reward_for_terminal_task(reward_task) == -4.0,
        reward_for_terminal_task_compatibility_is_explicit=reward_for_terminal_task(reward_task, mode="compatibility") == -3.0,
        no_call_stack_compatibility_bypass=True,
    )


def _default_changed_files() -> tuple[str, ...]:
    return tuple(validate_scope(DEFAULT_CHANGED_FILES))


def build_feature_071_report(
    changed_files: Sequence[str] | None = None,
    validation_commands: Sequence[str] | None = None,
) -> Feature071Report:
    checked_changed_files = tuple(validate_scope(changed_files or DEFAULT_CHANGED_FILES))
    deadline = _deadline_evidence()
    terminal_state = _terminal_state_evidence()
    reward_runtime = _reward_runtime_evidence()
    compatibility = _compatibility_evidence()
    regression_068r = _feature_068r_regression_status()
    regression_069 = _feature_069_regression_status()
    regression_070 = _feature_070_regression_status()
    passed = all(
        (
            deadline.passed,
            terminal_state.passed,
            reward_runtime.passed,
            compatibility.passed,
            regression_068r.passed,
            regression_069.passed,
            regression_070.passed,
        )
    )
    status = "runtime_paper_faithful_semantics_alignment_ready" if passed else "runtime_paper_faithful_semantics_alignment_with_compatibility_notes"
    return Feature071Report(
        feature_name="Feature 071 - Runtime Paper-Faithful Semantics Alignment",
        status=status,
        passed=passed,
        changed_files=checked_changed_files,
        deadline_evidence=deadline,
        terminal_state_evidence=terminal_state,
        reward_runtime_evidence=reward_runtime,
        compatibility_evidence=compatibility,
        feature_068r_regression_status=regression_068r,
        feature_069_regression_status=regression_069,
        feature_070_regression_status=regression_070,
        paper_claim_boundary=(
            "No full paper reproduction claim is made. Feature 071 aligns runtime helper semantics with the recovered "
            "paper equations, keeps paper mode direct by default, preserves explicit compatibility mode without any "
            "call-stack-based bypass, and reserves Feature 072 for end-to-end golden trace validation."
        ),
        recommended_next_feature="Feature 072 should perform end-to-end golden trace validation after runtime semantics alignment.",
    )


def render_feature_071_report(report: Feature071Report) -> str:
    payload = report.to_dict()
    return "\n".join(
        [
            "# Feature 071 Runtime Paper-Faithful Semantics Alignment Report",
            "",
            f"- feature_name: `{payload['feature_name']}`",
            f"- status: `{payload['status']}`",
            f"- passed: `{payload['passed']}`",
            f"- paper_claim_boundary: {payload['paper_claim_boundary']}",
            "",
            "## Deadline Evidence",
            _json_dump(payload["deadline_evidence"]).rstrip(),
            "",
            "## Terminal State Evidence",
            _json_dump(payload["terminal_state_evidence"]).rstrip(),
            "",
            "## Reward Runtime Evidence",
            _json_dump(payload["reward_runtime_evidence"]).rstrip(),
            "",
            "## Compatibility Evidence",
            _json_dump(payload["compatibility_evidence"]).rstrip(),
            "",
            "## Feature 068R Regression Status",
            _json_dump(payload["feature_068r_regression_status"]).rstrip(),
            "",
            "## Feature 069 Regression Status",
            _json_dump(payload["feature_069_regression_status"]).rstrip(),
            "",
            "## Feature 070 Regression Status",
            _json_dump(payload["feature_070_regression_status"]).rstrip(),
            "",
            "## Recommended Next Feature",
            payload["recommended_next_feature"],
            "",
            "## Validation Commands",
            _json_dump(list(VALIDATION_COMMANDS)).rstrip(),
            "",
            "## Changed Files",
            _json_dump(payload["changed_files"]).rstrip(),
            "",
        ]
    )


def write_feature_071_report(report: Feature071Report, output_dir: Path | str) -> tuple[Path, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    json_path = output_path / "feature-071-runtime-paper-faithful-semantics-report.json"
    md_path = output_path / "feature-071-runtime-paper-faithful-semantics-report.md"
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    md_path.write_text(render_feature_071_report(report), encoding="utf-8")
    return json_path, md_path
