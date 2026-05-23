from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from .model import BehaviorEquivalenceCheck, LegalityEvidenceReport

FEATURE_ID = "048-legality-evidence-expansion"
DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/legality-evidence-expansion")
JSON_FILENAME = "legality-evidence-report.json"
MARKDOWN_FILENAME = "legality-evidence-report.md"


def _json_dump(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _report_dict(report: LegalityEvidenceReport) -> dict[str, Any]:
    return report.to_dict()


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Legality Evidence Expansion Report",
        "",
        f"- feature_id: `{payload['feature_id']}`",
        f"- final_verdict: `{payload['final_verdict']}`",
        f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
        f"- legal_evidence_coverage_ratio: `{payload['legal_evidence_coverage_ratio']}`",
        "",
        "## Coverage Summary",
        _json_dump(payload["legality_evidence_coverage_summary"]).strip(),
        "",
        "## Selected Illegal Action Summary",
        _json_dump(payload["selected_illegal_action_summary"]).strip(),
        "",
        "## Behavior Equivalence Summary",
        _json_dump(payload["behavior_equivalence_summary"]).strip(),
        "",
        "## Per-Strategy Coverage",
        _json_dump(payload["per_strategy_seed_legality_coverage"]).strip(),
    ]
    return "\n".join(lines)


def write_legality_evidence_report(report: LegalityEvidenceReport, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / JSON_FILENAME
    markdown_path = target_dir / MARKDOWN_FILENAME
    payload = _report_dict(report)
    json_path.write_text(_json_dump(payload), encoding="utf-8")
    markdown_path.write_text(_render_markdown(payload), encoding="utf-8")
    return json_path, markdown_path

