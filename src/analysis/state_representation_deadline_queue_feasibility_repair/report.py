from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import (
    ACTION_COLLAPSE_DIAGNOSTICS_JSON,
    DIAGNOSTIC_DECISION_JSON,
    FEATURE_ID,
    FIGURE_MANIFEST_JSON,
    FINAL_STATE_REPAIR_SUMMARY_MD,
    LEGACY_VS_NEW_STATE_PROFILE_COMPARISON_JSON,
    OUTPUT_DIR,
    POLICY_EFFECT_AFTER_STATE_REPAIR_JSON,
    RECONCILIATION_AFTER_STATE_REPAIR_JSON,
    REPORT_JSON,
    REPORT_MD,
    SELECTED_ACTION_FEASIBILITY_DIAGNOSTICS_JSON,
    STATE_FEATURE_COVERAGE_AUDIT_JSON,
    STATE_NORMALIZATION_AUDIT_JSON,
    STATE_PROFILE_50_100_COMPARISON_JSON,
    STATE_REPRESENTATION_REPAIR_REPORT_JSON,
    STATE_REPRESENTATION_REPAIR_REPORT_MD,
)


def json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json_dump(payload), encoding="utf-8")


def _compact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    compact = dict(payload)
    policy_effect = dict(compact.get("policy_effect_after_state_repair", {}))
    policy_effect.pop("policy_results", None)
    compact["policy_effect_after_state_repair"] = policy_effect
    return compact


def _render_markdown(payload: dict[str, Any]) -> str:
    sections = [
        "# State Representation Repair",
        "",
        f"- feature_id: `{payload['feature_id']}`",
        f"- final_verdict: `{payload['final_verdict']}`",
        f"- diagnostic_decision: `{payload['diagnostic_decision']['recommended_next_action']}`",
        f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
        f"- feature_070_prerequisite_verified: `{payload['feature_070_prerequisite_verified']}`",
        f"- metric_universe_consistency_passed: `{payload['metric_universe_consistency_passed']}`",
        "",
        "## 1. Feature 070 Prerequisite Verification",
        json_dump(
            {
                "prerequisite_artifacts": payload["prerequisite_artifacts"],
                "prerequisite_tags_verified": payload["prerequisite_tags_verified"],
                "scope_guard_summary": payload["scope_guard_summary"],
            }
        ).strip(),
        "",
        "## 2. State Feature Coverage Audit",
        json_dump(payload["state_feature_coverage_audit"]).strip(),
        "",
        "## 3. State Normalization Audit",
        json_dump(payload["state_normalization_audit"]).strip(),
        "",
        "## 4. Legacy vs New State Profile Comparison",
        json_dump(payload["legacy_vs_new_state_profile_comparison"]).strip(),
        "",
        "## 5. 50/100 Comparison",
        json_dump(payload["state_profile_50_100_comparison"]).strip(),
        "",
        "## 6. Action Collapse Diagnostics",
        json_dump(payload["action_collapse_diagnostics"]).strip(),
        "",
        "## 7. Selected-Action Feasibility Diagnostics",
        json_dump(payload["selected_action_feasibility_diagnostics"]).strip(),
        "",
        "## 8. Policy-Effect After State Repair",
        json_dump(payload["policy_effect_after_state_repair"]).strip(),
        "",
        "## 9. Reconciliation After State Repair",
        json_dump(payload["reconciliation_after_state_repair"]).strip(),
        "",
        "## 10. Diagnostic Decision",
        json_dump(payload["diagnostic_decision"]).strip(),
        "",
        "## 11. Claim Safety",
        json_dump(payload["claim_safety_status"]).strip(),
        "",
        "## 12. Figure Manifest",
        json_dump(payload["figure_manifest"]).strip(),
        "",
        "## 13. Final Verdict",
        payload["final_verdict"],
    ]
    return "\n".join(sections) + "\n"


def _render_summary_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Final State Representation Summary",
            "",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- diagnostic_decision: `{payload['diagnostic_decision']['recommended_next_action']}`",
            f"- state_dim: `{payload['new_state_dim']}`",
            f"- reward_reconciliation_passed: `{payload['reconciliation_after_state_repair']['reward_reconciliation_passed']}`",
            f"- terminal_reconciliation_passed: `{payload['reconciliation_after_state_repair']['terminal_reconciliation_passed']}`",
            f"- completion_count_nonzero: `{int(payload['policy_effect_after_state_repair']['candidate_policy_at_100']['completed_count']) > 0}`",
            f"- fixed_policy_completion_present: `{payload['policy_effect_after_state_repair']['any_fixed_policy_completes']}`",
            "",
            "The repaired state vector exposes deadline, queue, and path-feasibility signals without changing reward or policy semantics.",
        ]
    ) + "\n"


def write_state_representation_repair_outputs(payload: dict[str, Any], *, output_dir: Path | None = None) -> tuple[Path, Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    compact_payload = _compact_payload(payload)

    report_json_path = target_dir / REPORT_JSON.name
    report_md_path = target_dir / REPORT_MD.name
    summary_path = target_dir / FINAL_STATE_REPAIR_SUMMARY_MD.name
    report_json_path.write_text(json_dump(compact_payload), encoding="utf-8")
    report_md_path.write_text(_render_markdown(compact_payload), encoding="utf-8")
    summary_path.write_text(_render_summary_markdown(compact_payload), encoding="utf-8")

    _write_json(target_dir / STATE_REPRESENTATION_REPAIR_REPORT_JSON.name, compact_payload)
    (target_dir / STATE_REPRESENTATION_REPAIR_REPORT_MD.name).write_text(_render_markdown(compact_payload), encoding="utf-8")
    _write_json(target_dir / STATE_FEATURE_COVERAGE_AUDIT_JSON.name, compact_payload["state_feature_coverage_audit"])
    _write_json(target_dir / STATE_NORMALIZATION_AUDIT_JSON.name, compact_payload["state_normalization_audit"])
    _write_json(target_dir / LEGACY_VS_NEW_STATE_PROFILE_COMPARISON_JSON.name, compact_payload["legacy_vs_new_state_profile_comparison"])
    _write_json(target_dir / STATE_PROFILE_50_100_COMPARISON_JSON.name, compact_payload["state_profile_50_100_comparison"])
    _write_json(target_dir / ACTION_COLLAPSE_DIAGNOSTICS_JSON.name, compact_payload["action_collapse_diagnostics"])
    _write_json(target_dir / SELECTED_ACTION_FEASIBILITY_DIAGNOSTICS_JSON.name, compact_payload["selected_action_feasibility_diagnostics"])
    _write_json(target_dir / POLICY_EFFECT_AFTER_STATE_REPAIR_JSON.name, compact_payload["policy_effect_after_state_repair"])
    _write_json(target_dir / RECONCILIATION_AFTER_STATE_REPAIR_JSON.name, compact_payload["reconciliation_after_state_repair"])
    _write_json(target_dir / DIAGNOSTIC_DECISION_JSON.name, compact_payload["diagnostic_decision"])
    _write_json(target_dir / FIGURE_MANIFEST_JSON.name, compact_payload["figure_manifest"])

    return report_json_path, report_md_path, summary_path
