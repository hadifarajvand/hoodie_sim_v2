from __future__ import annotations

from pathlib import Path
import argparse
import json
import subprocess
from typing import Any

from .config import (
    COMMITTED_INPUT_REPORTS,
    DEPENDENCY_FILE_NAMES,
    EXPECTED_FEATURE_IDS,
    FEATURE_053_PREREQUISITE_TAG,
    FEATURE_054A_PREREQUISITE_TAG,
    FEATURE_038_REPORT,
    FEATURE_040_REPORT,
    FEATURE_041_REPORT,
    FEATURE_042_REPORT,
    FEATURE_ID,
    READY_NEXT_FEATURE,
    TrainingReadinessContractConfig,
)
from .model import BehaviorEquivalenceSummary, TrainingReadinessContractReport
from .report import write_training_readiness_contract_report

BLOCKED_NEXT_FEATURES = {
    "evidence_chain_prerequisite_blocked": "prerequisite evidence repair before training",
    "paper_default_config_contract_blocked": "paper-default config contract repair before training",
    "observation_contract_blocked": "observation contract repair before training",
    "action_or_legality_contract_blocked": "action legality contract repair before training",
    "reward_timeout_capacity_contract_blocked": "runtime contract repair before training",
    "metric_or_artifact_contract_blocked": "metric artifact contract repair before training",
    "behavior_drift_detected": "repair drift before training",
}


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_output(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _git_bool(*args: str) -> bool:
    return subprocess.run(["git", *args], check=False, capture_output=True, text=True).returncode == 0


def _load_committed_inputs(config: TrainingReadinessContractConfig) -> dict[str, dict[str, Any]]:
    payloads = {
        "048": _load_json(config.feature_048_report),
        "049": _load_json(config.feature_049_report),
        "050": _load_json(config.feature_050_report),
        "051": _load_json(config.feature_051_report),
        "052": _load_json(config.feature_052_report),
        "053": _load_json(config.feature_053_report),
    }
    for feature, payload in payloads.items():
        expected_feature_id = EXPECTED_FEATURE_IDS[feature]
        if payload.get("feature_id") != expected_feature_id:
            raise ValueError(f"{config.__class__.__name__} expected {expected_feature_id} in {feature} report")
    return payloads


def _prerequisite_tags_verified() -> list[dict[str, Any]]:
    diff_names = _git_output("diff", "--name-only", "main...HEAD").splitlines()
    return [
        {"name": "branch", "verified": _git_output("branch", "--show-current") == FEATURE_ID, "details": f"git branch --show-current == {FEATURE_ID}"},
        {"name": "not_main", "verified": _git_output("branch", "--show-current") != "main", "details": "current branch != main"},
        {"name": "main_contains_feature_053", "verified": _git_bool("merge-base", "--is-ancestor", FEATURE_053_PREREQUISITE_TAG[:-3], "main"), "details": f"main contains {FEATURE_053_PREREQUISITE_TAG[:-3]}"},
        {"name": "main_contains_054a_hygiene", "verified": _git_bool("merge-base", "--is-ancestor", FEATURE_054A_PREREQUISITE_TAG[:-3], "main"), "details": f"main contains {FEATURE_054A_PREREQUISITE_TAG[:-3]}"},
        {"name": "main_is_branch_base", "verified": _git_output("merge-base", "main", "HEAD") == _git_output("rev-parse", "main"), "details": "branch is based on current main"},
        {"name": "feature_diff_contains_only_approved_paths", "verified": all(
            path.startswith("specs/054-training-readiness-contract/")
            or path.startswith("src/analysis/training_readiness_contract/")
            or path.startswith("tests/unit/test_training_readiness_contract")
            or path.startswith("tests/integration/test_training_readiness_contract")
            or path.startswith("artifacts/analysis/training-readiness-contract/")
            for path in diff_names
        ), "details": "main...HEAD diff contains only approved Feature 054 paths"},
        {"name": "no_feature_037_053_artifact_rewrites", "verified": not any(path.startswith("artifacts/analysis/") and not path.startswith("artifacts/analysis/training-readiness-contract/") for path in diff_names), "details": "no Feature 037-053 artifacts are rewritten"},
        {"name": "agents_stable_not_modified", "verified": "AGENTS.md" not in diff_names, "details": "AGENTS.md is stable and not modified"},
        {"name": "pointer_local_only_not_in_committed_diff", "verified": ".specify/feature.json" not in diff_names, "details": ".specify/feature.json is ignored/local-only and absent from committed diff"},
    ]


def _prior_feature_gates_verified(payloads: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    gates: list[dict[str, Any]] = []
    for feature, path in COMMITTED_INPUT_REPORTS.items():
        payload = payloads[feature]
        gates.append(
            {
                "feature": feature,
                "name": EXPECTED_FEATURE_IDS[feature],
                "verified": path.exists() and payload.get("feature_id") == EXPECTED_FEATURE_IDS[feature],
                "details": f"{path} exists and contains {EXPECTED_FEATURE_IDS[feature]}",
            }
        )
    return gates


def _load_contract_evidence() -> dict[str, dict[str, Any]]:
    return {
        "038": _load_json(FEATURE_038_REPORT),
        "040": _load_json(FEATURE_040_REPORT),
        "041": _load_json(FEATURE_041_REPORT),
        "042": _load_json(FEATURE_042_REPORT),
    }


def _behavior_equivalence_summary(feature_053: dict[str, Any]) -> BehaviorEquivalenceSummary:
    summary = feature_053.get("behavior_equivalence_summary", {})
    checks = [
        {
            "name": str(check.get("name")),
            "verified": bool(check.get("verified")),
            "details": check.get("details", ""),
        }
        for check in summary.get("checks", [])
    ]
    return BehaviorEquivalenceSummary(checks=checks, passed=bool(summary.get("passed")))


def _feature_053_readiness_verified(feature_053: dict[str, Any]) -> bool:
    required_alignment_fields = (
        "observation_vector_alignment_status",
        "formula_unit_alignment_status",
        "exposure_matrix_alignment_status",
        "selected_action_outcome_alignment_status",
        "training_readiness_contract_status",
    )
    return (
        feature_053.get("paper_mechanism_alignment_ready") is True
        and feature_053.get("final_verdict") == "paper_mechanism_alignment_ready_for_training_contract"
        and feature_053.get("remaining_blockers") == []
        and all(feature_053.get(field) == "available" for field in required_alignment_fields)
        and feature_053.get("behavior_equivalence_passed") is True
        and feature_053.get("recommended_next_feature") == "Feature 054 — Training Readiness Contract"
    )


def _current_feature_diff() -> list[str]:
    return _git_output("diff", "--name-only", "main...HEAD").splitlines()


def _no_dependency_drift(diff_names: list[str]) -> bool:
    return not any(Path(path).name in DEPENDENCY_FILE_NAMES for path in diff_names)


def _no_policy_drift(diff_names: list[str]) -> bool:
    return not any(path.startswith("src/policies/") for path in diff_names)


def _no_runtime_semantic_changes(diff_names: list[str]) -> bool:
    return not any(path.startswith("src/environment/") for path in diff_names)


def _no_prior_artifact_rewrite(diff_names: list[str]) -> bool:
    allowed_prefix = str(Path("artifacts/analysis/training-readiness-contract"))
    return not any(path.startswith("artifacts/analysis/") and not path.startswith(allowed_prefix) for path in diff_names)


def _lock_state(
    *,
    feature_038: dict[str, Any],
    feature_040: dict[str, Any],
    feature_041: dict[str, Any],
    feature_042: dict[str, Any],
    feature_048: dict[str, Any],
) -> tuple[bool, ...]:
    paper_default_config_locked = (
        bool(feature_042.get("paper_default_runtime_verified"))
        and feature_042.get("final_verdict") == "terminal_exposure_present"
        and bool(feature_042.get("legal_action_mask_verified"))
        and bool(feature_042.get("pending_at_horizon_contract_verified"))
        and bool(feature_042.get("reward_timing_contract_verified"))
        and all(bool(value) for value in feature_042.get("runtime_contracts_verified", {}).values())
    )
    observation_contract_locked = (
        bool(feature_038.get("state_contract", {}).get("observable_only"))
        and bool(feature_038.get("state_contract", {}).get("no_privileged_future_information"))
        and bool(feature_038.get("state_contract", {}).get("diagnostics_excluded_from_model_input"))
        and bool(feature_041.get("train_eval_split_verified", {}).get("disjoint"))
    )
    action_contract_locked = (
        int(feature_040.get("network_contract_verified", {}).get("action_count", 0)) == 3
        and bool(feature_042.get("legal_action_mask_verified"))
        and int(feature_048.get("selected_illegal_action_count", 1)) == 0
    )
    legality_contract_locked = (
        feature_048.get("selected_illegal_action_evidence_status") == "available"
        and int(feature_048.get("selected_illegal_action_count", 1)) == 0
        and bool(feature_048.get("exposure_matrix_unblocked"))
    )
    reward_contract_locked = (
        feature_038.get("replay_schema", {}).get("delayed_reward_policy") == "reward_available_false_until_terminal"
        and feature_038.get("replay_schema", {}).get("pending_at_horizon_policy") == "explicit_pending_at_horizon"
        and bool(feature_040.get("delayed_reward_contract_verified", {}).get("terminal_reward_available_true"))
        and bool(feature_042.get("reward_timing_contract_verified"))
    )
    timeout_contract_locked = (
        feature_038.get("replay_schema", {}).get("pending_at_horizon_policy") == "explicit_pending_at_horizon"
        and bool(feature_040.get("replay_contract_verified", {}).get("pending_at_horizon_preserved"))
        and bool(feature_042.get("pending_at_horizon_contract_verified"))
    )
    capacity_contract_locked = (
        bool(feature_040.get("no_full_training"))
        and not bool(feature_041.get("checkpoint_schema_verified", {}).get("full_campaign_enabled"))
        and bool(feature_048.get("no_capacity_contract_drift", True))
    )
    transmission_contract_locked = (
        bool(feature_048.get("no_transmission_contract_drift", True))
        and bool(feature_040.get("no_reward_timing_change"))
        and bool(feature_042.get("reward_timing_contract_verified"))
    )
    queue_contract_locked = (
        feature_038.get("state_contract", {}).get("history_buffer_policy") == "separate_history_buffer"
        and bool(feature_040.get("replay_contract_verified", {}).get("pending_at_horizon_preserved"))
        and bool(feature_041.get("terminal_exposure_gate", {}).get("pending_at_horizon", 0) >= 0)
    )
    metric_contract_locked = (
        bool(feature_041.get("evaluation_summary", {}).get("trace_bank_disjoint"))
        and not bool(feature_041.get("evaluation_summary", {}).get("evaluation_on_training_traces"))
        and bool(feature_040.get("loss_summary", {}).get("is_finite"))
    )
    seed_contract_locked = (
        feature_038.get("seed_protocol", {}).get("version") == "1.0"
        and bool(feature_040.get("seed_protocol_verified"))
        and bool(feature_041.get("checkpoint_schema_verified", {}).get("seed_bundle"))
    )
    artifact_contract_locked = (
        bool(feature_038.get("checkpoint_schema", {}).get("metadata_only"))
        and bool(feature_041.get("checkpoint_schema_verified"))
        and feature_041.get("checkpoint_schema_verified", {}).get("stage") == "readiness_probe"
    )
    return (
        paper_default_config_locked,
        observation_contract_locked,
        action_contract_locked,
        legality_contract_locked,
        reward_contract_locked,
        timeout_contract_locked,
        capacity_contract_locked,
        transmission_contract_locked,
        queue_contract_locked,
        metric_contract_locked,
        seed_contract_locked,
        artifact_contract_locked,
    )


def _no_drift_flags(diff_names: list[str]) -> dict[str, bool]:
    return {
        "no_training_started": True,
        "no_optimizer_step": True,
        "no_replay_training": True,
        "no_target_update_execution": True,
        "no_checkpoint_written": True,
        "no_campaign_run": True,
        "no_policy_drift": _no_policy_drift(diff_names),
        "no_runtime_semantic_changes": _no_runtime_semantic_changes(diff_names),
        "no_dependency_drift": _no_dependency_drift(diff_names),
        "no_prior_artifact_rewrite": _no_prior_artifact_rewrite(diff_names),
        "no_paper_reproduction_claim": True,
    }


def _remaining_blockers(
    *,
    prerequisite_tags_verified: bool,
    feature_053_readiness_verified: bool,
    evidence_chain_ready_for_training_contract: bool,
    paper_default_config_locked: bool,
    observation_contract_locked: bool,
    action_contract_locked: bool,
    legality_contract_locked: bool,
    reward_contract_locked: bool,
    timeout_contract_locked: bool,
    capacity_contract_locked: bool,
    transmission_contract_locked: bool,
    queue_contract_locked: bool,
    metric_contract_locked: bool,
    seed_contract_locked: bool,
    artifact_contract_locked: bool,
    behavior_equivalence_passed: bool,
    no_flags: dict[str, bool],
) -> list[str]:
    blockers: list[str] = []
    if not prerequisite_tags_verified:
        blockers.append("prerequisite_tags_failed")
    if not feature_053_readiness_verified:
        blockers.append("feature_053_readiness_failed")
    if not evidence_chain_ready_for_training_contract:
        blockers.append("evidence_chain_prerequisite_blocked")
    if not paper_default_config_locked:
        blockers.append("paper_default_config_contract_blocked")
    if not observation_contract_locked:
        blockers.append("observation_contract_blocked")
    if not action_contract_locked:
        blockers.append("action_contract_blocked")
    if not legality_contract_locked:
        blockers.append("legality_contract_blocked")
    if not reward_contract_locked:
        blockers.append("reward_contract_blocked")
    if not timeout_contract_locked:
        blockers.append("timeout_contract_blocked")
    if not capacity_contract_locked:
        blockers.append("capacity_contract_blocked")
    if not transmission_contract_locked:
        blockers.append("transmission_contract_blocked")
    if not queue_contract_locked:
        blockers.append("queue_contract_blocked")
    if not metric_contract_locked:
        blockers.append("metric_contract_blocked")
    if not seed_contract_locked:
        blockers.append("seed_contract_blocked")
    if not artifact_contract_locked:
        blockers.append("artifact_contract_blocked")
    if not behavior_equivalence_passed:
        blockers.append("behavior_drift_detected")
    for field_name, flag in no_flags.items():
        if not flag:
            blockers.append(field_name)
    return blockers


def _final_verdict(
    *,
    prerequisite_tags_verified: bool,
    feature_053_readiness_verified: bool,
    evidence_chain_ready_for_training_contract: bool,
    paper_default_config_locked: bool,
    observation_contract_locked: bool,
    action_contract_locked: bool,
    legality_contract_locked: bool,
    reward_contract_locked: bool,
    timeout_contract_locked: bool,
    capacity_contract_locked: bool,
    transmission_contract_locked: bool,
    queue_contract_locked: bool,
    metric_contract_locked: bool,
    seed_contract_locked: bool,
    artifact_contract_locked: bool,
    behavior_equivalence_passed: bool,
    no_flags: dict[str, bool],
) -> tuple[bool, str, str]:
    if not prerequisite_tags_verified or not feature_053_readiness_verified or not evidence_chain_ready_for_training_contract:
        return False, "evidence_chain_prerequisite_blocked", BLOCKED_NEXT_FEATURES["evidence_chain_prerequisite_blocked"]
    if not paper_default_config_locked:
        return False, "paper_default_config_contract_blocked", BLOCKED_NEXT_FEATURES["paper_default_config_contract_blocked"]
    if not observation_contract_locked:
        return False, "observation_contract_blocked", BLOCKED_NEXT_FEATURES["observation_contract_blocked"]
    if not action_contract_locked or not legality_contract_locked:
        return False, "action_or_legality_contract_blocked", BLOCKED_NEXT_FEATURES["action_or_legality_contract_blocked"]
    if not reward_contract_locked or not timeout_contract_locked or not capacity_contract_locked or not transmission_contract_locked or not queue_contract_locked:
        return False, "reward_timeout_capacity_contract_blocked", BLOCKED_NEXT_FEATURES["reward_timeout_capacity_contract_blocked"]
    if not metric_contract_locked or not seed_contract_locked or not artifact_contract_locked:
        return False, "metric_or_artifact_contract_blocked", BLOCKED_NEXT_FEATURES["metric_or_artifact_contract_blocked"]
    if not behavior_equivalence_passed or not all(no_flags.values()):
        return False, "behavior_drift_detected", BLOCKED_NEXT_FEATURES["behavior_drift_detected"]
    return True, "training_readiness_contract_ready_for_smoke_run", READY_NEXT_FEATURE


def build_training_readiness_contract_report(
    config: TrainingReadinessContractConfig | None = None,
) -> TrainingReadinessContractReport:
    config = config or TrainingReadinessContractConfig()
    payloads = _load_committed_inputs(config)
    evidence_payloads = _load_contract_evidence()
    feature_053 = payloads["053"]
    feature_053_readiness_verified = _feature_053_readiness_verified(feature_053)
    prerequisite_tags_verified = _prerequisite_tags_verified()
    prerequisite_tags_ready = all(entry["verified"] for entry in prerequisite_tags_verified)
    prior_feature_gates_verified = _prior_feature_gates_verified(payloads)
    evidence_chain_ready_for_training_contract = feature_053_readiness_verified and prerequisite_tags_ready and all(entry["verified"] for entry in prior_feature_gates_verified)
    behavior_equivalence_summary = _behavior_equivalence_summary(feature_053)
    behavior_equivalence_passed = bool(feature_053.get("behavior_equivalence_passed")) and behavior_equivalence_summary.passed
    diff_names = _current_feature_diff()
    no_flags = _no_drift_flags(diff_names)
    (
        paper_default_config_locked,
        observation_contract_locked,
        action_contract_locked,
        legality_contract_locked,
        reward_contract_locked,
        timeout_contract_locked,
        capacity_contract_locked,
        transmission_contract_locked,
        queue_contract_locked,
        metric_contract_locked,
        seed_contract_locked,
        artifact_contract_locked,
    ) = _lock_state(
        feature_038=evidence_payloads["038"],
        feature_040=evidence_payloads["040"],
        feature_041=evidence_payloads["041"],
        feature_042=evidence_payloads["042"],
        feature_048=payloads["048"],
    )
    training_execution_allowed_next, final_verdict, recommended_next_feature = _final_verdict(
        prerequisite_tags_verified=prerequisite_tags_ready,
        feature_053_readiness_verified=feature_053_readiness_verified,
        evidence_chain_ready_for_training_contract=evidence_chain_ready_for_training_contract,
        paper_default_config_locked=paper_default_config_locked,
        observation_contract_locked=observation_contract_locked,
        action_contract_locked=action_contract_locked,
        legality_contract_locked=legality_contract_locked,
        reward_contract_locked=reward_contract_locked,
        timeout_contract_locked=timeout_contract_locked,
        capacity_contract_locked=capacity_contract_locked,
        transmission_contract_locked=transmission_contract_locked,
        queue_contract_locked=queue_contract_locked,
        metric_contract_locked=metric_contract_locked,
        seed_contract_locked=seed_contract_locked,
        artifact_contract_locked=artifact_contract_locked,
        behavior_equivalence_passed=behavior_equivalence_passed,
        no_flags=no_flags,
    )
    remaining_blockers = _remaining_blockers(
        prerequisite_tags_verified=prerequisite_tags_ready,
        feature_053_readiness_verified=feature_053_readiness_verified,
        evidence_chain_ready_for_training_contract=evidence_chain_ready_for_training_contract,
        paper_default_config_locked=paper_default_config_locked,
        observation_contract_locked=observation_contract_locked,
        action_contract_locked=action_contract_locked,
        legality_contract_locked=legality_contract_locked,
        reward_contract_locked=reward_contract_locked,
        timeout_contract_locked=timeout_contract_locked,
        capacity_contract_locked=capacity_contract_locked,
        transmission_contract_locked=transmission_contract_locked,
        queue_contract_locked=queue_contract_locked,
        metric_contract_locked=metric_contract_locked,
        seed_contract_locked=seed_contract_locked,
        artifact_contract_locked=artifact_contract_locked,
        behavior_equivalence_passed=behavior_equivalence_passed,
        no_flags=no_flags,
    )
    if training_execution_allowed_next:
        remaining_blockers = []
    report = TrainingReadinessContractReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=prerequisite_tags_verified,
        prior_feature_gates_verified=prior_feature_gates_verified,
        feature_053_readiness_verified=feature_053_readiness_verified,
        evidence_chain_ready_for_training_contract=evidence_chain_ready_for_training_contract,
        paper_default_config_locked=paper_default_config_locked,
        observation_contract_locked=observation_contract_locked,
        action_contract_locked=action_contract_locked,
        legality_contract_locked=legality_contract_locked,
        reward_contract_locked=reward_contract_locked,
        timeout_contract_locked=timeout_contract_locked,
        capacity_contract_locked=capacity_contract_locked,
        transmission_contract_locked=transmission_contract_locked,
        queue_contract_locked=queue_contract_locked,
        metric_contract_locked=metric_contract_locked,
        seed_contract_locked=seed_contract_locked,
        artifact_contract_locked=artifact_contract_locked,
        behavior_equivalence_summary=behavior_equivalence_summary,
        behavior_equivalence_passed=behavior_equivalence_passed,
        training_execution_allowed_next=training_execution_allowed_next,
        remaining_blockers=remaining_blockers,
        recommended_next_feature=recommended_next_feature,
        no_training_started=no_flags["no_training_started"],
        no_optimizer_step=no_flags["no_optimizer_step"],
        no_replay_training=no_flags["no_replay_training"],
        no_target_update_execution=no_flags["no_target_update_execution"],
        no_checkpoint_written=no_flags["no_checkpoint_written"],
        no_campaign_run=no_flags["no_campaign_run"],
        no_policy_drift=no_flags["no_policy_drift"],
        no_runtime_semantic_changes=no_flags["no_runtime_semantic_changes"],
        no_dependency_drift=no_flags["no_dependency_drift"],
        no_prior_artifact_rewrite=no_flags["no_prior_artifact_rewrite"],
        no_paper_reproduction_claim=no_flags["no_paper_reproduction_claim"],
        final_verdict=final_verdict,
    )
    return report


def run_training_readiness_contract(
    config: TrainingReadinessContractConfig | None = None,
) -> TrainingReadinessContractReport:
    config = config or TrainingReadinessContractConfig()
    report = build_training_readiness_contract_report(config)
    write_training_readiness_contract_report(report, config.output_dir)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Feature 054 training readiness contract analysis.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Override the report output directory.")
    args = parser.parse_args(argv)
    config = TrainingReadinessContractConfig(output_dir=args.output_dir or TrainingReadinessContractConfig().output_dir)
    run_training_readiness_contract(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
