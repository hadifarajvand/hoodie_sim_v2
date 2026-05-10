from __future__ import annotations

from pathlib import Path
import json

from .sweeps import ControlledMechanisticSweepReport


DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/controlled-mechanistic-sweeps")
JSON_FILENAME = "controlled-mechanistic-sweeps.json"
MARKDOWN_FILENAME = "controlled-mechanistic-sweeps.md"


def _json_dump(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def render_markdown(report: ControlledMechanisticSweepReport) -> str:
    payload = report.to_dict()
    lines: list[str] = []
    lines.append("# Controlled Mechanistic Sweeps")
    lines.append("")
    lines.append("## Metadata")
    for key in ("feature_id", "generated_by", "deterministic", "source_refs"):
        value = payload["metadata"].get(key)
        lines.append(f"- **{key}**: {value}")
    lines.append("")
    lines.append("## Sweep Definitions")
    for sweep in payload["sweep_definitions"]:
        lines.append(f"### {sweep['name']}")
        lines.append(f"- parameter: {sweep['parameter']}")
        lines.append(f"- values: {sweep['values']}")
        lines.append(f"- fixed_seeds: {sweep['fixed_seeds']}")
        lines.append(f"- expected_direction: {sweep['expected_direction']}")
        lines.append(f"- control_source: {sweep['control_source']}")
    lines.append("")
    lines.append("## Fixed Inputs")
    for item in payload["fixed_inputs"]:
        lines.append(f"- {item['sweep_name']} seed={item['seed']} value={item['parameter_value']} trace={item['trace_identifier']}")
    lines.append("")
    lines.append("## Observations")
    for item in payload["observations"]:
        lines.append(
            f"- {item['sweep_name']} seed={item['seed']} value={item['parameter_value']} "
            f"indicator={item['observed_pressure_indicator']} evidence={item['evidence_available']} "
            f"summary={item['observed_outcome_summary']}"
        )
    lines.append("")
    lines.append("## Monotonic Checks")
    for item in payload["monotonic_checks"]:
        lines.append(f"- {item['sweep_name']}: {item['status']} ({item['support_level']}) - {item['rationale']}")
    lines.append("")
    lines.append("## Warnings")
    if payload["warnings"]:
        for warning in payload["warnings"]:
            lines.append(f"- {warning}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Instrumentation Gaps")
    if payload["instrumentation_gaps"]:
        for gap in payload["instrumentation_gaps"]:
            lines.append(f"- {gap}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Limitations")
    for item in payload["limitations"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append(f"## No Campaign Rerun Disclaimer\n{payload['no_campaign_rerun_disclaimer']}")
    lines.append("")
    lines.append(f"## No Paper Validity Disclaimer\n{payload['no_paper_validity_disclaimer']}")
    lines.append("")
    lines.append("## Reproducibility")
    for key, value in payload["reproducibility"].items():
        lines.append(f"- **{key}**: {value}")
    lines.append("")
    lines.append(f"## Overall Status\n{payload['overall_status']}")
    lines.append("")
    return "\n".join(lines)


def write_controlled_mechanistic_sweep_report(report: ControlledMechanisticSweepReport, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / JSON_FILENAME
    markdown_path = target_dir / MARKDOWN_FILENAME
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, markdown_path
