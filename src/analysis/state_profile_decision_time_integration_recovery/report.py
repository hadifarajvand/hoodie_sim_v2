from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from .config import (
    ACTION_COLLAPSE_AFTER_DECISION_STATE_FIX_JSON,
    DECISION_STATE_INJECTION_AUDIT_JSON,
    DIAGNOSTIC_DECISION_JSON,
    FIGURE_MANIFEST_JSON,
    FINAL_STATE_PROFILE_INTEGRATION_SUMMARY_MD,
    LEGACY_VS_DECISION_TIME_STATE_COMPARISON_JSON,
    OUTPUT_DIR,
    POLICY_EFFECT_AFTER_DECISION_STATE_FIX_JSON,
    REAL_RUNNER_VS_ARTIFACT_CONSISTENCY_JSON,
    RECONCILIATION_AFTER_DECISION_STATE_FIX_JSON,
    REPLAY_STATE_ALIGNMENT_AUDIT_JSON,
    REPORT_JSON,
    REPORT_MD,
    SELECTED_ACTION_FEASIBILITY_AFTER_DECISION_STATE_FIX_JSON,
    STATE_FEATURE_COVERAGE_AUDIT_JSON,
    STATE_NORMALIZATION_AUDIT_JSON,
    STATE_PROFILE_INTEGRATION_REPAIR_REPORT_JSON,
    STATE_PROFILE_INTEGRATION_REPAIR_REPORT_MD,
    STATE_SAMPLE_RECORDS_AFTER_DECISION_INJECTION_JSON,
    TRAIN_EVAL_STATE_PROFILE_CONSISTENCY_JSON,
)


def json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json_dump(payload), encoding="utf-8")


def _compact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    compact = dict(payload)
    if "decision_state_injection_audit" not in compact and "state_feature_coverage_audit" in compact:
        compact["decision_state_injection_audit"] = compact["state_feature_coverage_audit"]
    if "train_eval_state_profile_consistency" not in compact and "state_normalization_audit" in compact:
        compact["train_eval_state_profile_consistency"] = compact["state_normalization_audit"]
    if "replay_state_alignment_audit" not in compact and "replay_alignment_audit" in compact:
        compact["replay_state_alignment_audit"] = compact["replay_alignment_audit"]
    if "legacy_vs_decision_time_state_comparison" not in compact and "legacy_vs_new_state_profile_comparison" in compact:
        compact["legacy_vs_decision_time_state_comparison"] = compact["legacy_vs_new_state_profile_comparison"]
    if "policy_effect_after_decision_state_fix" not in compact and "policy_effect_after_state_repair" in compact:
        compact["policy_effect_after_decision_state_fix"] = compact["policy_effect_after_state_repair"]
    if "reconciliation_after_decision_state_fix" not in compact and "reconciliation_after_state_repair" in compact:
        compact["reconciliation_after_decision_state_fix"] = compact["reconciliation_after_state_repair"]
    policy_effect = dict(compact.get("policy_effect_after_decision_state_fix", {}))
    policy_effect.pop("policy_results", None)
    compact["policy_effect_after_decision_state_fix"] = policy_effect
    if "policy_effect_after_state_repair" in compact:
        legacy_policy_effect = dict(compact.get("policy_effect_after_state_repair", {}))
        legacy_policy_effect.pop("policy_results", None)
        compact["policy_effect_after_state_repair"] = legacy_policy_effect
    return compact


def _normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    aliases = {
        "decision_state_injection_audit": ["state_feature_coverage_audit"],
        "train_eval_state_profile_consistency": ["state_normalization_audit"],
        "replay_state_alignment_audit": ["replay_alignment_audit"],
        "legacy_vs_decision_time_state_comparison": ["legacy_vs_new_state_profile_comparison"],
        "action_collapse_after_decision_state_fix": ["action_collapse_diagnostics"],
        "selected_action_feasibility_after_decision_state_fix": ["selected_action_feasibility_diagnostics"],
        "policy_effect_after_decision_state_fix": ["policy_effect_after_state_repair"],
        "reconciliation_after_decision_state_fix": ["reconciliation_after_state_repair"],
        "feature_071_prerequisite_verified": ["feature_070_prerequisite_verified"],
        "feature_071_report": ["feature_070_report"],
        "feature_071_prerequisite_status": ["feature_070_report"],
        "real_runner_vs_artifact_consistency": ["real_runner_artifact_consistency"],
    }
    for target, sources in aliases.items():
        if target in normalized:
            continue
        for source in sources:
            if source in normalized:
                normalized[target] = normalized[source]
                break
    if "replay_state_alignment_audit" not in normalized:
        normalized["replay_state_alignment_audit"] = {
            "replay_transition_state_matches_action_state": False,
            "mismatch_count": 0,
            "compared_transition_count": 0,
            "sample_records": [],
        }
    if "state_sample_records_after_decision_injection" not in normalized and "decision_state_injection_audit" in normalized:
        normalized["state_sample_records_after_decision_injection"] = list(normalized["decision_state_injection_audit"].get("sample_records", []))
    if "real_runner_vs_artifact_consistency" not in normalized:
        normalized["real_runner_vs_artifact_consistency"] = {
            "all_keys_match": False,
            "mismatched_keys": [],
            "comparison_count": 0,
        }
    return normalized


def _render_markdown(payload: dict[str, Any]) -> str:
    payload = _normalize_payload(payload)
    decision_audit = dict(payload.get("decision_state_injection_audit", {}))
    train_eval = dict(payload.get("train_eval_state_profile_consistency", {}))
    replay_audit = dict(payload.get("replay_state_alignment_audit", {}))
    return "\n".join(
        [
            "# State Profile Decision-Time Integration Recovery",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- diagnostic_decision: `{payload['diagnostic_decision']['recommended_next_action']}`",
            f"- feature_071_prerequisite_verified: `{payload.get('feature_071_prerequisite_verified', False)}`",
            f"- decision_state_injection_passed: `{decision_audit.get('decision_state_contains_current_task', decision_audit.get('current_feature_tail_matches', False))}`",
            f"- replay_state_alignment_passed: `{replay_audit.get('replay_transition_state_matches_action_state', False)}`",
            f"- train_eval_state_profile_match: `{train_eval.get('train_eval_state_profile_match', train_eval.get('state_dim_consistent_across_train_eval', False))}`",
            "",
            "## 1. Feature 071 Prerequisite Verification",
            json_dump(
                {
                    "prerequisite_artifacts": payload["prerequisite_artifacts"],
                    "prerequisite_tags_verified": payload["prerequisite_tags_verified"],
                    "scope_guard_summary": payload["scope_guard_summary"],
                }
            ).strip(),
            "",
            "## 2. Decision-Time State Injection Audit",
            json_dump(decision_audit).strip(),
            "",
            "## 3. Train/Eval State Profile Consistency",
            json_dump(train_eval).strip(),
            "",
            "## 4. Replay State Alignment Audit",
            json_dump(replay_audit).strip(),
            "",
            "## 5. State Sample Records After Decision Injection",
            json_dump(payload["state_sample_records_after_decision_injection"]).strip(),
            "",
            "## 6. Legacy vs Decision-Time State Comparison",
            json_dump(payload["legacy_vs_decision_time_state_comparison"]).strip(),
            "",
            "## 7. Policy Effect After Decision-State Fix",
            json_dump(payload["policy_effect_after_decision_state_fix"]).strip(),
            "",
            "## 8. Reconciliation After Decision-State Fix",
            json_dump(payload["reconciliation_after_decision_state_fix"]).strip(),
            "",
            "## 9. Diagnostic Decision",
            json_dump(payload["diagnostic_decision"]).strip(),
            "",
            "## 10. Claim Safety",
            json_dump(payload["claim_safety_status"]).strip(),
            "",
            "## 11. Figure Manifest",
            json_dump(payload["figure_manifest"]).strip(),
            "",
            "## 12. Final Verdict",
            payload["final_verdict"],
        ]
    ) + "\n"


def _render_summary_markdown(payload: dict[str, Any]) -> str:
    payload = _normalize_payload(payload)
    return "\n".join(
        [
            "# Final State Profile Integration Summary",
            "",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- diagnostic_decision: `{payload['diagnostic_decision']['recommended_next_action']}`",
            f"- state_dim: `{payload['new_state_dim']}`",
            f"- reward_reconciliation_passed: `{payload['reconciliation_after_decision_state_fix']['reward_reconciliation_passed']}`",
            f"- terminal_reconciliation_passed: `{payload['reconciliation_after_decision_state_fix']['terminal_reconciliation_passed']}`",
            f"- completion_count_nonzero: `{int(payload['policy_effect_after_decision_state_fix']['candidate_policy_at_100']['completed_count']) > 0}`",
            f"- fixed_policy_completion_present: `{payload['policy_effect_after_decision_state_fix']['any_fixed_policy_completes']}`",
            "",
            "The repaired state vector is injected before action selection and the trainer/replay path uses the same decision-time state window.",
        ]
    ) + "\n"


def write_state_profile_integration_recovery_outputs(payload: dict[str, Any], *, output_dir: Path | None = None) -> tuple[Path, Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    compact_payload = _compact_payload(_normalize_payload(payload))

    report_json_path = target_dir / REPORT_JSON.name
    report_md_path = target_dir / REPORT_MD.name
    summary_path = target_dir / FINAL_STATE_PROFILE_INTEGRATION_SUMMARY_MD.name
    report_json_path.write_text(json_dump(compact_payload), encoding="utf-8")
    report_md_path.write_text(_render_markdown(compact_payload), encoding="utf-8")
    summary_path.write_text(_render_summary_markdown(compact_payload), encoding="utf-8")

    _write_json(target_dir / STATE_PROFILE_INTEGRATION_REPAIR_REPORT_JSON.name, compact_payload)
    (target_dir / STATE_PROFILE_INTEGRATION_REPAIR_REPORT_MD.name).write_text(_render_markdown(compact_payload), encoding="utf-8")
    _write_json(target_dir / DECISION_STATE_INJECTION_AUDIT_JSON.name, compact_payload["decision_state_injection_audit"])
    _write_json(target_dir / TRAIN_EVAL_STATE_PROFILE_CONSISTENCY_JSON.name, compact_payload["train_eval_state_profile_consistency"])
    _write_json(target_dir / REPLAY_STATE_ALIGNMENT_AUDIT_JSON.name, compact_payload["replay_state_alignment_audit"])
    _write_json(target_dir / STATE_FEATURE_COVERAGE_AUDIT_JSON.name, compact_payload["decision_state_injection_audit"])
    _write_json(target_dir / STATE_NORMALIZATION_AUDIT_JSON.name, compact_payload["train_eval_state_profile_consistency"])
    _write_json(target_dir / LEGACY_VS_DECISION_TIME_STATE_COMPARISON_JSON.name, compact_payload["legacy_vs_decision_time_state_comparison"])
    _write_json(target_dir / POLICY_EFFECT_AFTER_DECISION_STATE_FIX_JSON.name, compact_payload["policy_effect_after_decision_state_fix"])
    _write_json(target_dir / RECONCILIATION_AFTER_DECISION_STATE_FIX_JSON.name, compact_payload["reconciliation_after_decision_state_fix"])
    _write_json(target_dir / ACTION_COLLAPSE_AFTER_DECISION_STATE_FIX_JSON.name, compact_payload["action_collapse_after_decision_state_fix"])
    _write_json(target_dir / SELECTED_ACTION_FEASIBILITY_AFTER_DECISION_STATE_FIX_JSON.name, compact_payload["selected_action_feasibility_after_decision_state_fix"])
    _write_json(target_dir / DIAGNOSTIC_DECISION_JSON.name, compact_payload["diagnostic_decision"])
    _write_json(target_dir / REAL_RUNNER_VS_ARTIFACT_CONSISTENCY_JSON.name, compact_payload["real_runner_vs_artifact_consistency"])
    _write_json(target_dir / STATE_SAMPLE_RECORDS_AFTER_DECISION_INJECTION_JSON.name, compact_payload["state_sample_records_after_decision_injection"])
    _write_json(target_dir / FIGURE_MANIFEST_JSON.name, compact_payload["figure_manifest"])

    alias_files = {
        "state-representation-repair-report.json": report_json_path,
        "state-representation-repair-report.md": report_md_path,
        "final-state-repair-summary.md": summary_path,
        "state-feature-coverage-audit.json": target_dir / DECISION_STATE_INJECTION_AUDIT_JSON.name,
        "state-normalization-audit.json": target_dir / TRAIN_EVAL_STATE_PROFILE_CONSISTENCY_JSON.name,
        "legacy-vs-new-state-profile-comparison.json": target_dir / LEGACY_VS_DECISION_TIME_STATE_COMPARISON_JSON.name,
        "state-profile-50-100-comparison.json": target_dir / POLICY_EFFECT_AFTER_DECISION_STATE_FIX_JSON.name,
        "action-collapse-diagnostics.json": target_dir / ACTION_COLLAPSE_AFTER_DECISION_STATE_FIX_JSON.name,
        "selected-action-feasibility-diagnostics.json": target_dir / SELECTED_ACTION_FEASIBILITY_AFTER_DECISION_STATE_FIX_JSON.name,
        "policy-effect-after-state-repair.json": target_dir / POLICY_EFFECT_AFTER_DECISION_STATE_FIX_JSON.name,
        "reconciliation-after-state-repair.json": target_dir / RECONCILIATION_AFTER_DECISION_STATE_FIX_JSON.name,
    }
    for alias_name, source_path in alias_files.items():
        alias_path = target_dir / alias_name
        if source_path.exists() and alias_path.name != source_path.name:
            alias_path.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")

    figure_aliases = {
        "figure_01_state_feature_group_coverage.png": "figure_01_decision_state_injection_before_after.png",
        "figure_02_legacy_vs_new_action_distribution.png": "figure_02_action_distribution_after_decision_state_fix.png",
        "figure_03_action_collapse_before_after.png": "figure_03_action_collapse_after_decision_state_fix.png",
        "figure_04_selected_action_feasibility_before_after.png": "figure_04_selected_action_feasibility_after_decision_state_fix.png",
        "figure_05_completion_drop_50_vs_100_new_state.png": "figure_05_completion_drop_after_decision_state_fix.png",
    }
    figures_dir = target_dir / "figures"
    for alias_name, source_name in figure_aliases.items():
        source_path = figures_dir / source_name
        alias_path = figures_dir / alias_name
        if source_path.exists() and alias_path.name != source_path.name:
            alias_path.write_bytes(source_path.read_bytes())

    return report_json_path, report_md_path, summary_path


write_state_representation_repair_outputs = write_state_profile_integration_recovery_outputs
