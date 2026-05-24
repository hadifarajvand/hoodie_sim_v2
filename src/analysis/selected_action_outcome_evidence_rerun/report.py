from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from .config import DEFAULT_JSON_FILENAME, DEFAULT_MARKDOWN_FILENAME, DEFAULT_OUTPUT_DIR
from .model import SelectedActionOutcomeEvidenceRerunReport


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_selected_action_outcome_evidence_rerun_report(
    report: SelectedActionOutcomeEvidenceRerunReport,
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
            "# Selected-Action Outcome Evidence Rerun Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
            f"- feature_051_trace_readiness_verified: `{payload['feature_051_trace_readiness_verified']}`",
            f"- selected_action_family_evidence_status: `{payload['selected_action_family_evidence_status']}`",
            f"- selected_action_to_task_join_status: `{payload['selected_action_to_task_join_status']}`",
            f"- per_action_outcome_evidence_status: `{payload['per_action_outcome_evidence_status']}`",
            f"- feature_049_can_be_rerun: `{payload['feature_049_can_be_rerun']}`",
            "",
            "## Feature 049 Unblock Assessment",
            _json_dump(payload["feature_049_unblock_assessment"]).strip(),
            "",
            "## Selected Action Family Evidence Summary",
            _json_dump(payload["selected_action_family_evidence_summary"]).strip(),
            "",
            "## Selected Action To Task Join Summary",
            _json_dump(payload["selected_action_to_task_join_summary"]).strip(),
            "",
            "## Per Action Outcome Join Summary",
            _json_dump(payload["per_action_outcome_join_summary"]).strip(),
            "",
            "## Legal But Unselected Consistency Summary",
            _json_dump(payload["legal_but_unselected_consistency_summary"]).strip(),
            "",
            "## Exposure Matrix Internal Consistency Summary",
            _json_dump(payload["exposure_matrix_internal_consistency_summary"]).strip(),
            "",
            "## Behavior Equivalence Summary",
            _json_dump(payload["behavior_equivalence_summary"]).strip(),
        ]
    )
