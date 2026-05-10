from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import json
from typing import Any


DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/baseline-rebuild-sensitivity-audit")
JSON_FILENAME = "baseline-rebuild-sensitivity-audit.json"
MARKDOWN_FILENAME = "baseline-rebuild-sensitivity-audit.md"
CSV_FILENAME = "baseline-rebuild-sensitivity-audit.csv"


def _json_dump(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@dataclass(slots=True)
class BaselineRebuildSensitivityAuditReport:
    metadata: dict[str, Any]
    source_gate_status: dict[str, Any]
    sensitivity_dimensions: dict[str, Any]
    seeds_scenarios_episode_lengths_used: dict[str, Any]
    fairness_controls: dict[str, Any]
    included_baselines: list[str]
    reused_metrics: list[str]
    per_setting_baseline_signatures: list[dict[str, Any]]
    collapse_stability_indicators: list[dict[str, Any]]
    sensitivity_classification: dict[str, Any]
    limitations: list[str]
    no_training_disclaimer: str
    no_policy_redesign_disclaimer: str
    no_metric_change_disclaimer: str
    no_paper_validity_disclaimer: str
    reproducibility: dict[str, Any]
    overall_status: str

    def to_dict(self) -> dict[str, object]:
        return {
            "metadata": dict(self.metadata),
            "source_gate_status": dict(self.source_gate_status),
            "sensitivity_dimensions": dict(self.sensitivity_dimensions),
            "seeds_scenarios_episode_lengths_used": dict(self.seeds_scenarios_episode_lengths_used),
            "fairness_controls": dict(self.fairness_controls),
            "included_baselines": list(self.included_baselines),
            "reused_metrics": list(self.reused_metrics),
            "per_setting_baseline_signatures": list(self.per_setting_baseline_signatures),
            "collapse_stability_indicators": list(self.collapse_stability_indicators),
            "sensitivity_classification": dict(self.sensitivity_classification),
            "limitations": list(self.limitations),
            "no_training_disclaimer": self.no_training_disclaimer,
            "no_policy_redesign_disclaimer": self.no_policy_redesign_disclaimer,
            "no_metric_change_disclaimer": self.no_metric_change_disclaimer,
            "no_paper_validity_disclaimer": self.no_paper_validity_disclaimer,
            "reproducibility": dict(self.reproducibility),
            "overall_status": self.overall_status,
        }


def render_markdown(report: BaselineRebuildSensitivityAuditReport) -> str:
    payload = report.to_dict()
    lines: list[str] = []
    lines.append("# Baseline Rebuild Sensitivity Audit")
    lines.append("")
    lines.append("## Metadata")
    for key in ("feature_id", "generated_by", "deterministic", "source_refs"):
        lines.append(f"- **{key}**: {payload['metadata'].get(key)}")
    lines.append("")
    lines.append("## Source Gate Status")
    lines.append(f"- **passed**: {payload['source_gate_status'].get('passed')}")
    for item in payload["source_gate_status"].get("checks", []):
        lines.append(f"- **{item['artifact']}**: valid={item['valid']} details={item['details']}")
    lines.append("")
    lines.append("## Sensitivity Dimensions")
    for key, value in payload["sensitivity_dimensions"].items():
        lines.append(f"- **{key}**: {value}")
    lines.append("")
    lines.append("## Used Settings")
    for key, value in payload["seeds_scenarios_episode_lengths_used"].items():
        lines.append(f"- **{key}**: {value}")
    lines.append("")
    lines.append("## Fairness Controls")
    for key, value in payload["fairness_controls"].items():
        lines.append(f"- **{key}**: {value}")
    lines.append("")
    lines.append("## Included Baselines")
    for baseline in payload["included_baselines"]:
        lines.append(f"- {baseline}")
    lines.append("")
    lines.append("## Reused Metrics")
    for metric in payload["reused_metrics"]:
        lines.append(f"- {metric}")
    lines.append("")
    lines.append("## Baseline Signatures")
    for setting in payload["per_setting_baseline_signatures"]:
        lines.append(
            f"- seed={setting['seed']} scenario={setting['scenario_name']} episode_length={setting['episode_length']}"
        )
        for policy_name, signature in setting["baseline_signatures"].items():
            lines.append(f"  - {policy_name}: {signature}")
    lines.append("")
    lines.append("## Collapse Stability Indicators")
    for item in payload["collapse_stability_indicators"]:
        lines.append(
            f"- seed={item['seed']} scenario={item['scenario_name']} episode_length={item['episode_length']} "
            f"status={item['status']} support={item['support_level']} note={item['note']}"
        )
    lines.append("")
    lines.append("## Sensitivity Classification")
    lines.append(f"- **status**: {payload['sensitivity_classification'].get('status')}")
    for note in payload["sensitivity_classification"].get("notes", []):
        lines.append(f"- {note}")
    lines.append("")
    lines.append("## Limitations")
    for item in payload["limitations"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## No Training Disclaimer")
    lines.append(payload["no_training_disclaimer"])
    lines.append("")
    lines.append("## No Policy Redesign Disclaimer")
    lines.append(payload["no_policy_redesign_disclaimer"])
    lines.append("")
    lines.append("## No Metric Change Disclaimer")
    lines.append(payload["no_metric_change_disclaimer"])
    lines.append("")
    lines.append("## No Paper Validity Disclaimer")
    lines.append(payload["no_paper_validity_disclaimer"])
    lines.append("")
    lines.append("## Reproducibility")
    for key, value in payload["reproducibility"].items():
        lines.append(f"- **{key}**: {value}")
    lines.append("")
    lines.append(f"## Overall Status\n{payload['overall_status']}")
    lines.append("")
    return "\n".join(lines)


def write_baseline_rebuild_sensitivity_audit_report(
    report: BaselineRebuildSensitivityAuditReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / JSON_FILENAME
    markdown_path = target_dir / MARKDOWN_FILENAME
    csv_path = target_dir / CSV_FILENAME
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "seed",
                "scenario_name",
                "episode_length",
                "status",
                "support_level",
            ],
        )
        writer.writeheader()
        for item in report.collapse_stability_indicators:
            writer.writerow(
                {
                    "seed": item["seed"],
                    "scenario_name": item["scenario_name"],
                    "episode_length": item["episode_length"],
                    "status": item["status"],
                    "support_level": item["support_level"],
                }
            )
    return json_path, markdown_path
