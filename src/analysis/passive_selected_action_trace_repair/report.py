from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from .config import DEFAULT_JSON_FILENAME, DEFAULT_MARKDOWN_FILENAME, DEFAULT_OUTPUT_DIR
from .model import PassiveSelectedActionTraceRepairReport


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_passive_selected_action_trace_repair_report(
    report: PassiveSelectedActionTraceRepairReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / DEFAULT_JSON_FILENAME
    md_path = target_dir / DEFAULT_MARKDOWN_FILENAME
    payload = report.to_dict()
    json_path.write_text(_json_dump(payload), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    return json_path, md_path


def _render_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Passive Selected-Action Trace Repair Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
            f"- behavior_equivalence_passed: `{payload['behavior_equivalence_passed']}`",
            f"- selected_action_family_evidence_status: `{payload['selected_action_family_evidence_status']}`",
            f"- selected_action_to_task_join_status: `{payload['selected_action_to_task_join_status']}`",
            f"- terminal_outcome_join_status: `{payload['terminal_outcome_join_status']}`",
            f"- per_action_outcome_join_readiness: `{payload['per_action_outcome_join_readiness']}`",
            f"- evidence_readiness_for_feature_050_rerun: `{payload['evidence_readiness_for_feature_050_rerun']}`",
            "",
            "## Selected Action Trace Schema",
            _json_dump(payload["selected_action_trace_schema"]).strip(),
            "",
            "## Selected Action Trace Emission Summary",
            _json_dump(payload["selected_action_trace_emission_summary"]).strip(),
            "",
            "## Selected Action Family Trace Summary",
            _json_dump(payload["selected_action_family_trace_summary"]).strip(),
            "",
            "## Selected Action To Task Join Summary",
            _json_dump(payload["selected_action_to_task_join_summary"]).strip(),
            "",
            "## Terminal Outcome Join Key Summary",
            _json_dump(payload["terminal_outcome_join_key_summary"]).strip(),
            "",
            "## Behavior Equivalence Summary",
            _json_dump(payload["behavior_equivalence_summary"]).strip(),
            "",
            "## Evidence Readiness",
            _json_dump(
                {
                    "evidence_readiness_for_feature_050_rerun": payload["evidence_readiness_for_feature_050_rerun"],
                    "remaining_blockers": payload["remaining_blockers"],
                    "selected_action_family_evidence_status": payload["selected_action_family_evidence_status"],
                    "selected_action_to_task_join_status": payload["selected_action_to_task_join_status"],
                    "terminal_outcome_join_status": payload["terminal_outcome_join_status"],
                    "per_action_outcome_join_readiness": payload["per_action_outcome_join_readiness"],
                }
            ).strip(),
        ]
    )
