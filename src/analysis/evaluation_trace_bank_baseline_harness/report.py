from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from .config import OUTPUT_DIR, REPORT_JSON, REPORT_MD
from .model import EvaluationTraceBankBaselineHarnessReport


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _render_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Evaluation Trace Bank Baseline Harness Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
            f"- feature_057_pilot_verified: `{payload['feature_057_pilot_verified']}`",
            "",
            "## Evaluation Trace Bank Summary",
            _json_dump(payload["evaluation_trace_bank_summary"]).strip(),
            "",
            "## Train/Eval Separation Summary",
            _json_dump(payload["train_eval_separation_summary"]).strip(),
            "",
            "## Baseline Policy Registry Summary",
            _json_dump(payload["baseline_policy_registry_summary"]).strip(),
            "",
            "## Baseline Evaluation Harness Summary",
            _json_dump(payload["baseline_evaluation_harness_summary"]).strip(),
            "",
            "## Metric Schema Summary",
            _json_dump(payload["metric_schema_summary"]).strip(),
            "",
            "## Determinism Summary",
            _json_dump(payload["determinism_summary"]).strip(),
            "",
            "## Behavior Safety Summary",
            _json_dump(payload["behavior_safety_summary"]).strip(),
            "",
            "## Remaining Blockers",
            _json_dump(payload["remaining_blockers"]).strip(),
        ]
    )


def write_evaluation_trace_bank_baseline_harness_report(
    report: EvaluationTraceBankBaselineHarnessReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = report.to_dict()
    json_path = target_dir / REPORT_JSON.name
    md_path = target_dir / REPORT_MD.name
    json_path.write_text(_json_dump(payload), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    return json_path, md_path
